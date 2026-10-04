"""
ReqAgent AI processor.

Turns a raw stakeholder requirement into user stories, acceptance criteria,
and conflict flags.

Design rules:
  - Priority and MoSCoW are decided in CODE from the submitter's role.
    The model never decides them; whatever it returns is overwritten.
  - Model output is never trusted blindly: JSON mode + schema validation +
    bounded retries. If it still fails, a clear ProcessingError is raised
    instead of crashing the app.
  - Every call records model, latency, attempts, and token usage in
    result["_meta"] so we can measure cost/latency in evals later.
"""

import os
import json
import time

from groq import Groq
import groq
from dotenv import load_dotenv

load_dotenv()


def _get(key, default=""):
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Primary model can be changed without a code deploy by setting GROQ_MODEL
# in .env or Streamlit secrets. Fallbacks are tried only if a model has
# been retired / is not found on Groq.
PRIMARY_MODEL = _get("GROQ_MODEL", "openai/gpt-oss-120b")
FALLBACK_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]

MAX_ATTEMPTS = 3          # attempts per model for bad JSON / transient errors
MAX_EXISTING_REQS = 50    # cap on backlog items sent for conflict detection
NO_CONFLICT_TEXT = "No conflicts detected."   # the UI checks for this exact text

ROLE_PRIORITY_MAP = {
    "C-Suite / Executive": "High",
    "VP / Director": "High",
    "Department Head / Manager": "Medium",
    "Team Lead": "Medium",
    "End User": "Low",
    "External Stakeholder": "Low",
}

ROLE_MOSCOW_MAP = {
    "C-Suite / Executive": "Must Have",
    "VP / Director": "Must Have",
    "Department Head / Manager": "Should Have",
    "Team Lead": "Should Have",
    "End User": "Could Have",
    "External Stakeholder": "Could Have",
}


class ProcessingError(Exception):
    """Raised when the AI could not produce a valid analysis.

    user_message is safe to show in the UI.
    """

    def __init__(self, user_message, detail=""):
        super().__init__(f"{user_message} | {detail}")
        self.user_message = user_message
        self.detail = detail


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

def _build_prompt(title, description, department, role, objective,
                  existing_text, priority, moscow):
    return f"""
You are a senior Business Systems Analyst. Analyze the business requirement below.

REQUIREMENT DETAILS:
Title: {title}
Description: {description}
Department: {department}
Submitter Role: {role}
Business Objective: {objective}

PRIORITY (fixed by policy, do not change): {priority}
MOSCOW (fixed by policy, do not change): {moscow}

EXISTING REQUIREMENTS IN SYSTEM:
{existing_text}

Your task:
1. Write 3 user stories in "As a [user], I want to [action] so that [benefit]" format.
2. For each story, write 2-3 acceptance criteria in "Given... When... Then..." format.
3. Write a one-sentence priority justification.
4. Identify real conflicts or overlaps with EXISTING requirements only. Use the REQ id
   exactly as listed. Do not invent requirements. If there are none, return exactly one
   item with conflicting_req_id null and description "{NO_CONFLICT_TEXT}".

Return ONLY a JSON object with this shape:
{{
  "user_stories": [
    {{"story": "As a ..., I want to ... so that ...",
      "acceptance_criteria": "Given ..., When ..., Then ..."}}
  ],
  "priority_justification": "...",
  "conflicts": [
    {{"conflicting_req_id": "REQ-xxxxxx or null", "description": "..."}}
  ]
}}
"""


def _format_existing(existing_requirements):
    if not existing_requirements:
        return "No existing requirements yet.", set()
    recent = existing_requirements[-MAX_EXISTING_REQS:]
    lines, valid_ids = [], set()
    for r in recent:
        req_id = f"REQ-{str(r['_id'])[-6:]}"
        valid_ids.add(req_id)
        desc = (r.get("description") or "")[:100]
        lines.append(f"- {req_id}: {r.get('title', '')} — {desc}")
    return "\n".join(lines), valid_ids


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate(parsed, valid_ids):
    """Check shape and clean the model output. Raises ValueError if unusable."""
    if not isinstance(parsed, dict):
        raise ValueError("Response is not a JSON object")

    stories = parsed.get("user_stories")
    if not isinstance(stories, list) or not stories:
        raise ValueError("user_stories missing or empty")

    clean_stories = []
    for s in stories:
        if not isinstance(s, dict):
            continue
        story = str(s.get("story", "")).strip()
        ac = s.get("acceptance_criteria", "")
        if isinstance(ac, list):               # models sometimes return a list
            ac = "\n".join(str(x).strip() for x in ac)
        ac = str(ac).strip()
        if story and ac:
            clean_stories.append({"story": story, "acceptance_criteria": ac})
    if not clean_stories:
        raise ValueError("No usable user stories (missing story or acceptance criteria)")

    # Conflicts: drop anything that points at a requirement that doesn't exist
    # (a hallucinated ID). Keep the "no conflicts" sentinel the UI expects.
    clean_conflicts = []
    raw_conflicts = parsed.get("conflicts") or []
    if isinstance(raw_conflicts, list):
        for c in raw_conflicts:
            if not isinstance(c, dict):
                continue
            cid = c.get("conflicting_req_id")
            cid = None if cid in (None, "", "null", "None") else str(cid).strip()
            desc = str(c.get("description", "")).strip()
            if cid and cid in valid_ids and desc:
                clean_conflicts.append({"conflicting_req_id": cid, "description": desc})
    if not clean_conflicts:
        clean_conflicts = [{"conflicting_req_id": "null", "description": NO_CONFLICT_TEXT}]

    return {
        "user_stories": clean_stories,
        "priority_justification": str(parsed.get("priority_justification", "")).strip(),
        "conflicts": clean_conflicts,
    }


# ---------------------------------------------------------------------------
# Model call
# ---------------------------------------------------------------------------

def _call_model(client, model, prompt):
    kwargs = dict(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2500,
        response_format={"type": "json_object"},
    )
    if model.startswith("openai/gpt-oss"):
        # Low reasoning effort avoided JSON generation failures in the
        # legal-case-extraction project on the same models.
        kwargs["reasoning_effort"] = "low"
    return client.chat.completions.create(**kwargs)


def _strip_fences(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def process_requirement(title: str, description: str, department: str, role: str,
                        objective: str, existing_requirements: list,
                        model: str = None) -> dict:
    """Analyze one requirement. Returns the same dict shape the UI already uses,
    plus a "_meta" key. Raises ProcessingError on failure."""

    priority = ROLE_PRIORITY_MAP.get(role, "Medium")
    moscow = ROLE_MOSCOW_MAP.get(role, "Should Have")

    api_key = _get("GROQ_API_KEY")
    if not api_key:
        raise ProcessingError("The AI service is not configured.", "GROQ_API_KEY missing")
    client = Groq(api_key=api_key)

    existing_text, valid_ids = _format_existing(existing_requirements)
    prompt = _build_prompt(title, description, department, role, objective,
                           existing_text, priority, moscow)

    first = model or PRIMARY_MODEL
    models_to_try = [first] + [m for m in FALLBACK_MODELS if m != first]

    last_error = ""
    total_attempts = 0
    started = time.time()

    for m in models_to_try:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            total_attempts += 1
            try:
                response = _call_model(client, m, prompt)
                raw = _strip_fences(response.choices[0].message.content or "")
                result = _validate(json.loads(raw), valid_ids)

                # Policy fields always come from code, never the model.
                result["priority"] = priority
                result["moscow"] = moscow

                usage = getattr(response, "usage", None)
                result["_meta"] = {
                    "model": m,
                    "attempts": total_attempts,
                    "latency_ms": int((time.time() - started) * 1000),
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                }
                return result

            except groq.NotFoundError as e:
                last_error = f"{m}: model not found ({e})"
                break                                  # retired model -> next model

            except (json.JSONDecodeError, ValueError, groq.BadRequestError) as e:
                # Bad/invalid JSON (BadRequestError covers Groq's json_validate_failed)
                last_error = f"{m} attempt {attempt}: invalid output ({e})"
                continue

            except (groq.RateLimitError, groq.APIConnectionError,
                    groq.InternalServerError) as e:
                last_error = f"{m} attempt {attempt}: transient error ({e})"
                time.sleep(min(2 ** attempt, 8))
                continue

            except groq.AuthenticationError as e:
                raise ProcessingError("The AI service key is invalid.", str(e))

    raise ProcessingError(
        "The AI couldn't analyze this requirement right now. Please try again in a minute.",
        last_error,
    )


def generate_priority_score(role: str, department: str, objective: str) -> str:
    return ROLE_PRIORITY_MAP.get(role, "Medium")

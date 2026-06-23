import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ROLE_PRIORITY_MAP = {
    "C-Suite / Executive": "High",
    "VP / Director": "High",
    "Department Head / Manager": "Medium",
    "Team Lead": "Medium",
    "End User": "Low",
    "External Stakeholder": "Low"
}

ROLE_MOSCOW_MAP = {
    "C-Suite / Executive": "Must Have",
    "VP / Director": "Must Have",
    "Department Head / Manager": "Should Have",
    "Team Lead": "Should Have",
    "End User": "Could Have",
    "External Stakeholder": "Could Have"
}


def process_requirement(title: str, description: str, department: str, role: str, objective: str, existing_requirements: list) -> dict:

    priority = ROLE_PRIORITY_MAP.get(role, "Medium")
    moscow = ROLE_MOSCOW_MAP.get(role, "Should Have")

    existing_text = ""
    if existing_requirements:
        existing_text = "\n".join([
            f"- REQ-{str(r['_id'])[-6:]}: {r['title']} — {r.get('description', '')[:100]}"
            for r in existing_requirements
        ])
    else:
        existing_text = "No existing requirements yet."

    prompt = f"""
You are a senior Business Systems Analyst. Analyze the following business requirement and return a structured JSON response.

REQUIREMENT DETAILS:
Title: {title}
Description: {description}
Department: {department}
Submitter Role: {role}
Business Objective: {objective}

PRIORITY (already determined by role — do NOT change this): {priority}
MOSCOW (already determined by role — do NOT change this): {moscow}

EXISTING REQUIREMENTS IN SYSTEM:
{existing_text}

Your task:
1. Generate 3 detailed user stories in "As a [user], I want to [action] so that [benefit]" format
2. For each user story, write 2-3 acceptance criteria in "Given... When... Then..." format
3. Use EXACTLY this MoSCoW value (do not change it): {moscow}
4. Use EXACTLY this priority value (do not change it): {priority}
5. Write a one-sentence priority justification explaining why this role gets this priority
6. Detect any conflicts or overlaps with existing requirements. If none, say "No conflicts detected."

Return ONLY valid JSON in this exact format, no extra text, no markdown:
{{
    "user_stories": [
        {{
            "story": "As a [user], I want to [action] so that [benefit]",
            "acceptance_criteria": "Given [context], When [action], Then [outcome]. Given [context], When [action], Then [outcome]."
        }},
        {{
            "story": "As a [user], I want to [action] so that [benefit]",
            "acceptance_criteria": "Given [context], When [action], Then [outcome]. Given [context], When [action], Then [outcome]."
        }},
        {{
            "story": "As a [user], I want to [action] so that [benefit]",
            "acceptance_criteria": "Given [context], When [action], Then [outcome]. Given [context], When [action], Then [outcome]."
        }}
    ],
    "moscow": "{moscow}",
    "priority": "{priority}",
    "priority_justification": "One sentence explaining why a {role} submission receives {priority} priority.",
    "conflicts": [
        {{
            "conflicting_req_id": "null",
            "description": "No conflicts detected."
        }}
    ]
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    parsed = json.loads(raw)

    # Force priority and moscow regardless of what AI returned
    parsed["priority"] = priority
    parsed["moscow"] = moscow

    return parsed


def generate_priority_score(role: str, department: str, objective: str) -> str:
    return ROLE_PRIORITY_MAP.get(role, "Medium")
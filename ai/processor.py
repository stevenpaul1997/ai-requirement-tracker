import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_requirement(title: str, description: str, department: str, role: str, objective: str, existing_requirements: list) -> dict:
    
    existing_text = ""
    if existing_requirements:
        existing_text = "\n".join([
            f"- REQ-{str(r['_id'])[-6:]}: {r['title']} — {r['description'][:100]}"
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

EXISTING REQUIREMENTS IN SYSTEM:
{existing_text}

Your task:
1. Generate 3 detailed user stories in "As a [user], I want to [action] so that [benefit]" format
2. For each user story, write 2-3 acceptance criteria in "Given... When... Then..." format
3. Classify using MoSCoW: Must Have / Should Have / Could Have / Won't Have
4. Assign priority: High / Medium / Low with a one-sentence justification
5. Detect any conflicts or overlaps with existing requirements. If none, say "No conflicts detected."
6. Write a brief priority justification (1-2 sentences)

Return ONLY valid JSON in this exact format, no extra text:
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
    "moscow": "Must Have",
    "priority": "High",
    "priority_justification": "This requirement directly impacts core business operations and blocks other workflows.",
    "conflicts": [
        {{
            "conflicting_req_id": "REQ-xxxxxx or null",
            "description": "Description of conflict or No conflicts detected."
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
    
    # Clean up if model wraps in markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def generate_priority_score(role: str, department: str, objective: str) -> str:
    role_weights = {
        "C-Suite / Executive": "High",
        "VP / Director": "High",
        "Department Head / Manager": "Medium",
        "Team Lead": "Medium",
        "End User": "Low",
        "External Stakeholder": "Low"
    }
    return role_weights.get(role, "Medium")
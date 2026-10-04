"""Offline tests for ai/processor.py: no API key or network needed (Groq is mocked)."""
import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import httpx, groq, pytest
import ai.processor as P

EXISTING = [{"_id": "64f0000000000000abc123", "title": "Sales dashboard", "description": "Dashboard for reps"}]

def resp(content):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
                           usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50))

GOOD = json.dumps({
    "user_stories": [{"story": "As a rep, I want X so that Y", "acceptance_criteria": ["Given A", "When B", "Then C"]}],
    "priority_justification": "Exec request.",
    "moscow": "Won't Have", "priority": "Low",   # model tries to override policy
    "conflicts": [{"conflicting_req_id": "REQ-abc123", "description": "Overlaps dashboard"},
                  {"conflicting_req_id": "REQ-999999", "description": "Hallucinated"}]})

def run(side_effects):
    client = MagicMock()
    client.chat.completions.create.side_effect = side_effects
    with patch.object(P, "Groq", return_value=client), patch.object(P, "_get", side_effect=lambda k, d="": "key" if k == "GROQ_API_KEY" else d), patch.object(P.time, "sleep"):
        return P.process_requirement("T", "D", "Sales", "C-Suite / Executive", "O", EXISTING), client

def err(cls, code):
    r = httpx.Response(code, request=httpx.Request("POST", "https://x"))
    return cls("boom", response=r, body=None)

def test_policy_fields_enforced_and_hallucinated_conflict_dropped():
    r, _ = run([resp(GOOD)])
    assert r["priority"] == "High" and r["moscow"] == "Must Have"
    assert [c["conflicting_req_id"] for c in r["conflicts"]] == ["REQ-abc123"]
    assert "Given A\nWhen B\nThen C" == r["user_stories"][0]["acceptance_criteria"]
    assert r["_meta"]["attempts"] == 1

def test_bad_json_then_retry_succeeds():
    r, _ = run([resp("not json {"), resp(GOOD)])
    assert r["_meta"]["attempts"] == 2

def test_retired_model_falls_back():
    r, c = run([err(groq.NotFoundError, 404), resp(GOOD)])
    assert r["_meta"]["model"] != c.chat.completions.create.call_args_list[0].kwargs["model"]

def test_no_conflicts_sentinel():
    body = json.dumps({"user_stories": [{"story": "s", "acceptance_criteria": "a"}], "conflicts": []})
    r, _ = run([resp(body)])
    assert r["conflicts"][0]["description"] == P.NO_CONFLICT_TEXT

def test_total_failure_raises_friendly_error():
    with pytest.raises(P.ProcessingError) as e:
        run([resp("garbage")] * 20)
    assert "try again" in e.value.user_message

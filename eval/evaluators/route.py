"""Checks the intent identifier dispatched each case to an acceptable route
(expected_intents in eval/datasets/mira_baseline.py) — deterministic, no LLM."""

from langsmith.schemas import Example, Run


def check(run: Run, example: Example) -> dict:
    expected = (example.outputs or {}).get("expected_intents", [])
    actual = (run.outputs or {}).get("intent")
    correct = actual in expected
    return {
        "key": "route_correct",
        "score": 1.0 if correct else 0.0,
        "comment": f"routed to {actual!r}; expected one of {expected}",
    }

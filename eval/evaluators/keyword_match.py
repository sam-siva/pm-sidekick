"""Cheap, deterministic check against each example's expected `must_contain`
keywords — a fast tripwire that runs before the LLM-judge evaluators."""

from langsmith.schemas import Example, Run


def check(run: Run, example: Example) -> dict:
    expected = (example.outputs or {}).get("must_contain", [])
    output = ((run.outputs or {}).get("output", "") or "").lower()

    missing = [word for word in expected if word.lower() not in output]
    score = 0.0 if missing else 1.0
    return {
        "key": "keyword_match",
        "score": score,
        "comment": f"missing: {missing}" if missing else "all expected keywords present",
    }

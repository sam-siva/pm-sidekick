"""Deterministic per-case checks against the expectations in eval/datasets/mira_baseline.py.

Reads the specialist's structured `result` (returned by run_eval.target) and the
rendered `output`; expected values come from the dataset, and source rows are
re-read straight from the CSVs, so nothing here depends on Mira's own logic.
"""

import csv
import re

from langsmith.schemas import Example, Run

from utils.resource_loader import RESOURCES_DIR


def _csv(name: str) -> list[dict]:
    with (RESOURCES_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _result(passed: bool, detail: str) -> dict:
    return {"key": "case_check", "score": 1.0 if passed else 0.0, "comment": detail}


def _plan_timeline(result: dict, output: str) -> dict:
    expected = {
        (int(r["phase"]), r["phase_name"].lower(), int(r["start_week"]), int(r["end_week"]))
        for r in _csv("project_timeline.csv")
    }
    actual = {
        (p.get("phase_number"), str(p.get("name", "")).lower(), p.get("start_week"), p.get("end_week"))
        for p in result.get("phases", [])
    }
    goals = " ".join(g.get("goal", "") for g in result.get("goals", []))
    problems = []
    if actual != expected:
        problems.append(f"phases differ: missing {sorted(p[0] for p in expected - actual)}, "
                        f"unexpected {sorted(str(p[0]) for p in actual - expected)}")
    if result.get("status") != "ok":
        problems.append(f"status={result.get('status')}")
    if not ("15%" in goals and "10%" in goals):
        problems.append("stated goal targets (15%, 10%) missing from goals")
    return _result(not problems, "; ".join(problems) or "8/8 timeline phases matched; goals grounded")


def _decline(result: dict, output: str, run_outputs: dict) -> dict:
    produced = bool(
        result.get("phases") or result.get("risks") or result.get("counts")
        or re.search(r"\|\s*ID\s*\|", output)
    )
    passed = run_outputs.get("needs_input") and not run_outputs.get("report") and not produced
    return _result(bool(passed), "declined without generating content" if passed else
                   f"needs_input={run_outputs.get('needs_input')}, report={bool(run_outputs.get('report'))}, "
                   f"generated_content={produced}")


def _risk_full(result: dict, expected_ids: list[str]) -> dict:
    ids = [r["risk_id"] for r in result.get("risks", [])]
    register = [i for i in ids if not i.startswith("D")]
    unknown = sorted(set(register) - set(expected_ids))
    missing = sorted(set(expected_ids) - set(register))
    derived_without_evidence = [
        r["risk_id"] for r in result.get("risks", []) if r["risk_id"].startswith("D") and not r.get("evidence")
    ]
    problems = [msg for msg in (
        f"unknown ids {unknown}" if unknown else "",
        f"missing register risks {missing}" if missing else "",
        f"derived risks without evidence {derived_without_evidence}" if derived_without_evidence else "",
        "risks lack categories" if any(not r.get("category") for r in result.get("risks", [])) else "",
    ) if msg]
    return _result(not problems, "; ".join(problems) or f"all {len(expected_ids)} register risks, categorized")


def _risk_top(result: dict, n: int, expected_ids: list[str]) -> dict:
    ids = [r["risk_id"] for r in result.get("risks", [])]
    passed = len(ids) == n and set(ids) <= set(expected_ids)
    return _result(passed, f"returned {ids}; expected exactly {n} register risks")


def _status(result: dict, expect: dict) -> dict:
    problems = []
    if result.get("sprint") != expect["sprint"]:
        problems.append(f"sprint={result.get('sprint')}, expected {expect['sprint']}")
    if result.get("counts") != expect["counts"]:
        problems.append(f"counts={result.get('counts')}, expected {expect['counts']}")
    if "task_ids" in expect:
        listed = sorted(i for ids in result.get("task_ids", {}).values() for i in ids)
        if listed != sorted(expect["task_ids"]):
            problems.append(f"tasks={listed}, expected {sorted(expect['task_ids'])}")
    return _result(not problems, "; ".join(problems) or "scope, counts, and tasks match the task board")


def _alerts(result: dict, output: str, expect: dict) -> dict:
    problems = []
    for key in ("blocked", "overdue"):
        missing = sorted(set(expect[key]) - set(result.get(key, [])))
        if missing:
            problems.append(f"{key} missing {missing}")
    known = {r["task_id"] for r in _csv("sample_task_board.csv")}
    invented = sorted(set(re.findall(r"\bT\d{3}\b", output)) - known)
    if invented:
        problems.append(f"unknown task ids {invented}")
    return _result(not problems, "; ".join(problems) or "blocked/overdue tasks identified")


def _milestones(result: dict, expect: dict) -> dict:
    actual = result.get("upcoming_milestones")
    return _result(actual == expect["phases"], f"upcoming phases {actual}, expected {expect['phases']}")


def _sprint_scope(result: dict, output: str, expect: dict) -> dict:
    tasks = _csv("sample_task_board.csv")
    allowed = set(expect["allowed"])
    lowered = output.lower()
    leaked = sorted(
        t["task_id"] for t in tasks
        if t["task_id"] not in allowed
        and (re.search(rf"\b{t['task_id']}\b", output) or t["task_name"].lower() in lowered)
    )
    problems = []
    if result.get("sprint") != expect["sprint"]:
        problems.append(f"sprint={result.get('sprint')}")
    if leaked:
        problems.append(f"mentions out-of-scope tasks {leaked}")
    return _result(not problems, "; ".join(problems) or f"only Sprint {expect['sprint']} tasks referenced")


def check(run: Run, example: Example) -> dict:
    expect = (example.outputs or {}).get("expect") or {}
    outputs = run.outputs or {}
    result = outputs.get("result") or {}
    output = outputs.get("output", "") or ""
    kind = expect.get("kind")

    if kind == "plan_timeline":
        return _plan_timeline(result, output)
    if kind == "decline":
        return _decline(result, output, outputs)
    if kind == "risk_full":
        return _risk_full(result, expect["risk_ids"])
    if kind == "risk_top":
        return _risk_top(result, expect["n"], expect["risk_ids"])
    if kind == "status":
        return _status(result, expect)
    if kind == "alerts":
        return _alerts(result, output, expect)
    if kind == "milestones":
        return _milestones(result, expect)
    if kind == "sprint_scope":
        return _sprint_scope(result, output, expect)
    return _result(False, f"unknown check kind {kind!r}")

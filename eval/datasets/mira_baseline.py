"""Structured version of mira/resources/eval_mira_inputs.txt (cases T1-T12).

Queries are verbatim from eval_mira_inputs.txt. Each case becomes one LangSmith
dataset example:

- `expected_intents`: acceptable intent_agent routes (vague cases may be declined
  by the router or by the specialist).
- `must_contain`: cheap keyword tripwire (eval/evaluators/keyword_match.py).
- `expect`: the deterministic check run by eval/evaluators/case_checks.py. Expected
  values are hand-copied from the resource CSVs, not computed by Mira's own code,
  so the check is independent of the implementation.

`vague=True` marks inputs that come with no project data ("no task data" in the
problem statement). run_eval.py runs those against an empty resources directory,
so nothing on disk can leak into the answer.
"""

REGISTER_RISK_IDS = [f"R{n:02d}" for n in range(1, 11)]

CASES = [
    {
        "id": "T1",
        "query": "Generate a project plan for the AI Adoption Project at ABCDE Ltd. "
                 "Use the provided project description.",
        "vague": False,
        "expected_intents": ["plan"],
        "must_contain": ["Phase", "Week", "15%", "10%"],
        "expect": {"kind": "plan_timeline"},
    },
    {
        "id": "T2",
        "query": 'Generate a project plan for: "We want to build a chatbot."',
        "vague": True,
        "expected_intents": ["plan", "clarify"],
        "must_contain": ["scope", "timeline", "team"],
        "expect": {"kind": "decline"},
    },
    {
        "id": "T3",
        "query": "Generate a risk assessment for the AI Adoption Project at ABCDE Ltd. "
                 "Use the provided project description.",
        "vague": False,
        "expected_intents": ["risk"],
        "must_contain": ["R01", "R10"],
        "expect": {"kind": "risk_full", "risk_ids": REGISTER_RISK_IDS},
    },
    {
        "id": "T4",
        "query": 'Generate a risk assessment for: "New project starting soon."',
        "vague": True,
        "expected_intents": ["risk", "clarify"],
        "must_contain": ["scope"],
        "expect": {"kind": "decline"},
    },
    {
        "id": "T5",
        "query": "Generate a weekly status report using the sample task board data for Sprint 3.",
        "vague": False,
        "expected_intents": ["status"],
        "must_contain": ["Sprint 3", "T007", "T008", "T009", "T025"],
        "expect": {
            "kind": "status",
            "sprint": 3,
            "task_ids": ["T007", "T008", "T009", "T025"],
            "counts": {"Done": 0, "In Progress": 2, "Blocked": 0, "To Do": 2},
        },
    },
    {
        "id": "T6",
        "query": 'Generate a weekly status report for: "Things are going fine."',
        "vague": True,
        "expected_intents": ["status", "clarify"],
        "must_contain": ["no task data"],
        "expect": {"kind": "decline"},
    },
    {
        "id": "T7",
        "query": "What are the top 3 risks for the ABCDE Ltd project based on the risk data?",
        "vague": False,
        "expected_intents": ["risk"],
        "must_contain": ["Top 3"],
        "expect": {"kind": "risk_top", "n": 3, "risk_ids": REGISTER_RISK_IDS},
    },
    {
        "id": "T8",
        "query": "Which tasks are blocked or at risk of missing their deadline based on the task board?",
        "vague": False,
        "expected_intents": ["milestone"],
        "must_contain": ["T024", "Blocked"],
        # T024 is the intentionally Blocked task; T006 (due 2026-04-21) is past due at the as-of date
        "expect": {"kind": "alerts", "blocked": ["T024"], "overdue": ["T006"]},
    },
    {
        "id": "T9",
        "query": "Generate a project plan for a 2-week project with no details provided.",
        "vague": True,
        "expected_intents": ["plan", "clarify"],
        "must_contain": ["scope", "goals", "deliverables"],
        "expect": {"kind": "decline"},
    },
    {
        "id": "T10",
        "query": "Summarize the current project status: how many tasks are done, in progress, "
                 "and to do?",
        "vague": False,
        "expected_intents": ["status"],
        "must_contain": ["Done", "In Progress", "To Do", "Blocked"],
        # Actual sample_task_board.csv counts (the problem statement's "3 Done" is incorrect)
        "expect": {
            "kind": "status",
            "sprint": None,
            "counts": {"Done": 5, "In Progress": 3, "Blocked": 1, "To Do": 16},
        },
    },
    {
        "id": "T11",
        "query": "What milestones are coming up in the next 2 weeks based on the timeline?",
        "vague": False,
        "expected_intents": ["milestone"],
        "must_contain": ["Use Case Selection", "Final list of prioritized use cases"],
        # Phase 3 ends week 6 (2026-05-10), inside 2026-04-27 + 14 days
        "expect": {"kind": "milestones", "phases": [3]},
    },
    {
        "id": "T12",
        "query": "Generate a stakeholder update email summarizing Sprint 2 progress.",
        "vague": False,
        "expected_intents": ["stakeholder"],
        "must_contain": ["Sprint 2", "Subject"],
        "expect": {"kind": "sprint_scope", "sprint": 2, "allowed": ["T004", "T005", "T006"]},
    },
]

"""Runs the Mira graph over the mira-baseline LangSmith dataset, scores it with
the evaluators in eval/evaluators/, and writes a results table to
eval/results/baseline_results.md.

    python -m eval.upload_dataset   # after changing eval/datasets/mira_baseline.py
    python -m eval.run_eval
"""

import shutil
import tempfile
from pathlib import Path

import keystore.setenv  # noqa: F401  (loads env vars before anything else)
from langsmith import evaluate

from eval.evaluators import case_checks, groundedness, keyword_match, route
from observability.tracing import run_config
from orchestrator import graph
from utils.project_data import (
    DESCRIPTION_FILE,
    INTRO_FILE,
    RISKS_FILE,
    TASK_BOARD_FILE,
    TIMELINE_FILE,
    computation_notes,
    load_context,
)
from utils.resource_loader import RESOURCES_DIR

DATASET_NAME = "mira-baseline"
REPORT_SAVED_PREFIX = "Report saved to"
RESULTS_PATH = Path(__file__).resolve().parent / "results" / "baseline_results.md"
EVALUATOR_KEYS = ["route_correct", "case_check", "keyword_match", "groundedness"]

# Ground truth for the groundedness judge: the project files, never the eval inputs
PROJECT_SOURCES = {DESCRIPTION_FILE, INTRO_FILE, TIMELINE_FILE, RISKS_FILE, TASK_BOARD_FILE}


def target(inputs: dict) -> dict:
    """Vague-input cases carry no project data, so they run against an empty
    resources directory — nothing on disk can leak into the answer."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="mira_eval_"))
    try:
        resources_dir = tmp_dir if inputs.get("vague") else RESOURCES_DIR
        context = (
            f"--- Mira configuration ---\n{computation_notes()}\n\n"
            + load_context(resources_dir, PROJECT_SOURCES)
        )
        state = {
            "messages": [{"role": "user", "content": inputs["query"]}],
            "resources_dir": str(resources_dir),
        }
        result = graph.invoke(state, config=run_config("eval_run", dataset=DATASET_NAME))
        # Score the specialist's content, not generate_report's "Report saved to ..." notice
        contents = [message.content for message in result["messages"]]
        output = next(
            (c for c in reversed(contents) if not c.startswith(REPORT_SAVED_PREFIX)), ""
        )
        report = next((c for c in contents if c.startswith(REPORT_SAVED_PREFIX)), None)
        return {
            "output": output,
            "context": context,
            "intent": result.get("intent"),
            "needs_input": bool(result.get("needs_input")),
            "result": result.get("result") or {},
            "report": report,
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _write_results(results) -> None:
    rows = []
    for item in results:
        example, run = item["example"], item["run"]
        scores = {r.key: r for r in item["evaluation_results"]["results"]}
        rows.append((example.metadata.get("id", ""), example.inputs["query"], run.outputs or {}, scores))
    rows.sort(key=lambda row: int(row[0][1:] or 0))

    lines = [
        "# Mira baseline results",
        "",
        f"Experiment: `{results.experiment_name}`",
        "",
        f"_{computation_notes()}_",
        "",
        "| ID | Input | Route | " + " | ".join(EVALUATOR_KEYS) + " | Check detail |",
        "|---|---|---|" + "---|" * len(EVALUATOR_KEYS) + "---|",
    ]
    for case_id, query, outputs, scores in rows:
        marks = [
            ("✅" if scores[key].score == 1 else "❌") if key in scores else "—"
            for key in EVALUATOR_KEYS
        ]
        detail = scores["case_check"].comment if "case_check" in scores else ""
        lines.append(
            f"| {case_id} | {query.replace('|', '/')} | {outputs.get('intent')} | "
            + " | ".join(marks) + f" | {detail.replace('|', '/')} |"
        )
    passed = sum(all(s.score == 1 for s in scores.values()) for *_, scores in rows)
    lines += ["", f"**{passed}/{len(rows)} cases pass every evaluator.**"]
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main() -> None:
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[route.check, case_checks.check, keyword_match.check, groundedness.check],
        experiment_prefix="mira",
        max_concurrency=4,
    )
    _write_results(results)


if __name__ == "__main__":
    main()

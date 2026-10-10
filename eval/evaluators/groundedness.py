"""LLM judge: audits every factual claim in an output against the project files
and Mira's documented computation rules (utils.project_data.computation_notes).
Uses a different model from the generators (utils.model.judgemodel)."""

from typing import Literal

from langsmith.schemas import Example, Run
from pydantic import BaseModel, Field

from utils.model import judgemodel

JUDGE_PROMPT = (
    "You are auditing whether an output from Mira, an AI project assistant, is grounded in its source "
    "data. The source data starts with Mira's documented configuration: the as-of date, how project "
    "weeks map to calendar dates, and the rules for overdue, Missed, At risk, and Red/Amber/Green health. "
    "Treat that configuration as part of the source data.\n\n"
    "<source_data>\n{context}\n</source_data>\n\n"
    "<generated_output>\n{output}\n</generated_output>\n\n"
    "Extract every factual claim the output makes about the project — goals, targets, phases, weeks, "
    "dates, milestones, deliverables, tasks, statuses, assignees, counts, risks, impacts, mitigations, "
    "durations, and health. For each, give a verdict:\n"
    "- supported: stated in the source data, or a faithful paraphrase or summary of it.\n"
    "- computed: follows from the source data by arithmetic or by applying the documented configuration "
    "(for example: counts, total duration from the last end week, a calendar due date for a week, "
    "overdue/Missed/At risk status, a health rating).\n"
    "- assessment: a priority, ranking, or judgement that is presented as the assistant's assessment "
    "or comes with a rationale that cites the data.\n"
    "- data_gap: says the data lacks something (e.g. 'Owner: Not specified in project data'), "
    "and the data indeed lacks it.\n"
    "- unsupported: anything else — including invented goals, tasks, milestones, owners, budgets, or "
    "risks; wrong values; completion dates (the task board records due dates, not completion dates); "
    "and predictions presented as fact.\n"
    "Cite the evidence (file and row/line, or the configuration rule) for every verdict except "
    "unsupported. Recommendations, next steps, greetings, and requests for more information are not "
    "factual claims; skip them. If the source data is empty, any project-specific fact is unsupported."
)


class ClaimVerdict(BaseModel):
    claim: str = Field(description="The claim, quoted or closely paraphrased")
    verdict: Literal["supported", "computed", "assessment", "data_gap", "unsupported"]
    evidence: str = Field(description="Source file and row/line or configuration rule; '' if unsupported")


class GroundednessAudit(BaseModel):
    claims: list[ClaimVerdict]


def check(run: Run, example: Example) -> dict:
    # target() returns both "output" and "context" (see eval/run_eval.py)
    context = (run.outputs or {}).get("context", "")
    output = (run.outputs or {}).get("output", "") or ""

    audit = judgemodel.with_structured_output(GroundednessAudit).invoke(
        [{"role": "user", "content": JUDGE_PROMPT.format(context=context, output=output)}]
    )
    unsupported = [c.claim for c in audit.claims if c.verdict == "unsupported"]
    comment = f"{len(audit.claims)} claims checked, {len(unsupported)} unsupported"
    if unsupported:
        comment += ": " + "; ".join(unsupported)
    return {"key": "groundedness", "score": 0.0 if unsupported else 1.0, "comment": comment}

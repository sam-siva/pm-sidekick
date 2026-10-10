# Q2 — Building Mira

> Draft: review and personalise before submission.

## 1. Design

**Architecture.** Mira is a LangGraph state machine using the **Router/Dispatcher** pattern
(diagram: [../graph.png](../graph.png)). An intent identifier (`gpt-4o-mini`, structured output
restricted to six labels) classifies each request and a conditional edge dispatches it to one
specialist: Planner, Risk Assessor, Status Reporter, Milestone Tracker, or Stakeholder Update
Generator. A `clarify` route answers vague requests directly. Specialists that produce content hand
off to a report generator that saves a PDF, Word, or PowerPoint file; specialists that decline go
straight back to the user.

**Why a router.** PM requests are single-purpose ("top 3 risks", "Sprint 3 status"). A sequential
pipeline would run every agent on every request, multiplying cost and mixing unrelated content. A
hierarchical planner adds cost and failure modes that none of the baseline requests need. The router
is cheap (≈$0.0001 per call), and its decision is itself an evaluable output.

**Design principles.**
1. *Code computes, the model writes.* Counts, task IDs, due-date checks, milestone windows, and
   Red/Amber/Green health come from code over the CSVs. The LLM writes summaries and
   recommendations around those facts.
2. *Each agent sees only its data.* The Planner gets the description and timeline; the Status
   Reporter gets the task board and timeline. Test inputs and duplicate PDF/DOCX copies are never loaded.
3. *Decline instead of invent.* Vague requests get questions back, never a plan or a risk list.
4. *Structured outputs.* Every specialist returns a Pydantic model, validated in code (for example,
   risk IDs must exist in the register).

**Tools.** LangGraph (code-first, version-controlled graph), OpenAI models (`gpt-4o` for agents,
`gpt-4o-mini` for routing, `gpt-4.1` as an independent eval judge), LangSmith (tracing, dataset,
experiments, cost), and python-docx, reportlab, and python-pptx for output files.

## 2. Implementation

| Capability | Status | How |
|---|---|---|
| Project plan generation | Core ✅ | Uses the 8 timeline phases with exact week ranges; goals only from the description; declines vague requests |
| Risk assessment | Core ✅ | All 10 register risks, made specific to the project with cited evidence; priorities labelled as Mira's assessment; top-N is sliced from the full ranking so answers stay consistent |
| Weekly status report | Core ✅ | Sprint filter, exact counts, tasks by status, rule-based health, upcoming milestones; states "no task data" when there is none |
| Milestone alert system | Extended ✅ | Flags blocked (T024), overdue (T006), and due-soon tasks; upcoming (Phase 3) and missed (Phase 2) milestones, with reasons and one action each |
| Stakeholder update generator | Extended ✅ | Leadership, engineering, or client tone; strictly scoped to the requested sprint, regenerated if other tasks leak in |
| Observability | ✅ | LangSmith traces every node and LLM call, with token usage and cost |
| Baseline testing | ✅ | T1-T12 run in LangSmith: 12/12 pass every evaluator |

## 3. Cost and evaluation

**Metrics** (experiment `mira-97da2d94`):

| Metric | Result |
|---|---|
| Routing accuracy (`route_correct`) | 12/12 |
| Task-specific correctness (`case_check`) | 12/12 |
| Groundedness (claim-level audit by `gpt-4.1`) | 12/12, zero unsupported claims |
| Correct refusals on vague input (T2, T4, T6, T9) | 4/4, no content generated |
| Cost per plan | $0.0196 |
| Cost per request, mean of content requests | ≈ $0.015 |
| Latency | 0.8 s (declined) to 10 s (plan or risk) |

**Evaluation strategy.** Deterministic checks first (route, exact phases, counts, IDs, sprint
scope), with expected values copied by hand from the CSVs so they're independent of Mira's own
code. An LLM judge then audits each factual claim against the source files and Mira's documented
computation rules. Using a different model from the generators avoids self-grading.

**Observations.**
- The first judge (a single yes/no verdict from the generator model) produced false positives on
  correctly computed dates and missed a real error: an email that stated completion dates the data
  doesn't contain. The claim-level judge fixed both.
- Ranking drift: "top 3 risks" picked a different third risk than the full assessment did. It is now
  sliced from one canonical ranking.
- The problem statement's sample-data note ("3 Done") is inconsistent with the CSV (5 Done); Mira
  reports the CSV.
- The report generator is about a third of per-request cost and isn't evaluated; rendering files
  deterministically from the structured result is the next optimisation.

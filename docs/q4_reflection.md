# Q4 — Reflection and next steps

> Draft: review and personalise before submission.

## What the traces showed

LangSmith traces and evaluator comments drove every major fix:

1. **The first version scored the wrong thing.** The graph's last message was "Report saved to …",
   so evaluators graded a file path. The vague test cases also loaded the real project files,
   because the resources setting was silently dropped from the graph state. The eval now scores the
   specialist's output and structured result.
2. **Agents ignored the question.** Every request produced the same roadmap. Routing and passing the
   user's request to each agent fixed it.
3. **Generic prompts invented content.** "Proceed with assumptions" produced plans from one-sentence
   inputs. Explicit decline rules, plus a router `clarify` route, now produce 4/4 correct refusals.
4. **The first LLM judge was unreliable in both directions.** It flagged correctly computed dates
   and health ratings, yet missed an email that said tasks were "completed on April 18", which was
   their *due* date. A claim-by-claim audit, using a different model and given the documented
   computation rules, fixed both.
5. **Ranking drift.** "Top 3 risks" chose R06 while the full assessment ranked R03 higher, because
   the question's wording changed the model's ratings. Top-N is now sliced from one canonical ranking.
6. **Data inconsistency.** The brief says the board has 3 Done tasks; the CSV has 5. Code-computed
   counts made this visible instead of being smoothed over.

## Improvement plan

| Priority | Improvement | Why |
|---|---|---|
| 1 | Render report files from the structured result instead of an LLM rewrite | About a third of per-request cost, and the file content is currently unevaluated |
| 2 | PM approval step (human-in-the-loop) before sharing, using a LangGraph interrupt | No external sharing without review |
| 3 | Expand the eval from 12 to about 50 cases: paraphrases, other sprints, compound requests, injection attempts | 12 cases can't show robustness |
| 4 | Jira/Trello API input with data-quality warnings | Real boards are messier than the sample CSV |
| 5 | Multi-intent requests (hierarchical orchestration) | "Plan and risks for leadership" currently runs one agent |
| 6 | Reduce variance: pin model versions, run each case 3 times in CI | LLM priorities can still shift between runs |

## How evaluation connects to fine-tuning

The evaluation pipeline doubles as a data pipeline. Every PM correction to a plan or risk matrix
and every failed eval case becomes a labelled example: input, corrected structured output, and the
reason. Once there are a few hundred examples, fine-tuning a smaller model (for example
`gpt-4o-mini`) for the Planner or Risk Assessor could keep quality while cutting cost. The same
deterministic checks and groundedness audit then act as the acceptance test: a fine-tuned model
ships only if it matches or beats the current model on the eval set at lower cost. The router is the
first candidate, since its labels are cheap to collect and verify.

## Privacy considerations

- **Data minimisation:** each agent receives only the files it needs, and the router sees only the
  request text.
- **Client data:** use API terms with zero data retention and no training on inputs, and get client
  consent before processing their delivery or customer data (see task T025, legal review of data usage).
- **Personal data:** task boards contain names. Keep assignee names out of client-facing updates
  unless needed, and consider pseudonymising before sending to the model.
- **Traces:** LangSmith stores inputs and outputs. Restrict project access, set retention limits,
  and redact or disable tracing for sensitive projects.
- **Secrets:** keys live only in `.env` (gitignored); `.env.example` holds placeholders.
- **Prompt injection:** project documents are treated as data inside tags and never followed as instructions.

## Rollout for 10 PMs/TPMs

1. **Weeks 1-4, pilot with 3 PMs:** status reports and milestone alerts first. Weekly trace review;
   every correction becomes an eval case.
2. **Weeks 5-8, harden:** approval step, API input, deterministic report rendering, expanded eval
   with a ≥ 95% pass gate.
3. **Weeks 9-12, all 10 PMs:** onboarding session, one-page guide, shared templates, scheduled
   Monday runs, a feedback channel.
4. **Ongoing:** monthly eval regression, cost dashboard (target ≤ $0.05 per request; currently
   ≈ $0.015), quarterly review with the CTO on time saved and adoption.

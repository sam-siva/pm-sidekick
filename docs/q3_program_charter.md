# Q3 — Program charter: Mira

> Draft: review and personalise before submission.

## Vision

Every Nexora PM/TPM spends their time on decisions and stakeholders, not on assembling documents.
Mira produces grounded, standard-format plans, risk assessments, status reports, and alerts from
project data in minutes, and is trusted because it never invents facts.

## Scope

| In scope (v1) | Out of scope (v1) |
|---|---|
| Plan generation, risk assessment, weekly status reports, milestone alerts, stakeholder updates | Autonomous changes to task boards or plans |
| Input from CSV exports and project documents; Jira/Trello read-only API in phase 2 | Sending emails or messages without PM approval |
| PM review before anything is shared externally | Resource allocation and competitive analysis (backlog) |
| Nexora's internal projects and client projects with data-sharing approval | Financial forecasting and contract commitments |

## Success criteria

| Criterion | Target |
|---|---|
| Time saved per PM | ≥ 4 hours/week (plans, status, risk) |
| Accuracy | 100% count and ID agreement with source data; 0 invented facts in sampled reviews |
| Refusals | 100% of underspecified requests get clarifying questions, not content |
| Adoption | 10 of 10 PMs use Mira weekly by the end of rollout |
| Satisfaction | PM rating ≥ 4/5; stakeholder rating of update quality ≥ 4/5 |
| Cost | ≤ $0.05 per request; ≤ $50/month for the team |

## Timeline

| Phase | Weeks | Outcome |
|---|---|---|
| 1. Pilot build | 1-4 | Mira v1 (done for the ABCDE project): five agents, baseline eval 12/12, LangSmith tracing |
| 2. Hardening | 5-8 | Jira/Trello API input, PM approval step, report rendering from structured data, eval set expanded to ~50 cases |
| 3. Pilot with 3 PMs | 9-12 | Two live projects each; weekly feedback; trace review |
| 4. Rollout to 10 PMs | 13-16 | Onboarding, templates, office hours; scheduled weekly status and alert runs |
| 5. Steady state | 17+ | Monthly eval regression runs, quarterly review with the CTO |

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Hallucinated facts reach a client | Loss of trust, contractual exposure | Code-computed facts, groundedness eval, mandatory PM approval before sharing |
| Client data leaves approved boundaries | Privacy and contract breach | Zero-retention API agreements, data minimisation per agent, client consent, access controls |
| Low adoption | No time savings | Co-design templates with PMs, start with the most painful task (status reports), track usage |
| Data quality in task boards | Wrong status and health | Data-quality warnings, missing-field detection, board hygiene guidelines |
| Model or price changes | Regressions or cost increase | Pinned model versions, eval regression before upgrades, per-request cost monitoring |
| Over-reliance on automated assessments | Missed judgement calls | Priorities labelled as assessments, PM sign-off, rationale shown for every rating |

## Stakeholders

| Stakeholder | Role | Interest |
|---|---|---|
| CTO | Sponsor | Delivery predictability, team capacity |
| PMs/TPMs (10) | Primary users | Less manual reporting, earlier warnings |
| Engineering and data science leads | Contributors and consumers | Accurate status, fewer status meetings |
| Client stakeholders (e.g. ABCDE Ltd.) | Recipients of updates | Clear, accurate, timely communication |
| Security and legal | Approvers | Data privacy, client data handling |
| AI PM (owner) | Program lead | Roadmap, quality, adoption |

## Decision-making

| Decision | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Scope and roadmap | AI PM | CTO | PM leads | All PMs |
| Model and vendor choice | AI PM | CTO | Engineering, security | PMs |
| Go/no-go per rollout phase | AI PM | CTO | Pilot PMs | Team |
| Client data use | AI PM | Legal/security | Client | CTO |
| Prompt and eval changes | AI PM | AI PM | Pilot PMs | — |

Go/no-go gates: eval pass rate ≥ 95% on the expanded set, zero invented facts in the weekly sample
review, and pilot PM rating ≥ 4/5.

## Rollout plan

1. **Pilot (3 PMs, 4 weeks):** status reports and milestone alerts first, because they have the
   highest weekly time cost and are easy to verify. Then plans and risk assessments.
2. **Feedback loop:** weekly 30-minute review of traces and corrected outputs. Corrections become
   new eval cases and, later, fine-tuning examples.
3. **Rollout (10 PMs):** a 45-minute onboarding session, a one-page guide, shared templates, and a
   Slack channel. Scheduled Monday status and alert runs.
4. **Guardrails throughout:** PM approval before external sharing, per-request cost alerts, monthly
   eval regression.

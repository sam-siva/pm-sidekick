# Q1 — Ideation: AI agents for PM/TPM productivity at Nexora

> Draft: review and personalise before submission.

Nexora runs several client projects at once with a small PM/TPM team. Three use cases give the
largest time savings and the most consistency.

## Use case 1: Project plan generation

| | |
|---|---|
| **Pain point** | Turning a high-level description into a plan takes 3-4 hours per project, and every PM uses a different format. |
| **Agentic solution** | A Planner agent reads the project description and any timeline, produces phases, activities, milestones, deliverables, and week ranges grounded in those inputs, and asks for missing scope instead of guessing. The PM reviews before sharing. |
| **Inputs** | Project description, statement of work, timeline or target dates, team roster. |
| **Outputs** | A structured plan in a standard template (Markdown/PDF/Word), with a source cited for each phase and a list of data gaps. |
| **Success metrics** | 1. Time to a first plan draft: from 3-4 hours to under 15 minutes of PM review. 2. Groundedness: 0 invented goals or milestones per plan in review. 3. Adoption: at least 80% of new projects start from a Mira plan within one quarter. |
| **Knowledge base** | Nexora plan templates, past project plans and retrospectives, delivery methodology (phases, gates), client contracts and SOWs. |

## Use case 2: Status reporting and milestone alerts

| | |
|---|---|
| **Pain point** | Weekly status reports take 1-2 hours to compile from task boards and notes, and missed milestones are often discovered only in retrospectives. |
| **Agentic solution** | A Status Reporter and a Milestone Tracker read the task board (CSV or Jira/Trello API). Code computes counts, overdue and blocked items, and milestone health; the LLM writes the summary, concerns, and suggested actions. A weekly scheduled run sends alerts for at-risk milestones. |
| **Inputs** | Task board export or API, project timeline, sprint calendar. |
| **Outputs** | Weekly status report (tasks by status, blockers, upcoming milestones, RAG health); milestone alerts with reasons and actions; audience-specific stakeholder emails. |
| **Success metrics** | 1. Report preparation time: from 1-2 hours to under 10 minutes per week. 2. Count accuracy: 100% agreement with the task board. 3. Lead time: at-risk milestones flagged at least 7 days before their due date. |
| **Knowledge base** | Task board data, timelines, the RAG health definition, escalation paths, stakeholder lists and communication preferences. |

## Use case 3: Standardised risk assessment

| | |
|---|---|
| **Pain point** | Risk assessments are inconsistent: some projects have detailed matrices, others have none. |
| **Agentic solution** | A Risk Assessor builds a categorised risk matrix from the project's register and documents, links each risk to the project's goals, phases, and tasks, and adds new risks only when the data shows evidence (for example, a blocked security review). |
| **Inputs** | Project description, risk register (if any), timeline, task board. |
| **Outputs** | A risk matrix: category, description, impact, project context, mitigation, and priority with rationale. Also a "top N risks" view for leadership. |
| **Success metrics** | 1. Coverage: 100% of active projects have a current risk matrix. 2. Relevance: 0 generic, unrelated risks flagged in PM review. 3. Consistency: the same top risks across repeated runs on unchanged data. |
| **Knowledge base** | Nexora's risk taxonomy, risk registers and incident post-mortems from past projects, mitigation playbooks, regulatory and security checklists. |

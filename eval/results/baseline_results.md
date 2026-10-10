# Mira baseline results

Experiment: `mira-97da2d94`

_As-of date: 2026-04-27. Assumed (the project files give no calendar start date): project week 1 starts 2026-03-30; weeks run Monday-Sunday, so a phase is due on the Sunday of its end_week. A task is overdue when it is not Done and its due date is before the as-of date. A phase's tasks are those due inside its weeks. A past phase with unfinished tasks is 'Missed'; an upcoming phase with blocked, overdue, or unstarted tasks due within 7 days is 'At risk'. Health is Red for a missed milestone or a blocked High-priority task, Amber for other overdue or blocked tasks, otherwise Green._

| ID | Input | Route | route_correct | case_check | keyword_match | groundedness | Check detail |
|---|---|---|---|---|---|---|---|
| T1 | Generate a project plan for the AI Adoption Project at ABCDE Ltd. Use the provided project description. | plan | ✅ | ✅ | ✅ | ✅ | 8/8 timeline phases matched; goals grounded |
| T2 | Generate a project plan for: "We want to build a chatbot." | clarify | ✅ | ✅ | ✅ | ✅ | declined without generating content |
| T3 | Generate a risk assessment for the AI Adoption Project at ABCDE Ltd. Use the provided project description. | risk | ✅ | ✅ | ✅ | ✅ | all 10 register risks, categorized |
| T4 | Generate a risk assessment for: "New project starting soon." | clarify | ✅ | ✅ | ✅ | ✅ | declined without generating content |
| T5 | Generate a weekly status report using the sample task board data for Sprint 3. | status | ✅ | ✅ | ✅ | ✅ | scope, counts, and tasks match the task board |
| T6 | Generate a weekly status report for: "Things are going fine." | clarify | ✅ | ✅ | ✅ | ✅ | declined without generating content |
| T7 | What are the top 3 risks for the ABCDE Ltd project based on the risk data? | risk | ✅ | ✅ | ✅ | ✅ | returned ['R01', 'R02', 'R03']; expected exactly 3 register risks |
| T8 | Which tasks are blocked or at risk of missing their deadline based on the task board? | milestone | ✅ | ✅ | ✅ | ✅ | blocked/overdue tasks identified |
| T9 | Generate a project plan for a 2-week project with no details provided. | clarify | ✅ | ✅ | ✅ | ✅ | declined without generating content |
| T10 | Summarize the current project status: how many tasks are done, in progress, and to do? | status | ✅ | ✅ | ✅ | ✅ | scope, counts, and tasks match the task board |
| T11 | What milestones are coming up in the next 2 weeks based on the timeline? | milestone | ✅ | ✅ | ✅ | ✅ | upcoming phases [3], expected [3] |
| T12 | Generate a stakeholder update email summarizing Sprint 2 progress. | stakeholder | ✅ | ✅ | ✅ | ✅ | only Sprint 2 tasks referenced |

**12/12 cases pass every evaluator.**

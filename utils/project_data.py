"""Typed, deterministic access to the project files in mira/resources.

Agents use this for anything that must be exact — task counts, IDs, due dates,
milestone windows — and give the LLM only the computed facts to write about.
"""

import csv
import os
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from utils.resource_loader import RESOURCES_DIR, load_resources

DESCRIPTION_FILE = "project_description.txt"
INTRO_FILE = "ABCDE Ltd Introduction..txt"
TIMELINE_FILE = "project_timeline.csv"
RISKS_FILE = "project_risks.csv"
TASK_BOARD_FILE = "sample_task_board.csv"

# The timeline is in project weeks; week 1 is aligned so the Sprint 1-3 due dates on the
# task board fall inside their timeline phases. The as-of date is the task board snapshot
# (start of Sprint 3). Both are assumptions — override via env vars.
DEFAULT_PROJECT_START = "2026-03-30"
DEFAULT_AS_OF = "2026-04-27"

STATUSES = ("Done", "In Progress", "Blocked", "To Do")


def project_start() -> date:
    return date.fromisoformat(os.environ.get("MIRA_PROJECT_START", DEFAULT_PROJECT_START))


def as_of_date() -> date:
    return date.fromisoformat(os.environ.get("MIRA_AS_OF_DATE", DEFAULT_AS_OF))


def computation_notes() -> str:
    """The assumptions and rules Mira computes with, stated so outputs can be audited."""
    return (
        f"As-of date: {as_of_date()}. Assumed (the project files give no calendar start date): project "
        f"week 1 starts {project_start()}; weeks run Monday-Sunday, so a phase is due on the Sunday of "
        "its end_week. A task is overdue when it is not Done and its "
        "due date is before the as-of date. A phase's tasks are those due inside its weeks. A past phase "
        "with unfinished tasks is 'Missed'; an upcoming phase with blocked, overdue, or unstarted "
        "tasks due within 7 days is 'At risk'. Health is Red for a missed milestone or a blocked "
        "High-priority task, Amber for other overdue or blocked tasks, otherwise Green."
    )


def week_window(week: int) -> tuple[date, date]:
    """Calendar Monday-Sunday for a 1-based project week."""
    start = project_start() + timedelta(weeks=week - 1)
    return start, start + timedelta(days=6)


@dataclass(frozen=True)
class Task:
    task_id: str
    name: str
    status: str
    assignee: str
    priority: str
    sprint: int
    due_date: date
    labels: str
    description: str

    @property
    def is_open(self) -> bool:
        return self.status != "Done"


@dataclass(frozen=True)
class TimelinePhase:
    phase: int
    name: str
    start_week: int
    end_week: int
    key_activities: tuple[str, ...]
    milestones: tuple[str, ...]

    @property
    def start_date(self) -> date:
        return week_window(self.start_week)[0]

    @property
    def end_date(self) -> date:
        return week_window(self.end_week)[1]


@dataclass(frozen=True)
class Risk:
    risk_id: str
    category: str
    risk: str
    impact: str
    mitigation: str


def _rows(directory: str | Path, filename: str) -> list[dict] | None:
    path = Path(directory) / filename
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _split(cell: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in cell.split(";") if part.strip())


def _sprint_number(label: str) -> int:
    return int(re.search(r"\d+", label).group())


def load_tasks(directory: str | Path = RESOURCES_DIR) -> list[Task] | None:
    """Task board rows, or None when no task board was provided."""
    rows = _rows(directory, TASK_BOARD_FILE)
    if rows is None:
        return None
    return [
        Task(
            task_id=row["task_id"],
            name=row["task_name"],
            status=row["status"],
            assignee=row["assignee"],
            priority=row["priority"],
            sprint=_sprint_number(row["sprint"]),
            due_date=date.fromisoformat(row["due_date"]),
            labels=row["labels"],
            description=row["description"],
        )
        for row in rows
    ]


def load_timeline(directory: str | Path = RESOURCES_DIR) -> list[TimelinePhase] | None:
    rows = _rows(directory, TIMELINE_FILE)
    if rows is None:
        return None
    return [
        TimelinePhase(
            phase=int(row["phase"]),
            name=row["phase_name"],
            start_week=int(row["start_week"]),
            end_week=int(row["end_week"]),
            key_activities=_split(row["key_activities"]),
            milestones=_split(row["milestones_deliverables"]),
        )
        for row in rows
    ]


def load_risks(directory: str | Path = RESOURCES_DIR) -> list[Risk] | None:
    rows = _rows(directory, RISKS_FILE)
    if rows is None:
        return None
    return [
        Risk(
            risk_id=row["risk_id"],
            category=row["category"],
            risk=row["risk_challenge"],
            impact=row["impact"],
            mitigation=row["mitigation_strategy"],
        )
        for row in rows
    ]


def load_context(directory: str | Path, filenames: set[str]) -> str:
    """Concatenate the named files, each under a header the LLM can cite."""
    return "\n\n".join(
        f"--- {Path(doc.metadata['source']).name} ---\n{doc.page_content}"
        for doc in load_resources(directory, only=filenames)
    )


def sprint_in(text: str) -> int | None:
    match = re.search(r"sprint\s*(\d+)", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def status_counts(tasks: list[Task]) -> dict[str, int]:
    return {status: sum(task.status == status for task in tasks) for status in STATUSES}


def task_alerts(tasks: list[Task], as_of: date, horizon_days: int = 7) -> dict[str, list[Task]]:
    """Open tasks that are blocked, past due, or due within the horizon."""
    horizon = as_of + timedelta(days=horizon_days)
    open_tasks = [task for task in tasks if task.is_open]
    return {
        "blocked": [task for task in open_tasks if task.status == "Blocked"],
        "overdue": [
            task for task in open_tasks
            if task.status != "Blocked" and task.due_date < as_of
        ],
        "due_soon": [
            task for task in open_tasks
            if task.status != "Blocked" and as_of <= task.due_date <= horizon
        ],
    }


def phase_tasks(phase: TimelinePhase, tasks: list[Task]) -> list[Task]:
    """Tasks whose due date falls inside the phase's calendar window."""
    return [task for task in tasks if phase.start_date <= task.due_date <= phase.end_date]


def milestone_assessment(
    phase: TimelinePhase, tasks: list[Task], as_of: date
) -> tuple[str, list[str]]:
    """Return (health, reasons) for a phase's milestones based on its tasks."""
    related = phase_tasks(phase, tasks)
    reasons = []
    for task in related:
        if task.status == "Blocked":
            reasons.append(f"{task.task_id} '{task.name}' is Blocked")
        elif task.is_open and task.due_date < as_of:
            reasons.append(
                f"{task.task_id} '{task.name}' is {task.status}, due {task.due_date} (overdue)"
            )
        elif task.status == "To Do" and (task.due_date - as_of).days <= 7:
            reasons.append(
                f"{task.task_id} '{task.name}' has not started, due {task.due_date}"
            )
    if related and all(not task.is_open for task in related):
        return "Complete", []
    if phase.end_date < as_of:
        return ("Missed" if any(task.is_open for task in related) else "Complete"), reasons
    return ("At risk" if reasons else "On track"), reasons


def upcoming_milestones(
    timeline: list[TimelinePhase], as_of: date, days: int = 14
) -> list[TimelinePhase]:
    """Phases whose milestones fall due between as_of and as_of + days."""
    window_end = as_of + timedelta(days=days)
    return [phase for phase in timeline if as_of <= phase.end_date <= window_end]


def recently_due_milestones(
    timeline: list[TimelinePhase], as_of: date
) -> list[TimelinePhase]:
    """Phases already past their end date — checked for incomplete work."""
    return [phase for phase in timeline if phase.end_date < as_of]


def overall_health(tasks: list[Task], timeline: list[TimelinePhase] | None, as_of: date) -> tuple[str, str]:
    """Rule-based RAG health: Red for a missed milestone or a blocked High-priority task,
    Amber for overdue work, Green otherwise."""
    alerts = task_alerts(tasks, as_of)
    missed = [
        phase for phase in (timeline or [])
        if milestone_assessment(phase, tasks, as_of)[0] == "Missed"
    ]
    blocked_high = [task for task in alerts["blocked"] if task.priority == "High"]
    if missed or blocked_high:
        parts = []
        if missed:
            parts.append("missed milestone(s): " + ", ".join(f"Phase {p.phase} {p.name}" for p in missed))
        if blocked_high:
            parts.append("blocked High-priority task(s): " + ", ".join(t.task_id for t in blocked_high))
        return "Red", "; ".join(parts)
    if alerts["overdue"] or alerts["blocked"]:
        ids = [task.task_id for task in alerts["overdue"] + alerts["blocked"]]
        return "Amber", "overdue or blocked task(s): " + ", ".join(ids)
    return "Green", "no overdue or blocked tasks"


def task_table(tasks: list[Task]) -> str:
    if not tasks:
        return "_None_"
    lines = ["| ID | Task | Status | Assignee | Priority | Sprint | Due |", "|---|---|---|---|---|---|---|"]
    lines += [
        f"| {t.task_id} | {t.name} | {t.status} | {t.assignee} | {t.priority} | Sprint {t.sprint} | {t.due_date} |"
        for t in tasks
    ]
    return "\n".join(lines)

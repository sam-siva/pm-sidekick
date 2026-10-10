"""Mira orchestrator — Router/Dispatcher pattern.

identify_intent classifies each request and dispatches it to one specialist agent;
specialists that produce content hand off to generate_report, while clarifying
questions go straight back to the user.

    python orchestrator.py "What are the top 3 risks for the ABCDE Ltd project?"
"""

import sys

from langgraph.graph import END, START, StateGraph

from agent.planner.intent_agent import (
    INTENT_TO_NODE,
    SPECIALIST_NODES,
    UNSUPPORTED_NODE,
    MiraState,
    ask_clarifying_questions,
    identify_intent,
    report_or_end,
    route_by_intent,
    unsupported_request,
)
from agent.planner.mstracker_agent import track_milestone
from agent.planner.planner_agent import generate_plan
from agent.planner.reporter_agent import generate_report
from agent.planner.risk_agent import track_risk
from agent.planner.stakeholder_agent import generate_stakeholder_update
from agent.planner.status_agent import generate_status
from observability.tracing import run_config
from utils.logger import _logger

DEFAULT_REQUEST = (
    "identify and track risks for the project, "
    "for the stakehoder in the exective level in PDF format"
)

workflow = StateGraph(MiraState)

# Router/Dispatcher: identify_intent classifies the request, then dispatches to a specialist
workflow.add_node("identify_intent", identify_intent)
workflow.add_node("generate_plan", generate_plan)
workflow.add_node("track_risk", track_risk)
workflow.add_node("track_milestone", track_milestone)
workflow.add_node("generate_status", generate_status)
workflow.add_node("generate_stakeholder_update", generate_stakeholder_update)
workflow.add_node("ask_clarifying_questions", ask_clarifying_questions)
workflow.add_node(UNSUPPORTED_NODE, unsupported_request)
workflow.add_node("generate_report", generate_report)

workflow.add_edge(START, "identify_intent")
workflow.add_conditional_edges(
    "identify_intent", route_by_intent, [*INTENT_TO_NODE.values(), UNSUPPORTED_NODE]
)
# A specialist can decline a vague request; its questions go back in chat, not to a report
for specialist in SPECIALIST_NODES:
    workflow.add_conditional_edges(specialist, report_or_end, ["generate_report", END])
workflow.add_edge("generate_report", END)
workflow.add_edge("ask_clarifying_questions", END)
workflow.add_edge(UNSUPPORTED_NODE, END)

graph = workflow.compile()


def ask(request: str) -> dict:
    """Run one request through Mira and print the specialist's answer."""
    _logger.info("Mira request: %s", request)
    result = graph.invoke(
        {"messages": [{"role": "user", "content": request}]},
        config=run_config("mira_request", entrypoint="cli"),
    )
    for message in result["messages"][1:]:
        message.pretty_print()
    return result


if __name__ == "__main__":
    ask(" ".join(sys.argv[1:]) or DEFAULT_REQUEST)

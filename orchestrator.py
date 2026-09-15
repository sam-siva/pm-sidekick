import subprocess
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState
from agent.planner.planner_agent import generate_plan
from agent.planner.reporter_agent import generate_report
from utils.logger import _logger

workflow = StateGraph(MessagesState)

# Define the nodes to cycle between
workflow.add_node("generate_plan", generate_plan)
workflow.add_node("generate_report", generate_report)
workflow.add_edge(START, "generate_plan")
workflow.add_edge("generate_plan", "generate_report")
workflow.add_edge("generate_plan", END)

graph = workflow.compile()

def run_agentic_rag() -> None:
    _logger.info("Running the agentic RAG process.")
    for chunk in graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "generate project information for the current month, "
                    "for the stakehoder in the exective level in powerpoint format",
                }
            ]
        },
        stream_mode="values",
    ):
        _logger.info("Processing a new chunk from the agentic RAG stream.")
        last_message = chunk["messages"][-1]
        _logger.info("Last message retrieved from the chunk: %s", last_message)
        pretty_print = getattr(last_message, "pretty_print", None)
        if callable(pretty_print):
            pretty_print()
    _logger.info("Finished processing the agentic RAG stream.")

if __name__ == "__main__":
    _logger.info("Starting the agentic RAG process.")
    run_agentic_rag()
    _logger.info("Finished the agentic RAG process.")


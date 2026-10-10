from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState


def latest_user_request(state: MessagesState) -> str:
    """Return the content of the most recent user message, or '' if there is none."""
    for message in reversed(state.get("messages", [])):
        if isinstance(message, HumanMessage):
            return message.content
    return ""

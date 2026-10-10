import os
from functools import lru_cache

from langsmith import Client


@lru_cache
def get_client() -> Client:
    """Return a process-wide LangSmith client, built from env vars."""
    return Client()


def project_name() -> str:
    return os.environ.get("LANGSMITH_PROJECT", "mira-dev")


def tracing_enabled() -> bool:
    return os.environ.get("LANGSMITH_TRACING", "false").lower() == "true"

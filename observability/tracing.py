from observability.client import project_name


def run_config(run_name: str, **metadata) -> dict:
    """Build a LangChain/LangGraph `config` dict that names and tags a run in LangSmith."""
    return {
        "run_name": run_name,
        "tags": [f"{key}:{value}" for key, value in metadata.items()],
        "metadata": {**metadata, "project": project_name()},
    }

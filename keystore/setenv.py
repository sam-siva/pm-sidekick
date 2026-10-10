import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_REQUIRED = ["OPENAI_API_KEY", "LANGSMITH_API_KEY"]
_DEFAULTS = {"LANGSMITH_TRACING": "true", "LANGSMITH_PROJECT": "mira-dev"}

for key, default in _DEFAULTS.items():
    os.environ.setdefault(key, default)

missing = [key for key in _REQUIRED if not os.environ.get(key)]
if missing:
    raise RuntimeError(
        f"Missing required environment variable(s): {', '.join(missing)}. "
        "Copy mira/.env.example to mira/.env and fill in real values."
    )

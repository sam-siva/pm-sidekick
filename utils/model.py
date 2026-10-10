import keystore.setenv
from langchain.chat_models import init_chat_model
from utils.logger import _logger

llmmodel = None

def getchatmodel(model_name: str, temperature: float = 0):
    """Initialize a chat model with the given model name and temperature."""
    global llmmodel
    if llmmodel is None:
        try:
            llmmodel = init_chat_model(model_name, temperature=temperature)
        except Exception as e:
            _logger.error(f"Failed to initialize chat model {model_name}: {e}")
            raise
    return llmmodel

getchatmodel("gpt-4o")  # Initialize the model at module load time

# Intent classification is a short, constrained task — a smaller model keeps per-request cost low.
routermodel = init_chat_model("gpt-4o-mini", temperature=0)

# The groundedness judge uses a different model from the generators, so it isn't grading its own output.
judgemodel = init_chat_model("gpt-4.1", temperature=0)

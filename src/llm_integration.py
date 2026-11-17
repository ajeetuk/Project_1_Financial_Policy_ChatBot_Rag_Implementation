from langchain_openai import ChatOpenAI

from src.config_loader import load_config


def get_llm_model() -> ChatOpenAI:
    """Return a ChatOpenAI LLM instance.

    The API key is read automatically from the OPENAI_API_KEY
    environment variable by the LangChain client.
    """
    cfg = load_config()["llm"]
    return ChatOpenAI(model=cfg["model_name"], temperature=cfg["temperature"])
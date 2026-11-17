from langchain_openai import OpenAIEmbeddings

from src.config_loader import load_config


def get_embedding_model() -> OpenAIEmbeddings:
    """Return an OpenAI embedding model instance.

    The API key is read automatically from the OPENAI_API_KEY
    environment variable by the LangChain client.
    """
    model = load_config()["embeddings"]["model"]   # text-embedding-ada-002
    return OpenAIEmbeddings(model=model)
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings

from src.config_loader import load_config

PERSIST_DIRECTORY = load_config()["vector_store"]["persist_directory"]  # db


def create_vector_store(
    chunks: list[Document],
    embeddings: OpenAIEmbeddings,
    persist_directory: str = PERSIST_DIRECTORY,
) -> Chroma:
    """Create and persist a Chroma vector store from document chunks."""
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )


def load_vector_store(
    embeddings: OpenAIEmbeddings,
    persist_directory: str = PERSIST_DIRECTORY,
) -> Chroma:
    """Load an existing Chroma vector store from disk."""
    return Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )


def get_retriever(vector_store: Chroma) -> VectorStoreRetriever:
    """Return a retriever from the vector store (similarity search, top-k)."""
    cfg = load_config()["retriever"]
    return vector_store.as_retriever(
        search_type=cfg["search_type"],
        search_kwargs={"k": cfg["k"]},
    )
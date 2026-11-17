from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config_loader import load_config


def chunk_documents(docs: list[Document]) -> list[Document]:
    """Split documents into smaller chunks for embedding.

    Splits on paragraph (\\n\\n), then new line (\\n), then sentence (.),
    then word, so chunks break at natural boundaries where possible.
    """
    cfg = load_config()["chunking"]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg["chunk_size"],  # 1000
        chunk_overlap=cfg["chunk_overlap"],# 200
        separators=cfg["separators"],
    )
    return text_splitter.split_documents(docs)
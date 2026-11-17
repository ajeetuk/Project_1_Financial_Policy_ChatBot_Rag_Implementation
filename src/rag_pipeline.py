import os

from langchain_community.vectorstores import Chroma

from src.document_loaders import load_documents
from src.chunking import chunk_documents
from src.embeddings import get_embedding_model
from src.vectorstore import create_vector_store, load_vector_store, get_retriever, PERSIST_DIRECTORY
from src.llm_integration import get_llm_model
from prompts.prompt_template import build_prompt

def indexing_pipeline(file_path: str) -> Chroma:
    """Load a PDF, chunk it, embed it, and store in a vector database."""
    # step 1. Load documents from the PDF
    documents = load_documents(file_path)

    # step 2. Chunk the documents
    chunks = chunk_documents(documents)

    # step 3.  Get the embedding model
    embeddings = get_embedding_model()

    # step 4. Create and persist the vector store
    vector_store = create_vector_store(chunks, embeddings, persist_directory=PERSIST_DIRECTORY)

    return vector_store


def get_answer(question: str) -> str:
    """Retrieve relevant context and return an LLM-generated answer."""
    if not os.path.exists(PERSIST_DIRECTORY):
        raise FileNotFoundError(
            "No documents have been ingested yet. "
            "Please upload and process a document first."
        )

    embedding_model = get_embedding_model()
    vector_store = load_vector_store(embedding_model)
    retriever = get_retriever(vector_store)

    relevant_docs = retriever.invoke(question)
    # PyMuPDF pages are 0-based, so add 1 to show the real page number.
    context = "\n\n".join(
        f"(Source: {os.path.basename(doc.metadata.get('source', 'N/A'))}, "
        f"Page {doc.metadata.get('page', -1) + 1}) {doc.page_content}"
        for doc in relevant_docs
    )

    prompt = build_prompt(context, question)
    llm = get_llm_model()
    response = llm.invoke(prompt)
    return response.content


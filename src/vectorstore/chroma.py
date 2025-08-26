"""Interact with a ChromaDB vector store for Lyra journals."""

from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from src.journal.parser import parse_journal
from src.utils.device_fallback import safe_load_embeddings

_EMBEDDINGS: Embeddings | None = None


def _get_embeddings() -> Embeddings:
    """Return a reusable embedding model with VRAM OOM fallback."""

    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = safe_load_embeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )
    return _EMBEDDINGS


def get_client(
    persist_directory: str | Path,
    *,
    embedding: Embeddings | None = None,
) -> Chroma:
    """Initialize a ChromaDB client at ``persist_directory``."""

    embeddings = embedding or _get_embeddings()
    return Chroma(
        collection_name="lyra_journal",
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
    )


def ingest_journal(
    path: str | Path,
    *,
    persist_directory: str | Path,
    embedding: Embeddings | None = None,
) -> None:
    """Parse ``path`` and store entries into ChromaDB."""

    entries = parse_journal(path)
    client = get_client(persist_directory, embedding=embedding)
    texts = [e.text for e in entries]
    metadatas = [{"id": e.id, **e.metadata} for e in entries]
    ids = [e.id for e in entries]
    client.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    client.persist()


def search(
    query: str,
    *,
    persist_directory: str | Path,
    k: int = 4,
    embedding: Embeddings | None = None,
) -> list[str]:
    """Return the top ``k`` entries most similar to ``query``."""

    client = get_client(persist_directory, embedding=embedding)
    docs = client.similarity_search(query, k)
    return [doc.page_content for doc in docs]


"""Embedding generation tests."""

import pytest
from langchain_core.embeddings import FakeEmbeddings

from src.vectorstore.chroma import get_client, ingest_journal


class FailingEmbeddings(FakeEmbeddings):
    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        super().__init__(size=32)

    def embed_documents(self, texts):  # type: ignore[override]
        raise RuntimeError("embedding failure")


def test_embeddings_created_for_each_entry(journal_file, tmp_path) -> None:
    persist = tmp_path / "store"
    ingest_journal(
        journal_file,
        persist_directory=persist,
        embedding=FakeEmbeddings(size=32),
    )
    client = get_client(persist, embedding=FakeEmbeddings(size=32))
    assert client._collection.count() == 3


def test_embedding_failure_raises_error(journal_file, tmp_path) -> None:
    persist = tmp_path / "store"
    with pytest.raises(RuntimeError):
        ingest_journal(
            journal_file,
            persist_directory=persist,
            embedding=FailingEmbeddings(),
        )

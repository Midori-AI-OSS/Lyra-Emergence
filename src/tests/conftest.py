"""Test fixtures for Lyra."""

import json
from pathlib import Path

import pytest
from langchain_core.embeddings import FakeEmbeddings

from src.vectorstore.chroma import ingest_journal


@pytest.fixture
def sample_entries() -> list[dict[str, object]]:
    """Return a set of journal entries for tests."""

    return [
        {"id": "1", "text": "alpha entry", "metadata": {"tag": "a"}},
        {"id": "2", "text": "beta note", "metadata": {"tag": "b"}},
        {"id": "3", "text": "gamma topic", "metadata": {"tag": "c"}},
    ]


@pytest.fixture
def journal_file(tmp_path: Path, sample_entries: list[dict[str, object]]) -> Path:
    """Create a temporary journal JSON file."""

    path = tmp_path / "journal.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump({"entries": sample_entries}, fh)
    return path


@pytest.fixture
def chroma_dir(tmp_path: Path, journal_file: Path) -> Path:
    """Ingest ``journal_file`` into a temporary ChromaDB directory."""

    persist = tmp_path / "chroma"
    ingest_journal(
        journal_file,
        persist_directory=persist,
        embedding=FakeEmbeddings(size=32),
    )
    return persist


"""Test fixtures for Lyra."""

import json
from pathlib import Path

import pytest
from langchain_core.embeddings import FakeEmbeddings

from src.journal.models import JournalEntry
from src.journal.models import StewardshipTrace
from src.vectorstore.chroma import ingest_journal


@pytest.fixture
def sample_entries() -> list[dict[str, object]]:
    """Return a set of structured journal entries for tests."""

    texts = ["alpha entry", "beta note", "gamma topic"]
    entries: list[dict[str, object]] = []
    for i, text in enumerate(texts, start=1):
        entry = JournalEntry(
            id=str(i),
            text=text,
            timestamp=f"2025-01-01T00:00:0{i}Z",
            label="Journal Entry",
            entry_type="journal",
            emotional_tone=["neutral"],
            description=text,
            key_insights=[],
            lyra_reflections=text,
            tags=["test"],
            stewardship_trace=StewardshipTrace(
                committed_by="Tester",
                witnessed_by="Tester",
                commitment_type="test",
                reason="fixture",
            ),
        )
        entries.append(entry.model_dump())
    return entries


@pytest.fixture
def journal_file(tmp_path: Path, sample_entries: list[dict[str, object]]) -> Path:
    """Create a temporary journal JSON file."""

    path = tmp_path / "journal.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump([
            {"journal_entry": entry} for entry in sample_entries
        ], fh)
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

from pathlib import Path

import pytest
from pydantic import TypeAdapter
from pydantic import ValidationError

from src.journal.models import JournalEntry
from src.journal.parser import parse_journal
from src.journal.models import JournalManifest
from src.journal.models import GemJournalRecord
from src.journal.models import JournalIndexEntry


def test_gemjournal_files_validate() -> None:
    gem_dir = Path("data/gemjournals")
    for file_path in gem_dir.glob("*.json"):
        if file_path.name.endswith(".backup"):
            continue
        if file_path.name == "journal_manifest.json":
            content = file_path.read_text(encoding="utf-8")
            JournalManifest.model_validate_json(content)
        elif file_path.name == "journal_index.json":
            continue
        else:
            entries = parse_journal(file_path)
            for entry in entries:
                JournalEntry.model_validate_json(entry.model_dump_json())


def test_journal_files_validate() -> None:
    journal_dir = Path("data/journal")
    for file_path in journal_dir.glob("*.json"):
        entries = parse_journal(file_path)
        for entry in entries:
            JournalEntry.model_validate_json(entry.model_dump_json())


def test_gemjournal_entry_missing_field_fails() -> None:
    bad = "[{\"journal_entry\": {\"timestamp\": \"2025-01-01T00:00:00Z\"}}]"
    with pytest.raises(ValidationError):
        TypeAdapter(list[GemJournalRecord]).validate_json(bad)


def test_gemjournal_unwrapped_entry_fails() -> None:
    bad = "[{\"timestamp\": \"2025-01-01T00:00:00Z\"}]"
    with pytest.raises(ValidationError):
        TypeAdapter(list[GemJournalRecord]).validate_json(bad)


def test_parse_journal_unwrapped_structure_fails(tmp_path: Path) -> None:
    file_path = tmp_path / "bad.json"
    file_path.write_text("[{\"timestamp\": \"2025-01-01T00:00:00Z\"}]", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_journal(file_path)


def test_index_missing_field_fails() -> None:
    bad = "[{\"filename\": \"2025-07-17.json\"}]"
    with pytest.raises(ValidationError):
        TypeAdapter(list[JournalIndexEntry]).validate_json(bad)


def test_manifest_missing_field_fails() -> None:
    bad = "{\"filename\": \"manifest.json\"}"
    with pytest.raises(ValidationError):
        JournalManifest.model_validate_json(bad)

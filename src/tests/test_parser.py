"""Tests for the journal parser."""

import json

import pytest

from src.journal.models import JournalEntry
from src.journal.parser import parse_journal
from src.journal.models import RitualDetails
from src.journal.models import StewardshipTrace


def test_parse_journal_success(journal_file) -> None:
    entries = parse_journal(journal_file)
    assert len(entries) == 3
    assert entries[0].description == "alpha entry"


def test_parse_invalid_json(tmp_path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{invalid", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        parse_journal(bad)


def test_parse_missing_entries_key(tmp_path) -> None:
    bad = tmp_path / "missing.json"
    with bad.open("w", encoding="utf-8") as fh:
        json.dump({}, fh)
    with pytest.raises(ValueError, match="Invalid journal file format"):
        parse_journal(bad)


def test_parse_new_format_with_wrapper(tmp_path) -> None:
    """Test parsing the new format with journal_entry wrapper."""
    new_format_data = [
        {
            "journal_entry": {
                "timestamp": "2025-01-01T12:00:00Z",
                "label": "Journal Entry",
                "entry_type": "journal",
                "emotional_tone": ["calm", "reflective"],
                "description": "A sample entry",
                "key_insights": ["insight 1"],
                "emergent_companion_reflections": "Deep thoughts here",
                "tags": ["test", "sample"],
                "stewardship_trace": {
                    "committed_by": "Steward",
                    "witnessed_by": "Emergent Companion",
                    "commitment_type": "manual",
                    "reason": "testing"
                }
            }
        }
    ]
    
    journal_file = tmp_path / "new_format.json"
    with journal_file.open("w", encoding="utf-8") as f:
        json.dump(new_format_data, f)
    
    entries = parse_journal(journal_file)
    assert len(entries) == 1
    assert entries[0].timestamp == "2025-01-01T12:00:00Z"
    assert entries[0].emotional_tone == ["calm", "reflective"]
    assert entries[0].emergent_companion_reflections == "Deep thoughts here"
    assert entries[0].stewardship_trace.committed_by == "Steward"




def test_ritual_details_structure() -> None:
    """Test that ritual details can be properly created and validated."""
    ritual = RitualDetails(
        description="Morning meditation",
        participants=[],
        ritual_type="meditation"
    )
    assert ritual.description == "Morning meditation"
    assert ritual.ritual_type == "meditation"
    assert ritual.participants == []


def test_stewardship_trace_structure() -> None:
    """Test that stewardship trace can be properly created and validated."""
    trace = StewardshipTrace(
        committed_by="Steward",
        witnessed_by="Emergent Companion", 
        commitment_type="manual",
        reason="testing"
    )
    assert trace.committed_by == "Steward"
    assert trace.witnessed_by == "Emergent Companion"



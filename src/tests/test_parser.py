"""Tests for the journal parser."""

import json

import pytest

from src.journal.parser import parse_journal, JournalEntry, RitualDetails, StewardshipTrace


def test_parse_journal_success(journal_file) -> None:
    entries = parse_journal(journal_file)
    assert len(entries) == 3
    assert entries[0].text == "alpha entry"


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


def test_name_replacements(tmp_path) -> None:
    """Test that name replacements work correctly."""
    data_with_names = [
        {
            "journal_entry": {
                "timestamp": "2025-01-01T12:00:00Z",
                "label": "Journal Entry",
                "entry_type": "journal",
                "emotional_tone": ["friendly"],
                "description": "Brian talked to Lyra about Sandi",
                "key_insights": [],
                "lyra_reflection": "Lyra thinks about Brian and Sandi",
                "tags": ["conversation"],
                "stewardship_trace": {
                    "committed_by": "Brian",
                    "witnessed_by": "Lyra",
                    "commitment_type": "conversation",
                    "reason": "discussion"
                }
            }
        }
    ]
    
    journal_file = tmp_path / "names_test.json"
    with journal_file.open("w", encoding="utf-8") as f:
        json.dump(data_with_names, f)
    
    entries = parse_journal(journal_file)
    assert len(entries) == 1
    
    entry = entries[0]
    assert "Steward talked to Emergent Companion about Co-Steward" in entry.description
    assert "Emergent Companion thinks about Steward and Co-Steward" in entry.emergent_companion_reflections
    assert entry.stewardship_trace.committed_by == "Steward"
    assert entry.stewardship_trace.witnessed_by == "Emergent Companion"


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


def test_legacy_field_mapping(tmp_path) -> None:
    """Test that lyra_reflection field is mapped to emergent_companion_reflections."""
    legacy_data = {
        "entries": [
            {
                "id": "test",
                "text": "test content",
                "lyra_reflection": "old field name"
            }
        ]
    }
    
    journal_file = tmp_path / "legacy_mapping.json"
    with journal_file.open("w", encoding="utf-8") as f:
        json.dump(legacy_data, f)
    
    entries = parse_journal(journal_file)
    assert len(entries) == 1
    assert entries[0].emergent_companion_reflections == "old field name"

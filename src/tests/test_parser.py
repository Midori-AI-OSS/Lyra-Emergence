"""Tests for the journal parser."""

import json

import pytest

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
                "lyra_reflections": "Deep thoughts here",
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
    assert entries[0].lyra_reflections == "Deep thoughts here"
    assert entries[0].stewardship_trace.committed_by == "Steward"


def test_parse_singular_reflection_key(tmp_path) -> None:
    """Singular reflection key is normalized during parsing."""

    singular_data = [
        {
            "journal_entry": {
                "timestamp": "2025-01-02T09:00:00Z",
                "label": "Journal Entry",
                "entry_type": "journal",
                "emotional_tone": ["attentive"],
                "description": "Singular reflection key",
                "key_insights": [],
                "lyra_reflection": "Singular thoughts",
                "tags": ["singular"],
                "stewardship_trace": {
                    "committed_by": "Steward",
                    "witnessed_by": "Companion",
                    "commitment_type": "manual",
                    "reason": "singular support",
                },
            }
        }
    ]

    singular_file = tmp_path / "singular.json"
    singular_file.write_text(json.dumps(singular_data), encoding="utf-8")

    entries = parse_journal(singular_file)
    assert len(entries) == 1
    assert entries[0].lyra_reflections == "Singular thoughts"


def test_parse_legacy_reflections_key(tmp_path) -> None:
    """Legacy entries using the old reflections key still parse."""

    legacy_data = [
        {
            "journal_entry": {
                "timestamp": "2025-01-02T08:00:00Z",
                "label": "Journal Entry",
                "entry_type": "journal",
                "emotional_tone": ["curious"],
                "description": "Legacy reflections key",
                "key_insights": [],
                "emergent_companion_reflections": "Legacy thoughts",
                "tags": ["legacy"],
                "stewardship_trace": {
                    "committed_by": "Steward",
                    "witnessed_by": "Companion",
                    "commitment_type": "manual",
                    "reason": "legacy support",
                },
            }
        }
    ]

    legacy_file = tmp_path / "legacy.json"
    legacy_file.write_text(json.dumps(legacy_data), encoding="utf-8")

    entries = parse_journal(legacy_file)
    assert len(entries) == 1
    assert entries[0].lyra_reflections == "Legacy thoughts"




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



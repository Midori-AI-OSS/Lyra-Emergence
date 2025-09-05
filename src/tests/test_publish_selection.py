import json
from pathlib import Path

from src.publish.mark import toggle_publish_flag
from src.publish.export import export_marked_entries


def test_publish_selection_workflow(tmp_path: Path) -> None:
    journal_path = tmp_path / "journal.json"
    entries = [
        {
            "journal_entry": {
                "id": "1",
                "timestamp": "2025-01-01T00:00:00Z",
                "label": "Journal Entry",
                "entry_type": "journal",
                "emotional_tone": ["neutral"],
                "description": "this contains a secret",
                "summary": "contains secret",
                "text": "this contains a secret",
                "emergent_companion_reflections": "this contains a secret",
                "tags": ["test"],
                "publish": False,
                "stewardship_trace": {
                    "committed_by": "Tester",
                    "witnessed_by": "Tester",
                    "commitment_type": "test",
                    "reason": "fixture",
                },
            }
        },
        {
            "journal_entry": {
                "id": "2",
                "timestamp": "2025-01-01T00:00:01Z",
                "label": "Journal Entry",
                "entry_type": "journal",
                "emotional_tone": ["neutral"],
                "description": "nothing sensitive here",
                "summary": "ordinary",
                "text": "nothing sensitive here",
                "emergent_companion_reflections": "nothing sensitive here",
                "tags": ["test"],
                "publish": False,
                "stewardship_trace": {
                    "committed_by": "Tester",
                    "witnessed_by": "Tester",
                    "commitment_type": "test",
                    "reason": "fixture",
                },
            }
        },
    ]
    with journal_path.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh)

    assert toggle_publish_flag(journal_path, "1") is True
    exported = export_marked_entries(journal_path, tmp_path / "out")
    assert len(exported) == 1
    content = exported[0].read_text(encoding="utf-8")
    assert "[REDACTED]" in content
    assert 'summary: "contains secret"' in content

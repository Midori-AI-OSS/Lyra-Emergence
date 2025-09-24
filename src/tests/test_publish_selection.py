import json
from pathlib import Path

import pytest

from src.journal.paths import JournalPathError
from src.journal.paths import normalize_journal_path
from src.publish.export import export_marked_entries
from src.publish.mark import toggle_publish_flag


def test_publish_selection_workflow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trusted_dir = tmp_path / "journals"
    trusted_dir.mkdir()
    monkeypatch.setattr(
        "src.journal.paths.TRUSTED_JOURNAL_DIRS",
        (trusted_dir.resolve(),),
        raising=False,
    )

    journal_path = trusted_dir / "journal.json"
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
                "lyra_reflections": "this contains a secret",
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
                "lyra_reflections": "nothing sensitive here",
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


def test_toggle_publish_flag_rejects_untrusted_path(tmp_path: Path) -> None:
    journal_path = tmp_path / "journal.json"
    with journal_path.open("w", encoding="utf-8") as fh:
        json.dump([], fh)

    with pytest.raises(JournalPathError):
        toggle_publish_flag(journal_path, "1")


def test_normalize_journal_path_accepts_trusted_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trusted_dir = tmp_path / "journals"
    trusted_dir.mkdir()
    monkeypatch.setattr(
        "src.journal.paths.TRUSTED_JOURNAL_DIRS",
        (trusted_dir.resolve(),),
        raising=False,
    )

    journal_path = trusted_dir / "entry.json"
    journal_path.write_text("[]", encoding="utf-8")

    normalized = normalize_journal_path(journal_path)
    assert normalized == journal_path.resolve()


def test_normalize_journal_path_rejects_unexpected_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trusted_dir = tmp_path / "journals"
    trusted_dir.mkdir()
    monkeypatch.setattr(
        "src.journal.paths.TRUSTED_JOURNAL_DIRS",
        (trusted_dir.resolve(),),
        raising=False,
    )

    journal_path = trusted_dir / "entry.txt"
    journal_path.write_text("[]", encoding="utf-8")

    with pytest.raises(JournalPathError):
        normalize_journal_path(journal_path)

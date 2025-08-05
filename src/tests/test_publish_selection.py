import json
from pathlib import Path

from src.publish.export import export_marked_entries
from src.publish.mark import toggle_publish_flag


def test_publish_selection_workflow(tmp_path: Path) -> None:
    journal_path = tmp_path / "journal.json"
    entries = [
        {
            "id": "1",
            "text": "this contains a secret",
            "summary": "contains secret",
            "publish": False,
        },
        {
            "id": "2",
            "text": "nothing sensitive here",
            "summary": "ordinary",
            "publish": False,
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

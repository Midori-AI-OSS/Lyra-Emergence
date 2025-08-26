import json
from pathlib import Path
from typing import Any


def toggle_publish_flag(journal_path: Path, entry_id: str) -> bool:
    """Toggle the ``publish`` flag for the entry with ``entry_id``.

    Returns ``True`` if the entry was found and updated, otherwise ``False``.
    """
    journal_path = Path(journal_path)
    with journal_path.open("r", encoding="utf-8") as fh:
        data: Any = json.load(fh)

    entries = data if isinstance(data, list) else data.get("entries", [])
    updated = False
    for entry in entries:
        if str(entry.get("id")) == entry_id:
            entry["publish"] = not bool(entry.get("publish", False))
            updated = True
            break

    if updated:
        with journal_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
    return updated

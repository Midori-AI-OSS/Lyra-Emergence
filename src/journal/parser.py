"""Read Lyra journal entries stored as JSON."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class JournalEntry:
    """A single journal record."""

    id: str
    text: str
    metadata: dict[str, Any]
    publish: bool = False
    summary: str | None = None


def parse_journal(path: str | Path) -> list[JournalEntry]:
    """Parse a JSON file containing journal entries.

    The file may contain either a top-level list of entries or an object with an
    ``entries`` list. Each entry must provide ``id`` and ``text`` fields and may
    include optional ``metadata``.
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    raw_entries = data["entries"] if isinstance(data, dict) else data
    entries: list[JournalEntry] = []
    for item in raw_entries:
        entry_id = str(item.get("id", ""))
        text = item.get("text", "")
        metadata = item.get("metadata", {})
        publish = bool(item.get("publish", False))
        summary = item.get("summary")
        entries.append(
            JournalEntry(
                id=entry_id,
                text=text,
                metadata=metadata,
                publish=publish,
                summary=summary,
            )
        )
    return entries

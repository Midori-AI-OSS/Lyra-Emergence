"""Utilities for reading structured journal entries."""

import json
from pathlib import Path

from .models import JournalEntry


def parse_journal(path: str | Path) -> list[JournalEntry]:
    """Parse a JSON file containing journal entries.

    The file must be either a list of objects each containing a ``journal_entry``
    field or a single object with that field. Any deviation from this structure
    raises ``ValueError``.

    Returns a list of validated :class:`JournalEntry` models.
    """

    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8"))

    if isinstance(data, dict) and "journal_entry" in data:
        records = [data["journal_entry"]]
    elif isinstance(data, list) and all(
        isinstance(item, dict) and "journal_entry" in item for item in data
    ):
        records = [item["journal_entry"] for item in data]
    else:
        raise ValueError("Invalid journal file format")

    for record in records:
        trace = record.get("stewardship_trace")
        if isinstance(trace, dict):
            if isinstance(trace.get("witnessed_by"), list):
                trace["witnessed_by"] = ", ".join(trace["witnessed_by"])
            if isinstance(trace.get("committed_by"), list):
                trace["committed_by"] = ", ".join(trace["committed_by"])

    return [JournalEntry.model_validate(record) for record in records]


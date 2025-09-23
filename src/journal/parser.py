"""Utilities for reading structured journal entries."""

import json

from typing import Any
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

    def collect_records(raw: Any) -> list[dict[str, Any]]:
        if isinstance(raw, dict):
            if "journal_entry" in raw:
                entry = raw["journal_entry"]
                if isinstance(entry, dict):
                    return [entry]
            raise ValueError("Invalid journal file format")
        if isinstance(raw, list):
            records: list[dict[str, Any]] = []
            for item in raw:
                records.extend(collect_records(item))
            if records:
                return records
            raise ValueError("Invalid journal file format")
        raise ValueError("Invalid journal file format")

    records = collect_records(data)

    for record in records:
        if "lyra_reflections" not in record:
            if "lyra_reflection" in record:
                record["lyra_reflections"] = record.pop("lyra_reflection")
            elif "emergent_companion_reflections" in record:
                record["lyra_reflections"] = record.pop("emergent_companion_reflections")
        trace = record.get("stewardship_trace")
        if isinstance(trace, dict):
            if isinstance(trace.get("witnessed_by"), list):
                trace["witnessed_by"] = ", ".join(trace["witnessed_by"])
            if isinstance(trace.get("committed_by"), list):
                trace["committed_by"] = ", ".join(trace["committed_by"])

    return [JournalEntry.model_validate(record) for record in records]


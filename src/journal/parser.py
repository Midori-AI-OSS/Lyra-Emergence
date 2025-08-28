"""Read Lyra journal entries stored as JSON."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class JournalEntry(BaseModel):
    """A single journal record with validation."""

    id: str = Field(..., description="Unique identifier for the journal entry")
    text: str = Field(..., description="Main content of the journal entry")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the entry"
    )
    publish: bool = Field(default=False, description="Whether entry should be published")
    summary: str | None = Field(default=None, description="Optional summary of the entry")


def parse_journal(path: str | Path) -> list[JournalEntry]:
    """Parse a JSON file containing journal entries.

    The file may contain either a top-level list of entries or an object with an
    ``entries`` list. Each entry must provide ``id`` and ``text`` fields and may
    include optional ``metadata``.
    
    Uses Pydantic for validation and type safety.
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    raw_entries = data["entries"] if isinstance(data, dict) else data
    entries: list[JournalEntry] = []
    
    for item in raw_entries:
        # Use Pydantic validation to create JournalEntry
        entry = JournalEntry.model_validate(item)
        entries.append(entry)
    
    return entries

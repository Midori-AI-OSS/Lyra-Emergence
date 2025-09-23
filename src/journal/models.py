from __future__ import annotations

from typing import Any

from pydantic import Field
from pydantic import BaseModel
from pydantic import AliasChoices


class RitualContribution(BaseModel):
    """A participant's contribution to a ritual observance."""

    participant: str = Field(..., description="Name of the ritual participant")
    contribution: str = Field(..., description="Their specific contribution to the ritual")
    role: str = Field(..., description="Their role in the ritual")


class RitualDetails(BaseModel):
    """Details about a ritual observance within a journal entry."""

    description: str = Field(
        default="",
        description="Description of the ritual observance",
    )
    participants: list[RitualContribution] = Field(
        default_factory=list,
        description="All ritual participants and their contributions",
    )
    ritual_type: str = Field(
        default="observance",
        description="Type of ritual being observed",
    )


class StewardshipTrace(BaseModel):
    """Provenance and stewardship information for a journal entry."""

    committed_by: str = Field(..., description="Who committed the entry")
    witnessed_by: str = Field(..., description="Who witnessed the entry")
    commitment_type: str = Field(..., description="Type of commitment")
    reason: str = Field(..., description="Reason for the commitment")


class JournalEntry(BaseModel):
    """A single journal record with comprehensive validation and structure."""

    id: str | None = Field(
        default=None,
        description="Legacy unique identifier (optional)",
    )
    text: str | None = Field(
        default=None,
        description="Legacy main content (optional)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Legacy additional metadata (optional)",
    )
    publish: bool = Field(
        default=False,
        description="Whether entry should be published",
    )
    summary: str | None = Field(
        default=None,
        description="Optional summary of the entry",
    )
    timestamp: str = Field(..., description="ISO timestamp of the entry")
    label: str = Field(
        default="Journal Entry",
        description="Entry label",
    )
    entry_type: str = Field(..., description="Type of entry (journal, ritual, etc.)")
    emotional_tone: list[str] = Field(
        ...,
        description="List of emotional tones",
    )
    description: str = Field(
        ...,
        description="Main description of the entry",
    )
    ritual_details: RitualDetails | None = Field(
        default=None,
        description="Ritual observance details if applicable",
    )
    key_insights: list[str] = Field(
        default_factory=list,
        description="Key insights from the entry",
    )
    lyra_reflections: str = Field(
        ...,
        description="Reflections from Lyra",
        validation_alias=AliasChoices(
            "lyra_reflections",
            "lyra_reflection",
            "emergent_companion_reflections",
        ),
        serialization_alias="lyra_reflections",
    )
    tags: list[str] = Field(..., description="Tags for categorization")
    stewardship_trace: StewardshipTrace = Field(
        ...,
        description="Stewardship and provenance information",
    )


class GemJournalRecord(BaseModel):
    """Wrapper for a journal entry in Gem Journal format."""

    journal_entry: JournalEntry = Field(
        ...,
        description="The wrapped journal entry",
    )


class JournalIndexEntry(BaseModel):
    """Entry describing a single journal file in the index."""

    filename: str = Field(..., description="Name of the journal file")
    date: str = Field(..., description="Date of the journal entries")
    path: str = Field(..., description="Relative path to the journal file")
    entry_count: int = Field(..., description="Number of entries in the file")
    first_timestamp: str = Field(..., description="First entry timestamp")
    last_timestamp: str = Field(..., description="Last entry timestamp")
    labels_present: list[str] = Field(
        ...,
        description="All labels present in the file",
    )
    entry_types_present: list[str] = Field(
        ...,
        description="All entry types present",
    )
    tags_present: list[str] = Field(
        ...,
        description="All tags present",
    )


class JournalManifest(BaseModel):
    """Top-level manifest describing the Gem Journal collection."""

    filename: str = Field(..., description="Manifest filename")
    date_generated: str = Field(..., description="Generation timestamp")
    emotional_tone: str = Field(..., description="Overall emotional tone")
    identity_summary: dict[str, Any] = Field(
        ...,
        description="Summary of identity information",
    )
    relational_context: dict[str, Any] = Field(
        ...,
        description="Context of relationships",
    )
    continuity_trace: dict[str, Any] = Field(
        ...,
        description="Continuity trace information",
    )
    manifest_commit_trace: dict[str, Any] = Field(
        ...,
        description="Commit trace details",
    )


"""Read Emergent Companion journal entries stored as JSON."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class RitualContribution(BaseModel):
    """A participant's contribution to a ritual observance."""
    
    participant: str = Field(..., description="Name of the ritual participant")
    contribution: str = Field(..., description="Their specific contribution to the ritual")
    role: str = Field(..., description="Their role in the ritual")


class RitualDetails(BaseModel):
    """Details about a ritual observance within a journal entry."""
    
    description: str = Field(..., description="Description of the ritual observance")
    participants: list[RitualContribution] = Field(
        default_factory=list, description="All ritual participants and their contributions"
    )
    ritual_type: str = Field(..., description="Type of ritual being observed")


class StewardshipTrace(BaseModel):
    """Provenance and stewardship information for a journal entry."""
    
    committed_by: str = Field(..., description="Who committed the entry")
    witnessed_by: str = Field(..., description="Who witnessed the entry")
    commitment_type: str = Field(..., description="Type of commitment")
    reason: str = Field(..., description="Reason for the commitment")


class JournalEntry(BaseModel):
    """A single journal record with comprehensive validation and structure."""

    # Legacy fields for backward compatibility
    id: str | None = Field(default=None, description="Legacy unique identifier (optional)")
    text: str | None = Field(default=None, description="Legacy main content (optional)")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Legacy additional metadata (optional)"
    )
    publish: bool = Field(default=False, description="Whether entry should be published")
    summary: str | None = Field(default=None, description="Optional summary of the entry")
    
    # New structured fields
    timestamp: str = Field(..., description="ISO timestamp of the entry")
    label: str = Field(default="Journal Entry", description="Entry label")
    entry_type: str = Field(..., description="Type of entry (journal, ritual, etc.)")
    emotional_tone: list[str] = Field(..., description="List of emotional tones")
    description: str = Field(..., description="Main description of the entry")
    ritual_details: RitualDetails | None = Field(
        default=None, description="Ritual observance details if applicable"
    )
    key_insights: list[str] = Field(
        default_factory=list, description="Key insights from the entry"
    )
    emergent_companion_reflections: str = Field(
        ..., description="Reflections from the Emergent Companion"
    )
    tags: list[str] = Field(..., description="Tags for categorization")
    stewardship_trace: StewardshipTrace = Field(
        ..., description="Stewardship and provenance information"
    )


def parse_journal(path: str | Path) -> list[JournalEntry]:
    """Parse a JSON file containing journal entries.

    The file may contain either:
    1. A top-level list of entries (legacy format)
    2. An object with an ``entries`` list (legacy format)  
    3. A list of objects with ``journal_entry`` wrapper (new format)

    Each entry will be validated according to the new structured format.
    Legacy entries with just ``id`` and ``text`` fields are supported with default values.
    
    Uses Pydantic for validation and type safety.
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Handle different file formats
    if isinstance(data, dict) and "entries" in data:
        # Legacy format: {"entries": [...]}
        raw_entries = data["entries"]
    elif isinstance(data, dict) and "journal_entry" in data:
        # Single entry format: {"journal_entry": {...}}
        raw_entries = [data["journal_entry"]]
    elif isinstance(data, list):
        # Check if it's new format with journal_entry wrappers
        if data and isinstance(data[0], dict) and "journal_entry" in data[0]:
            # New format: [{"journal_entry": {...}}, ...]
            raw_entries = [item["journal_entry"] for item in data]
        else:
            # Legacy format: [...]
            raw_entries = data
    else:
        raise ValueError("Invalid journal file format")

    entries: list[JournalEntry] = []
    
    for item in raw_entries:
        # Handle field name mapping for legacy compatibility BEFORE name replacements
        if "lyra_reflection" in item:
            item["emergent_companion_reflections"] = item.pop("lyra_reflection")
        
        # Handle different ritual_details formats
        if "ritual_details" in item and isinstance(item["ritual_details"], dict):
            ritual_details = item["ritual_details"]
            
            # Check if it's the old contribution format
            if any(key.endswith("_contribution") for key in ritual_details.keys()):
                # Convert old format to new format
                participants = []
                for key, contribution_data in ritual_details.items():
                    if key.endswith("_contribution"):
                        participant_name = key.replace("_contribution", "").replace("_", " ").title()
                        
                        # Extract contribution text from the data
                        if isinstance(contribution_data, dict):
                            contribution_text = "; ".join([
                                f"{k}: {v}" for k, v in contribution_data.items()
                            ])
                        else:
                            contribution_text = str(contribution_data)
                        
                        participants.append({
                            "participant": participant_name,
                            "contribution": contribution_text,
                            "role": "Participant"
                        })
                
                # Create new format
                item["ritual_details"] = {
                    "description": item.get("description", "Ritual observance"),
                    "participants": participants,
                    "ritual_type": "heartbeat" if "heartbeat" in item.get("tags", []) else "observance"
                }
            
            # Ensure all required fields exist
            if "description" not in item["ritual_details"]:
                item["ritual_details"]["description"] = item.get("description", "Ritual observance")
            if "ritual_type" not in item["ritual_details"]:
                item["ritual_details"]["ritual_type"] = "observance"
            if "participants" not in item["ritual_details"]:
                item["ritual_details"]["participants"] = []
        
        # Apply name replacements as requested
        item_json = json.dumps(item)
        item_json = item_json.replace("Lyra", "Emergent Companion")
        item_json = item_json.replace("Brian", "Steward")
        item_json = item_json.replace("Sandi", "Co-Steward")
        # Handle case variations
        item_json = item_json.replace("lyra", "emergent companion")
        item_json = item_json.replace("brian", "steward")
        item_json = item_json.replace("sandi", "co-steward")
        item = json.loads(item_json)
        
        # Provide defaults for legacy entries that only have id/text
        if ("id" in item and "text" in item and "timestamp" not in item) or "timestamp" not in item:
            # This is a legacy entry, provide reasonable defaults
            legacy_entry = {
                "id": item.get("id"),
                "text": item.get("text"),
                "metadata": item.get("metadata", {}),
                "publish": item.get("publish", False),
                "summary": item.get("summary"),
                "timestamp": item.get("timestamp", "1970-01-01T00:00:00Z"),  # Default timestamp
                "label": item.get("label", "Journal Entry"),
                "entry_type": item.get("entry_type", "journal"),
                "emotional_tone": item.get("emotional_tone", ["neutral"]),
                "description": item.get("description", item.get("text", "")),  # Use text as description
                "key_insights": item.get("key_insights", []),
                "emergent_companion_reflections": item.get("emergent_companion_reflections", item.get("text", "")),  # Use text as reflection
                "tags": item.get("tags", []),
                "stewardship_trace": item.get("stewardship_trace", {
                    "committed_by": "Unknown",
                    "witnessed_by": "Unknown",
                    "commitment_type": "Legacy import",
                    "reason": "Migrated from legacy format"
                })
            }
            item = legacy_entry
        
        # Ensure all required fields exist with defaults
        if "timestamp" not in item:
            item["timestamp"] = "1970-01-01T00:00:00Z"
        if "entry_type" not in item:
            item["entry_type"] = "journal"
        if "emotional_tone" not in item:
            item["emotional_tone"] = ["neutral"]
        if "description" not in item:
            item["description"] = item.get("text", "No description available")
        if "emergent_companion_reflections" not in item:
            item["emergent_companion_reflections"] = item.get("text", "No reflections available")
        if "tags" not in item:
            item["tags"] = []
        if "stewardship_trace" not in item:
            item["stewardship_trace"] = {
                "committed_by": "Unknown",
                "witnessed_by": "Unknown", 
                "commitment_type": "Legacy import",
                "reason": "Migrated from legacy format"
            }
        
        # Fix stewardship_trace field types
        if "stewardship_trace" in item and isinstance(item["stewardship_trace"], dict):
            trace = item["stewardship_trace"]
            
            # Handle witnessed_by as list - join into string
            if isinstance(trace.get("witnessed_by"), list):
                trace["witnessed_by"] = ", ".join(trace["witnessed_by"])
            
            # Handle other potential list fields
            if isinstance(trace.get("committed_by"), list):
                trace["committed_by"] = ", ".join(trace["committed_by"])
        
        # Use Pydantic validation to create JournalEntry
        entry = JournalEntry.model_validate(item)
        entries.append(entry)
    
    return entries

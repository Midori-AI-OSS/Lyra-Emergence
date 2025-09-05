# JSON Validation

The project validates journal data using Pydantic models. The `scripts/validate_json.py` helper now loads each JSON file and validates it by instantiating the corresponding Pydantic model with [`model_validate_json`].

## Journal Data

- **Journal entries** — validated against `JournalEntry` from `src/journal/models.py`.
- **Gem journals** — each element wraps a `journal_entry` and is represented by `GemJournalRecord`.
- **Journal index** — parsed as a list of `JournalIndexEntry` objects.
- **Journal manifest** — validated with `JournalManifest`.

Legacy journal formats are no longer supported; files must follow this structure to pass validation.

Any missing or malformed field now raises a `ValidationError`, allowing CI and contributors to catch issues early.

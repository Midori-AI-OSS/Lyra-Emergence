# Add selection mechanism for publishing journal entries externally (stretch)

## Problem
There is no system for choosing which journal entries to publish externally. A manual or automated selection process is required for curated sharing.

## Tasks
- [ ] Extend the journal schema or metadata to include a boolean `publish` flag and a short summary field.
- [ ] Provide a CLI command such as `uv run lyra.py --mark <id>` to toggle the flag for specific entries.
- [ ] Implement an export script (`src/publish/export.py`) that gathers all flagged entries and writes them to `data/published/` as Markdown files with front-matter.
- [ ] Sanitize exported content to remove sensitive information and include a warning if potential secrets are detected.
- [ ] Document the review and export workflow in `.codex/implementation/publish-selection.md`, emphasizing manual review before publication.
- [ ] Add a test in `src/tests/test_publish_selection.py` that marks a sample entry, runs the export script, and verifies the output file is created with the expected content.

## Acceptance Criteria
- Contributors can mark entries for publication and generate sanitized exports in `data/published/`.
- Exported files omit sensitive data and include front-matter suitable for external sharing.
- Documentation outlines the marking and export process, and associated tests pass via `uv run pytest`.

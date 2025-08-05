# Publish Selection Workflow

## Marking Entries
- Run `uv run lyra.py --mark <id>` to toggle the `publish` flag on a journal entry.
- The command edits the journal JSON in place (default `data/journal/sample.json`).

## Exporting Marked Entries
- Use `export_marked_entries` from `src.publish.export` to generate Markdown files:
  ```bash
  uv run python -m src.publish.export
  ```
- The export writes Markdown files to `data/published/` with YAML front matter including `id` and `summary`.
- If sensitive terms like `password` or `secret` are detected, they are redacted and a warning comment is inserted.

## Review
- Always review the exported Markdown under `data/published/` before sharing externally to ensure no sensitive information remains.

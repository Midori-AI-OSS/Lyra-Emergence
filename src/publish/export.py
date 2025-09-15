import re
import sys
from argparse import ArgumentParser
from pathlib import Path

from src.journal.parser import parse_journal

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"


def _validate_data_path(path: Path, *, description: str) -> Path:
    """Ensure ``path`` stays within the project's data directory."""

    candidate = Path(path)
    if any(part == ".." for part in candidate.parts):
        raise ValueError(
            f"The {description} '{candidate}' may not contain '..' segments. "
            f"Please provide a location inside '{DATA_ROOT}'.",
        )

    if candidate.is_absolute():
        base_path = candidate
    elif candidate.parts and candidate.parts[0] == "data":
        base_path = PROJECT_ROOT / candidate
    else:
        base_path = DATA_ROOT / candidate

    resolved = base_path.resolve(strict=False)

    try:
        resolved.relative_to(DATA_ROOT)
    except ValueError as exc:
        raise ValueError(
            f"The {description} '{candidate}' must be located inside the data directory at '{DATA_ROOT}'.",
        ) from exc

    return resolved

SENSITIVE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in ["password", "secret"]
]


def sanitize_text(text: str) -> tuple[str, bool]:
    """Redact simple sensitive terms from ``text``.

    Returns the sanitized text and a flag indicating whether any redactions were
    applied.
    """
    sanitized = text
    redacted = False
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(sanitized):
            sanitized = pattern.sub("[REDACTED]", sanitized)
            redacted = True
    return sanitized, redacted


def export_marked_entries(journal_path: Path, output_dir: Path) -> list[Path]:
    """Export journal entries marked for publication to Markdown files."""

    safe_journal_path = _validate_data_path(journal_path, description="journal file path")
    safe_output_dir = _validate_data_path(output_dir, description="output directory")

    entries = parse_journal(safe_journal_path)
    safe_output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []
    for entry in entries:
        if not entry.publish:
            continue
        sanitized, redacted = sanitize_text(entry.text)
        file_path = safe_output_dir / f"{entry.id}.md"
        with file_path.open("w", encoding="utf-8") as fh:
            fh.write("---\n")
            fh.write(f'id: "{entry.id}"\n')
            if entry.summary:
                fh.write(f'summary: "{entry.summary}"\n')
            fh.write("---\n\n")
            if redacted:
                fh.write("<!-- WARNING: Potential secrets were redacted -->\n\n")
            fh.write(sanitized)
        exported.append(file_path)
    return exported


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--journal",
        type=Path,
        default=Path("data/gemjournals/sample.json"),
        help="Path to the journal JSON file",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/published"),
        help="Directory to write exported Markdown files",
    )
    args = parser.parse_args()

    try:
        export_marked_entries(args.journal, args.out)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

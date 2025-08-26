import re
from argparse import ArgumentParser
from pathlib import Path

from src.journal.parser import parse_journal

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
    entries = parse_journal(journal_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []
    for entry in entries:
        if not entry.publish:
            continue
        sanitized, redacted = sanitize_text(entry.text)
        file_path = output_dir / f"{entry.id}.md"
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
        default=Path("data/journal/sample.json"),
        help="Path to the journal JSON file",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/published"),
        help="Directory to write exported Markdown files",
    )
    args = parser.parse_args()
    export_marked_entries(args.journal, args.out)


if __name__ == "__main__":
    main()

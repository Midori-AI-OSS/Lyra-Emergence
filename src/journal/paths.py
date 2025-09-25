"""Utilities for validating journal file paths."""

from __future__ import annotations

from pathlib import Path

class JournalPathError(ValueError):
    """Raised when a journal path fails validation."""


ALLOWED_JOURNAL_EXTENSIONS = frozenset({".json"})

TRUSTED_JOURNAL_DIRS = (
    Path("data/gemjournals").resolve(),
    Path("data/journal").resolve(),
)


def normalize_journal_path(
    path: str | Path,
    *,
    require_exists: bool = True,
) -> Path:
    """Return a normalized path if it resides within a trusted journal directory."""

    raw_candidate = Path(path).expanduser()
    trusted_dirs = tuple(directory.resolve() for directory in TRUSTED_JOURNAL_DIRS)

    if raw_candidate.is_absolute():
        candidate = raw_candidate
    else:
        candidate = Path.cwd() / raw_candidate

    resolved = candidate.resolve(strict=False)

    if require_exists and not resolved.exists():
        raise JournalPathError(f"Journal file not found: {raw_candidate}")

    if resolved.exists() and resolved.is_dir():
        raise JournalPathError(f"Journal path must reference a file: {raw_candidate}")

    if resolved.suffix.lower() not in ALLOWED_JOURNAL_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_JOURNAL_EXTENSIONS))
        raise JournalPathError(
            "Journal files must use one of the allowed extensions "
            f"({allowed}). Received: {resolved.name}"
        )

    if not any(resolved.is_relative_to(directory) for directory in trusted_dirs):
        trusted = ", ".join(str(directory) for directory in trusted_dirs)
        raise JournalPathError(
            f"Journal path {raw_candidate} must reside within a trusted directory: {trusted}"
        )

    # Reject symbolic links anywhere in the provided path
    current = candidate
    while True:
        if current.exists() and current.is_symlink():
            raise JournalPathError(
                f"Journal path cannot include symbolic links: {raw_candidate}"
            )
        if current == current.parent:
            break
        current = current.parent

    return resolved


__all__ = [
    "ALLOWED_JOURNAL_EXTENSIONS",
    "JournalPathError",
    "TRUSTED_JOURNAL_DIRS",
    "normalize_journal_path",
]


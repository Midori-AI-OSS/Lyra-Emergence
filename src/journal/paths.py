"""Utilities for validating journal file paths."""

from __future__ import annotations

from pathlib import Path
import os

class JournalPathError(ValueError):
    """Raised when a journal path fails validation."""


ALLOWED_JOURNAL_EXTENSIONS = frozenset({".json"})

TRUSTED_JOURNAL_DIRS = (
    Path("data/gemjournals").resolve(),
    Path("data/journal").resolve(),
)


def _is_within_directory(path: Path, directory: Path) -> bool:
    """Return ``True`` if ``path`` is located inside ``directory``."""

    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def normalize_journal_path(
    path: str | Path,
    *,
    require_exists: bool = True,
) -> Path:
    """Return a normalized path if it resides within a trusted journal directory.

    Args:
        path: Path-like object pointing to the journal file.
        require_exists: If ``True`` (the default), the path must point to an
            existing file.

    Raises:
        JournalPathError: If the path falls outside the trusted directories,
            has an unexpected extension, or does not exist when required.
    """

    candidate = Path(path).expanduser()
    # Use strict resolution if the path exists; fallback to normpath otherwise.
    if candidate.exists():
        normalized = candidate.resolve(strict=True)
        # Reject symlinks to avoid escape via links
        if normalized.is_symlink():
            raise JournalPathError(f"Journal path cannot be a symlink: {candidate}")
    else:
        # When the file does not exist, construct a normpath variant rooted in the safest allowed directory.
        # For each trusted dir, try to resolve; only allow if normalization stays within the trusted root.
        normalized = None
        for trusted_dir in TRUSTED_JOURNAL_DIRS:
            base_dir = trusted_dir
            try_path = base_dir / candidate.name
            combined = os.path.normpath(os.path.join(str(base_dir), str(candidate.name)))
            try_path_obj = Path(combined)
            if _is_within_directory(try_path_obj.resolve(strict=False), base_dir):
                normalized = try_path_obj
                break
        if normalized is None:
            trusted = ", ".join(str(directory) for directory in TRUSTED_JOURNAL_DIRS)
            raise JournalPathError(
                f"Journal path {candidate} must reside within a trusted directory: {trusted}"
            )

    if normalized.suffix.lower() not in ALLOWED_JOURNAL_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_JOURNAL_EXTENSIONS))
        raise JournalPathError(
            "Journal files must use one of the allowed extensions "
            f"({allowed}). Received: {candidate.name}"
        )

    # Double-check: path must reside inside trusted directories after all normalization
    if not any(_is_within_directory(normalized.resolve(strict=False), directory) for directory in TRUSTED_JOURNAL_DIRS):
        trusted = ", ".join(str(directory) for directory in TRUSTED_JOURNAL_DIRS)
        raise JournalPathError(
            f"Journal path {candidate} must reside within a trusted directory: {trusted}"
        )

    if require_exists and not normalized.exists():
        raise JournalPathError(f"Journal file not found: {candidate}")

    if normalized.exists() and normalized.is_dir():
        raise JournalPathError(f"Journal path must reference a file: {candidate}")

    return normalized


__all__ = [
    "ALLOWED_JOURNAL_EXTENSIONS",
    "JournalPathError",
    "TRUSTED_JOURNAL_DIRS",
    "normalize_journal_path",
]


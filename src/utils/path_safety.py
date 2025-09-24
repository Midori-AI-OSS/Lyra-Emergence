from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

APPROVED_JOURNAL_ROOTS: tuple[Path, ...] = (
    (PROJECT_ROOT / "data" / "gemjournals").resolve(),
    (PROJECT_ROOT / "data" / "journal").resolve(),
)


def ensure_journal_path(candidate: Path) -> Path:
    """Validate a journal path and return its resolved location.

    The helper ensures that the provided path exists, does not traverse through
    any symbolic links, and ultimately resides within one of the approved journal
    directories for the project.

    Args:
        candidate: User-provided path to a journal file.

    Returns:
        The fully resolved absolute path to the journal file.

    Raises:
        ValueError: If the path is missing, points to a directory, contains a
            symbolic link, or resolves outside the approved journal roots.
    """
    # Expand potential "~" in input
    expanded_candidate = candidate.expanduser()

    # Disallow absolute paths provided by user input
    if expanded_candidate.is_absolute():
        raise ValueError(
            f"Absolute paths are not allowed for journal files: {candidate} "
            f"(must be relative to one of the approved roots)"
        )

    # Try to resolve the candidate path under each approved root
    valid_resolved_path = None
    for root in APPROVED_JOURNAL_ROOTS:
        try:
            joined_path = (root / expanded_candidate)
            resolved_path = joined_path.resolve(strict=True)
            # Check that resolved path is contained within this root
            if resolved_path.is_relative_to(root):
                valid_resolved_path = resolved_path
                break
        except Exception:
            continue # Try next root

    if valid_resolved_path is None:
        allowed = ", ".join(str(root) for root in APPROVED_JOURNAL_ROOTS)
        raise ValueError(
            f"Journal path must be located within an approved journal directory ({allowed}): {expanded_candidate}"
        )

    # Disallow directories
    if valid_resolved_path.is_dir():
        raise ValueError(f"Journal path must reference a file: {valid_resolved_path}")

    # Disallow any symlinks in the path or its parents
    current_path = valid_resolved_path
    while True:
        if current_path.is_symlink():
            raise ValueError(
                f"Journal path cannot include symbolic links: {candidate}"
            )
        if current_path == current_path.parent:
            break
        current_path = current_path.parent

    return valid_resolved_path

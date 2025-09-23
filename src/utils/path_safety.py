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

    # If path is not absolute, anchor it in the first approved root
    if not expanded_candidate.is_absolute():
        expanded_candidate = (APPROVED_JOURNAL_ROOTS[0] / expanded_candidate)

    # Resolve the path, ensuring it exists and is canonical
    try:
        resolved_path = expanded_candidate.resolve(strict=True)
    except Exception:
        raise ValueError(f"Journal path does not exist: {candidate}")

    # Disallow directories
    if resolved_path.is_dir():
        raise ValueError(f"Journal path must reference a file: {resolved_path}")

    # Disallow any symlinks in the path or its parents
    # Ensure the resolved file is strictly within an approved root
    current_path = resolved_path
    while True:
        if current_path.is_symlink():
            raise ValueError(
                f"Journal path cannot include symbolic links: {candidate}"
            )
        if current_path == current_path.parent:
            break
        current_path = current_path.parent

    if not any(resolved_path.is_relative_to(root) for root in APPROVED_JOURNAL_ROOTS):
        allowed = ", ".join(str(root) for root in APPROVED_JOURNAL_ROOTS)
        raise ValueError(
            f"Journal path must be located within an approved journal directory ({allowed}): {resolved_path}"
        )

    return resolved_path

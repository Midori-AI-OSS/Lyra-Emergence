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

    # If absolute, must be strictly under one of the roots; else, treat as relative to first root
    approved_root = None
    for root in APPROVED_JOURNAL_ROOTS:
        try:
            candidate_rel = expanded_candidate.relative_to(root)
            approved_root = root
            break
        except ValueError:
            continue

    if expanded_candidate.is_absolute():
        if not approved_root:
            allowed = ", ".join(str(root) for root in APPROVED_JOURNAL_ROOTS)
            raise ValueError(
                f"Absolute journal path must be located within an approved journal directory ({allowed}): {expanded_candidate}"
            )
        raw_path = expanded_candidate
    else:
        # If path is relative, anchor it strictly in the first approved root
        root = APPROVED_JOURNAL_ROOTS[0]
        raw_path = (root / expanded_candidate)
        approved_root = root

    # Now resolve the path and check containment
    try:
        resolved_path = raw_path.resolve(strict=True)
    except Exception:
        raise ValueError(f"Journal path does not exist: {candidate}")

    # Disallow any directories
    if resolved_path.is_dir():
        raise ValueError(f"Journal path must reference a file: {resolved_path}")

    # Disallow any links in the resolved path's parents or itself
    # (better to check after fully resolved)
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

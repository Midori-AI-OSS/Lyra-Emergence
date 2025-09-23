from __future__ import annotations

from pathlib import Path

import pytest

from src.utils.path_safety import ensure_journal_path


def _get_existing_journal_file() -> Path:
    for base in (Path("data/gemjournals"), Path("data/journal")):
        if not base.exists():
            continue

        for candidate in sorted(base.glob("*.json")):
            if candidate.name.endswith(".backup"):
                continue
            return candidate

    pytest.skip("No journal files available for testing")


def test_ensure_journal_path_accepts_valid_file():
    journal_file = _get_existing_journal_file().resolve()
    relative_path = journal_file.relative_to(Path.cwd())

    result = ensure_journal_path(relative_path)

    assert result == journal_file


def test_ensure_journal_path_rejects_absolute_path_outside(tmp_path: Path):
    outside_file = tmp_path / "outside.json"
    outside_file.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        ensure_journal_path(outside_file)

    assert "approved journal directory" in str(exc.value)


def test_ensure_journal_path_rejects_directory_traversal(tmp_path: Path):
    outside_file = Path("data") / "temp_outside.json"
    outside_file.write_text("{}", encoding="utf-8")

    try:
        with pytest.raises(ValueError) as exc:
            ensure_journal_path(Path("data/gemjournals/../temp_outside.json"))

        assert "approved journal directory" in str(exc.value)
    finally:
        outside_file.unlink(missing_ok=True)


def test_ensure_journal_path_rejects_symlink_file():
    journal_file = _get_existing_journal_file().resolve()
    link_path = journal_file.parent / "sample_symlink.json"

    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()

    link_path.symlink_to(journal_file)

    try:
        with pytest.raises(ValueError) as exc:
            ensure_journal_path(link_path)

        assert "symbolic" in str(exc.value)
    finally:
        link_path.unlink(missing_ok=True)


def test_ensure_journal_path_rejects_symlink_directory():
    journal_file = _get_existing_journal_file().resolve()
    link_dir = journal_file.parent / "_symlink_dir_for_tests"

    if link_dir.exists() and not link_dir.is_symlink():
        pytest.fail("Unexpected directory at symlink test location")

    if link_dir.is_symlink():
        link_dir.unlink()

    link_dir.symlink_to(journal_file.parent, target_is_directory=True)

    try:
        with pytest.raises(ValueError) as exc:
            ensure_journal_path(link_dir / journal_file.name)

        assert "symbolic" in str(exc.value)
    finally:
        link_dir.unlink(missing_ok=True)

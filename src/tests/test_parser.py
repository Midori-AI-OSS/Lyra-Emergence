"""Tests for the journal parser."""

import json

import pytest

from src.journal.parser import parse_journal


def test_parse_journal_success(journal_file) -> None:
    entries = parse_journal(journal_file)
    assert len(entries) == 3
    assert entries[0].text == "alpha entry"


def test_parse_invalid_json(tmp_path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{invalid", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        parse_journal(bad)


def test_parse_missing_entries_key(tmp_path) -> None:
    bad = tmp_path / "missing.json"
    with bad.open("w", encoding="utf-8") as fh:
        json.dump({}, fh)
    with pytest.raises(KeyError):
        parse_journal(bad)


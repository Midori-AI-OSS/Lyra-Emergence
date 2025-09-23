import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.journal.paths import JournalPathError
from src.journal.paths import normalize_journal_path


def toggle_publish_flag(journal_path: Path, entry_id: str) -> bool:
    """Toggle the ``publish`` flag for the entry with ``entry_id``.

    Returns ``True`` if the entry was found and updated, otherwise ``False``.
    """
    safe_path = normalize_journal_path(journal_path)

    try:
        with safe_path.open("r", encoding="utf-8") as fh:
            data: Any = json.load(fh)
    except FileNotFoundError as exc:
        raise JournalPathError(f"Journal file not found: {safe_path}") from exc
    except JSONDecodeError as exc:
        raise JournalPathError(
            f"Journal file {safe_path} is not valid JSON: {exc.msg}"
        ) from exc
    except OSError as exc:  # pragma: no cover - unexpected I/O failure
        raise JournalPathError(
            f"Unable to read journal file {safe_path}: {exc.strerror or exc}"
        ) from exc

    entries = data if isinstance(data, list) else data.get("entries", [])
    updated = False
    for item in entries:
        entry = item.get("journal_entry", item)
        if str(entry.get("id")) == entry_id:
            entry["publish"] = not bool(entry.get("publish", False))
            updated = True
            break

    if updated:
        try:
            with safe_path.open("w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except OSError as exc:  # pragma: no cover - unexpected I/O failure
            raise JournalPathError(
                f"Unable to write journal file {safe_path}: {exc.strerror or exc}"
            ) from exc
    return updated

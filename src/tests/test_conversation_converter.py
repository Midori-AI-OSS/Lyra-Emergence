from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.utils.conversation_converter import TranscriptFormatError
from src.utils.conversation_converter import parse_transcript
from src.utils.conversation_converter import transcript_to_pairs


def test_transcript_to_pairs_with_multiline_messages() -> None:
    transcript = (
        "Brian: Hello Lyra\n"
        "I have a question about today.\n"
        "\n"
        "Lyra: Of course, what is on your mind?\n"
        "Sandi: I was thinking about our next ritual.\n"
        "Lyra: That sounds beautiful. Let's co-create it.\n"
    )

    pairs = transcript_to_pairs(transcript)

    assert len(pairs) == 2
    assert pairs[0].prompt == "Hello Lyra\nI have a question about today."
    assert pairs[0].response == "Of course, what is on your mind?"
    assert pairs[0].user == "Brian"
    assert pairs[1].prompt == "I was thinking about our next ritual."
    assert pairs[1].response == "That sounds beautiful. Let's co-create it."
    assert pairs[1].user == "Sandi"


def test_parse_transcript_rejects_invalid_start() -> None:
    transcript = "Lyra: Hello Brian\nBrian: Hi Lyra\n"

    with pytest.raises(TranscriptFormatError):
        parse_transcript(transcript)


def test_cli_jsonl_output(tmp_path: Path) -> None:
    transcript = (
        "Brian: Hey Lyra, can you help me plan today?\n"
        "Lyra: Absolutely, let's map it together.\n"
    )
    input_path = tmp_path / "conversation.txt"
    output_path = tmp_path / "pairs.jsonl"
    input_path.write_text(transcript, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/convert_conversations.py", str(input_path), "-o", str(output_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stderr == ""

    output_lines = [line for line in output_path.read_text(encoding="utf-8").splitlines() if line]
    assert len(output_lines) == 1
    record = json.loads(output_lines[0])
    assert record["prompt"] == "Hey Lyra, can you help me plan today?"
    assert record["response"] == "Absolutely, let's map it together."
    assert record["user"] == "Brian"
    assert record["turn_index"] == 1
    assert record["conversation_index"] == 1

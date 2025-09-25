"""Utilities for converting Lyra conversations into prompt/response pairs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable
from typing import Iterator
from typing import Literal
from typing import Sequence

SPEAKER_ALIASES: dict[str, str] = {
    "brian": "Brian",
    "b": "Brian",
    "sandi": "Sandi",
    "s": "Sandi",
    "lyra": "Lyra",
    "l": "Lyra",
}

Role = Literal["user", "assistant"]


@dataclass(slots=True)
class Message:
    """Single turn extracted from a transcript."""

    speaker: str
    role: Role
    content: str


@dataclass(slots=True)
class PromptResponsePair:
    """Pair of prompt and response extracted from a conversation."""

    prompt: str
    response: str
    user: str
    turn_index: int

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation of the pair."""

        return {
            "prompt": self.prompt,
            "response": self.response,
            "user": self.user,
            "turn_index": self.turn_index,
        }


SPEAKER_LINE_PATTERN = re.compile(r"^(?P<speaker>[A-Za-z][^:]*?):\s*(?P<content>.*)$")


class TranscriptFormatError(ValueError):
    """Raised when a transcript cannot be parsed into alternating turns."""


def _normalise_speaker(raw: str) -> str:
    candidate = raw.strip().lower()
    candidate = re.sub(r"\s*\(.*?\)$", "", candidate)

    if candidate not in SPEAKER_ALIASES:
        raise TranscriptFormatError(f"Unrecognised speaker label: '{raw}'")
    return SPEAKER_ALIASES[candidate]


def parse_transcript(transcript: str) -> list[Message]:
    """Parse a raw transcript into structured messages."""

    messages: list[Message] = []
    current_speaker: str | None = None
    current_role: Role | None = None
    current_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_speaker, current_role, current_lines
        if current_speaker is None or current_role is None:
            return
        content = "\n".join(line.rstrip() for line in current_lines).strip()
        messages.append(Message(current_speaker, current_role, content))
        current_speaker = None
        current_role = None
        current_lines = []

    for raw_line in transcript.splitlines():
        line = raw_line.rstrip()
        if not line:
            if current_lines:
                current_lines.append("")
            continue

        match = SPEAKER_LINE_PATTERN.match(line)
        if match:
            speaker = _normalise_speaker(match.group("speaker"))
            if speaker == "Lyra":
                role = "assistant"
            else:
                role = "user"

            flush_current()
            current_speaker = speaker
            current_role = role
            current_lines = [match.group("content").strip()]
        else:
            if current_speaker is None:
                raise TranscriptFormatError(
                    "Found content before a speaker label: '{line}'".format(line=line)
                )
            current_lines.append(line.strip())

    flush_current()

    if not messages:
        raise TranscriptFormatError("Transcript did not contain any turns")

    if messages[0].role != "user":
        raise TranscriptFormatError("Transcript must begin with a user turn")

    return messages


def pair_messages(messages: Sequence[Message]) -> list[PromptResponsePair]:
    """Convert alternating user/assistant messages into prompt/response pairs."""

    pairs: list[PromptResponsePair] = []
    turn_index = 1
    idx = 0

    while idx < len(messages):
        user_msg = messages[idx]
        if user_msg.role != "user":
            raise TranscriptFormatError(
                f"Expected a user message at turn {turn_index}, got {user_msg.speaker}"
            )

        if idx + 1 >= len(messages):
            raise TranscriptFormatError(
                f"User turn from {user_msg.speaker} missing Lyra response"
            )

        assistant_msg = messages[idx + 1]
        if assistant_msg.role != "assistant":
            raise TranscriptFormatError(
                "User turn must be followed by Lyra's response"
            )

        pairs.append(
            PromptResponsePair(
                prompt=user_msg.content,
                response=assistant_msg.content,
                user=user_msg.speaker,
                turn_index=turn_index,
            )
        )

        turn_index += 1
        idx += 2

    return pairs


def transcript_to_pairs(transcript: str) -> list[PromptResponsePair]:
    """Parse a transcript and return prompt/response pairs."""

    return pair_messages(parse_transcript(transcript))


def iter_pairs_as_jsonl(pairs: Iterable[PromptResponsePair]) -> Iterator[str]:
    """Yield JSONL strings for a sequence of pairs."""

    for pair in pairs:
        yield json.dumps(pair.to_dict(), ensure_ascii=False)


__all__ = [
    "Message",
    "PromptResponsePair",
    "TranscriptFormatError",
    "parse_transcript",
    "pair_messages",
    "transcript_to_pairs",
    "iter_pairs_as_jsonl",
]

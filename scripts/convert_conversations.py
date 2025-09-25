#!/usr/bin/env python3
"""Convert Lyra transcripts into prompt/response pairs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.conversation_converter import TranscriptFormatError
from src.utils.conversation_converter import iter_pairs_as_jsonl
from src.utils.conversation_converter import transcript_to_pairs


def _read_transcript(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert plain-text transcripts of Brian/Sandi and Lyra conversations into "
            "prompt/response pairs suitable for fine-tuning."
        )
    )
    parser.add_argument(
        "paths",
        metavar="TRANSCRIPT",
        nargs="*",
        help=(
            "Path(s) to transcript text files. Use '-' to read a single transcript from stdin."
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Optional output file. Defaults to stdout.",
    )
    parser.add_argument(
        "--format",
        choices=("jsonl", "json"),
        default="jsonl",
        help="Output format. Defaults to jsonl (one record per line).",
    )

    args = parser.parse_args(argv)

    if not args.paths:
        transcripts = [sys.stdin.read()]
    else:
        if args.paths.count("-") > 1:
            parser.error("stdin can only be specified once")
        transcripts = [_read_transcript(path) for path in args.paths]

    output_lines: list[str] = []

    try:
        if args.format == "jsonl":
            for conversation_index, transcript in enumerate(transcripts, start=1):
                pairs = transcript_to_pairs(transcript)
                for line in iter_pairs_as_jsonl(pairs):
                    enriched = json.loads(line)
                    enriched["conversation_index"] = conversation_index
                    output_lines.append(json.dumps(enriched, ensure_ascii=False))
        else:
            conversations: list[list[dict[str, object]]] = []
            for transcript in transcripts:
                pairs = transcript_to_pairs(transcript)
                conversations.append([pair.to_dict() for pair in pairs])
            output_lines.append(json.dumps(conversations, ensure_ascii=False, indent=2))
    except TranscriptFormatError as exc:
        parser.error(str(exc))

    output_text = "\n".join(output_lines)

    if args.output:
        Path(args.output).write_text(output_text + ("\n" if args.format == "jsonl" else ""), encoding="utf-8")
    else:
        sys.stdout.write(output_text)
        if args.format == "jsonl":
            sys.stdout.write("\n")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())

# Implement CLI chat interface for Lyra

## Problem
Lyra currently lacks an interactive command-line interface for live chatting. Users need a way to converse with the agent directly from the terminal.

## Tasks
- [x] Scaffold a new `src/cli/` package and implement `chat.py` with a `ChatSession` class that reads user input, streams agent responses, and exits cleanly on `exit` or `Ctrl+C`.
- [x] Keep `lyra.py` as the root entry point; import `ChatSession` from `src/cli/chat.py` and start the session when executed with `uv run lyra.py`.
- [x] Style all output with `rich` and ensure imports follow the conventions in `AGENTS.md` (each import on its own line, grouped and sorted).
- [x] Add placeholder functions (`retrieve`, `rerank`) inside `ChatSession` to allow later connection to retrieval and vector store components without altering the chat loop.
- [x] Document the CLI module in `.codex/implementation/cli-chat.md`, covering usage and future extension points.
- [x] Create a minimal test in `src/tests/test_cli_chat.py` that instantiates `ChatSession` and verifies the session exits immediately when fed the `exit` command.

## Acceptance Criteria
- Running `uv run lyra.py` launches a terminal chat session that responds to user prompts and terminates when the user types `exit`.
- `ChatSession` contains stub `retrieve` and `rerank` functions ready for future implementation.
- Code resides under `src/`, follows style guidelines, and includes documentation and tests passing via `uv run pytest`.

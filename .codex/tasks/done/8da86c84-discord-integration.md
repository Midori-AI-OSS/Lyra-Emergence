# Implement Discord integration for Lyra chat

## Problem
Lyra needs a way to interact with users via Discord in addition to the CLI.

## Tasks
- [x] Add `discord.py` to `pyproject.toml` and run `uv sync` to install the library.
- [x] Implement `src/integrations/discord_bot.py` that authenticates using the `DISCORD_BOT_TOKEN` environment variable and forwards messages to the existing CLI chat pipeline.
- [x] Ensure the bot reuses `ChatSession` or a shared conversation handler so responses are consistent across interfaces.
- [x] Document required environment variables and bot setup in `.codex/implementation/discord-bot.md` without committing any secrets.
- [x] Provide a short run guide in the documentation showing how to start the bot with `uv run discord_bot.py`.
- [x] Create `src/tests/test_discord_bot.py` with a minimal test that verifies the bot refuses to start when `DISCORD_BOT_TOKEN` is missing.

## Acceptance Criteria
- Running the bot with a valid token allows Discord users to chat with Lyra using the same logic as the CLI.
- Documentation clearly describes setup, required environment variables, and how to run the bot.
- Tests and code respect security guidelines (no tokens in repo) and pass `uv run pytest`.

# Discord Bot Integration

## Setup
- Set the `DISCORD_BOT_TOKEN` environment variable with your bot token.

## Usage
- Start the bot with `uv run discord_bot.py`.
- Messages sent to the bot are processed through `ChatSession` for responses, which defaults to a HuggingFace `microsoft/phi-2` pipeline.

## Security
- Never commit tokens or secrets to the repository.

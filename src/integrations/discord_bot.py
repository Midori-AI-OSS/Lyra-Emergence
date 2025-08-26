"""Discord bot interface for Lyra."""

import asyncio
import os

import discord

from src.cli.chat import ChatSession
from src.utils.device_fallback import safe_load_pipeline


class LyraDiscordBot(discord.Client):
    """Discord client that forwards messages to a ChatSession."""

    def __init__(self, session: ChatSession, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.session = session

    async def on_message(self, message: discord.Message) -> None:  # type: ignore[override]
        if message.author == self.user:
            return
        response = self.session.respond(message.content)
        await message.channel.send(response)


def _build_session() -> ChatSession:
    """Create a chat session with a HuggingFace LLM for responses."""
    llm = safe_load_pipeline(
        model_id="Qwen/Qwen2.5-7B-Instruct",
        task="text-generation",
        pipeline_kwargs={"max_new_tokens": 4000},
    )
    return ChatSession(llm=llm)


async def _run() -> None:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is not set")

    intents = discord.Intents.default()
    session = _build_session()
    client = LyraDiscordBot(session=session, intents=intents)
    await client.start(token)


def main() -> None:
    """Entrypoint for starting the Discord bot."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()

"""Discord bot startup tests."""

import pytest

from src.integrations import discord_bot


def test_missing_token_raises_error(monkeypatch) -> None:
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        discord_bot.main()

"""Tests for the CLI entry point defined in ``lyra.py``."""

from __future__ import annotations

import sys

from typing import Any
from pathlib import Path

import pytest

import lyra
from src.config.model_config import ModelConfig


class _StubConsole:
    """Simple console stub that records printed messages."""

    instances: list["_StubConsole"] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.messages: list[str] = []
        _StubConsole.instances.append(self)

    def print(self, message: str) -> None:
        self.messages.append(message)


def _prepare_common_patches(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch shared dependencies to keep CLI tests lightweight."""

    monkeypatch.setattr(lyra, "Console", _StubConsole)
    monkeypatch.setattr(lyra, "get_env_status", lambda: None)


def test_cli_reports_invalid_model_config_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid config paths should be reported and exit with status 1."""

    _StubConsole.instances.clear()
    _prepare_common_patches(monkeypatch)

    monkeypatch.setattr(lyra, "safe_load_pipeline", lambda *args, **kwargs: None)
    monkeypatch.setattr(lyra, "ChatSession", lambda *args, **kwargs: None)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lyra.py",
            "--notui",
            "--model-config",
            "config/invalid.txt",
        ],
    )

    with pytest.raises(SystemExit) as excinfo:
        lyra.main()

    assert excinfo.value.code == 1
    assert _StubConsole.instances, "Console should have been instantiated"
    error_messages = _StubConsole.instances[0].messages
    assert any("Invalid model configuration path" in msg for msg in error_messages)
    assert any(".json" in msg for msg in error_messages)


def test_cli_allows_valid_model_config_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """A valid config path should allow the CLI to continue running."""

    _StubConsole.instances.clear()
    _prepare_common_patches(monkeypatch)

    config_path = Path("config/valid.json")
    recorded_kwargs: dict[str, Any] = {}

    def fake_load_config(
        config_path: Path | None = None,
        auto_select: bool = False,
    ) -> ModelConfig:
        assert config_path == Path("config/valid.json")
        assert auto_select is True
        return ModelConfig(model_id="test/model")

    class StubSession:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.run_called = False

        def run(self) -> None:
            self.run_called = True
            StubSession.last_instance = self

    StubSession.last_instance: StubSession | None = None

    def fake_safe_load_pipeline(*args: Any, **kwargs: Any) -> str:
        recorded_kwargs.update(kwargs)
        return "pipeline"

    monkeypatch.setattr(lyra, "load_config", fake_load_config)
    monkeypatch.setattr(lyra, "safe_load_pipeline", fake_safe_load_pipeline)
    monkeypatch.setattr(lyra, "ChatSession", StubSession)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lyra.py",
            "--notui",
            "--model-config",
            str(config_path),
        ],
    )

    lyra.main()

    assert recorded_kwargs["config_path"] == config_path
    assert isinstance(StubSession.last_instance, StubSession)
    assert StubSession.last_instance.run_called is True

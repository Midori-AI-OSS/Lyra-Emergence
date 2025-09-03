from __future__ import annotations

from unittest.mock import mock_open

from src.tools import get_tools
from src.utils import env_check


def test_parse_os_release_detection(monkeypatch):
    data = 'NAME="PixelArch"\nID=pixelarch\n'
    monkeypatch.setattr("builtins.open", mock_open(read_data=data))
    info = env_check._read_os_release("/etc/os-release")
    assert info["ID"] == "pixelarch"
    monkeypatch.setattr(env_check, "_check_url", lambda url, timeout=3.0: True)
    assert env_check.compute_env_status().is_pixelarch is True


def test_tools_disabled_on_non_pixelarch(monkeypatch):
    monkeypatch.setattr(env_check, "_read_os_release", lambda path="/etc/os-release": {"ID": "ubuntu"})
    monkeypatch.setattr(env_check, "_check_url", lambda url, timeout=3.0: True)
    status = env_check.compute_env_status()
    assert not status.tools_enabled
    assert get_tools(status) == []


def test_network_tools_toggle(monkeypatch):
    monkeypatch.setattr(env_check, "_read_os_release", lambda path="/etc/os-release": {"ID": "pixelarch"})
    monkeypatch.setattr(env_check, "_check_url", lambda url, timeout=3.0: False)
    status = env_check.compute_env_status()
    assert status.tools_enabled
    assert not status.network_tools_enabled
    assert get_tools(status) == []


def test_tools_enabled(monkeypatch):
    monkeypatch.setattr(env_check, "_read_os_release", lambda path="/etc/os-release": {"ID": "pixelarch"})
    monkeypatch.setattr(env_check, "_check_url", lambda url, timeout=3.0: True)
    status = env_check.compute_env_status()
    tools = get_tools(status)
    assert status.network_tools_enabled
    assert len(tools) == 2

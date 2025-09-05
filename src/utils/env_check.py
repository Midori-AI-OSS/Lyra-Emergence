from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import urlopen

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EnvStatus:
    """State of the current runtime environment."""

    is_pixelarch: bool
    has_internet: bool
    endpoint_ok: bool

    @property
    def tools_enabled(self) -> bool:
        """Return True if general tools should be enabled."""

        return self.is_pixelarch

    @property
    def network_tools_enabled(self) -> bool:
        """Return True if network-dependent tools should be enabled."""

        return self.tools_enabled and self.has_internet and self.endpoint_ok


_ENV_STATUS: EnvStatus | None = None


def _read_os_release(path: str = "/etc/os-release") -> dict[str, str]:
    """Parse a Linux os-release file into a dictionary."""

    data: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    data[key] = value.strip().strip('"')
    except FileNotFoundError:
        logger.debug("os-release file not found at %s", path)
    return data


def _check_url(url: str, timeout: float = 3.0) -> bool:
    """Return True if the given URL responds within timeout."""

    try:
        with urlopen(url, timeout=timeout):
            return True
    except URLError as err:
        logger.debug("URL check failed for %s: %s", url, err)
    except Exception as err:  # pragma: no cover - unexpected errors
        logger.debug("Unexpected error when checking %s: %s", url, err)
    return False


def compute_env_status() -> EnvStatus:
    """Detect environment capabilities and return an EnvStatus."""

    os_info = _read_os_release()
    is_pixelarch = "pixelarch" in os_info.get("ID", "").lower() or "pixelarch" in os_info.get("NAME", "").lower()
    has_internet = _check_url("https://www.google.com")
    endpoint_ok = _check_url("https://tea-cup.midori-ai.xyz/health")
    status = EnvStatus(is_pixelarch=is_pixelarch, has_internet=has_internet, endpoint_ok=endpoint_ok)
    logger.info("EnvStatus computed: %s", status)
    return status


def get_env_status() -> EnvStatus:
    """Return cached environment status, computing it once."""

    global _ENV_STATUS
    if _ENV_STATUS is None:
        _ENV_STATUS = compute_env_status()
    return _ENV_STATUS

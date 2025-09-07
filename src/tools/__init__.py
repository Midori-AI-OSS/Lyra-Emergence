from __future__ import annotations

import logging
from typing import Any
from pathlib import Path

from langchain_core.tools import BaseTool

from src.utils.env_check import EnvStatus
from src.utils.env_check import get_env_status
from src.vectorstore.chroma import search
from src.vectorstore.chroma import ingest_journal

logger = logging.getLogger(__name__)


class JournalIngestTool(BaseTool):
    """Tool for ingesting journal files into ChromaDB."""

    name: str = "ingest_journal"
    description: str = (
        "Ingest a journal JSON file into the local vector store. Input: path to file."
    )

    def _run(self, path: str, *args: Any, **kwargs: Any) -> str:
        ingest_journal(Path(path), persist_directory=Path("data/chroma"))
        return "ingested"

    async def _arun(self, path: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError


class JournalSearchTool(BaseTool):
    """Tool for searching ingested journal entries."""

    name: str = "search_journal"
    description: str = (
        "Search the vector store for entries related to a query. Input: search string."
    )

    def _run(self, query: str, *args: Any, **kwargs: Any) -> str:
        results = search(query, persist_directory=Path("data/chroma"))
        return "\n".join(results)

    async def _arun(self, query: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError


def get_tools(env: EnvStatus | None = None) -> list[BaseTool]:
    """Return available tools based on environment state."""

    env_status = env or get_env_status()
    tools: list[BaseTool] = []
    
    # Always include basic journal tools if network tools are enabled
    if env_status.network_tools_enabled:
        tools.extend([JournalIngestTool(), JournalSearchTool()])
    
    # Add MCP tools if network is available (using LangChain patterns)
    if env_status.network_tools_enabled:
        try:
            from src.tools.mcp_tools import get_mcp_tools
            tools.extend(get_mcp_tools())
            logger.info("MCP tools added using LangChain patterns")
        except ImportError as e:
            logger.warning("MCP tools not available: %s", e)
        except Exception as e:
            logger.error("Error loading MCP tools: %s", e)
    
    # Add Playwright tools if they are available and we have network access (using LangChain toolkit)
    if env_status.network_tools_enabled:
        try:
            from src.tools.playwright_tools import get_playwright_tools
            tools.extend(get_playwright_tools())
            logger.info("LangChain Playwright toolkit added successfully")
        except ImportError as e:
            logger.warning("Playwright toolkit not available: %s", e)
        except Exception as e:
            logger.error("Error loading Playwright toolkit: %s", e)
    
    return tools


__all__ = ["get_tools", "JournalIngestTool", "JournalSearchTool"]

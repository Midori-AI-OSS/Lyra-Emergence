from __future__ import annotations

from pathlib import Path

from langchain_core.tools import BaseTool

from src.utils.env_check import EnvStatus, get_env_status
from src.vectorstore.chroma import ingest_journal, search


class JournalIngestTool(BaseTool):
    """Tool for ingesting journal files into ChromaDB."""

    name: str = "ingest_journal"
    description: str = (
        "Ingest a journal JSON file into the local vector store. Input: path to file."
    )

    def _run(self, path: str) -> str:  # type: ignore[override]
        ingest_journal(Path(path), persist_directory=Path("data/chroma"))
        return "ingested"

    async def _arun(self, path: str) -> str:  # pragma: no cover
        raise NotImplementedError


class JournalSearchTool(BaseTool):
    """Tool for searching ingested journal entries."""

    name: str = "search_journal"
    description: str = (
        "Search the vector store for entries related to a query. Input: search string."
    )

    def _run(self, query: str) -> str:  # type: ignore[override]
        results = search(query, persist_directory=Path("data/chroma"))
        return "\n".join(results)

    async def _arun(self, query: str) -> str:  # pragma: no cover
        raise NotImplementedError


def get_tools(env: EnvStatus | None = None) -> list[BaseTool]:
    """Return available tools based on environment state."""

    env_status = env or get_env_status()
    if not env_status.network_tools_enabled:
        return []
    return [JournalIngestTool(), JournalSearchTool()]


__all__ = ["get_tools", "JournalIngestTool", "JournalSearchTool"]

"""CPU-based reranker for journal entries using Flashrank."""

from typing import Sequence

from flashrank import Ranker
from langchain_core.documents import Document
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank

_DEFAULT_RANKER: Ranker | None = None


def rerank_entries(
    query: str,
    entries: Sequence[str],
    *,
    client: Ranker | None = None,
) -> list[str]:
    """Rerank entries by relevance to the query using Flashrank.

    Args:
        query: User search query.
        entries: Retrieved entries in original order.
        client: Optional ``flashrank`` Ranker for reuse or mocking.

    Returns:
        Entries ordered by decreasing relevance score. Returns an empty list if
        no entries are provided.
    """
    if not entries:
        return []

    ranker = client
    if ranker is None:
        global _DEFAULT_RANKER
        if _DEFAULT_RANKER is None:
            _DEFAULT_RANKER = Ranker()
        ranker = _DEFAULT_RANKER

    compressor = FlashrankRerank(client=ranker, top_n=len(entries))
    documents = [Document(page_content=entry) for entry in entries]
    ranked_docs = compressor.compress_documents(documents, query)
    return [doc.page_content for doc in ranked_docs]

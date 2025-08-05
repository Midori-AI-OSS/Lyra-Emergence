"""Search and rerank pipeline tests."""

from flashrank import Ranker
from flashrank import RerankRequest
from langchain_core.embeddings import FakeEmbeddings

from src.rerank.cpu_reranker import rerank_entries
from src.vectorstore.chroma import search


class DummyRanker(Ranker):
    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        pass

    def rerank(self, request: RerankRequest):  # type: ignore[override]
        passages = request.passages or []
        results = []
        for p in passages:
            score = 1.0 if "alpha" in p["text"] else 0.0
            results.append({"id": p["id"], "text": p["text"], "score": score, "meta": p.get("meta", {})})
        results.sort(key=lambda r: r["score"], reverse=True)
        return results


def test_search_and_rerank(chroma_dir) -> None:
    results = search(
        "alpha",
        persist_directory=chroma_dir,
        embedding=FakeEmbeddings(size=32),
    )
    assert results
    ranked = rerank_entries("alpha", results, client=DummyRanker())
    assert ranked[0] == "alpha entry"


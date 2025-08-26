from flashrank import Ranker, RerankRequest

from src.cli.chat import ChatSession
from src.rerank.cpu_reranker import rerank_entries


class DummyRanker(Ranker):
    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        pass

    def rerank(self, request: RerankRequest):  # type: ignore[override]
        passages = request.passages or []
        results = []
        for p in passages:
            score = 1.0 if "alpha" in p["text"] else 0.0
            results.append(
                {
                    "id": p["id"],
                    "text": p["text"],
                    "score": score,
                    "meta": p.get("meta", {}),
                }
            )
        results.sort(key=lambda r: r["score"], reverse=True)
        return results


def test_rerank_entries_orders_results() -> None:
    entries = ["beta text", "alpha only", "gamma"]
    ranked = rerank_entries("alpha", entries, client=DummyRanker())
    assert ranked == ["alpha only", "beta text", "gamma"]


def test_chat_session_rerank_toggle() -> None:
    entries = ["beta", "alpha entry", "gamma"]
    dummy = DummyRanker()
    session = ChatSession(rerank=True, ranker=dummy)
    assert session.rerank("alpha", entries) == ["alpha entry", "beta", "gamma"]
    session_off = ChatSession(rerank=False, ranker=dummy)
    assert session_off.rerank("alpha", entries) == entries

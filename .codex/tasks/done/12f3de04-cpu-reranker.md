# Add CPU-based reranking for retrieved journal entries

## Problem
Search results from the vector store may be poorly ordered. A CPU-friendly reranker is needed to improve relevance without requiring a GPU.

## Tasks
- [x] Add a lightweight CPU reranking dependency (e.g., `flashrank` or `sentence-transformers`) to `pyproject.toml` and lock it with `uv sync`.
- [x] Implement `src/rerank/cpu_reranker.py` with a `rerank_entries(query, entries)` function that orders search results using the selected model.
- [x] Call `rerank_entries` after ChromaDB retrieval in the query pipeline and ensure it gracefully handles cases with no results.
- [x] Extend the CLI to accept a `--rerank/--no-rerank` flag so users can enable or disable reranking at runtime.
- [x] Document the reranker in `.codex/implementation/cpu-reranker.md`, including performance notes and links to the upstream project.
- [x] Add unit tests in `src/tests/test_cpu_reranker.py` that feed mock search results and confirm the output order changes when reranking is enabled.

## Acceptance Criteria
- Retrieval results are reordered by the CPU reranker when the `--rerank` flag is set.
- Disabling reranking returns results in the original vector-store order.
- Documentation describes how to enable the feature and all new tests pass via `uv run pytest`.

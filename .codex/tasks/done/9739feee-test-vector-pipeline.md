# Add tests for saving, embedding, and searching journal entries

## Problem
The journal ingestion and retrieval pipeline lacks automated tests, making regressions likely.

## Tasks
- [ ] Add fixture utilities in `src/tests/conftest.py` to create temporary journal files and an in-memory ChromaDB instance.
- [ ] Write `test_parser.py` to verify that the journal parser correctly handles valid and malformed JSON entries.
- [ ] Write `test_embeddings.py` to confirm embeddings are generated for each entry and raise clear errors on failure.
- [ ] Write `test_search_and_rerank.py` that ingests sample journals, performs a query, and asserts that results are returned and reranked as expected.
- [ ] Ensure `uv run pytest` is documented as the way to run the suite locally and in CI.

## Acceptance Criteria
- Tests cover parsing, embedding, storage, search, and reranking, and complete within the 25‑second limit.
- Failures clearly identify which stage (parsing, embedding, storage, search, rerank) failed.
- Running `uv run pytest` reports all tests passing.

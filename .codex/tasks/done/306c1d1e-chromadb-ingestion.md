# Integrate ChromaDB vector store and ingest Lyra journal entries

## Problem
Lyra lacks persistent storage for journal entries and semantic search. We need ChromaDB integration that captures new journals, embeds them, and enables retrieval.

## Tasks
- [ ] Add `chromadb` and any required embedding libraries to `pyproject.toml` and run `uv sync` to lock dependencies.
- [ ] Create `src/journal/parser.py` that reads journal entries in JSON format from `data/journal/` and yields structured records.
- [ ] Implement `src/vectorstore/chroma.py` with functions to initialize a ChromaDB client, add parsed journal entries with embeddings, and perform similarity search.
- [ ] Use a CPU-friendly embedding model (e.g., via LangChain `HuggingFaceEmbeddings`) and document the choice in code comments.
- [ ] Wire ingestion so that new journal files are automatically parsed and stored when `uv run lyra.py --ingest <path>` is executed.
- [ ] Document setup and usage in `.codex/implementation/chromadb-ingestion.md`, including instructions for starting a local ChromaDB instance.
- [ ] Add unit tests in `src/tests/test_chromadb_ingestion.py` covering parsing, embedding generation, storage, and search.

## Acceptance Criteria
- Running `uv run lyra.py --ingest data/journal/sample.json` parses the file, embeds each entry, and writes records to ChromaDB.
- Calling the search function returns relevant entries when queried with a semantic phrase.
- Implementation resides under `src/`, includes documentation, and all related tests pass with `uv run pytest`.

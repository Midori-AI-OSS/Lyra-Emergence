# ChromaDB journal ingestion

This module parses Lyra journal files and stores them in a local ChromaDB
collection for semantic search.

## Setup
1. Ensure dependencies are installed with `uv sync`.
2. A local Chroma database is created under `data/chroma` on first use.

## Usage
- Ingest a journal file:
  ```bash
  uv run lyra.py --ingest data/journal/sample.json
  ```
- Query stored entries via the `search` function in
  `src/vectorstore/chroma.py`.

## Embeddings
Embeddings use LangChain's `HuggingFaceEmbeddings` with the
`sentence-transformers/all-MiniLM-L6-v2` model, which runs on CPU.

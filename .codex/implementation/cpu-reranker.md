# CPU Reranker

Reorders retrieved journal entries using [Flashrank](https://pypi.org/project/flashrank/) through LangChain's `FlashrankRerank` document compressor. The reranker runs entirely on CPU and requires no external services.

## Usage
- Enabled by default in the CLI. Disable with `--no-rerank`.
- `rerank_entries(query, entries, client=None)` returns entries ordered by relevance. A custom `Ranker` client may be supplied for testing.

## Performance Notes
- Defaults to the lightweight `ms-marco-TinyBERT-L-2-v2` model.
- All processing occurs on CPU, making it suitable for environments without GPU access.

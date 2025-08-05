# CLI Chat Interface

## Usage
- Run `uv run lyra.py` to start an interactive chat session in the terminal.
- Type messages at the `you>` prompt to converse with the agent.
- Enter `exit` or press `Ctrl+C` to close the session.
- `lyra.py` wires a LangChain `HuggingFacePipeline` by default so responses are generated through the LangChain pipeline.
- Swap in a different `BaseLanguageModel` when constructing `ChatSession` to change model behavior.

## Extension Points
- `ChatSession.retrieve(query: str)`: hook for future document retrieval logic.
- `ChatSession.rerank(query: str, results: list[str])`: hook for reranking retrieved results prior to response generation.
- `ChatSession.respond(query: str)`: uses the configured language model to craft a reply.

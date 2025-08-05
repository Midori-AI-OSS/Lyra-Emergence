"""Command-line chat interface for Lyra."""

from typing import Callable
from typing import Optional

from flashrank import Ranker
from rich.console import Console
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.rerank.cpu_reranker import rerank_entries


class ChatSession:
    """Interactive chat session that reads user input and displays responses."""

    def __init__(
        self,
        console: Optional[Console] = None,
        input_func: Callable[[str], str] | None = None,
        rerank: bool = True,
        ranker: Ranker | None = None,
        llm: BaseLanguageModel | None = None,
    ) -> None:
        self.console = console or Console()
        self.input_func = input_func or input
        self.rerank_enabled = rerank
        self.rerank_client = ranker
        self.llm = llm

    def retrieve(self, query: str) -> list[str]:
        """Placeholder retrieval hook."""
        return []

    def rerank(self, query: str, results: list[str]) -> list[str]:
        """Rerank results if enabled."""
        if not self.rerank_enabled:
            return results

        return rerank_entries(query, results, client=self.rerank_client)

    def respond(self, query: str) -> str:
        """Generate a response using the configured language model."""
        if not self.llm:
            return f"echo: {query}"

        prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
        chain = prompt | self.llm
        result = chain.invoke({"input": query})
        return getattr(result, "content", str(result))

    def run(self) -> None:
        """Start the chat loop."""
        while True:
            try:
                user_input = self.input_func("you> ")
            except KeyboardInterrupt:
                self.console.print("\nExiting...")
                break

            if user_input.strip().lower() == "exit":
                self.console.print("Goodbye!")
                break

            _retrieved = self.retrieve(user_input)
            _ranked = self.rerank(user_input, _retrieved)
            response = self.respond(user_input)
            self.console.print(response)

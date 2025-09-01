"""Command-line chat interface for Lyra."""

from collections.abc import Callable, Iterator
from typing import Generator

from flashrank import Ranker
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from rich.console import Console
from rich.live import Live
from rich.text import Text

from src.rerank.cpu_reranker import rerank_entries
from src.utils.chat_templates import AutoChatTemplateManager


class ChatSession:
    """Interactive chat session that reads user input and displays responses."""

    def __init__(
        self,
        console: Console | None = None,
        input_func: Callable[[str], str] | None = None,
        rerank: bool = True,
        ranker: Ranker | None = None,
        llm: BaseLanguageModel | None = None,
        model_id: str | None = None,
    ) -> None:
        self.console = console or Console()
        self.input_func = input_func or input
        self.rerank_enabled = rerank
        self.rerank_client = ranker
        self.llm = llm
        self.model_id = model_id

        # Initialize chat template manager for automatic templating
        self.template_manager: AutoChatTemplateManager | None = None
        if model_id:
            try:
                self.template_manager = AutoChatTemplateManager(model_id)
                if self.template_manager.has_chat_template():
                    self.console.print(
                        f"[green]✓[/green] Using automatic chat template for {model_id}"
                    )
                else:
                    self.console.print(
                        f"[yellow]![/yellow] Using fallback template for {model_id}"
                    )
            except Exception as e:
                self.console.print(
                    f"[yellow]![/yellow] Template manager initialization failed: {e}"
                )

        # Conversation history for template-based chat
        self.conversation_history: list[dict[str, str]] = []

    def retrieve(self, query: str) -> list[str]:
        """Placeholder retrieval hook."""
        return []

    def rerank(self, query: str, results: list[str]) -> list[str]:
        """Rerank results if enabled."""
        if not self.rerank_enabled:
            return results

        return rerank_entries(query, results, client=self.rerank_client)

    def respond_stream(self, query: str) -> Generator[str, None, None]:
        """Generate a streaming response using the configured language model."""
        if not self.llm:
            yield f"echo: {query}"
            return

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": query})

        # Use automatic chat templating if available
        if self.template_manager:
            try:
                # Format the entire conversation using the model's chat template
                formatted_prompt = self.template_manager.format_conversation(
                    self.conversation_history, add_generation_prompt=True
                )

                # Use the formatted prompt directly with LangChain streaming
                if hasattr(self.llm, "pipeline"):
                    # For HuggingFace pipelines, try to use streaming if available
                    try:
                        # Try using LangChain's streaming interface
                        response_parts = []
                        for chunk in self.llm.stream(formatted_prompt):
                            response_parts.append(chunk)
                            yield chunk
                        
                        # Build complete response for history
                        response_text = "".join(response_parts)
                        
                    except Exception as e:
                        # Fallback to non-streaming if streaming fails
                        self.console.print(
                            f"[yellow]![/yellow] Streaming failed, using non-streaming mode: {e}"
                        )
                        result = self.llm.pipeline(
                            formatted_prompt,
                            max_new_tokens=512,
                            do_sample=True,
                            temperature=0.7,
                        )
                        if isinstance(result, list) and len(result) > 0:
                            response_text = result[0].get("generated_text", "")
                            # Extract only the new response (remove the prompt part)
                            if response_text.startswith(formatted_prompt):
                                response_text = response_text[
                                    len(formatted_prompt) :
                                ].strip()
                        else:
                            response_text = str(result)
                        yield response_text
                else:
                    # Use LangChain streaming for other models
                    try:
                        prompt = ChatPromptTemplate.from_template(formatted_prompt)
                        chain = prompt | self.llm
                        response_parts = []
                        for chunk in chain.stream({}):
                            chunk_text = getattr(chunk, "content", str(chunk))
                            response_parts.append(chunk_text)
                            yield chunk_text
                        response_text = "".join(response_parts)
                    except Exception as e:
                        # Fallback to non-streaming
                        self.console.print(
                            f"[yellow]![/yellow] LangChain streaming failed: {e}. Using fallback."
                        )
                        prompt = ChatPromptTemplate.from_template(formatted_prompt)
                        chain = prompt | self.llm
                        result = chain.invoke({})
                        response_text = getattr(result, "content", str(result))
                        yield response_text

                # Add assistant response to conversation history
                self.conversation_history.append(
                    {"role": "assistant", "content": response_text}
                )

                return

            except Exception as e:
                self.console.print(
                    f"[yellow]![/yellow] Template formatting failed: {e}. Using fallback."
                )

        # Fallback to original LangChain approach with streaming
        try:
            prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
            chain = prompt | self.llm
            response_parts = []
            for chunk in chain.stream({"input": query}):
                chunk_text = getattr(chunk, "content", str(chunk))
                response_parts.append(chunk_text)
                yield chunk_text
            response_text = "".join(response_parts)
        except Exception as e:
            # Final fallback to non-streaming
            self.console.print(
                f"[yellow]![/yellow] Streaming failed: {e}. Using non-streaming fallback."
            )
            prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
            chain = prompt | self.llm
            result = chain.invoke({"input": query})
            response_text = getattr(result, "content", str(result))
            yield response_text

        # Add to history for fallback case
        self.conversation_history.append(
            {"role": "assistant", "content": response_text}
        )
    def respond(self, query: str) -> str:
        """Generate a response using the configured language model."""
        # Use streaming and collect the full response
        response_parts = []
        for chunk in self.respond_stream(query):
            response_parts.append(chunk)
        return "".join(response_parts)

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        if self.console:
            self.console.print("[blue]Conversation history cleared[/blue]")

    def get_template_info(self) -> dict | None:
        """Get information about the current chat template."""
        if self.template_manager:
            return self.template_manager.get_template_info()
        return None

    def set_system_message(self, system_message: str) -> None:
        """Set a system message for the conversation."""
        # Remove any existing system message
        self.conversation_history = [
            msg for msg in self.conversation_history if msg.get("role") != "system"
        ]

        # Add new system message at the beginning
        self.conversation_history.insert(
            0, {"role": "system", "content": system_message}
        )

        if self.console:
            self.console.print(f"[blue]System message set: {system_message}[/blue]")

    def run(self) -> None:
        """Start the chat loop with streaming output."""
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
            
            # Display streaming response
            self.console.print("lyra> ", end="", style="bold cyan")
            
            # Create a Text object to accumulate the response
            response_text = Text()
            
            try:
                # Use Rich's Live context for real-time updates
                with Live(response_text, console=self.console, refresh_per_second=10) as live:
                    for chunk in self.respond_stream(user_input):
                        response_text.append(chunk)
                        live.update(response_text)
                
                # Print a newline after the streaming is complete
                self.console.print()
                
            except Exception as e:
                # Fallback to non-streaming display if streaming fails
                self.console.print(f"\n[yellow]![/yellow] Streaming display failed: {e}")
                response = self.respond(user_input)
                self.console.print(response)

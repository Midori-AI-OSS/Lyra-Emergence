"""Command-line chat interface for Lyra."""

from typing import Callable
from typing import Optional, List, Dict

from flashrank import Ranker
from rich.console import Console
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.rerank.cpu_reranker import rerank_entries
from src.utils.chat_templates import AutoChatTemplateManager


class ChatSession:
    """Interactive chat session that reads user input and displays responses."""

    def __init__(
        self,
        console: Optional[Console] = None,
        input_func: Callable[[str], str] | None = None,
        rerank: bool = True,
        ranker: Ranker | None = None,
        llm: BaseLanguageModel | None = None,
        model_id: Optional[str] = None,
    ) -> None:
        self.console = console or Console()
        self.input_func = input_func or input
        self.rerank_enabled = rerank
        self.rerank_client = ranker
        self.llm = llm
        self.model_id = model_id
        
        # Initialize chat template manager for automatic templating
        self.template_manager: Optional[AutoChatTemplateManager] = None
        if model_id:
            try:
                self.template_manager = AutoChatTemplateManager(model_id)
                if self.template_manager.has_chat_template():
                    self.console.print(f"[green]✓[/green] Using automatic chat template for {model_id}")
                else:
                    self.console.print(f"[yellow]![/yellow] Using fallback template for {model_id}")
            except Exception as e:
                self.console.print(f"[yellow]![/yellow] Template manager initialization failed: {e}")
        
        # Conversation history for template-based chat
        self.conversation_history: List[Dict[str, str]] = []

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

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": query})

        # Use automatic chat templating if available
        if self.template_manager:
            try:
                # Format the entire conversation using the model's chat template
                formatted_prompt = self.template_manager.format_conversation(
                    self.conversation_history,
                    add_generation_prompt=True
                )
                
                # Use the formatted prompt directly with LangChain
                # Since we're using HuggingFacePipeline, we can pass the raw formatted text
                if hasattr(self.llm, 'pipeline'):
                    # Direct pipeline call with formatted prompt
                    result = self.llm.pipeline(formatted_prompt, max_new_tokens=512, do_sample=True, temperature=0.7)
                    if isinstance(result, list) and len(result) > 0:
                        response_text = result[0].get('generated_text', '')
                        # Extract only the new response (remove the prompt part)
                        if response_text.startswith(formatted_prompt):
                            response_text = response_text[len(formatted_prompt):].strip()
                    else:
                        response_text = str(result)
                else:
                    # Fallback to LangChain prompt template
                    prompt = ChatPromptTemplate.from_template(formatted_prompt)
                    chain = prompt | self.llm
                    result = chain.invoke({})
                    response_text = getattr(result, "content", str(result))
                
                # Add assistant response to conversation history
                self.conversation_history.append({"role": "assistant", "content": response_text})
                
                return response_text
                
            except Exception as e:
                self.console.print(f"[yellow]![/yellow] Template formatting failed: {e}. Using fallback.")
        
        # Fallback to original LangChain approach
        prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
        chain = prompt | self.llm
        result = chain.invoke({"input": query})
        response_text = getattr(result, "content", str(result))
        
        # Still add to history for fallback case
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        if self.console:
            self.console.print("[blue]Conversation history cleared[/blue]")

    def get_template_info(self) -> Optional[Dict]:
        """Get information about the current chat template."""
        if self.template_manager:
            return self.template_manager.get_template_info()
        return None

    def set_system_message(self, system_message: str) -> None:
        """Set a system message for the conversation."""
        # Remove any existing system message
        self.conversation_history = [msg for msg in self.conversation_history if msg.get("role") != "system"]
        
        # Add new system message at the beginning
        self.conversation_history.insert(0, {"role": "system", "content": system_message})
        
        if self.console:
            self.console.print(f"[blue]System message set: {system_message}[/blue]")

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

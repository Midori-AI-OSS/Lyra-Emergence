from rich.console import Console
from langchain_community.llms.fake import FakeListLLM

from src.cli.chat import ChatSession


def test_chat_session_exit_immediately() -> None:
    console = Console(record=True)
    session = ChatSession(console=console, input_func=lambda _: "exit")
    session.run()
    assert "Goodbye!" in console.export_text()


def test_chat_session_uses_llm_response() -> None:
    llm = FakeListLLM(responses=["hi"])
    session = ChatSession(llm=llm)
    assert session.respond("hello") == "hi"

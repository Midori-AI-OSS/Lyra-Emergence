from langchain_community.llms.fake import FakeListLLM
from rich.console import Console

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


def test_chat_session_streaming_response() -> None:
    """Test that streaming response generates the same content as regular response."""
    llm = FakeListLLM(responses=["hello world"])
    session = ChatSession(llm=llm)
    
    # Test streaming
    streaming_parts = []
    for chunk in session.respond_stream("test"):
        streaming_parts.append(chunk)
    streaming_result = "".join(streaming_parts)
    
    # Reset conversation history and test regular response
    session.clear_conversation()
    regular_result = session.respond("test")
    
    # They should produce the same content
    assert streaming_result == regular_result == "hello world"


def test_chat_session_streaming_with_no_llm() -> None:
    """Test that streaming works gracefully when no LLM is configured."""
    session = ChatSession(llm=None)
    
    streaming_parts = []
    for chunk in session.respond_stream("test"):
        streaming_parts.append(chunk)
    result = "".join(streaming_parts)
    
    assert result == "echo: test"

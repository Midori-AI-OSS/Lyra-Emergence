"""Tests for automatic chat template functionality."""

from unittest.mock import MagicMock, patch

import pytest

from src.utils.chat_templates import AutoChatTemplateManager, create_template_manager


class TestAutoChatTemplateManager:
    """Test the AutoChatTemplateManager class."""

    def test_init_with_valid_model(self):
        """Test initialization with a valid model ID."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer = MagicMock()
            mock_tokenizer.chat_template = "test template"
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            manager = AutoChatTemplateManager("test/model")

            assert manager.model_id == "test/model"
            assert manager.tokenizer == mock_tokenizer
            mock_tokenizer_class.from_pretrained.assert_called_once_with(
                "test/model", trust_remote_code=True, use_fast=True
            )

    def test_has_chat_template_true(self):
        """Test has_chat_template returns True when template exists."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer = MagicMock()
            mock_tokenizer.chat_template = "test template"
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            manager = AutoChatTemplateManager("test/model")
            assert manager.has_chat_template() is True

    def test_has_chat_template_false(self):
        """Test has_chat_template returns False when no template."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer = MagicMock()
            mock_tokenizer.chat_template = None
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            manager = AutoChatTemplateManager("test/model")
            assert manager.has_chat_template() is False

    def test_format_conversation_with_template(self):
        """Test conversation formatting with chat template."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer = MagicMock()
            mock_tokenizer.chat_template = "test template"
            mock_tokenizer.apply_chat_template.return_value = "formatted conversation"
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            manager = AutoChatTemplateManager("test/model")

            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]

            result = manager.format_conversation(messages)

            assert result == "formatted conversation"
            mock_tokenizer.apply_chat_template.assert_called_once_with(
                conversation=messages,
                add_generation_prompt=True,
                tokenize=False,
                return_tensors=None,
            )

    def test_format_conversation_fallback(self):
        """Test conversation formatting falls back when template fails."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer = MagicMock()
            mock_tokenizer.chat_template = "test template"
            mock_tokenizer.apply_chat_template.side_effect = Exception("Template error")
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            manager = AutoChatTemplateManager("test/model")

            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]

            result = manager.format_conversation(messages)

            # Should use fallback format
            expected = "Human: Hello\n\nAssistant: Hi there!\n\nAssistant:"
            assert result == expected

    def test_fallback_format(self):
        """Test the fallback formatting method."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer_class.from_pretrained.side_effect = Exception("No tokenizer")

            manager = AutoChatTemplateManager("test/model")

            messages = [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
            ]

            result = manager.format_conversation(messages, add_generation_prompt=True)

            expected = (
                "System: You are helpful\n\n"
                "Human: Hello\n\n"
                "Assistant: Hi there!\n\n"
                "Human: How are you?\n\n"
                "Assistant:"
            )
            assert result == expected

    def test_format_single_message(self):
        """Test formatting a single message."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer = MagicMock()
            mock_tokenizer.apply_chat_template.return_value = "User: Hello\nAssistant:"
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            manager = AutoChatTemplateManager("test/model")

            result = manager.format_single_message("Hello", "user")

            assert result == "User: Hello\nAssistant:"

    def test_get_template_info(self):
        """Test getting template information."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer = MagicMock()
            mock_tokenizer.chat_template = "test template"
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            manager = AutoChatTemplateManager("test/model")

            info = manager.get_template_info()

            expected = {
                "model_id": "test/model",
                "tokenizer_loaded": True,
                "has_chat_template": True,
                "chat_template": "test template",
            }
            assert info == expected

    def test_tokenizer_load_failure(self):
        """Test handling tokenizer load failure."""
        with patch("src.utils.chat_templates.AutoTokenizer") as mock_tokenizer_class:
            mock_tokenizer_class.from_pretrained.side_effect = Exception("Load failed")

            manager = AutoChatTemplateManager("test/model")

            assert manager.tokenizer is None
            assert manager.has_chat_template() is False

            # Should use fallback formatting
            messages = [{"role": "user", "content": "Hello"}]
            result = manager.format_conversation(messages)
            assert "Human: Hello" in result


def test_create_template_manager():
    """Test the factory function."""
    with patch("src.utils.chat_templates.AutoTokenizer"):
        manager = create_template_manager("test/model")
        assert isinstance(manager, AutoChatTemplateManager)
        assert manager.model_id == "test/model"


@pytest.mark.integration
def test_template_integration_with_real_model():
    """Integration test with a real model (if network available)."""
    try:
        # Try with a small, commonly available model
        manager = create_template_manager("microsoft/DialoGPT-medium")

        # Test basic functionality
        messages = [{"role": "user", "content": "Hello"}]
        result = manager.format_conversation(messages)

        # Should return a string
        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain the message content
        assert "Hello" in result

    except Exception as e:
        # Skip if no network/model access
        pytest.skip(f"Integration test skipped due to: {e}")

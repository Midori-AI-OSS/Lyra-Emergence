"""Tests for Playwright browser automation tools."""

from unittest.mock import Mock, patch

import pytest

from src.tools.playwright_tools import (
    PlaywrightNavigateTool,
    PlaywrightExtractTextTool,
    PlaywrightClickTool,
    get_playwright_tools,
)


class TestPlaywrightNavigateTool:
    """Test the Playwright navigation tool."""

    def test_init(self):
        """Test tool initialization."""
        tool = PlaywrightNavigateTool()
        assert tool.name == "playwright_navigate"
        assert "Navigate to a specific URL" in tool.description

    @patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser")
    @patch("langchain_community.tools.playwright.NavigateTool")
    def test_navigate_success(self, mock_nav_tool_class, mock_browser_factory):
        """Test successful navigation."""
        # Mock browser and navigation tool
        mock_browser = Mock()
        mock_browser_factory.return_value = mock_browser
        
        mock_nav_tool = Mock()
        mock_nav_tool.run.return_value = "Navigation successful"
        mock_nav_tool_class.from_browser.return_value = mock_nav_tool

        tool = PlaywrightNavigateTool()
        result = tool._run("https://example.com")

        assert "Successfully navigated to https://example.com" in result
        mock_browser.close.assert_called_once()

    def test_navigate_import_error(self):
        """Test handling of Playwright import error."""
        with patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser", side_effect=ImportError("Playwright not found")):
            tool = PlaywrightNavigateTool()
            result = tool._run("https://example.com")
            assert "Playwright browser not available" in result

    @patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser")
    def test_navigate_general_error(self, mock_browser_factory):
        """Test handling of general navigation errors."""
        mock_browser_factory.side_effect = Exception("Browser failed")
        
        tool = PlaywrightNavigateTool()
        result = tool._run("https://example.com")
        assert "Error navigating to https://example.com" in result

    def test_async_not_implemented(self):
        """Test that async version raises NotImplementedError."""
        tool = PlaywrightNavigateTool()
        with pytest.raises(NotImplementedError):
            import asyncio
            asyncio.run(tool._arun("https://example.com"))


class TestPlaywrightExtractTextTool:
    """Test the Playwright text extraction tool."""

    def test_init(self):
        """Test tool initialization."""
        tool = PlaywrightExtractTextTool()
        assert tool.name == "playwright_extract_text"
        assert "Extract text content" in tool.description

    @patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser")
    @patch("langchain_community.tools.playwright.ExtractTextTool")
    @patch("langchain_community.tools.playwright.NavigateTool")
    def test_extract_text_with_url(self, mock_nav_tool_class, mock_extract_tool_class, mock_browser_factory):
        """Test text extraction with URL navigation."""
        # Mock browser
        mock_browser = Mock()
        mock_browser_factory.return_value = mock_browser
        
        # Mock navigation tool
        mock_nav_tool = Mock()
        mock_nav_tool_class.from_browser.return_value = mock_nav_tool
        
        # Mock extraction tool
        mock_extract_tool = Mock()
        mock_extract_tool.run.return_value = "Extracted text content"
        mock_extract_tool_class.from_browser.return_value = mock_extract_tool

        tool = PlaywrightExtractTextTool()
        result = tool._run("https://example.com")

        assert result == "Extracted text content"
        mock_nav_tool.run.assert_called_once_with("https://example.com")
        mock_extract_tool.run.assert_called_once()
        mock_browser.close.assert_called_once()

    @patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser")
    @patch("langchain_community.tools.playwright.ExtractTextTool")
    def test_extract_text_without_url(self, mock_extract_tool_class, mock_browser_factory):
        """Test text extraction without URL (current page)."""
        # Mock browser
        mock_browser = Mock()
        mock_browser_factory.return_value = mock_browser
        
        # Mock extraction tool
        mock_extract_tool = Mock()
        mock_extract_tool.run.return_value = "Current page text"
        mock_extract_tool_class.from_browser.return_value = mock_extract_tool

        tool = PlaywrightExtractTextTool()
        result = tool._run("")

        assert result == "Current page text"
        mock_extract_tool.run.assert_called_once()
        mock_browser.close.assert_called_once()

    def test_extract_text_import_error(self):
        """Test handling of Playwright import error."""
        with patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser", side_effect=ImportError("Playwright not found")):
            tool = PlaywrightExtractTextTool()
            result = tool._run("https://example.com")
            assert "Playwright browser not available" in result

    def test_async_not_implemented(self):
        """Test that async version raises NotImplementedError."""
        tool = PlaywrightExtractTextTool()
        with pytest.raises(NotImplementedError):
            import asyncio
            asyncio.run(tool._arun("https://example.com"))


class TestPlaywrightClickTool:
    """Test the Playwright click tool."""

    def test_init(self):
        """Test tool initialization."""
        tool = PlaywrightClickTool()
        assert tool.name == "playwright_click"
        assert "Click on an element" in tool.description

    @patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser")
    @patch("langchain_community.tools.playwright.ClickTool")
    def test_click_success(self, mock_click_tool_class, mock_browser_factory):
        """Test successful element clicking."""
        # Mock browser
        mock_browser = Mock()
        mock_browser_factory.return_value = mock_browser
        
        # Mock click tool
        mock_click_tool = Mock()
        mock_click_tool.run.return_value = "Click successful"
        mock_click_tool_class.from_browser.return_value = mock_click_tool

        tool = PlaywrightClickTool()
        result = tool._run("#submit-button")

        assert "Successfully clicked element: #submit-button" in result
        mock_click_tool.run.assert_called_once_with("#submit-button")
        mock_browser.close.assert_called_once()

    def test_click_import_error(self):
        """Test handling of Playwright import error."""
        with patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser", side_effect=ImportError("Playwright not found")):
            tool = PlaywrightClickTool()
            result = tool._run("#button")
            assert "Playwright browser not available" in result

    @patch("langchain_community.tools.playwright.utils.create_sync_playwright_browser")
    def test_click_general_error(self, mock_browser_factory):
        """Test handling of general click errors."""
        mock_browser_factory.side_effect = Exception("Click failed")
        
        tool = PlaywrightClickTool()
        result = tool._run("#button")
        assert "Error clicking element #button" in result

    def test_async_not_implemented(self):
        """Test that async version raises NotImplementedError."""
        tool = PlaywrightClickTool()
        with pytest.raises(NotImplementedError):
            import asyncio
            asyncio.run(tool._arun("#button"))


def test_get_playwright_tools():
    """Test getting all Playwright tools."""
    tools = get_playwright_tools()
    assert len(tools) == 3
    assert any(tool.name == "playwright_navigate" for tool in tools)
    assert any(tool.name == "playwright_extract_text" for tool in tools)
    assert any(tool.name == "playwright_click" for tool in tools)
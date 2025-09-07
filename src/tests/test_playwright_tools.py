"""Tests for Playwright browser automation tools using LangChain's toolkit."""

from unittest.mock import Mock, patch

import pytest

from src.tools.playwright_tools import get_playwright_tools


class TestPlaywrightToolkit:
    """Test the LangChain Playwright toolkit integration."""

    @patch("src.tools.playwright_tools.sync_playwright")
    @patch("src.tools.playwright_tools.PlayWrightBrowserToolkit")
    def test_get_playwright_tools_success(self, mock_toolkit_class, mock_sync_playwright):
        """Test successful creation of Playwright tools using LangChain toolkit."""
        # Mock playwright context and browser
        mock_playwright_context = Mock()
        mock_browser = Mock()
        mock_chromium = Mock()
        
        mock_sync_playwright.return_value = mock_playwright_context
        mock_playwright_context.start.return_value = mock_browser
        mock_browser.chromium.launch.return_value = mock_chromium
        
        # Mock toolkit and tools
        mock_toolkit = Mock()
        mock_tools = [
            Mock(name="navigate_browser", description="Navigate to URL"),
            Mock(name="extract_text", description="Extract text from page"),
            Mock(name="click_element", description="Click element on page"),
            Mock(name="get_elements", description="Get elements from page"),
            Mock(name="current_page", description="Get current page info")
        ]
        mock_toolkit.get_tools.return_value = mock_tools
        mock_toolkit_class.from_browser.return_value = mock_toolkit

        tools = get_playwright_tools()

        # Verify toolkit creation
        mock_sync_playwright.assert_called_once()
        mock_playwright_context.start.assert_called_once()
        mock_browser.chromium.launch.assert_called_once_with(headless=True)
        mock_toolkit_class.from_browser.assert_called_once_with(sync_browser=mock_chromium)
        
        # Verify tools returned
        assert len(tools) == 5
        assert tools == mock_tools

    @patch("src.tools.playwright_tools.PLAYWRIGHT_AVAILABLE", False)
    def test_get_playwright_tools_not_available(self):
        """Test handling when Playwright is not available."""
        tools = get_playwright_tools()
        assert tools == []

    @patch("src.tools.playwright_tools.sync_playwright")
    def test_get_playwright_tools_browser_launch_error(self, mock_sync_playwright):
        """Test handling of browser launch errors."""
        # Mock playwright context setup
        mock_playwright_context = Mock()
        mock_browser = Mock()
        
        mock_sync_playwright.return_value = mock_playwright_context
        mock_playwright_context.start.return_value = mock_browser
        
        # Make browser launch fail
        mock_browser.chromium.launch.side_effect = Exception("Browser launch failed")

        tools = get_playwright_tools()

        # Should return empty list and clean up properly
        assert tools == []
        mock_browser.stop.assert_called_once()

    @patch("src.tools.playwright_tools.sync_playwright")
    def test_get_playwright_tools_general_error(self, mock_sync_playwright):
        """Test handling of general errors during toolkit creation."""
        # Make sync_playwright fail
        mock_sync_playwright.side_effect = Exception("Playwright initialization failed")

        tools = get_playwright_tools()

        # Should return empty list
        assert tools == []


def test_playwright_imports():
    """Test that imports work correctly when Playwright is available."""
    try:
        from src.tools.playwright_tools import PLAYWRIGHT_AVAILABLE
        # If imports succeed, PLAYWRIGHT_AVAILABLE should be True
        # If they fail, it should be False and that's also valid
        assert isinstance(PLAYWRIGHT_AVAILABLE, bool)
    except ImportError:
        # This is expected if Playwright is not installed
        pass
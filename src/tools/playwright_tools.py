"""Playwright browser automation tools for LangChain integration."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class PlaywrightNavigateTool(BaseTool):
    """Tool for navigating to web pages using Playwright."""

    name: str = "playwright_navigate"
    description: str = (
        "Navigate to a specific URL using Playwright browser automation. "
        "Input: URL to navigate to."
    )

    def _run(self, url: str, *args: Any, **kwargs: Any) -> str:
        """Navigate to the specified URL."""
        try:
            from langchain_community.tools.playwright import NavigateTool
            from langchain_community.tools.playwright.utils import create_sync_playwright_browser
            
            # Create a browser instance
            browser = create_sync_playwright_browser()
            
            # Create and use the tool
            tool = NavigateTool.from_browser(browser)
            result = tool.run(url)
            
            # Clean up
            browser.close()
            
            return f"Successfully navigated to {url}. Page loaded."
            
        except ImportError as e:
            logger.warning("Playwright not properly installed: %s", e)
            return f"Error: Playwright browser not available - {e}"
        except Exception as e:
            logger.error("Error navigating with Playwright: %s", e)
            return f"Error navigating to {url}: {e}"

    async def _arun(self, url: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Async navigation not implemented yet")


class PlaywrightExtractTextTool(BaseTool):
    """Tool for extracting text from web pages using Playwright."""

    name: str = "playwright_extract_text"
    description: str = (
        "Extract text content from the current web page using Playwright. "
        "Returns the visible text content of the page."
    )

    def _run(self, url: str = "", *args: Any, **kwargs: Any) -> str:
        """Extract text from the current page or a specific URL."""
        try:
            from langchain_community.tools.playwright import ExtractTextTool, NavigateTool
            from langchain_community.tools.playwright.utils import create_sync_playwright_browser
            
            # Create a browser instance
            browser = create_sync_playwright_browser()
            
            # If URL provided, navigate first
            if url:
                nav_tool = NavigateTool.from_browser(browser)
                nav_tool.run(url)
            
            # Extract text
            extract_tool = ExtractTextTool.from_browser(browser)
            result = extract_tool.run()
            
            # Clean up
            browser.close()
            
            return result
            
        except ImportError as e:
            logger.warning("Playwright not properly installed: %s", e)
            return f"Error: Playwright browser not available - {e}"
        except Exception as e:
            logger.error("Error extracting text with Playwright: %s", e)
            return f"Error extracting text: {e}"

    async def _arun(self, url: str = "", *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Async text extraction not implemented yet")


class PlaywrightClickTool(BaseTool):
    """Tool for clicking elements on web pages using Playwright."""

    name: str = "playwright_click"
    description: str = (
        "Click on an element on the current web page using CSS selector. "
        "Input: CSS selector of the element to click."
    )

    def _run(self, selector: str, *args: Any, **kwargs: Any) -> str:
        """Click on the element matching the CSS selector."""
        try:
            from langchain_community.tools.playwright import ClickTool
            from langchain_community.tools.playwright.utils import create_sync_playwright_browser
            
            # Create a browser instance
            browser = create_sync_playwright_browser()
            
            # Create and use the click tool
            click_tool = ClickTool.from_browser(browser)
            result = click_tool.run(selector)
            
            # Clean up
            browser.close()
            
            return f"Successfully clicked element: {selector}"
            
        except ImportError as e:
            logger.warning("Playwright not properly installed: %s", e)
            return f"Error: Playwright browser not available - {e}"
        except Exception as e:
            logger.error("Error clicking with Playwright: %s", e)
            return f"Error clicking element {selector}: {e}"

    async def _arun(self, selector: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Async clicking not implemented yet")


def get_playwright_tools() -> list[BaseTool]:
    """Return available Playwright tools."""
    return [
        PlaywrightNavigateTool(),
        PlaywrightExtractTextTool(),
        PlaywrightClickTool(),
    ]
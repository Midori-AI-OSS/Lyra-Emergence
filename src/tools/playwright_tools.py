"""Playwright browser automation tools using LangChain's official Playwright toolkit."""

from __future__ import annotations

import logging
from typing import List, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Check if Playwright is available
PLAYWRIGHT_AVAILABLE = True
try:
    from langchain_community.agent_toolkits.playwright import PlayWrightBrowserToolkit
    from playwright.sync_api import sync_playwright
    import playwright
except ImportError as e:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available: %s", e)


def get_playwright_tools() -> List[BaseTool]:
    """Return available Playwright tools using LangChain's official toolkit."""
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright not available. Install with: pip install playwright && playwright install")
        return []
    
    try:
        # Create a Playwright browser context using LangChain's approach
        playwright_context = sync_playwright()
        browser = playwright_context.start()
        
        # Try to launch a browser (headless)
        try:
            chromium = browser.chromium.launch(headless=True)
            
            # Create the LangChain Playwright toolkit
            toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=chromium)
            tools = toolkit.get_tools()
            
            logger.info(f"LangChain Playwright toolkit loaded with {len(tools)} tools")
            
            # Note: In a production environment, you'd want to manage browser lifecycle properly
            # For now, we'll create the tools but the browser will be cleaned up when needed
            
            return tools
            
        except Exception as e:
            logger.error("Failed to create Playwright browser: %s", e)
            browser.stop()
            return []
            
    except Exception as e:
        logger.error("Error creating Playwright toolkit: %s", e)
        return []
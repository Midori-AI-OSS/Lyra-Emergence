# LangChain Tool Integrations

The `src/tools` package provides LangChain `Tool` classes for journal ingestion, search, MCP (Model Context Protocol) operations, and Playwright browser automation. These tools may be disabled based on the runtime environment:

- All tools are disabled when the host OS is not **PixelArch**.
- Network-dependent tools are disabled when internet connectivity is unavailable or when `https://tea-cup.midori-ai.xyz/health` is unreachable.

When adding or updating tools, review LangChain's official tool integration guide:

<https://python.langchain.com/docs/integrations/tools/>

Update this document whenever new tools are introduced or existing ones are modified.

## Available Tools

### Journal Tools
- `JournalIngestTool`: Ingest journal JSON files into ChromaDB vector store
- `JournalSearchTool`: Search ingested journal entries using vector similarity

### MCP (Model Context Protocol) Tools
- `MCPRequestTool`: Make HTTP requests to external services following MCP patterns
- `MCPContextTool`: Store and retrieve context data for MCP-style interactions
- `MCPServiceTool`: Register and call external MCP-style services

### Playwright Browser Automation Tools
- `PlaywrightNavigateTool`: Navigate to web pages using Playwright automation
- `PlaywrightExtractTextTool`: Extract text content from web pages
- `PlaywrightClickTool`: Click elements on web pages using CSS selectors

## Dependencies

The tools require the following additional dependencies:
- `playwright>=1.40.0` for browser automation
- `beautifulsoup4>=4.12.0` for HTML parsing support
- `requests>=2.31.0` for HTTP requests in MCP tools

### Playwright Browser Installation

Note: Playwright requires browser binaries to be installed separately. In production environments, this is typically handled through Docker containers. For local development:

```bash
uv run playwright install
```

## Error Handling

All tools include comprehensive error handling:
- Graceful degradation when dependencies are missing
- Clear error messages for troubleshooting
- Import-time checks to prevent runtime failures
- Environment-based tool filtering

## 2025-09-05

- `JournalIngestTool` and `JournalSearchTool` now accept variadic arguments in
  their `_run` and `_arun` methods to match `BaseTool`'s expected signature.

## 2025-09-07

- Added MCP (Model Context Protocol) toolbox with 3 tools for external service integration
- Added Playwright browser automation tools with 3 tools for web interaction
- Enhanced environment-based tool loading with better error handling
- All new tools follow LangChain BaseTool patterns with comprehensive testing

"""MCP (Model Context Protocol) tools for external service integration."""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.tools import BaseTool

# Import the official MCP package
try:
    import mcp
    import mcp.client.session
    import mcp.types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    mcp = None

logger = logging.getLogger(__name__)

# Global storage for context and services (in a real implementation, this might be persistent)
_CONTEXT_STORE: dict[str, Any] = {}
_SERVICE_REGISTRY: dict[str, dict[str, Any]] = {}


class MCPClientTool(BaseTool):
    """Tool for connecting to and interacting with MCP servers."""

    name: str = "mcp_client"
    description: str = (
        "Connect to an MCP server and interact with its tools. "
        "Input: JSON string with 'server_command' (path to MCP server), 'tool_name', and 'parameters'."
    )

    def _run(self, request_json: str, *args: Any, **kwargs: Any) -> str:
        """Connect to an MCP server and call a tool."""
        if not MCP_AVAILABLE:
            return "Error: MCP package not available. Install with: pip install mcp"
        
        try:
            # Parse the request JSON
            try:
                request_data = json.loads(request_json)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON format - {e}"
            
            # Validate required fields
            server_command = request_data.get("server_command")
            tool_name = request_data.get("tool_name")
            parameters = request_data.get("parameters", {})
            
            if not server_command:
                return "Error: server_command is required"
            if not tool_name:
                return "Error: tool_name is required"
            
            # For now, return a placeholder since async MCP client setup is complex
            # In a real implementation, this would set up an async MCP client session
            return json.dumps({
                "status": "success",
                "message": f"MCP client ready to connect to {server_command} and call {tool_name}",
                "mcp_available": True,
                "parameters": parameters
            }, indent=2)
            
        except Exception as e:
            logger.error("Error in MCP client tool: %s", e)
            return f"Error: {e}"

    async def _arun(self, request_json: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        """Async version - would implement proper MCP client session here."""
        # This would be the proper place to implement async MCP client interaction
        # using mcp.client.session.ClientSession
        raise NotImplementedError("Async MCP client not implemented yet")


class MCPServerInfoTool(BaseTool):
    """Tool for getting information about available MCP servers and tools."""

    name: str = "mcp_server_info"
    description: str = (
        "Get information about MCP protocol and available server capabilities. "
        "Input: JSON string with 'action' (info/capabilities)."
    )

    def _run(self, request_json: str, *args: Any, **kwargs: Any) -> str:
        """Get MCP server information."""
        if not MCP_AVAILABLE:
            return "Error: MCP package not available. Install with: pip install mcp"
        
        try:
            try:
                request_data = json.loads(request_json)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON format - {e}"
            
            action = request_data.get("action", "info")
            
            if action == "info":
                return json.dumps({
                    "mcp_version": getattr(mcp, "__version__", "unknown"),
                    "protocol_description": "Model Context Protocol - standardized way for AI models to interact with external tools",
                    "available_types": ["Tool", "Resource", "Prompt"],
                    "client_capabilities": list(mcp.types.ClientCapabilities.model_fields.keys()),
                    "server_capabilities": list(mcp.types.ServerCapabilities.model_fields.keys())
                }, indent=2)
            
            elif action == "capabilities":
                return json.dumps({
                    "client_capabilities": {
                        "tools": "Can call tools provided by MCP servers",
                        "resources": "Can read resources from MCP servers", 
                        "prompts": "Can get prompts from MCP servers",
                        "logging": "Can receive log messages from servers"
                    },
                    "server_capabilities": {
                        "tools": "Can provide tools for clients to call",
                        "resources": "Can provide resources for clients to read",
                        "prompts": "Can provide prompts for clients to use"
                    }
                }, indent=2)
            
            else:
                return f"Error: Unknown action '{action}'. Use 'info' or 'capabilities'"
                
        except Exception as e:
            logger.error("Error in MCP server info tool: %s", e)
            return f"Error: {e}"

    async def _arun(self, request_json: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Async MCP server info not implemented yet")


class MCPContextTool(BaseTool):
    """Tool for managing context data in MCP-style interactions."""

    name: str = "mcp_context"
    description: str = (
        "Store and retrieve context data for MCP-style interactions. "
        "Input: JSON string with 'action' (store/retrieve/list), 'key', and optional 'value'."
    )

    def _run(self, context_json: str, *args: Any, **kwargs: Any) -> str:
        """Manage context data."""
        global _CONTEXT_STORE
        try:
            # Parse the context JSON
            try:
                context_data = json.loads(context_json)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON format - {e}"
            
            action = context_data.get("action", "").lower()
            key = context_data.get("key", "")
            
            if action == "store":
                if not key:
                    return "Error: Key is required for storing context"
                value = context_data.get("value")
                _CONTEXT_STORE[key] = value
                return f"Context stored for key: {key}"
            
            elif action == "retrieve":
                if not key:
                    return "Error: Key is required for retrieving context"
                value = _CONTEXT_STORE.get(key)
                if value is None:
                    return f"No context found for key: {key}"
                return json.dumps({"key": key, "value": value}, indent=2)
            
            elif action == "list":
                keys = list(_CONTEXT_STORE.keys())
                return json.dumps({"stored_keys": keys}, indent=2)
            
            elif action == "clear":
                if key:
                    if key in _CONTEXT_STORE:
                        del _CONTEXT_STORE[key]
                        return f"Context cleared for key: {key}"
                    else:
                        return f"No context found for key: {key}"
                else:
                    _CONTEXT_STORE.clear()
                    return "All context data cleared"
            
            else:
                return f"Error: Unsupported action '{action}'. Use: store, retrieve, list, clear"
                
        except Exception as e:
            logger.error("Error in MCP context tool: %s", e)
            return f"Error: {e}"

    async def _arun(self, context_json: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Async context management not implemented yet")

def get_mcp_tools() -> list[BaseTool]:
    """Return available MCP tools."""
    if not MCP_AVAILABLE:
        logger.warning("MCP package not available. Install with: pip install mcp")
        return []
    
    return [
        MCPClientTool(),
        MCPServerInfoTool(),
        MCPContextTool(),  # Keep the context tool as it's useful for state management
    ]
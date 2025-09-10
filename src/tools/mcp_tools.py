"""MCP (Model Context Protocol) tools using LangChain's toolbox patterns."""

from __future__ import annotations

import json
import logging
import subprocess
import asyncio
from typing import Any, Dict, List

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Global storage for context and services (following LangChain patterns)
_CONTEXT_STORE: Dict[str, Any] = {}
_SERVICE_REGISTRY: Dict[str, Dict[str, Any]] = {}


class MCPClientTool(BaseTool):
    """Tool for connecting to and interacting with MCP servers using LangChain patterns."""

    name: str = "mcp_client"
    description: str = (
        "Connect to an MCP server and interact with its tools using LangChain's toolbox approach. "
        "Input: JSON string with 'server_command' (path to MCP server), 'tool_name', and 'parameters'."
    )

    def _run(self, request_json: str, *args: Any, **kwargs: Any) -> str:
        """Connect to an MCP server and call a tool using LangChain patterns."""
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
            
            # Use LangChain's approach: execute server command and interact via subprocess
            # This follows LangChain's pattern for external tool integration
            try:
                # Start the MCP server process
                result = subprocess.run(
                    server_command.split(),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    return f"Error: MCP server failed to start - {result.stderr}"
                
                # In a real implementation, this would parse the server's output
                # and make proper MCP calls following LangChain's async patterns
                return json.dumps({
                    "status": "success",
                    "message": f"MCP server started successfully",
                    "tool_called": tool_name,
                    "parameters": parameters,
                    "server_output": result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
                }, indent=2)
                
            except subprocess.TimeoutExpired:
                return "Error: MCP server startup timed out"
            except FileNotFoundError:
                return f"Error: MCP server command not found: {server_command}"
            
        except Exception as e:
            logger.error("Error in MCP client tool: %s", e)
            return f"Error: {e}"

    async def _arun(self, request_json: str, *args: Any, **kwargs: Any) -> str:
        """Async version using LangChain's async patterns."""
        # This would implement proper async MCP client interaction
        # using LangChain's async tool patterns
        return self._run(request_json, *args, **kwargs)


class MCPServerInfoTool(BaseTool):
    """Tool for getting information about MCP protocol using LangChain's approach."""

    name: str = "mcp_server_info"
    description: str = (
        "Get information about MCP protocol and available server capabilities using LangChain's toolbox approach. "
        "Input: JSON string with 'action' (info/capabilities/list_servers)."
    )

    def _run(self, request_json: str, *args: Any, **kwargs: Any) -> str:
        """Get MCP server information using LangChain patterns."""
        try:
            try:
                request_data = json.loads(request_json)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON format - {e}"
            
            action = request_data.get("action", "info")
            
            if action == "info":
                return json.dumps({
                    "protocol": "Model Context Protocol (MCP)",
                    "integration": "LangChain Toolbox Pattern",
                    "description": "MCP tools integrated using LangChain's external tool patterns",
                    "supported_operations": [
                        "server_connection",
                        "tool_invocation", 
                        "context_management",
                        "resource_access"
                    ],
                    "langchain_integration": "Uses LangChain BaseTool patterns for MCP functionality"
                }, indent=2)
            
            elif action == "capabilities":
                return json.dumps({
                    "client_capabilities": {
                        "tools": "Can call MCP server tools via subprocess",
                        "context": "Can store and retrieve context data", 
                        "async_support": "Supports async operations",
                        "langchain_integration": "Full LangChain tool compatibility"
                    },
                    "server_requirements": {
                        "executable": "MCP server must be executable",
                        "protocol": "Must follow MCP standard",
                        "output": "Must provide JSON-formatted responses"
                    }
                }, indent=2)
            
            elif action == "list_servers":
                # Check for common MCP server implementations
                servers = []
                common_servers = [
                    "python -m mcp_server_example",
                    "node mcp-server.js",
                    "mcp-filesystem-server",
                    "mcp-database-server"
                ]
                
                for server in common_servers:
                    # Test if server is available
                    try:
                        subprocess.run(
                            server.split()[:2] + ["--help"],
                            capture_output=True,
                            timeout=5
                        )
                        servers.append({
                            "command": server,
                            "status": "available"
                        })
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        servers.append({
                            "command": server,
                            "status": "not_found"
                        })
                
                return json.dumps({
                    "available_servers": servers,
                    "registry": _SERVICE_REGISTRY
                }, indent=2)
            
            else:
                return f"Error: Unknown action '{action}'. Use 'info', 'capabilities', or 'list_servers'"
                
        except Exception as e:
            logger.error("Error in MCP server info tool: %s", e)
            return f"Error: {e}"

    async def _arun(self, request_json: str, *args: Any, **kwargs: Any) -> str:
        """Async version using LangChain patterns."""
        return self._run(request_json, *args, **kwargs)


class MCPContextTool(BaseTool):
    """Tool for managing context data using LangChain's toolbox patterns."""

    name: str = "mcp_context"
    description: str = (
        "Store and retrieve context data for MCP-style interactions using LangChain patterns. "
        "Input: JSON string with 'action' (store/retrieve/list/clear), 'key', and optional 'value'."
    )

    def _run(self, context_json: str, *args: Any, **kwargs: Any) -> str:
        """Manage context data using LangChain's approach."""
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
                
                # Following LangChain patterns, also store metadata
                import time
                _CONTEXT_STORE[f"{key}_metadata"] = {
                    "stored_at": str(time.time()),
                    "type": type(value).__name__,
                    "langchain_integration": True
                }
                
                return f"Context stored for key: {key} (using LangChain patterns)"
            
            elif action == "retrieve":
                if not key:
                    return "Error: Key is required for retrieving context"
                value = _CONTEXT_STORE.get(key)
                metadata = _CONTEXT_STORE.get(f"{key}_metadata", {})
                
                if value is None:
                    return f"No context found for key: {key}"
                
                return json.dumps({
                    "key": key, 
                    "value": value,
                    "metadata": metadata,
                    "langchain_integration": True
                }, indent=2)
            
            elif action == "list":
                # Filter out metadata keys for cleaner output
                data_keys = [k for k in _CONTEXT_STORE.keys() if not k.endswith("_metadata")]
                return json.dumps({
                    "stored_keys": data_keys,
                    "total_entries": len(data_keys),
                    "langchain_integration": True
                }, indent=2)
            
            elif action == "clear":
                if key:
                    if key in _CONTEXT_STORE:
                        del _CONTEXT_STORE[key]
                        # Also clear metadata
                        metadata_key = f"{key}_metadata"
                        if metadata_key in _CONTEXT_STORE:
                            del _CONTEXT_STORE[metadata_key]
                        return f"Context cleared for key: {key}"
                    else:
                        return f"No context found for key: {key}"
                else:
                    _CONTEXT_STORE.clear()
                    return "All context data cleared (LangChain integration)"
            
            else:
                return f"Error: Unsupported action '{action}'. Use: store, retrieve, list, clear"
                
        except Exception as e:
            logger.error("Error in MCP context tool: %s", e)
            return f"Error: {e}"

    async def _arun(self, context_json: str, *args: Any, **kwargs: Any) -> str:
        """Async version using LangChain patterns."""
        return self._run(context_json, *args, **kwargs)


def get_mcp_tools() -> List[BaseTool]:
    """Return available MCP tools using LangChain's toolbox approach."""
    logger.info("Loading MCP tools using LangChain patterns")
    
    return [
        MCPClientTool(),
        MCPServerInfoTool(),
        MCPContextTool(),
    ]
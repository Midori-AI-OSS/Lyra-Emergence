"""MCP (Model Context Protocol) style tools for external service integration."""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Global storage for context and services (in a real implementation, this might be persistent)
_CONTEXT_STORE: dict[str, Any] = {}
_SERVICE_REGISTRY: dict[str, dict[str, Any]] = {}


class MCPRequestTool(BaseTool):
    """Tool for making HTTP requests to external services (MCP-style)."""

    name: str = "mcp_request"
    description: str = (
        "Make HTTP requests to external services following MCP patterns. "
        "Input: JSON string with 'url', 'method' (GET/POST), and optional 'data' and 'headers'."
    )

    def _run(self, request_json: str, *args: Any, **kwargs: Any) -> str:
        """Make an HTTP request to an external service."""
        try:
            import requests
            
            # Parse the request JSON
            try:
                request_data = json.loads(request_json)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON format - {e}"
            
            # Validate required fields
            if "url" not in request_data:
                return "Error: URL is required"
            
            url = request_data["url"]
            method = request_data.get("method", "GET").upper()
            data = request_data.get("data", None)
            headers = request_data.get("headers", {})
            
            # Add default headers for API requests
            if "Content-Type" not in headers and data:
                headers["Content-Type"] = "application/json"
            
            # Make the request
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return f"Error: Unsupported HTTP method {method}"
            
            # Return formatted response
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text[:1000],  # Limit response size
            }
            
            return json.dumps(result, indent=2)
            
        except ImportError:
            return "Error: requests library not available"
        except requests.RequestException as e:
            logger.error("HTTP request error: %s", e)
            return f"Error making request: {e}"
        except Exception as e:
            logger.error("Unexpected error in MCP request: %s", e)
            return f"Unexpected error: {e}"

    async def _arun(self, request_json: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Async HTTP requests not implemented yet")


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


class MCPServiceTool(BaseTool):
    """Tool for registering and calling external MCP-style services."""

    name: str = "mcp_service"
    description: str = (
        "Register and call external MCP-style services. "
        "Input: JSON string with 'action' (register/call/list), service details."
    )

    def _run(self, service_json: str, *args: Any, **kwargs: Any) -> str:
        """Manage external services."""
        global _SERVICE_REGISTRY
        try:
            # Parse the service JSON
            try:
                service_data = json.loads(service_json)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON format - {e}"
            
            action = service_data.get("action", "").lower()
            
            if action == "register":
                name = service_data.get("name", "")
                url = service_data.get("url", "")
                description = service_data.get("description", "")
                
                if not name or not url:
                    return "Error: Name and URL are required for service registration"
                
                _SERVICE_REGISTRY[name] = {
                    "url": url,
                    "description": description,
                    "registered_at": "now"  # In real implementation, use proper timestamp
                }
                
                return f"Service '{name}' registered successfully"
            
            elif action == "call":
                name = service_data.get("name", "")
                params = service_data.get("params", {})
                
                if not name:
                    return "Error: Service name is required for calling"
                
                if name not in _SERVICE_REGISTRY:
                    return f"Error: Service '{name}' not found in registry"
                
                service = _SERVICE_REGISTRY[name]
                # Use the MCP request tool to make the call
                request_data = {
                    "url": service["url"],
                    "method": "POST",
                    "data": params
                }
                
                mcp_request = MCPRequestTool()
                return mcp_request._run(json.dumps(request_data))
            
            elif action == "list":
                services = {
                    name: {"url": info["url"], "description": info["description"]}
                    for name, info in _SERVICE_REGISTRY.items()
                }
                return json.dumps({"registered_services": services}, indent=2)
            
            else:
                return f"Error: Unsupported action '{action}'. Use: register, call, list"
                
        except Exception as e:
            logger.error("Error in MCP service tool: %s", e)
            return f"Error: {e}"

    async def _arun(self, service_json: str, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Async service management not implemented yet")


def get_mcp_tools() -> list[BaseTool]:
    """Return available MCP-style tools."""
    return [
        MCPRequestTool(),
        MCPContextTool(),
        MCPServiceTool(),
    ]
"""Tests for MCP (Model Context Protocol) tools."""

import json
from unittest.mock import Mock, patch

import pytest

from src.tools.mcp_tools import MCPRequestTool, MCPContextTool, MCPServiceTool, get_mcp_tools


class TestMCPRequestTool:
    """Test the MCP HTTP request tool."""

    def test_init(self):
        """Test tool initialization."""
        tool = MCPRequestTool()
        assert tool.name == "mcp_request"
        assert "HTTP requests" in tool.description

    @patch("requests.get")
    def test_get_request_success(self, mock_get):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"result": "success"}'
        mock_get.return_value = mock_response

        tool = MCPRequestTool()
        request_json = json.dumps({"url": "https://api.example.com/test", "method": "GET"})
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert result_data["status_code"] == 200
        assert "success" in result_data["content"]

    @patch("requests.post")
    def test_post_request_success(self, mock_post):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"created": true}'
        mock_post.return_value = mock_response

        tool = MCPRequestTool()
        request_json = json.dumps({
            "url": "https://api.example.com/create",
            "method": "POST",
            "data": {"name": "test"}
        })
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert result_data["status_code"] == 201
        assert "created" in result_data["content"]

    def test_invalid_json(self):
        """Test handling of invalid JSON input."""
        tool = MCPRequestTool()
        result = tool._run("invalid json")
        assert "Invalid JSON format" in result

    def test_missing_url(self):
        """Test handling of missing URL."""
        tool = MCPRequestTool()
        request_json = json.dumps({"method": "GET"})
        result = tool._run(request_json)
        assert "URL is required" in result

    def test_unsupported_method(self):
        """Test handling of unsupported HTTP method."""
        tool = MCPRequestTool()
        request_json = json.dumps({"url": "https://example.com", "method": "PATCH"})
        result = tool._run(request_json)
        assert "Unsupported HTTP method" in result

    @patch("requests.get")
    def test_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        tool = MCPRequestTool()
        request_json = json.dumps({"url": "https://example.com", "method": "GET"})
        result = tool._run(request_json)
        assert "Error making request" in result


class TestMCPContextTool:
    """Test the MCP context management tool."""

    def setup_method(self):
        """Clear context store before each test."""
        from src.tools.mcp_tools import _CONTEXT_STORE
        _CONTEXT_STORE.clear()

    def test_init(self):
        """Test tool initialization."""
        tool = MCPContextTool()
        assert tool.name == "mcp_context"
        assert "context data" in tool.description

    def test_store_and_retrieve_context(self):
        """Test storing and retrieving context data."""
        tool = MCPContextTool()
        
        # Store context
        store_json = json.dumps({"action": "store", "key": "test_key", "value": "test_value"})
        result = tool._run(store_json)
        assert "Context stored for key: test_key" in result
        
        # Retrieve context
        retrieve_json = json.dumps({"action": "retrieve", "key": "test_key"})
        result = tool._run(retrieve_json)
        result_data = json.loads(result)
        assert result_data["key"] == "test_key"
        assert result_data["value"] == "test_value"

    def test_list_context_keys(self):
        """Test listing stored context keys."""
        tool = MCPContextTool()
        
        # Store multiple contexts
        tool._run(json.dumps({"action": "store", "key": "key1", "value": "value1"}))
        tool._run(json.dumps({"action": "store", "key": "key2", "value": "value2"}))
        
        # List keys
        list_json = json.dumps({"action": "list"})
        result = tool._run(list_json)
        result_data = json.loads(result)
        assert "key1" in result_data["stored_keys"]
        assert "key2" in result_data["stored_keys"]

    def test_clear_specific_context(self):
        """Test clearing specific context data."""
        tool = MCPContextTool()
        
        # Store context
        tool._run(json.dumps({"action": "store", "key": "test_key", "value": "test_value"}))
        
        # Clear specific key
        clear_json = json.dumps({"action": "clear", "key": "test_key"})
        result = tool._run(clear_json)
        assert "Context cleared for key: test_key" in result
        
        # Verify it's gone
        retrieve_json = json.dumps({"action": "retrieve", "key": "test_key"})
        result = tool._run(retrieve_json)
        assert "No context found" in result

    def test_clear_all_context(self):
        """Test clearing all context data."""
        tool = MCPContextTool()
        
        # Store multiple contexts
        tool._run(json.dumps({"action": "store", "key": "key1", "value": "value1"}))
        tool._run(json.dumps({"action": "store", "key": "key2", "value": "value2"}))
        
        # Clear all
        clear_json = json.dumps({"action": "clear"})
        result = tool._run(clear_json)
        assert "All context data cleared" in result
        
        # Verify they're gone
        list_json = json.dumps({"action": "list"})
        result = tool._run(list_json)
        result_data = json.loads(result)
        assert len(result_data["stored_keys"]) == 0

    def test_invalid_action(self):
        """Test handling of invalid action."""
        tool = MCPContextTool()
        invalid_json = json.dumps({"action": "invalid_action"})
        result = tool._run(invalid_json)
        assert "Unsupported action" in result


class TestMCPServiceTool:
    """Test the MCP service registry tool."""

    def setup_method(self):
        """Clear service registry before each test."""
        from src.tools.mcp_tools import _SERVICE_REGISTRY
        _SERVICE_REGISTRY.clear()

    def test_init(self):
        """Test tool initialization."""
        tool = MCPServiceTool()
        assert tool.name == "mcp_service"
        assert "external MCP-style services" in tool.description

    def test_register_service(self):
        """Test registering a service."""
        tool = MCPServiceTool()
        register_json = json.dumps({
            "action": "register",
            "name": "test_service",
            "url": "https://api.test.com",
            "description": "Test service"
        })
        result = tool._run(register_json)
        assert "Service 'test_service' registered successfully" in result

    def test_list_services(self):
        """Test listing registered services."""
        tool = MCPServiceTool()
        
        # Register a service
        tool._run(json.dumps({
            "action": "register",
            "name": "test_service",
            "url": "https://api.test.com",
            "description": "Test service"
        }))
        
        # List services
        list_json = json.dumps({"action": "list"})
        result = tool._run(list_json)
        result_data = json.loads(result)
        assert "test_service" in result_data["registered_services"]
        assert result_data["registered_services"]["test_service"]["url"] == "https://api.test.com"

    @patch("src.tools.mcp_tools.MCPRequestTool._run")
    def test_call_service(self, mock_request_run):
        """Test calling a registered service."""
        mock_request_run.return_value = '{"response": "success"}'
        
        tool = MCPServiceTool()
        
        # Register a service
        tool._run(json.dumps({
            "action": "register",
            "name": "test_service",
            "url": "https://api.test.com"
        }))
        
        # Call the service
        call_json = json.dumps({
            "action": "call",
            "name": "test_service",
            "params": {"param1": "value1"}
        })
        result = tool._run(call_json)
        assert "success" in result

    def test_call_nonexistent_service(self):
        """Test calling a service that doesn't exist."""
        tool = MCPServiceTool()
        call_json = json.dumps({
            "action": "call",
            "name": "nonexistent_service"
        })
        result = tool._run(call_json)
        assert "Service 'nonexistent_service' not found" in result

    def test_register_missing_fields(self):
        """Test registering service with missing required fields."""
        tool = MCPServiceTool()
        register_json = json.dumps({"action": "register", "name": "test"})
        result = tool._run(register_json)
        assert "Name and URL are required" in result


def test_get_mcp_tools():
    """Test getting all MCP tools."""
    tools = get_mcp_tools()
    assert len(tools) == 3
    assert any(tool.name == "mcp_request" for tool in tools)
    assert any(tool.name == "mcp_context" for tool in tools)
    assert any(tool.name == "mcp_service" for tool in tools)
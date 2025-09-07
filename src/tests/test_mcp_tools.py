"""Tests for MCP (Model Context Protocol) tools."""

import json
from unittest.mock import Mock, patch

import pytest

from src.tools.mcp_tools import MCPClientTool, MCPContextTool, MCPServerInfoTool, get_mcp_tools


class TestMCPClientTool:
    """Test the MCP client tool."""

    def test_init(self):
        """Test tool initialization."""
        tool = MCPClientTool()
        assert tool.name == "mcp_client"
        assert "MCP server" in tool.description

    def test_client_tool_success(self):
        """Test successful MCP client tool call."""
        tool = MCPClientTool()
        request_json = json.dumps({
            "server_command": "python -m some_mcp_server",
            "tool_name": "test_tool",
            "parameters": {"param1": "value1"}
        })
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert result_data["status"] == "success"
        assert result_data["mcp_available"] is True
        assert "python -m some_mcp_server" in result_data["message"]

    def test_invalid_json(self):
        """Test handling of invalid JSON input."""
        tool = MCPClientTool()
        result = tool._run("invalid json")
        assert "Invalid JSON format" in result

    def test_missing_server_command(self):
        """Test handling of missing server command."""
        tool = MCPClientTool()
        request_json = json.dumps({"tool_name": "test"})
        result = tool._run(request_json)
        assert "server_command is required" in result

    def test_missing_tool_name(self):
        """Test handling of missing tool name."""
        tool = MCPClientTool()
        request_json = json.dumps({"server_command": "python -m test"})
        result = tool._run(request_json)
        assert "tool_name is required" in result


class TestMCPServerInfoTool:
    """Test the MCP server info tool."""

    def test_init(self):
        """Test tool initialization."""
        tool = MCPServerInfoTool()
        assert tool.name == "mcp_server_info"
        assert "MCP protocol" in tool.description

    def test_info_action(self):
        """Test getting MCP protocol info."""
        tool = MCPServerInfoTool()
        request_json = json.dumps({"action": "info"})
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert "mcp_version" in result_data
        assert "protocol_description" in result_data
        assert "Model Context Protocol" in result_data["protocol_description"]

    def test_capabilities_action(self):
        """Test getting MCP capabilities info."""
        tool = MCPServerInfoTool()
        request_json = json.dumps({"action": "capabilities"})
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert "client_capabilities" in result_data
        assert "server_capabilities" in result_data
        assert "tools" in result_data["client_capabilities"]

    def test_unknown_action(self):
        """Test handling of unknown action."""
        tool = MCPServerInfoTool()
        request_json = json.dumps({"action": "unknown"})
        result = tool._run(request_json)
        assert "Unknown action" in result

    def test_invalid_json(self):
        """Test handling of invalid JSON input."""
        tool = MCPServerInfoTool()
        result = tool._run("invalid json")
        assert "Invalid JSON format" in result


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


def test_get_mcp_tools():
    """Test getting all MCP tools."""
    tools = get_mcp_tools()
    assert len(tools) == 3
    assert any(tool.name == "mcp_client" for tool in tools)
    assert any(tool.name == "mcp_context" for tool in tools)
    assert any(tool.name == "mcp_server_info" for tool in tools)
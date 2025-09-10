"""Tests for MCP (Model Context Protocol) tools using LangChain patterns."""

import json
from unittest.mock import Mock, patch

import pytest

from src.tools.mcp_tools import MCPClientTool, MCPContextTool, MCPServerInfoTool, get_mcp_tools


class TestMCPClientTool:
    """Test the MCP client tool using LangChain patterns."""

    def test_init(self):
        """Test tool initialization."""
        tool = MCPClientTool()
        assert tool.name == "mcp_client"
        assert "LangChain's toolbox approach" in tool.description

    @patch("src.tools.mcp_tools.subprocess.run")
    def test_client_tool_success(self, mock_subprocess):
        """Test successful MCP client tool call using subprocess."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "MCP server started successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        tool = MCPClientTool()
        request_json = json.dumps({
            "server_command": "python -m some_mcp_server",
            "tool_name": "test_tool",
            "parameters": {"param1": "value1"}
        })
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert result_data["status"] == "success"
        assert result_data["tool_called"] == "test_tool"
        assert "MCP server started successfully" in result_data["message"]
        mock_subprocess.assert_called_once()

    @patch("src.tools.mcp_tools.subprocess.run")
    def test_client_tool_server_failure(self, mock_subprocess):
        """Test handling of MCP server startup failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Server failed to start"
        mock_subprocess.return_value = mock_result
        
        tool = MCPClientTool()
        request_json = json.dumps({
            "server_command": "python -m broken_server",
            "tool_name": "test_tool",
            "parameters": {}
        })
        result = tool._run(request_json)

        assert "MCP server failed to start" in result
        assert "Server failed to start" in result

    @patch("src.tools.mcp_tools.subprocess.run")
    def test_client_tool_timeout(self, mock_subprocess):
        """Test handling of server startup timeout."""
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired("cmd", 30)
        
        tool = MCPClientTool()
        request_json = json.dumps({
            "server_command": "python -m slow_server",
            "tool_name": "test_tool",
            "parameters": {}
        })
        result = tool._run(request_json)

        assert "MCP server startup timed out" in result

    @patch("src.tools.mcp_tools.subprocess.run")
    def test_client_tool_not_found(self, mock_subprocess):
        """Test handling of missing server command."""
        mock_subprocess.side_effect = FileNotFoundError("Command not found")
        
        tool = MCPClientTool()
        request_json = json.dumps({
            "server_command": "nonexistent_command",
            "tool_name": "test_tool",
            "parameters": {}
        })
        result = tool._run(request_json)

        assert "MCP server command not found" in result

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
    """Test the MCP server info tool using LangChain patterns."""

    def test_init(self):
        """Test tool initialization."""
        tool = MCPServerInfoTool()
        assert tool.name == "mcp_server_info"
        assert "LangChain's toolbox approach" in tool.description

    def test_info_action(self):
        """Test getting MCP protocol info."""
        tool = MCPServerInfoTool()
        request_json = json.dumps({"action": "info"})
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert result_data["protocol"] == "Model Context Protocol (MCP)"
        assert result_data["integration"] == "LangChain Toolbox Pattern"
        assert "LangChain BaseTool patterns" in result_data["langchain_integration"]

    def test_capabilities_action(self):
        """Test getting MCP capabilities info."""
        tool = MCPServerInfoTool()
        request_json = json.dumps({"action": "capabilities"})
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert "client_capabilities" in result_data
        assert "server_requirements" in result_data
        assert "subprocess" in result_data["client_capabilities"]["tools"]

    @patch("src.tools.mcp_tools.subprocess.run")
    def test_list_servers_action(self, mock_subprocess):
        """Test listing available MCP servers."""
        # Mock subprocess calls for server availability checks
        mock_subprocess.return_value = Mock(returncode=0)
        
        tool = MCPServerInfoTool()
        request_json = json.dumps({"action": "list_servers"})
        result = tool._run(request_json)

        result_data = json.loads(result)
        assert "available_servers" in result_data
        assert "registry" in result_data
        assert len(result_data["available_servers"]) > 0

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
    """Test the MCP context management tool using LangChain patterns."""

    def setup_method(self):
        """Clear context store before each test."""
        from src.tools.mcp_tools import _CONTEXT_STORE
        _CONTEXT_STORE.clear()

    def test_init(self):
        """Test tool initialization."""
        tool = MCPContextTool()
        assert tool.name == "mcp_context"
        assert "LangChain patterns" in tool.description

    def test_store_and_retrieve_context(self):
        """Test storing and retrieving context data with LangChain metadata."""
        tool = MCPContextTool()
        
        # Store context
        store_json = json.dumps({"action": "store", "key": "test_key", "value": "test_value"})
        result = tool._run(store_json)
        assert "Context stored for key: test_key" in result
        assert "LangChain patterns" in result
        
        # Retrieve context
        retrieve_json = json.dumps({"action": "retrieve", "key": "test_key"})
        result = tool._run(retrieve_json)
        result_data = json.loads(result)
        assert result_data["key"] == "test_key"
        assert result_data["value"] == "test_value"
        assert result_data["langchain_integration"] is True
        assert "metadata" in result_data

    def test_list_context_keys(self):
        """Test listing stored context keys with LangChain integration info."""
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
        assert result_data["langchain_integration"] is True
        assert result_data["total_entries"] == 2

    def test_clear_specific_context(self):
        """Test clearing specific context data including metadata."""
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
        assert "LangChain integration" in result
        
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
    """Test getting all MCP tools using LangChain patterns."""
    tools = get_mcp_tools()
    assert len(tools) == 3
    assert any(tool.name == "mcp_client" for tool in tools)
    assert any(tool.name == "mcp_context" for tool in tools)
    assert any(tool.name == "mcp_server_info" for tool in tools)
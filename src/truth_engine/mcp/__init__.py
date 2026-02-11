"""
Model Context Protocol (MCP) Module
Truth Engine / Truth Forge

MCP server exposing verification tools for universal agent access.
"""

from .server import MCPResource, MCPTool, MCPToolResult, TruthEngineMCPServer, create_http_server


__all__ = ["TruthEngineMCPServer", "MCPTool", "MCPResource", "MCPToolResult", "create_http_server"]

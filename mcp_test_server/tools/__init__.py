"""Tool group registry for MCP test server."""

from mcp_test_server.tools import (
    math_tools,
    string_tools,
    collection_tools,
    encoding_tools,
    datetime_tools,
    validation_tools,
    conversion_tools,
    echo_tools,
    weather_tools,
)

ALL_GROUPS = [
    math_tools,
    string_tools,
    collection_tools,
    encoding_tools,
    datetime_tools,
    validation_tools,
    conversion_tools,
    echo_tools,
    weather_tools,
]


def register_all(mcp):
    """Register all tool groups with the MCP server."""
    for group in ALL_GROUPS:
        group.register(mcp)

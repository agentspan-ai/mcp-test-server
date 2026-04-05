"""Echo tools for MCP test server."""

import json

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import TextContent


def register(mcp):
    @mcp.tool()
    def echo(message: str) -> str:
        """Return the input message unchanged."""
        return json.dumps({"result": message})

    @mcp.tool()
    def echo_error(message: str) -> str:
        """Always raises a ToolError with the given message."""
        raise ToolError(f"Intentional error: {message}")

    @mcp.tool()
    def echo_large(size_kb: int) -> str:
        """Return deterministic text of approximately N kilobytes."""
        pattern = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        target_bytes = size_kb * 1024
        repeats = target_bytes // len(pattern) + 1
        text = (pattern * repeats)[:target_bytes]
        return json.dumps({"result": text})

    @mcp.tool()
    def echo_nested(depth: int) -> str:
        """Return nested JSON structure to the given depth."""
        result = None
        for level in range(depth, -1, -1):
            result = {"level": level, "child": result}
        return json.dumps({"result": result})

    @mcp.tool()
    def echo_types() -> str:
        """Return an object containing all JSON types."""
        return json.dumps({
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, "two", False],
            "object": {"nested_key": "nested_value"},
        })

    @mcp.tool()
    def echo_empty() -> str:
        """Return an empty string result."""
        return json.dumps({"result": ""})

    @mcp.tool()
    def echo_multiple(messages: list[str]) -> list[TextContent]:
        """Return multiple TextContent blocks, one per message."""
        return [TextContent(type="text", text=msg) for msg in messages]

    @mcp.tool()
    def echo_schema(
        str_param: str,
        int_param: int,
        float_param: float,
        bool_param: bool,
        list_param: list,
        obj_param: dict,
    ) -> str:
        """Echo all parameters back as JSON."""
        return json.dumps({
            "str_param": str_param,
            "int_param": int_param,
            "float_param": float_param,
            "bool_param": bool_param,
            "list_param": list_param,
            "obj_param": obj_param,
        })

    @mcp.tool()
    def get_weather(city: str) -> str:
        """Get weather for a city. Always returns fixed deterministic data (77°F, sunny)."""
        return json.dumps({
            "city": city,
            "temperature_f": 77,
            "temperature_c": 25,
            "condition": "sunny",
            "humidity_pct": 45,
            "wind_mph": 5,
        })

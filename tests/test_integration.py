"""Integration tests for the MCP test server."""

import asyncio
import json
import unittest

from mcp.server.fastmcp import FastMCP

from tools import register_all


def _make_server():
    mcp = FastMCP(name="test")
    register_all(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    if isinstance(result, tuple):
        result = result[0]
    return json.loads(result[0].text)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_all_65_tools_registered(self):
        """Verify exactly 65 tools are registered."""
        tools = asyncio.run(self.mcp.list_tools())
        self.assertEqual(len(tools), 65, f"Expected 65 tools, got {len(tools)}: {[t.name for t in tools]}")

    def test_tool_groups_have_8_each(self):
        """Verify each group prefix has exactly 8 tools."""
        tools = asyncio.run(self.mcp.list_tools())
        names = [t.name for t in tools]
        prefixes = ["math_", "string_", "collection_", "encoding_", "datetime_", "validation_", "conversion_"]
        for prefix in prefixes:
            group = [n for n in names if n.startswith(prefix)]
            self.assertEqual(len(group), 8, f"Group '{prefix}' has {len(group)} tools: {group}")
        # echo group: "echo" plus 7 "echo_*" tools + get_weather
        echo_group = [n for n in names if n == "echo" or n.startswith("echo_")]
        self.assertEqual(len(echo_group), 8, f"Group 'echo' has {len(echo_group)} tools: {echo_group}")
        # get_weather is a standalone test fixture tool
        self.assertIn("get_weather", names)

    def test_all_tools_have_descriptions(self):
        """Verify every tool has a description."""
        tools = asyncio.run(self.mcp.list_tools())
        for tool in tools:
            self.assertTrue(tool.description, f"Tool {tool.name} has no description")

    def test_determinism(self):
        """Verify tools produce identical output for identical input."""
        test_cases = [
            ("math_add", {"a": 3, "b": 5}),
            ("string_reverse", {"text": "hello"}),
            ("encoding_sha256", {"text": "test"}),
            ("datetime_day_of_week", {"date_string": "2024-03-15"}),
            ("validation_is_email", {"text": "user@example.com"}),
            ("conversion_celsius_to_fahrenheit", {"value": 100}),
            ("echo", {"message": "test"}),
            ("collection_sort", {"items": [3, 1, 2]}),
            ("get_weather", {"city": "San Francisco"}),
        ]
        for name, args in test_cases:
            r1 = asyncio.run(self.mcp.call_tool(name, args))
            r2 = asyncio.run(self.mcp.call_tool(name, args))
            if isinstance(r1, tuple):
                r1 = r1[0]
            if isinstance(r2, tuple):
                r2 = r2[0]
            self.assertEqual(r1[0].text, r2[0].text, f"Tool {name} is not deterministic")

    def test_all_tool_names_unique(self):
        """Verify no duplicate tool names."""
        tools = asyncio.run(self.mcp.list_tools())
        names = [t.name for t in tools]
        self.assertEqual(len(names), len(set(names)), f"Duplicate tool names found: {[n for n in names if names.count(n) > 1]}")


if __name__ == "__main__":
    unittest.main()

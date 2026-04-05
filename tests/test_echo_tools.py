"""Tests for echo tools."""

import asyncio
import json

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import TextContent

from tools.echo_tools import register


def _make_server():
    mcp = FastMCP(name="test")
    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    content_list = result[0] if isinstance(result, tuple) else result
    return json.loads(content_list[0].text)


def _call_raw(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    return result[0] if isinstance(result, tuple) else result


# ---------- echo ----------

class TestEcho:
    def test_simple_message(self):
        mcp = _make_server()
        assert _call(mcp, "echo", {"message": "hello"}) == {"result": "hello"}

    def test_empty_message(self):
        mcp = _make_server()
        assert _call(mcp, "echo", {"message": ""}) == {"result": ""}

    def test_special_characters(self):
        mcp = _make_server()
        msg = 'quotes "and" \'single\' <html> & symbols!'
        assert _call(mcp, "echo", {"message": msg}) == {"result": msg}

    def test_unicode(self):
        mcp = _make_server()
        msg = "Hello, world!"
        assert _call(mcp, "echo", {"message": msg}) == {"result": msg}

    def test_long_message(self):
        mcp = _make_server()
        msg = "x" * 10000
        assert _call(mcp, "echo", {"message": msg}) == {"result": msg}

    def test_newlines(self):
        mcp = _make_server()
        msg = "line1\nline2\nline3"
        assert _call(mcp, "echo", {"message": msg}) == {"result": msg}

    def test_json_string(self):
        mcp = _make_server()
        msg = '{"key": "value"}'
        assert _call(mcp, "echo", {"message": msg}) == {"result": msg}


# ---------- echo_error ----------

class TestEchoError:
    def test_raises_tool_error(self):
        mcp = _make_server()
        with __import__("pytest").raises(ToolError):
            _call(mcp, "echo_error", {"message": "fail"})

    def test_error_message_content(self):
        mcp = _make_server()
        try:
            _call(mcp, "echo_error", {"message": "test msg"})
            assert False, "Should have raised ToolError"
        except ToolError as e:
            assert "Intentional error: test msg" in str(e)

    def test_always_raises(self):
        mcp = _make_server()
        for msg in ["a", "b", "hello world", ""]:
            with __import__("pytest").raises(ToolError):
                _call(mcp, "echo_error", {"message": msg})


# ---------- echo_large ----------

class TestEchoLarge:
    def test_1kb(self):
        mcp = _make_server()
        res = _call(mcp, "echo_large", {"size_kb": 1})
        assert len(res["result"]) == 1024

    def test_5kb(self):
        mcp = _make_server()
        res = _call(mcp, "echo_large", {"size_kb": 5})
        assert len(res["result"]) == 5 * 1024

    def test_0kb(self):
        mcp = _make_server()
        res = _call(mcp, "echo_large", {"size_kb": 0})
        assert len(res["result"]) == 0

    def test_deterministic(self):
        mcp = _make_server()
        res1 = _call(mcp, "echo_large", {"size_kb": 2})
        res2 = _call(mcp, "echo_large", {"size_kb": 2})
        assert res1 == res2

    def test_pattern_content(self):
        mcp = _make_server()
        res = _call(mcp, "echo_large", {"size_kb": 1})
        pattern = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        assert res["result"].startswith(pattern)


# ---------- echo_nested ----------

class TestEchoNested:
    def test_depth_0(self):
        mcp = _make_server()
        res = _call(mcp, "echo_nested", {"depth": 0})
        assert res == {"result": {"level": 0, "child": None}}

    def test_depth_1(self):
        mcp = _make_server()
        res = _call(mcp, "echo_nested", {"depth": 1})
        assert res == {"result": {"level": 0, "child": {"level": 1, "child": None}}}

    def test_depth_3(self):
        mcp = _make_server()
        res = _call(mcp, "echo_nested", {"depth": 3})
        node = res["result"]
        for i in range(4):
            assert node["level"] == i
            if i < 3:
                assert node["child"] is not None
                node = node["child"]
            else:
                assert node["child"] is None

    def test_depth_10(self):
        mcp = _make_server()
        res = _call(mcp, "echo_nested", {"depth": 10})
        node = res["result"]
        for i in range(11):
            assert node["level"] == i
            if i < 10:
                node = node["child"]
            else:
                assert node["child"] is None


# ---------- echo_types ----------

class TestEchoTypes:
    def test_all_types_present(self):
        mcp = _make_server()
        res = _call(mcp, "echo_types", {})
        assert res["string"] == "hello"
        assert res["integer"] == 42
        assert res["float"] == 3.14
        assert res["boolean"] is True
        assert res["null"] is None
        assert res["array"] == [1, "two", False]
        assert res["object"] == {"nested_key": "nested_value"}

    def test_types_are_correct(self):
        mcp = _make_server()
        res = _call(mcp, "echo_types", {})
        assert isinstance(res["string"], str)
        assert isinstance(res["integer"], int)
        assert isinstance(res["float"], float)
        assert isinstance(res["boolean"], bool)
        assert res["null"] is None
        assert isinstance(res["array"], list)
        assert isinstance(res["object"], dict)

    def test_deterministic(self):
        mcp = _make_server()
        res1 = _call(mcp, "echo_types", {})
        res2 = _call(mcp, "echo_types", {})
        assert res1 == res2


# ---------- echo_empty ----------

class TestEchoEmpty:
    def test_returns_empty_string(self):
        mcp = _make_server()
        assert _call(mcp, "echo_empty", {}) == {"result": ""}

    def test_result_is_string(self):
        mcp = _make_server()
        res = _call(mcp, "echo_empty", {})
        assert isinstance(res["result"], str)

    def test_result_is_empty(self):
        mcp = _make_server()
        res = _call(mcp, "echo_empty", {})
        assert len(res["result"]) == 0


# ---------- echo_multiple ----------

class TestEchoMultiple:
    def test_single_message(self):
        mcp = _make_server()
        raw = _call_raw(mcp, "echo_multiple", {"messages": ["hello"]})
        assert len(raw) == 1
        assert isinstance(raw[0], TextContent)
        assert raw[0].text == "hello"

    def test_multiple_messages(self):
        mcp = _make_server()
        msgs = ["one", "two", "three"]
        raw = _call_raw(mcp, "echo_multiple", {"messages": msgs})
        assert len(raw) == 3
        for i, msg in enumerate(msgs):
            assert raw[i].text == msg
            assert raw[i].type == "text"

    def test_empty_list(self):
        mcp = _make_server()
        raw = _call_raw(mcp, "echo_multiple", {"messages": []})
        assert len(raw) == 0

    def test_messages_preserve_content(self):
        mcp = _make_server()
        msgs = ["special chars: <>&\"'", "unicode: cafe", ""]
        raw = _call_raw(mcp, "echo_multiple", {"messages": msgs})
        assert len(raw) == 3
        for i, msg in enumerate(msgs):
            assert raw[i].text == msg


# ---------- echo_schema ----------

class TestEchoSchema:
    def test_all_param_types(self):
        mcp = _make_server()
        args = {
            "str_param": "hello",
            "int_param": 42,
            "float_param": 3.14,
            "bool_param": True,
            "list_param": [1, 2, 3],
            "obj_param": {"key": "value"},
        }
        res = _call(mcp, "echo_schema", args)
        assert res["str_param"] == "hello"
        assert res["int_param"] == 42
        assert res["float_param"] == 3.14
        assert res["bool_param"] is True
        assert res["list_param"] == [1, 2, 3]
        assert res["obj_param"] == {"key": "value"}

    def test_empty_values(self):
        mcp = _make_server()
        args = {
            "str_param": "",
            "int_param": 0,
            "float_param": 0.0,
            "bool_param": False,
            "list_param": [],
            "obj_param": {},
        }
        res = _call(mcp, "echo_schema", args)
        assert res["str_param"] == ""
        assert res["int_param"] == 0
        assert res["float_param"] == 0.0
        assert res["bool_param"] is False
        assert res["list_param"] == []
        assert res["obj_param"] == {}

    def test_complex_nested(self):
        mcp = _make_server()
        args = {
            "str_param": "test",
            "int_param": -1,
            "float_param": -0.5,
            "bool_param": True,
            "list_param": [1, "two", [3, 4], {"five": 5}],
            "obj_param": {"a": {"b": {"c": "deep"}}},
        }
        res = _call(mcp, "echo_schema", args)
        assert res["list_param"] == [1, "two", [3, 4], {"five": 5}]
        assert res["obj_param"]["a"]["b"]["c"] == "deep"

    def test_large_int(self):
        mcp = _make_server()
        args = {
            "str_param": "x",
            "int_param": 999999999,
            "float_param": 1.0,
            "bool_param": False,
            "list_param": [],
            "obj_param": {},
        }
        res = _call(mcp, "echo_schema", args)
        assert res["int_param"] == 999999999

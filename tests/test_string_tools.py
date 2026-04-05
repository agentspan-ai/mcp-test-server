"""Comprehensive tests for string tools."""

import asyncio
import json

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.string_tools import register

    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    # call_tool returns (list[Content], meta); we need the first Content's text
    contents = result[0] if isinstance(result, tuple) else result
    first = contents[0]
    return json.loads(first.text)


# --- string_reverse ---


class TestStringReverse:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_reverse", {"text": "hello"}) == {"result": "olleh"}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "string_reverse", {"text": ""}) == {"result": ""}

    def test_single_char(self):
        mcp = _make_server()
        assert _call(mcp, "string_reverse", {"text": "a"}) == {"result": "a"}

    def test_palindrome(self):
        mcp = _make_server()
        assert _call(mcp, "string_reverse", {"text": "racecar"}) == {"result": "racecar"}

    def test_with_spaces(self):
        mcp = _make_server()
        assert _call(mcp, "string_reverse", {"text": "hello world"}) == {"result": "dlrow olleh"}

    def test_unicode(self):
        mcp = _make_server()
        assert _call(mcp, "string_reverse", {"text": "abc123"}) == {"result": "321cba"}


# --- string_uppercase ---


class TestStringUppercase:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_uppercase", {"text": "hello"}) == {"result": "HELLO"}

    def test_already_upper(self):
        mcp = _make_server()
        assert _call(mcp, "string_uppercase", {"text": "HELLO"}) == {"result": "HELLO"}

    def test_mixed_case(self):
        mcp = _make_server()
        assert _call(mcp, "string_uppercase", {"text": "HeLLo WoRLd"}) == {"result": "HELLO WORLD"}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "string_uppercase", {"text": ""}) == {"result": ""}

    def test_with_numbers(self):
        mcp = _make_server()
        assert _call(mcp, "string_uppercase", {"text": "abc123"}) == {"result": "ABC123"}


# --- string_lowercase ---


class TestStringLowercase:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_lowercase", {"text": "HELLO"}) == {"result": "hello"}

    def test_already_lower(self):
        mcp = _make_server()
        assert _call(mcp, "string_lowercase", {"text": "hello"}) == {"result": "hello"}

    def test_mixed_case(self):
        mcp = _make_server()
        assert _call(mcp, "string_lowercase", {"text": "HeLLo WoRLd"}) == {"result": "hello world"}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "string_lowercase", {"text": ""}) == {"result": ""}

    def test_with_numbers(self):
        mcp = _make_server()
        assert _call(mcp, "string_lowercase", {"text": "ABC123"}) == {"result": "abc123"}


# --- string_length ---


class TestStringLength:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_length", {"text": "hello"}) == {"result": 5}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "string_length", {"text": ""}) == {"result": 0}

    def test_with_spaces(self):
        mcp = _make_server()
        assert _call(mcp, "string_length", {"text": "hello world"}) == {"result": 11}

    def test_single_char(self):
        mcp = _make_server()
        assert _call(mcp, "string_length", {"text": "x"}) == {"result": 1}

    def test_special_chars(self):
        mcp = _make_server()
        assert _call(mcp, "string_length", {"text": "!@#$%"}) == {"result": 5}


# --- string_char_count ---


class TestStringCharCount:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_char_count", {"text": "hello", "char": "l"}) == {"result": 2}

    def test_not_found(self):
        mcp = _make_server()
        assert _call(mcp, "string_char_count", {"text": "hello", "char": "z"}) == {"result": 0}

    def test_all_same(self):
        mcp = _make_server()
        assert _call(mcp, "string_char_count", {"text": "aaaa", "char": "a"}) == {"result": 4}

    def test_empty_text(self):
        mcp = _make_server()
        assert _call(mcp, "string_char_count", {"text": "", "char": "a"}) == {"result": 0}

    def test_space_char(self):
        mcp = _make_server()
        assert _call(mcp, "string_char_count", {"text": "a b c", "char": " "}) == {"result": 2}

    def test_multi_char_substring(self):
        mcp = _make_server()
        assert _call(mcp, "string_char_count", {"text": "abcabc", "char": "ab"}) == {"result": 2}


# --- string_replace ---


class TestStringReplace:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_replace", {"text": "hello world", "old": "world", "new": "there"}) == {
            "result": "hello there"
        }

    def test_multiple_occurrences(self):
        mcp = _make_server()
        assert _call(mcp, "string_replace", {"text": "aaa", "old": "a", "new": "b"}) == {"result": "bbb"}

    def test_no_match(self):
        mcp = _make_server()
        assert _call(mcp, "string_replace", {"text": "hello", "old": "xyz", "new": "abc"}) == {"result": "hello"}

    def test_replace_with_empty(self):
        mcp = _make_server()
        assert _call(mcp, "string_replace", {"text": "hello", "old": "l", "new": ""}) == {"result": "heo"}

    def test_replace_empty_string(self):
        mcp = _make_server()
        # Python str.replace("", x) inserts x between every character and at boundaries
        assert _call(mcp, "string_replace", {"text": "ab", "old": "", "new": "-"}) == {"result": "-a-b-"}

    def test_replace_longer(self):
        mcp = _make_server()
        assert _call(mcp, "string_replace", {"text": "hi", "old": "hi", "new": "hello"}) == {"result": "hello"}


# --- string_split ---


class TestStringSplit:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_split", {"text": "a,b,c", "delimiter": ","}) == {"result": ["a", "b", "c"]}

    def test_space_delimiter(self):
        mcp = _make_server()
        assert _call(mcp, "string_split", {"text": "hello world foo", "delimiter": " "}) == {
            "result": ["hello", "world", "foo"]
        }

    def test_no_delimiter_found(self):
        mcp = _make_server()
        assert _call(mcp, "string_split", {"text": "hello", "delimiter": ","}) == {"result": ["hello"]}

    def test_empty_string(self):
        mcp = _make_server()
        assert _call(mcp, "string_split", {"text": "", "delimiter": ","}) == {"result": [""]}

    def test_multi_char_delimiter(self):
        mcp = _make_server()
        assert _call(mcp, "string_split", {"text": "a::b::c", "delimiter": "::"}) == {"result": ["a", "b", "c"]}

    def test_trailing_delimiter(self):
        mcp = _make_server()
        assert _call(mcp, "string_split", {"text": "a,b,", "delimiter": ","}) == {"result": ["a", "b", ""]}


# --- string_join ---


class TestStringJoin:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "string_join", {"items": ["a", "b", "c"], "delimiter": ","}) == {"result": "a,b,c"}

    def test_space_delimiter(self):
        mcp = _make_server()
        assert _call(mcp, "string_join", {"items": ["hello", "world"], "delimiter": " "}) == {
            "result": "hello world"
        }

    def test_empty_list(self):
        mcp = _make_server()
        assert _call(mcp, "string_join", {"items": [], "delimiter": ","}) == {"result": ""}

    def test_single_item(self):
        mcp = _make_server()
        assert _call(mcp, "string_join", {"items": ["only"], "delimiter": ","}) == {"result": "only"}

    def test_empty_delimiter(self):
        mcp = _make_server()
        assert _call(mcp, "string_join", {"items": ["a", "b", "c"], "delimiter": ""}) == {"result": "abc"}

    def test_multi_char_delimiter(self):
        mcp = _make_server()
        assert _call(mcp, "string_join", {"items": ["x", "y"], "delimiter": " -- "}) == {"result": "x -- y"}

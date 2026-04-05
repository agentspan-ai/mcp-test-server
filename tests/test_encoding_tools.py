"""Tests for encoding tools."""

import asyncio
import json

import pytest
from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.encoding_tools import register

    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    # call_tool returns (list[Content], meta); we need the first content item's text
    content_list = result[0] if isinstance(result, tuple) else result
    item = content_list[0]
    return json.loads(item.text)


# ── Base64 ───────────────────────────────────────────────────────────────────


class TestBase64Encode:
    def test_hello(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_base64_encode", {"text": "hello"}) == {"result": "aGVsbG8="}

    def test_empty_string(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_base64_encode", {"text": ""}) == {"result": ""}

    def test_unicode(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_base64_encode", {"text": "héllo"})
        assert res["result"] == "aMOpbGxv"

    def test_whitespace(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_base64_encode", {"text": "hello world"})
        assert res["result"] == "aGVsbG8gd29ybGQ="

    def test_special_characters(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_base64_encode", {"text": "a+b/c=d"})
        assert "result" in res


class TestBase64Decode:
    def test_hello(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_base64_decode", {"data": "aGVsbG8="}) == {"result": "hello"}

    def test_empty_string(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_base64_decode", {"data": ""}) == {"result": ""}

    def test_invalid_base64(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_base64_decode", {"data": "!!!invalid!!!"})
        assert "error" in res

    def test_roundtrip(self):
        mcp = _make_server()
        original = "The quick brown fox jumps over the lazy dog"
        encoded = _call(mcp, "encoding_base64_encode", {"text": original})
        decoded = _call(mcp, "encoding_base64_decode", {"data": encoded["result"]})
        assert decoded == {"result": original}


# ── URL Encoding ─────────────────────────────────────────────────────────────


class TestUrlEncode:
    def test_spaces(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_url_encode", {"text": "hello world"})
        assert res == {"result": "hello+world"}

    def test_special_chars(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_url_encode", {"text": "a=1&b=2"})
        assert res == {"result": "a%3D1%26b%3D2"}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_url_encode", {"text": ""}) == {"result": ""}

    def test_already_safe(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_url_encode", {"text": "hello"}) == {"result": "hello"}

    def test_unicode(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_url_encode", {"text": "café"})
        assert "result" in res
        assert "caf" in res["result"]


class TestUrlDecode:
    def test_plus_to_space(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_url_decode", {"text": "hello+world"}) == {"result": "hello world"}

    def test_percent_encoded(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_url_decode", {"text": "a%3D1%26b%3D2"}) == {"result": "a=1&b=2"}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_url_decode", {"text": ""}) == {"result": ""}

    def test_roundtrip(self):
        mcp = _make_server()
        original = "key=hello world&foo=bar baz"
        encoded = _call(mcp, "encoding_url_encode", {"text": original})
        decoded = _call(mcp, "encoding_url_decode", {"text": encoded["result"]})
        assert decoded == {"result": original}


# ── Hex ──────────────────────────────────────────────────────────────────────


class TestHexEncode:
    def test_hello(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_hex_encode", {"text": "hello"}) == {"result": "68656c6c6f"}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_hex_encode", {"text": ""}) == {"result": ""}

    def test_space(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_hex_encode", {"text": " "})
        assert res == {"result": "20"}

    def test_digits(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_hex_encode", {"text": "123"})
        assert res == {"result": "313233"}


class TestHexDecode:
    def test_hello(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_hex_decode", {"data": "68656c6c6f"}) == {"result": "hello"}

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_hex_decode", {"data": ""}) == {"result": ""}

    def test_invalid_hex(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_hex_decode", {"data": "zzzz"})
        assert "error" in res

    def test_odd_length(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_hex_decode", {"data": "abc"})
        assert "error" in res

    def test_roundtrip(self):
        mcp = _make_server()
        original = "Test 123!"
        encoded = _call(mcp, "encoding_hex_encode", {"text": original})
        decoded = _call(mcp, "encoding_hex_decode", {"data": encoded["result"]})
        assert decoded == {"result": original}


# ── Hashes ───────────────────────────────────────────────────────────────────


class TestMd5:
    def test_hello(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_md5", {"text": "hello"}) == {
            "result": "5d41402abc4b2a76b9719d911017c592"
        }

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_md5", {"text": ""}) == {
            "result": "d41d8cd98f00b204e9800998ecf8427e"
        }

    def test_deterministic(self):
        mcp = _make_server()
        r1 = _call(mcp, "encoding_md5", {"text": "test"})
        r2 = _call(mcp, "encoding_md5", {"text": "test"})
        assert r1 == r2

    def test_different_inputs(self):
        mcp = _make_server()
        r1 = _call(mcp, "encoding_md5", {"text": "abc"})
        r2 = _call(mcp, "encoding_md5", {"text": "def"})
        assert r1["result"] != r2["result"]


class TestSha256:
    def test_hello(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_sha256", {"text": "hello"}) == {
            "result": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        }

    def test_empty(self):
        mcp = _make_server()
        assert _call(mcp, "encoding_sha256", {"text": ""}) == {
            "result": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }

    def test_deterministic(self):
        mcp = _make_server()
        r1 = _call(mcp, "encoding_sha256", {"text": "test"})
        r2 = _call(mcp, "encoding_sha256", {"text": "test"})
        assert r1 == r2

    def test_different_inputs(self):
        mcp = _make_server()
        r1 = _call(mcp, "encoding_sha256", {"text": "abc"})
        r2 = _call(mcp, "encoding_sha256", {"text": "def"})
        assert r1["result"] != r2["result"]

    def test_length(self):
        mcp = _make_server()
        res = _call(mcp, "encoding_sha256", {"text": "anything"})
        assert len(res["result"]) == 64  # SHA-256 hex digest is always 64 chars

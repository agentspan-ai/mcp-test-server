"""Tests for validation tools."""

import asyncio
import json

import pytest
from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.validation_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    # call_tool returns (list[TextContent], meta); we need the first content item
    content = result[0] if isinstance(result, list) else result[0]
    text = content[0].text if isinstance(content, list) else content.text
    return json.loads(text)


# ---------- validation_is_email ----------

class TestIsEmail:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_simple(self):
        r = _call(self.mcp, "validation_is_email", {"text": "user@example.com"})
        assert r["valid"] is True

    def test_valid_with_dots_and_plus(self):
        r = _call(self.mcp, "validation_is_email", {"text": "first.last+tag@sub.domain.org"})
        assert r["valid"] is True

    def test_invalid_no_at(self):
        r = _call(self.mcp, "validation_is_email", {"text": "userexample.com"})
        assert r["valid"] is False

    def test_invalid_no_domain(self):
        r = _call(self.mcp, "validation_is_email", {"text": "user@"})
        assert r["valid"] is False

    def test_invalid_no_tld(self):
        r = _call(self.mcp, "validation_is_email", {"text": "user@example"})
        assert r["valid"] is False

    def test_invalid_empty(self):
        r = _call(self.mcp, "validation_is_email", {"text": ""})
        assert r["valid"] is False


# ---------- validation_is_url ----------

class TestIsUrl:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_http(self):
        r = _call(self.mcp, "validation_is_url", {"text": "http://example.com"})
        assert r["valid"] is True

    def test_valid_https_with_path(self):
        r = _call(self.mcp, "validation_is_url", {"text": "https://example.com/path?q=1"})
        assert r["valid"] is True

    def test_invalid_no_scheme(self):
        r = _call(self.mcp, "validation_is_url", {"text": "example.com"})
        assert r["valid"] is False

    def test_invalid_ftp_scheme(self):
        r = _call(self.mcp, "validation_is_url", {"text": "ftp://files.example.com"})
        assert r["valid"] is False

    def test_invalid_no_netloc(self):
        r = _call(self.mcp, "validation_is_url", {"text": "http://"})
        assert r["valid"] is False

    def test_invalid_empty(self):
        r = _call(self.mcp, "validation_is_url", {"text": ""})
        assert r["valid"] is False


# ---------- validation_is_ipv4 ----------

class TestIsIpv4:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_loopback(self):
        r = _call(self.mcp, "validation_is_ipv4", {"text": "127.0.0.1"})
        assert r["valid"] is True

    def test_valid_broadcast(self):
        r = _call(self.mcp, "validation_is_ipv4", {"text": "255.255.255.255"})
        assert r["valid"] is True

    def test_valid_zeros(self):
        r = _call(self.mcp, "validation_is_ipv4", {"text": "0.0.0.0"})
        assert r["valid"] is True

    def test_invalid_too_many_octets(self):
        r = _call(self.mcp, "validation_is_ipv4", {"text": "1.2.3.4.5"})
        assert r["valid"] is False

    def test_invalid_octet_out_of_range(self):
        r = _call(self.mcp, "validation_is_ipv4", {"text": "256.1.1.1"})
        assert r["valid"] is False

    def test_invalid_text(self):
        r = _call(self.mcp, "validation_is_ipv4", {"text": "not-an-ip"})
        assert r["valid"] is False


# ---------- validation_is_ipv6 ----------

class TestIsIpv6:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_full(self):
        r = _call(self.mcp, "validation_is_ipv6", {"text": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"})
        assert r["valid"] is True

    def test_valid_loopback(self):
        r = _call(self.mcp, "validation_is_ipv6", {"text": "::1"})
        assert r["valid"] is True

    def test_valid_abbreviated(self):
        r = _call(self.mcp, "validation_is_ipv6", {"text": "fe80::1"})
        assert r["valid"] is True

    def test_invalid_ipv4(self):
        r = _call(self.mcp, "validation_is_ipv6", {"text": "192.168.1.1"})
        assert r["valid"] is False

    def test_invalid_text(self):
        r = _call(self.mcp, "validation_is_ipv6", {"text": "not-ipv6"})
        assert r["valid"] is False

    def test_invalid_too_many_groups(self):
        r = _call(self.mcp, "validation_is_ipv6", {"text": "2001:db8:85a3:0:0:8a2e:370:7334:extra"})
        assert r["valid"] is False


# ---------- validation_is_uuid ----------

class TestIsUuid:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_v4(self):
        r = _call(self.mcp, "validation_is_uuid", {"text": "550e8400-e29b-41d4-a716-446655440000"})
        assert r["valid"] is True

    def test_valid_uppercase(self):
        r = _call(self.mcp, "validation_is_uuid", {"text": "550E8400-E29B-41D4-A716-446655440000"})
        assert r["valid"] is True

    def test_invalid_short(self):
        r = _call(self.mcp, "validation_is_uuid", {"text": "550e8400-e29b-41d4"})
        assert r["valid"] is False

    def test_invalid_text(self):
        r = _call(self.mcp, "validation_is_uuid", {"text": "not-a-uuid"})
        assert r["valid"] is False

    def test_invalid_empty(self):
        r = _call(self.mcp, "validation_is_uuid", {"text": ""})
        assert r["valid"] is False


# ---------- validation_is_json ----------

class TestIsJson:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_object(self):
        r = _call(self.mcp, "validation_is_json", {"text": '{"key": "value"}'})
        assert r["valid"] is True

    def test_valid_array(self):
        r = _call(self.mcp, "validation_is_json", {"text": "[1, 2, 3]"})
        assert r["valid"] is True

    def test_valid_string(self):
        r = _call(self.mcp, "validation_is_json", {"text": '"hello"'})
        assert r["valid"] is True

    def test_valid_number(self):
        r = _call(self.mcp, "validation_is_json", {"text": "42"})
        assert r["valid"] is True

    def test_valid_null(self):
        r = _call(self.mcp, "validation_is_json", {"text": "null"})
        assert r["valid"] is True

    def test_invalid_trailing_comma(self):
        r = _call(self.mcp, "validation_is_json", {"text": '{"a": 1,}'})
        assert r["valid"] is False

    def test_invalid_bare_text(self):
        r = _call(self.mcp, "validation_is_json", {"text": "not json"})
        assert r["valid"] is False

    def test_invalid_empty(self):
        r = _call(self.mcp, "validation_is_json", {"text": ""})
        assert r["valid"] is False


# ---------- validation_is_palindrome ----------

class TestIsPalindrome:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_simple(self):
        r = _call(self.mcp, "validation_is_palindrome", {"text": "racecar"})
        assert r["valid"] is True

    def test_valid_single_char(self):
        r = _call(self.mcp, "validation_is_palindrome", {"text": "a"})
        assert r["valid"] is True

    def test_valid_empty(self):
        r = _call(self.mcp, "validation_is_palindrome", {"text": ""})
        assert r["valid"] is True

    def test_valid_even_length(self):
        r = _call(self.mcp, "validation_is_palindrome", {"text": "abba"})
        assert r["valid"] is True

    def test_invalid_case_sensitive(self):
        r = _call(self.mcp, "validation_is_palindrome", {"text": "Racecar"})
        assert r["valid"] is False

    def test_invalid_not_palindrome(self):
        r = _call(self.mcp, "validation_is_palindrome", {"text": "hello"})
        assert r["valid"] is False


# ---------- validation_matches_regex ----------

class TestMatchesRegex:
    def setup_method(self):
        self.mcp = _make_server()

    def test_valid_digits(self):
        r = _call(self.mcp, "validation_matches_regex", {"text": "abc123", "pattern": r"\d+"})
        assert r["valid"] is True

    def test_valid_full_match(self):
        r = _call(self.mcp, "validation_matches_regex", {"text": "hello", "pattern": r"^hello$"})
        assert r["valid"] is True

    def test_valid_partial_match(self):
        r = _call(self.mcp, "validation_matches_regex", {"text": "hello world", "pattern": "world"})
        assert r["valid"] is True

    def test_invalid_no_match(self):
        r = _call(self.mcp, "validation_matches_regex", {"text": "abc", "pattern": r"^\d+$"})
        assert r["valid"] is False

    def test_invalid_bad_pattern(self):
        r = _call(self.mcp, "validation_matches_regex", {"text": "test", "pattern": "[invalid"})
        assert r["valid"] is False
        assert "Invalid regex" in r["reason"]

    def test_invalid_empty_text_nonempty_pattern(self):
        r = _call(self.mcp, "validation_matches_regex", {"text": "", "pattern": r"\d+"})
        assert r["valid"] is False

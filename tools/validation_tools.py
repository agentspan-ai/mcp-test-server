"""Validation tools for MCP test server."""

import ipaddress
import json
import re
import uuid
from urllib.parse import urlparse


def register(mcp):
    @mcp.tool()
    def validation_is_email(text: str) -> str:
        """Check whether a string is a valid email address format."""
        pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if re.match(pattern, text):
            return json.dumps({"valid": True, "reason": "Text is a valid email address."})
        return json.dumps({"valid": False, "reason": "Text is not a valid email address."})

    @mcp.tool()
    def validation_is_url(text: str) -> str:
        """Check whether a string is a valid URL with http or https scheme."""
        parsed = urlparse(text)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return json.dumps({"valid": True, "reason": "Text is a valid URL."})
        return json.dumps({"valid": False, "reason": "Text is not a valid URL. Must have http/https scheme and a network location."})

    @mcp.tool()
    def validation_is_ipv4(text: str) -> str:
        """Check whether a string is a valid IPv4 address."""
        try:
            ipaddress.IPv4Address(text)
            return json.dumps({"valid": True, "reason": "Text is a valid IPv4 address."})
        except (ipaddress.AddressValueError, ValueError):
            return json.dumps({"valid": False, "reason": "Text is not a valid IPv4 address."})

    @mcp.tool()
    def validation_is_ipv6(text: str) -> str:
        """Check whether a string is a valid IPv6 address."""
        try:
            ipaddress.IPv6Address(text)
            return json.dumps({"valid": True, "reason": "Text is a valid IPv6 address."})
        except (ipaddress.AddressValueError, ValueError):
            return json.dumps({"valid": False, "reason": "Text is not a valid IPv6 address."})

    @mcp.tool()
    def validation_is_uuid(text: str) -> str:
        """Check whether a string is a valid UUID."""
        try:
            uuid.UUID(text)
            return json.dumps({"valid": True, "reason": "Text is a valid UUID."})
        except (ValueError, AttributeError):
            return json.dumps({"valid": False, "reason": "Text is not a valid UUID."})

    @mcp.tool()
    def validation_is_json(text: str) -> str:
        """Check whether a string is valid JSON."""
        try:
            json.loads(text)
            return json.dumps({"valid": True, "reason": "Text is valid JSON."})
        except (json.JSONDecodeError, TypeError):
            return json.dumps({"valid": False, "reason": "Text is not valid JSON."})

    @mcp.tool()
    def validation_is_palindrome(text: str) -> str:
        """Check whether a string is a case-sensitive palindrome."""
        if text == text[::-1]:
            return json.dumps({"valid": True, "reason": "Text is a palindrome."})
        return json.dumps({"valid": False, "reason": "Text is not a palindrome."})

    @mcp.tool()
    def validation_matches_regex(text: str, pattern: str) -> str:
        """Check whether a string matches a given regular expression pattern."""
        try:
            if re.search(pattern, text):
                return json.dumps({"valid": True, "reason": f"Text matches the pattern '{pattern}'."})
            return json.dumps({"valid": False, "reason": f"Text does not match the pattern '{pattern}'."})
        except re.error as e:
            return json.dumps({"valid": False, "reason": f"Invalid regex pattern: {e}"})

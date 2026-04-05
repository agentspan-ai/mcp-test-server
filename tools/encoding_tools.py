"""Encoding tools for MCP test server."""

import base64
import hashlib
import json
from urllib.parse import quote_plus, unquote_plus


def register(mcp):
    @mcp.tool()
    def encoding_base64_encode(text: str) -> str:
        """Base64-encode a string."""
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        return json.dumps({"result": encoded})

    @mcp.tool()
    def encoding_base64_decode(data: str) -> str:
        """Base64-decode a string. Returns an error if the input is not valid base64."""
        try:
            decoded = base64.b64decode(data).decode("utf-8")
            return json.dumps({"result": decoded})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def encoding_url_encode(text: str) -> str:
        """URL-encode a string using percent-encoding (spaces become +)."""
        return json.dumps({"result": quote_plus(text)})

    @mcp.tool()
    def encoding_url_decode(text: str) -> str:
        """URL-decode a percent-encoded string."""
        try:
            return json.dumps({"result": unquote_plus(text)})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def encoding_hex_encode(text: str) -> str:
        """Hex-encode a string."""
        encoded = text.encode("utf-8").hex()
        return json.dumps({"result": encoded})

    @mcp.tool()
    def encoding_hex_decode(data: str) -> str:
        """Hex-decode a string. Returns an error if the input is not valid hex."""
        try:
            decoded = bytes.fromhex(data).decode("utf-8")
            return json.dumps({"result": decoded})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def encoding_md5(text: str) -> str:
        """Return the MD5 hash hex digest of a string."""
        digest = hashlib.md5(text.encode("utf-8")).hexdigest()
        return json.dumps({"result": digest})

    @mcp.tool()
    def encoding_sha256(text: str) -> str:
        """Return the SHA-256 hash hex digest of a string."""
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return json.dumps({"result": digest})

"""String tools for MCP test server."""

import json


def register(mcp):
    @mcp.tool()
    def string_reverse(text: str) -> str:
        """Reverse a string."""
        return json.dumps({"result": text[::-1]})

    @mcp.tool()
    def string_uppercase(text: str) -> str:
        """Convert a string to uppercase."""
        return json.dumps({"result": text.upper()})

    @mcp.tool()
    def string_lowercase(text: str) -> str:
        """Convert a string to lowercase."""
        return json.dumps({"result": text.lower()})

    @mcp.tool()
    def string_length(text: str) -> str:
        """Return the character count of a string."""
        return json.dumps({"result": len(text)})

    @mcp.tool()
    def string_char_count(text: str, char: str) -> str:
        """Count occurrences of a character in a string."""
        return json.dumps({"result": text.count(char)})

    @mcp.tool()
    def string_replace(text: str, old: str, new: str) -> str:
        """Replace all occurrences of old with new in a string."""
        return json.dumps({"result": text.replace(old, new)})

    @mcp.tool()
    def string_split(text: str, delimiter: str) -> str:
        """Split a string by a delimiter."""
        return json.dumps({"result": text.split(delimiter)})

    @mcp.tool()
    def string_join(items: list[str], delimiter: str) -> str:
        """Join a list of strings with a delimiter."""
        return json.dumps({"result": delimiter.join(items)})

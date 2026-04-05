"""Conversion tools for MCP test server."""

import json
import re


def register(mcp):
    @mcp.tool()
    def conversion_celsius_to_fahrenheit(value: float) -> str:
        """Convert a temperature from Celsius to Fahrenheit."""
        result = round(value * 9 / 5 + 32, 2)
        return json.dumps({"result": result})

    @mcp.tool()
    def conversion_fahrenheit_to_celsius(value: float) -> str:
        """Convert a temperature from Fahrenheit to Celsius."""
        result = round((value - 32) * 5 / 9, 2)
        return json.dumps({"result": result})

    @mcp.tool()
    def conversion_km_to_miles(value: float) -> str:
        """Convert a distance from kilometers to miles."""
        result = round(value * 0.621371, 6)
        return json.dumps({"result": result})

    @mcp.tool()
    def conversion_miles_to_km(value: float) -> str:
        """Convert a distance from miles to kilometers."""
        result = round(value * 1.60934, 6)
        return json.dumps({"result": result})

    @mcp.tool()
    def conversion_bytes_to_human(bytes: int) -> str:
        """Convert a byte count to a human-readable string (e.g., '1.00 KB')."""
        if bytes < 0:
            return json.dumps({"error": "Byte count must be non-negative"})
        if bytes == 0:
            return json.dumps({"result": "0 B"})
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        value = float(bytes)
        for unit in units:
            if abs(value) < 1024:
                if unit == "B":
                    return json.dumps({"result": f"{int(value)} B"})
                return json.dumps({"result": f"{value:.2f} {unit}"})
            if unit != units[-1]:
                value /= 1024
        return json.dumps({"result": f"{value:.2f} {units[-1]}"})

    @mcp.tool()
    def conversion_rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB color values (0-255) to a hex color string."""
        for name, val in [("r", r), ("g", g), ("b", b)]:
            if val < 0 or val > 255:
                return json.dumps({"error": f"{name} must be between 0 and 255"})
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        return json.dumps({"result": hex_color})

    @mcp.tool()
    def conversion_hex_to_rgb(hex_color: str) -> str:
        """Convert a hex color string to RGB values. Supports with or without '#' prefix."""
        color = hex_color.strip().lstrip("#")
        if not re.match(r"^[0-9a-fA-F]{6}$", color):
            return json.dumps({"error": "Invalid hex color format. Expected 6-digit hex string."})
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        return json.dumps({"result": {"r": r, "g": g, "b": b}})

    @mcp.tool()
    def conversion_decimal_to_binary(value: int) -> str:
        """Convert a decimal integer to its binary string representation (without '0b' prefix)."""
        if value < 0:
            return json.dumps({"result": "-" + bin(abs(value))[2:]})
        return json.dumps({"result": bin(value)[2:]})

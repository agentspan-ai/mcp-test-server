"""Tests for conversion tools."""

import asyncio
import json

from mcp.server.fastmcp import FastMCP

from tools.conversion_tools import register


def _make_server():
    mcp = FastMCP(name="test")
    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    # call_tool returns (list[Content], raw_result); we need list[Content][0].text
    content_list = result[0] if isinstance(result, tuple) else result
    return json.loads(content_list[0].text)


# ---------- conversion_celsius_to_fahrenheit ----------

class TestCelsiusToFahrenheit:
    def test_freezing_point(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_celsius_to_fahrenheit", {"value": 0}) == {"result": 32.0}

    def test_boiling_point(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_celsius_to_fahrenheit", {"value": 100}) == {"result": 212.0}

    def test_negative(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_celsius_to_fahrenheit", {"value": -40}) == {"result": -40.0}

    def test_body_temperature(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_celsius_to_fahrenheit", {"value": 37}) == {"result": 98.6}

    def test_fractional(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_celsius_to_fahrenheit", {"value": 25.5}) == {"result": 77.9}


# ---------- conversion_fahrenheit_to_celsius ----------

class TestFahrenheitToCelsius:
    def test_freezing_point(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_fahrenheit_to_celsius", {"value": 32}) == {"result": 0.0}

    def test_boiling_point(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_fahrenheit_to_celsius", {"value": 212}) == {"result": 100.0}

    def test_negative(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_fahrenheit_to_celsius", {"value": -40}) == {"result": -40.0}

    def test_body_temperature(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_fahrenheit_to_celsius", {"value": 98.6}) == {"result": 37.0}

    def test_zero(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_fahrenheit_to_celsius", {"value": 0})
        assert res == {"result": -17.78}


# ---------- conversion_km_to_miles ----------

class TestKmToMiles:
    def test_one_km(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_km_to_miles", {"value": 1}) == {"result": 0.621371}

    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_km_to_miles", {"value": 0}) == {"result": 0.0}

    def test_marathon(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_km_to_miles", {"value": 42.195})
        assert abs(res["result"] - 26.218757) < 1e-4

    def test_ten_km(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_km_to_miles", {"value": 10}) == {"result": 6.21371}


# ---------- conversion_miles_to_km ----------

class TestMilesToKm:
    def test_one_mile(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_miles_to_km", {"value": 1}) == {"result": 1.60934}

    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_miles_to_km", {"value": 0}) == {"result": 0.0}

    def test_ten_miles(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_miles_to_km", {"value": 10}) == {"result": 16.0934}

    def test_half_mile(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_miles_to_km", {"value": 0.5}) == {"result": 0.80467}


# ---------- conversion_bytes_to_human ----------

class TestBytesToHuman:
    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_bytes_to_human", {"bytes": 0}) == {"result": "0 B"}

    def test_one_byte(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_bytes_to_human", {"bytes": 1}) == {"result": "1 B"}

    def test_one_kb(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_bytes_to_human", {"bytes": 1024}) == {"result": "1.00 KB"}

    def test_one_mb(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_bytes_to_human", {"bytes": 1048576}) == {"result": "1.00 MB"}

    def test_one_gb(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_bytes_to_human", {"bytes": 1073741824}) == {"result": "1.00 GB"}

    def test_one_tb(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_bytes_to_human", {"bytes": 1099511627776}) == {"result": "1.00 TB"}

    def test_500_bytes(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_bytes_to_human", {"bytes": 500}) == {"result": "500 B"}

    def test_1500_bytes(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_bytes_to_human", {"bytes": 1500})
        assert res == {"result": "1.46 KB"}

    def test_negative(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_bytes_to_human", {"bytes": -1})
        assert "error" in res


# ---------- conversion_rgb_to_hex ----------

class TestRgbToHex:
    def test_orange(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_rgb_to_hex", {"r": 255, "g": 128, "b": 0}) == {"result": "#ff8000"}

    def test_black(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_rgb_to_hex", {"r": 0, "g": 0, "b": 0}) == {"result": "#000000"}

    def test_white(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_rgb_to_hex", {"r": 255, "g": 255, "b": 255}) == {"result": "#ffffff"}

    def test_red(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_rgb_to_hex", {"r": 255, "g": 0, "b": 0}) == {"result": "#ff0000"}

    def test_out_of_range(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_rgb_to_hex", {"r": 256, "g": 0, "b": 0})
        assert "error" in res

    def test_negative_value(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_rgb_to_hex", {"r": -1, "g": 0, "b": 0})
        assert "error" in res


# ---------- conversion_hex_to_rgb ----------

class TestHexToRgb:
    def test_with_hash(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_hex_to_rgb", {"hex_color": "#ff8000"}) == {
            "result": {"r": 255, "g": 128, "b": 0}
        }

    def test_without_hash(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_hex_to_rgb", {"hex_color": "ff8000"}) == {
            "result": {"r": 255, "g": 128, "b": 0}
        }

    def test_black(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_hex_to_rgb", {"hex_color": "#000000"}) == {
            "result": {"r": 0, "g": 0, "b": 0}
        }

    def test_white(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_hex_to_rgb", {"hex_color": "#ffffff"}) == {
            "result": {"r": 255, "g": 255, "b": 255}
        }

    def test_uppercase(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_hex_to_rgb", {"hex_color": "#FF8000"}) == {
            "result": {"r": 255, "g": 128, "b": 0}
        }

    def test_invalid_format(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_hex_to_rgb", {"hex_color": "xyz"})
        assert "error" in res

    def test_too_short(self):
        mcp = _make_server()
        res = _call(mcp, "conversion_hex_to_rgb", {"hex_color": "#fff"})
        assert "error" in res


# ---------- conversion_decimal_to_binary ----------

class TestDecimalToBinary:
    def test_forty_two(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_decimal_to_binary", {"value": 42}) == {"result": "101010"}

    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_decimal_to_binary", {"value": 0}) == {"result": "0"}

    def test_one(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_decimal_to_binary", {"value": 1}) == {"result": "1"}

    def test_power_of_two(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_decimal_to_binary", {"value": 256}) == {"result": "100000000"}

    def test_negative(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_decimal_to_binary", {"value": -5}) == {"result": "-101"}

    def test_255(self):
        mcp = _make_server()
        assert _call(mcp, "conversion_decimal_to_binary", {"value": 255}) == {"result": "11111111"}

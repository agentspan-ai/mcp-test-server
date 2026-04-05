"""Tests for math tools."""

import asyncio
import json
import math

from mcp.server.fastmcp import FastMCP

from tools.math_tools import register


def _make_server():
    mcp = FastMCP(name="test")
    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    # call_tool returns (list[Content], raw_result); we need list[Content][0].text
    content_list = result[0] if isinstance(result, tuple) else result
    return json.loads(content_list[0].text)


# ---------- math_add ----------

class TestMathAdd:
    def test_positive_numbers(self):
        mcp = _make_server()
        assert _call(mcp, "math_add", {"a": 2, "b": 3}) == {"result": 5.0}

    def test_negative_numbers(self):
        mcp = _make_server()
        assert _call(mcp, "math_add", {"a": -2, "b": -3}) == {"result": -5.0}

    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "math_add", {"a": 0, "b": 0}) == {"result": 0.0}

    def test_floats(self):
        mcp = _make_server()
        res = _call(mcp, "math_add", {"a": 1.5, "b": 2.5})
        assert res == {"result": 4.0}

    def test_mixed_signs(self):
        mcp = _make_server()
        assert _call(mcp, "math_add", {"a": 10, "b": -3}) == {"result": 7.0}


# ---------- math_subtract ----------

class TestMathSubtract:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "math_subtract", {"a": 10, "b": 3}) == {"result": 7.0}

    def test_negative_result(self):
        mcp = _make_server()
        assert _call(mcp, "math_subtract", {"a": 3, "b": 10}) == {"result": -7.0}

    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "math_subtract", {"a": 5, "b": 0}) == {"result": 5.0}

    def test_same_numbers(self):
        mcp = _make_server()
        assert _call(mcp, "math_subtract", {"a": 7, "b": 7}) == {"result": 0.0}


# ---------- math_multiply ----------

class TestMathMultiply:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "math_multiply", {"a": 4, "b": 5}) == {"result": 20.0}

    def test_by_zero(self):
        mcp = _make_server()
        assert _call(mcp, "math_multiply", {"a": 100, "b": 0}) == {"result": 0.0}

    def test_negative(self):
        mcp = _make_server()
        assert _call(mcp, "math_multiply", {"a": -3, "b": 4}) == {"result": -12.0}

    def test_two_negatives(self):
        mcp = _make_server()
        assert _call(mcp, "math_multiply", {"a": -3, "b": -4}) == {"result": 12.0}

    def test_floats(self):
        mcp = _make_server()
        res = _call(mcp, "math_multiply", {"a": 2.5, "b": 4})
        assert res == {"result": 10.0}


# ---------- math_divide ----------

class TestMathDivide:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "math_divide", {"a": 10, "b": 2}) == {"result": 5.0}

    def test_float_result(self):
        mcp = _make_server()
        assert _call(mcp, "math_divide", {"a": 7, "b": 2}) == {"result": 3.5}

    def test_divide_by_zero(self):
        mcp = _make_server()
        res = _call(mcp, "math_divide", {"a": 10, "b": 0})
        assert "error" in res
        assert "zero" in res["error"].lower()

    def test_negative_divisor(self):
        mcp = _make_server()
        assert _call(mcp, "math_divide", {"a": 10, "b": -2}) == {"result": -5.0}

    def test_zero_dividend(self):
        mcp = _make_server()
        assert _call(mcp, "math_divide", {"a": 0, "b": 5}) == {"result": 0.0}


# ---------- math_modulo ----------

class TestMathModulo:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "math_modulo", {"a": 10, "b": 3}) == {"result": 1.0}

    def test_no_remainder(self):
        mcp = _make_server()
        assert _call(mcp, "math_modulo", {"a": 9, "b": 3}) == {"result": 0.0}

    def test_mod_by_zero(self):
        mcp = _make_server()
        res = _call(mcp, "math_modulo", {"a": 10, "b": 0})
        assert "error" in res
        assert "zero" in res["error"].lower()

    def test_float_modulo(self):
        mcp = _make_server()
        res = _call(mcp, "math_modulo", {"a": 5.5, "b": 2})
        assert abs(res["result"] - 1.5) < 1e-9


# ---------- math_power ----------

class TestMathPower:
    def test_basic(self):
        mcp = _make_server()
        assert _call(mcp, "math_power", {"base": 2, "exponent": 3}) == {"result": 8.0}

    def test_zero_exponent(self):
        mcp = _make_server()
        assert _call(mcp, "math_power", {"base": 5, "exponent": 0}) == {"result": 1.0}

    def test_negative_exponent(self):
        mcp = _make_server()
        assert _call(mcp, "math_power", {"base": 2, "exponent": -1}) == {"result": 0.5}

    def test_fractional_exponent(self):
        mcp = _make_server()
        res = _call(mcp, "math_power", {"base": 9, "exponent": 0.5})
        assert abs(res["result"] - 3.0) < 1e-9

    def test_zero_base(self):
        mcp = _make_server()
        assert _call(mcp, "math_power", {"base": 0, "exponent": 5}) == {"result": 0.0}


# ---------- math_factorial ----------

class TestMathFactorial:
    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "math_factorial", {"n": 0}) == {"result": 1}

    def test_one(self):
        mcp = _make_server()
        assert _call(mcp, "math_factorial", {"n": 1}) == {"result": 1}

    def test_five(self):
        mcp = _make_server()
        assert _call(mcp, "math_factorial", {"n": 5}) == {"result": 120}

    def test_ten(self):
        mcp = _make_server()
        assert _call(mcp, "math_factorial", {"n": 10}) == {"result": math.factorial(10)}

    def test_negative(self):
        mcp = _make_server()
        res = _call(mcp, "math_factorial", {"n": -1})
        assert "error" in res
        assert "negative" in res["error"].lower()


# ---------- math_fibonacci ----------

class TestMathFibonacci:
    def test_zero(self):
        mcp = _make_server()
        assert _call(mcp, "math_fibonacci", {"n": 0}) == {"result": 0}

    def test_one(self):
        mcp = _make_server()
        assert _call(mcp, "math_fibonacci", {"n": 1}) == {"result": 1}

    def test_two(self):
        mcp = _make_server()
        assert _call(mcp, "math_fibonacci", {"n": 2}) == {"result": 1}

    def test_ten(self):
        mcp = _make_server()
        assert _call(mcp, "math_fibonacci", {"n": 10}) == {"result": 55}

    def test_negative(self):
        mcp = _make_server()
        res = _call(mcp, "math_fibonacci", {"n": -1})
        assert "error" in res
        assert "negative" in res["error"].lower()

    def test_sequence(self):
        """Verify the first several Fibonacci numbers."""
        mcp = _make_server()
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        for i, val in enumerate(expected):
            assert _call(mcp, "math_fibonacci", {"n": i}) == {"result": val}

"""Math tools for MCP test server."""

import json
import math


def register(mcp):
    @mcp.tool()
    def math_add(a: float, b: float) -> str:
        """Add two numbers and return the sum."""
        return json.dumps({"result": a + b})

    @mcp.tool()
    def math_subtract(a: float, b: float) -> str:
        """Subtract b from a and return the difference."""
        return json.dumps({"result": a - b})

    @mcp.tool()
    def math_multiply(a: float, b: float) -> str:
        """Multiply two numbers and return the product."""
        return json.dumps({"result": a * b})

    @mcp.tool()
    def math_divide(a: float, b: float) -> str:
        """Divide a by b. Returns an error if b is zero."""
        if b == 0:
            return json.dumps({"error": "Division by zero"})
        return json.dumps({"result": a / b})

    @mcp.tool()
    def math_modulo(a: float, b: float) -> str:
        """Return the remainder of a divided by b. Returns an error if b is zero."""
        if b == 0:
            return json.dumps({"error": "Division by zero"})
        return json.dumps({"result": a % b})

    @mcp.tool()
    def math_power(base: float, exponent: float) -> str:
        """Raise base to the power of exponent."""
        return json.dumps({"result": base ** exponent})

    @mcp.tool()
    def math_factorial(n: int) -> str:
        """Return n factorial (n!). Returns an error if n is negative."""
        if n < 0:
            return json.dumps({"error": "Factorial is not defined for negative numbers"})
        return json.dumps({"result": math.factorial(n)})

    @mcp.tool()
    def math_fibonacci(n: int) -> str:
        """Return the nth Fibonacci number (0-indexed). Returns an error if n is negative."""
        if n < 0:
            return json.dumps({"error": "Fibonacci is not defined for negative numbers"})
        if n == 0:
            return json.dumps({"result": 0})
        if n == 1:
            return json.dumps({"result": 1})
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return json.dumps({"result": b})

# MCP Test Server Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python MCP server with 64 deterministic tools across 8 groups, supporting stdio and SSE transports.

**Architecture:** FastMCP high-level API with modular tool groups. Each group is a separate module that registers 8 tools via a `register(mcp)` function. Server entry point handles transport selection via CLI args.

**Tech Stack:** Python 3.12, `mcp` SDK (FastMCP), `requests`, stdlib (`json`, `base64`, `hashlib`, `urllib.parse`, `datetime`, `re`, `math`, `argparse`, `unittest`)

**Spec:** `docs/superpowers/specs/2026-04-05-mcp-test-server-design.md`

---

## Chunk 1: Scaffolding and Server Entry Point

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `tools/__init__.py`
- Create: `server.py`

- [ ] **Step 1: Create requirements.txt**

```
mcp[cli]>=1.0.0
requests
```

- [ ] **Step 2: Create tools/__init__.py**

```python
"""Tool group registry for MCP test server."""

from tools import (
    math_tools,
    string_tools,
    collection_tools,
    encoding_tools,
    datetime_tools,
    validation_tools,
    conversion_tools,
    echo_tools,
)

ALL_GROUPS = [
    math_tools,
    string_tools,
    collection_tools,
    encoding_tools,
    datetime_tools,
    validation_tools,
    conversion_tools,
    echo_tools,
]


def register_all(mcp):
    """Register all tool groups with the MCP server."""
    for group in ALL_GROUPS:
        group.register(mcp)
```

- [ ] **Step 3: Create server.py**

```python
"""MCP Test Server — 64 deterministic tools for MCP protocol testing."""

import argparse

from mcp.server.fastmcp import FastMCP

from tools import register_all

mcp = FastMCP(
    name="mcp-test-server",
    instructions="A test server with 64 deterministic tools across 8 groups for MCP protocol testing.",
)

register_all(mcp)


def main():
    parser = argparse.ArgumentParser(description="MCP Test Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="SSE host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="SSE port (default: 8000)")
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create stub modules for all 8 groups**

Create each of these files with a minimal `register(mcp)` stub:

`tools/math_tools.py`, `tools/string_tools.py`, `tools/collection_tools.py`, `tools/encoding_tools.py`, `tools/datetime_tools.py`, `tools/validation_tools.py`, `tools/conversion_tools.py`, `tools/echo_tools.py`

Each stub:
```python
"""<Group> tools for MCP test server."""


def register(mcp):
    pass
```

- [ ] **Step 5: Verify server starts**

Run: `python server.py --help`
Expected: Shows help with --transport, --host, --port options.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt server.py tools/
git commit -m "feat: add project scaffolding and server entry point"
```

---

## Chunk 2: Math Tools

### Task 2: Math tools group

**Files:**
- Create: `tests/test_math_tools.py`
- Modify: `tools/math_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/__init__.py` (empty) and `tests/test_math_tools.py`:

```python
"""Tests for math tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.math_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    """Call a tool and return parsed JSON result."""
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    # result is a list of content blocks
    return json.loads(result[0].text)


class TestMathTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_add(self):
        self.assertEqual(_call(self.mcp, "math_add", {"a": 3, "b": 5}), {"result": 8})

    def test_add_floats(self):
        self.assertEqual(_call(self.mcp, "math_add", {"a": 1.5, "b": 2.5}), {"result": 4.0})

    def test_subtract(self):
        self.assertEqual(_call(self.mcp, "math_subtract", {"a": 10, "b": 3}), {"result": 7})

    def test_multiply(self):
        self.assertEqual(_call(self.mcp, "math_multiply", {"a": 4, "b": 7}), {"result": 28})

    def test_divide(self):
        self.assertEqual(_call(self.mcp, "math_divide", {"a": 10, "b": 4}), {"result": 2.5})

    def test_divide_by_zero(self):
        result = _call(self.mcp, "math_divide", {"a": 10, "b": 0})
        self.assertIn("error", result)

    def test_modulo(self):
        self.assertEqual(_call(self.mcp, "math_modulo", {"a": 17, "b": 5}), {"result": 2})

    def test_power(self):
        self.assertEqual(_call(self.mcp, "math_power", {"base": 2, "exponent": 10}), {"result": 1024})

    def test_factorial(self):
        self.assertEqual(_call(self.mcp, "math_factorial", {"n": 5}), {"result": 120})

    def test_factorial_zero(self):
        self.assertEqual(_call(self.mcp, "math_factorial", {"n": 0}), {"result": 1})

    def test_factorial_negative(self):
        result = _call(self.mcp, "math_factorial", {"n": -1})
        self.assertIn("error", result)

    def test_fibonacci(self):
        self.assertEqual(_call(self.mcp, "math_fibonacci", {"n": 10}), {"result": 55})

    def test_fibonacci_zero(self):
        self.assertEqual(_call(self.mcp, "math_fibonacci", {"n": 0}), {"result": 0})

    def test_fibonacci_one(self):
        self.assertEqual(_call(self.mcp, "math_fibonacci", {"n": 1}), {"result": 1})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_math_tools.py -v`
Expected: All tests FAIL (tools not implemented yet).

- [ ] **Step 3: Implement math tools**

Replace `tools/math_tools.py`:

```python
"""Math tools for MCP test server."""

import json
import math


def register(mcp):
    @mcp.tool()
    def math_add(a: float, b: float) -> str:
        """Add two numbers. Returns {result: a + b}."""
        return json.dumps({"result": a + b})

    @mcp.tool()
    def math_subtract(a: float, b: float) -> str:
        """Subtract b from a. Returns {result: a - b}."""
        return json.dumps({"result": a - b})

    @mcp.tool()
    def math_multiply(a: float, b: float) -> str:
        """Multiply two numbers. Returns {result: a * b}."""
        return json.dumps({"result": a * b})

    @mcp.tool()
    def math_divide(a: float, b: float) -> str:
        """Divide a by b. Returns error if b is zero."""
        if b == 0:
            return json.dumps({"error": "Division by zero"})
        return json.dumps({"result": a / b})

    @mcp.tool()
    def math_modulo(a: float, b: float) -> str:
        """Compute a modulo b. Returns error if b is zero."""
        if b == 0:
            return json.dumps({"error": "Modulo by zero"})
        return json.dumps({"result": a % b})

    @mcp.tool()
    def math_power(base: float, exponent: float) -> str:
        """Raise base to exponent. Returns {result: base ** exponent}."""
        return json.dumps({"result": base ** exponent})

    @mcp.tool()
    def math_factorial(n: int) -> str:
        """Compute n factorial. Returns error if n is negative."""
        if n < 0:
            return json.dumps({"error": "Factorial undefined for negative numbers"})
        return json.dumps({"result": math.factorial(n)})

    @mcp.tool()
    def math_fibonacci(n: int) -> str:
        """Compute the nth Fibonacci number (0-indexed). Returns error if n is negative."""
        if n < 0:
            return json.dumps({"error": "Fibonacci undefined for negative numbers"})
        if n <= 1:
            return json.dumps({"result": n})
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return json.dumps({"result": b})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_math_tools.py -v`
Expected: All 14 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/ tools/math_tools.py
git commit -m "feat: implement math tools group with tests"
```

---

## Chunk 3: String Tools

### Task 3: String tools group

**Files:**
- Create: `tests/test_string_tools.py`
- Modify: `tools/string_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/test_string_tools.py`:

```python
"""Tests for string tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.string_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    return json.loads(result[0].text)


class TestStringTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_reverse(self):
        self.assertEqual(_call(self.mcp, "string_reverse", {"text": "hello"}), {"result": "olleh"})

    def test_reverse_empty(self):
        self.assertEqual(_call(self.mcp, "string_reverse", {"text": ""}), {"result": ""})

    def test_uppercase(self):
        self.assertEqual(_call(self.mcp, "string_uppercase", {"text": "hello"}), {"result": "HELLO"})

    def test_lowercase(self):
        self.assertEqual(_call(self.mcp, "string_lowercase", {"text": "HELLO"}), {"result": "hello"})

    def test_length(self):
        self.assertEqual(_call(self.mcp, "string_length", {"text": "hello"}), {"result": 5})

    def test_length_empty(self):
        self.assertEqual(_call(self.mcp, "string_length", {"text": ""}), {"result": 0})

    def test_char_count(self):
        self.assertEqual(_call(self.mcp, "string_char_count", {"text": "banana", "char": "a"}), {"result": 3})

    def test_replace(self):
        self.assertEqual(
            _call(self.mcp, "string_replace", {"text": "hello world", "old": "world", "new": "there"}),
            {"result": "hello there"},
        )

    def test_split(self):
        self.assertEqual(
            _call(self.mcp, "string_split", {"text": "a,b,c", "delimiter": ","}),
            {"result": ["a", "b", "c"]},
        )

    def test_join(self):
        self.assertEqual(
            _call(self.mcp, "string_join", {"items": ["a", "b", "c"], "delimiter": "-"}),
            {"result": "a-b-c"},
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_string_tools.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Implement string tools**

Replace `tools/string_tools.py`:

```python
"""String tools for MCP test server."""

import json


def register(mcp):
    @mcp.tool()
    def string_reverse(text: str) -> str:
        """Reverse a string."""
        return json.dumps({"result": text[::-1]})

    @mcp.tool()
    def string_uppercase(text: str) -> str:
        """Convert string to uppercase."""
        return json.dumps({"result": text.upper()})

    @mcp.tool()
    def string_lowercase(text: str) -> str:
        """Convert string to lowercase."""
        return json.dumps({"result": text.lower()})

    @mcp.tool()
    def string_length(text: str) -> str:
        """Return the length of a string."""
        return json.dumps({"result": len(text)})

    @mcp.tool()
    def string_char_count(text: str, char: str) -> str:
        """Count occurrences of a character in a string."""
        return json.dumps({"result": text.count(char)})

    @mcp.tool()
    def string_replace(text: str, old: str, new: str) -> str:
        """Replace all occurrences of old with new in text."""
        return json.dumps({"result": text.replace(old, new)})

    @mcp.tool()
    def string_split(text: str, delimiter: str) -> str:
        """Split a string by delimiter."""
        return json.dumps({"result": text.split(delimiter)})

    @mcp.tool()
    def string_join(items: list[str], delimiter: str) -> str:
        """Join a list of strings with a delimiter."""
        return json.dumps({"result": delimiter.join(items)})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_string_tools.py -v`
Expected: All 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_string_tools.py tools/string_tools.py
git commit -m "feat: implement string tools group with tests"
```

---

## Chunk 4: Collection Tools

### Task 4: Collection tools group

**Files:**
- Create: `tests/test_collection_tools.py`
- Modify: `tools/collection_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/test_collection_tools.py`:

```python
"""Tests for collection tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.collection_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    return json.loads(result[0].text)


class TestCollectionTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_sort(self):
        self.assertEqual(_call(self.mcp, "collection_sort", {"items": [3, 1, 2]}), {"result": [1, 2, 3]})

    def test_sort_reverse(self):
        self.assertEqual(
            _call(self.mcp, "collection_sort", {"items": [3, 1, 2], "reverse": True}),
            {"result": [3, 2, 1]},
        )

    def test_flatten(self):
        self.assertEqual(
            _call(self.mcp, "collection_flatten", {"items": [1, [2, 3], [4, [5, 6]]]}),
            {"result": [1, 2, 3, 4, 5, 6]},
        )

    def test_merge(self):
        self.assertEqual(
            _call(self.mcp, "collection_merge", {"dict_a": {"a": 1}, "dict_b": {"b": 2}}),
            {"result": {"a": 1, "b": 2}},
        )

    def test_merge_overlap(self):
        self.assertEqual(
            _call(self.mcp, "collection_merge", {"dict_a": {"a": 1}, "dict_b": {"a": 2}}),
            {"result": {"a": 2}},
        )

    def test_filter_gt(self):
        self.assertEqual(
            _call(self.mcp, "collection_filter_gt", {"items": [1, 5, 3, 8, 2], "threshold": 3}),
            {"result": [5, 8]},
        )

    def test_unique(self):
        self.assertEqual(
            _call(self.mcp, "collection_unique", {"items": [1, 2, 2, 3, 1, 4]}),
            {"result": [1, 2, 3, 4]},
        )

    def test_group_by(self):
        items = [{"name": "a", "type": "x"}, {"name": "b", "type": "y"}, {"name": "c", "type": "x"}]
        result = _call(self.mcp, "collection_group_by", {"items": items, "key": "type"})
        self.assertEqual(result, {
            "result": {
                "x": [{"name": "a", "type": "x"}, {"name": "c", "type": "x"}],
                "y": [{"name": "b", "type": "y"}],
            }
        })

    def test_zip(self):
        self.assertEqual(
            _call(self.mcp, "collection_zip", {"list_a": [1, 2, 3], "list_b": ["a", "b", "c"]}),
            {"result": [[1, "a"], [2, "b"], [3, "c"]]},
        )

    def test_chunk(self):
        self.assertEqual(
            _call(self.mcp, "collection_chunk", {"items": [1, 2, 3, 4, 5], "size": 2}),
            {"result": [[1, 2], [3, 4], [5]]},
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_collection_tools.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Implement collection tools**

Replace `tools/collection_tools.py`:

```python
"""Collection tools for MCP test server."""

import json


def _flatten(items):
    """Recursively flatten nested lists."""
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(_flatten(item))
        else:
            result.append(item)
    return result


def register(mcp):
    @mcp.tool()
    def collection_sort(items: list, reverse: bool = False) -> str:
        """Sort a list. Optionally reverse the order."""
        return json.dumps({"result": sorted(items, reverse=reverse)})

    @mcp.tool()
    def collection_flatten(items: list) -> str:
        """Recursively flatten nested lists."""
        return json.dumps({"result": _flatten(items)})

    @mcp.tool()
    def collection_merge(dict_a: dict, dict_b: dict) -> str:
        """Merge two dicts. dict_b values override dict_a on conflict."""
        merged = {**dict_a, **dict_b}
        return json.dumps({"result": merged})

    @mcp.tool()
    def collection_filter_gt(items: list[float], threshold: float) -> str:
        """Filter numbers strictly greater than threshold."""
        return json.dumps({"result": [x for x in items if x > threshold]})

    @mcp.tool()
    def collection_unique(items: list) -> str:
        """Remove duplicates preserving order."""
        seen = []
        result = []
        for item in items:
            key = json.dumps(item, sort_keys=True)
            if key not in seen:
                seen.append(key)
                result.append(item)
        return json.dumps({"result": result})

    @mcp.tool()
    def collection_group_by(items: list[dict], key: str) -> str:
        """Group a list of objects by a key."""
        groups = {}
        for item in items:
            k = str(item.get(key, ""))
            if k not in groups:
                groups[k] = []
            groups[k].append(item)
        return json.dumps({"result": groups})

    @mcp.tool()
    def collection_zip(list_a: list, list_b: list) -> str:
        """Zip two lists into a list of pairs."""
        return json.dumps({"result": [list(pair) for pair in zip(list_a, list_b)]})

    @mcp.tool()
    def collection_chunk(items: list, size: int) -> str:
        """Split a list into chunks of given size."""
        if size <= 0:
            return json.dumps({"error": "Chunk size must be positive"})
        chunks = [items[i:i + size] for i in range(0, len(items), size)]
        return json.dumps({"result": chunks})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_collection_tools.py -v`
Expected: All 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_collection_tools.py tools/collection_tools.py
git commit -m "feat: implement collection tools group with tests"
```

---

## Chunk 5: Encoding Tools

### Task 5: Encoding tools group

**Files:**
- Create: `tests/test_encoding_tools.py`
- Modify: `tools/encoding_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/test_encoding_tools.py`:

```python
"""Tests for encoding tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.encoding_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    return json.loads(result[0].text)


class TestEncodingTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_base64_encode(self):
        self.assertEqual(_call(self.mcp, "encoding_base64_encode", {"text": "hello"}), {"result": "aGVsbG8="})

    def test_base64_decode(self):
        self.assertEqual(_call(self.mcp, "encoding_base64_decode", {"data": "aGVsbG8="}), {"result": "hello"})

    def test_url_encode(self):
        self.assertEqual(
            _call(self.mcp, "encoding_url_encode", {"text": "hello world&foo=bar"}),
            {"result": "hello+world%26foo%3Dbar"},
        )

    def test_url_decode(self):
        self.assertEqual(
            _call(self.mcp, "encoding_url_decode", {"text": "hello+world%26foo%3Dbar"}),
            {"result": "hello world&foo=bar"},
        )

    def test_hex_encode(self):
        self.assertEqual(_call(self.mcp, "encoding_hex_encode", {"text": "hello"}), {"result": "68656c6c6f"})

    def test_hex_decode(self):
        self.assertEqual(_call(self.mcp, "encoding_hex_decode", {"data": "68656c6c6f"}), {"result": "hello"})

    def test_md5(self):
        self.assertEqual(
            _call(self.mcp, "encoding_md5", {"text": "hello"}),
            {"result": "5d41402abc4b2a76b9719d911017c592"},
        )

    def test_sha256(self):
        self.assertEqual(
            _call(self.mcp, "encoding_sha256", {"text": "hello"}),
            {"result": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"},
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_encoding_tools.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Implement encoding tools**

Replace `tools/encoding_tools.py`:

```python
"""Encoding tools for MCP test server."""

import base64
import hashlib
import json
import urllib.parse


def register(mcp):
    @mcp.tool()
    def encoding_base64_encode(text: str) -> str:
        """Base64 encode a string."""
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        return json.dumps({"result": encoded})

    @mcp.tool()
    def encoding_base64_decode(data: str) -> str:
        """Base64 decode a string."""
        try:
            decoded = base64.b64decode(data).decode("utf-8")
            return json.dumps({"result": decoded})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def encoding_url_encode(text: str) -> str:
        """URL-encode a string."""
        return json.dumps({"result": urllib.parse.quote_plus(text)})

    @mcp.tool()
    def encoding_url_decode(text: str) -> str:
        """URL-decode a string."""
        return json.dumps({"result": urllib.parse.unquote_plus(text)})

    @mcp.tool()
    def encoding_hex_encode(text: str) -> str:
        """Hex-encode a string."""
        return json.dumps({"result": text.encode("utf-8").hex()})

    @mcp.tool()
    def encoding_hex_decode(data: str) -> str:
        """Hex-decode a string."""
        try:
            decoded = bytes.fromhex(data).decode("utf-8")
            return json.dumps({"result": decoded})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def encoding_md5(text: str) -> str:
        """Compute MD5 hash of a string."""
        digest = hashlib.md5(text.encode("utf-8")).hexdigest()
        return json.dumps({"result": digest})

    @mcp.tool()
    def encoding_sha256(text: str) -> str:
        """Compute SHA-256 hash of a string."""
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return json.dumps({"result": digest})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_encoding_tools.py -v`
Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_encoding_tools.py tools/encoding_tools.py
git commit -m "feat: implement encoding tools group with tests"
```

---

## Chunk 6: DateTime Tools

### Task 6: DateTime tools group

**Files:**
- Create: `tests/test_datetime_tools.py`
- Modify: `tools/datetime_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/test_datetime_tools.py`:

```python
"""Tests for datetime tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.datetime_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    return json.loads(result[0].text)


class TestDatetimeTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_parse(self):
        result = _call(self.mcp, "datetime_parse", {"date_string": "2024-03-15T10:30:00"})
        self.assertEqual(result, {"result": {"year": 2024, "month": 3, "day": 15, "hour": 10, "minute": 30, "second": 0}})

    def test_parse_date_only(self):
        result = _call(self.mcp, "datetime_parse", {"date_string": "2024-03-15"})
        self.assertEqual(result, {"result": {"year": 2024, "month": 3, "day": 15, "hour": 0, "minute": 0, "second": 0}})

    def test_format(self):
        result = _call(self.mcp, "datetime_format", {"year": 2024, "month": 3, "day": 15, "format": "%Y/%m/%d"})
        self.assertEqual(result, {"result": "2024/03/15"})

    def test_add_days(self):
        result = _call(self.mcp, "datetime_add_days", {"date_string": "2024-02-28", "days": 1})
        self.assertEqual(result, {"result": "2024-02-29"})

    def test_add_days_negative(self):
        result = _call(self.mcp, "datetime_add_days", {"date_string": "2024-03-01", "days": -1})
        self.assertEqual(result, {"result": "2024-02-29"})

    def test_diff(self):
        result = _call(self.mcp, "datetime_diff", {"date_a": "2024-03-15", "date_b": "2024-03-10"})
        self.assertEqual(result, {"result": 5})

    def test_day_of_week(self):
        result = _call(self.mcp, "datetime_day_of_week", {"date_string": "2024-03-15"})
        self.assertEqual(result, {"result": "Friday"})

    def test_is_leap_year_true(self):
        self.assertEqual(_call(self.mcp, "datetime_is_leap_year", {"year": 2024}), {"result": True})

    def test_is_leap_year_false(self):
        self.assertEqual(_call(self.mcp, "datetime_is_leap_year", {"year": 2023}), {"result": False})

    def test_is_leap_year_century(self):
        self.assertEqual(_call(self.mcp, "datetime_is_leap_year", {"year": 1900}), {"result": False})
        self.assertEqual(_call(self.mcp, "datetime_is_leap_year", {"year": 2000}), {"result": True})

    def test_days_in_month(self):
        self.assertEqual(_call(self.mcp, "datetime_days_in_month", {"year": 2024, "month": 2}), {"result": 29})
        self.assertEqual(_call(self.mcp, "datetime_days_in_month", {"year": 2023, "month": 2}), {"result": 28})

    def test_week_number(self):
        result = _call(self.mcp, "datetime_week_number", {"date_string": "2024-01-01"})
        self.assertEqual(result, {"result": 1})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_datetime_tools.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Implement datetime tools**

Replace `tools/datetime_tools.py`:

```python
"""DateTime tools for MCP test server."""

import calendar
import json
from datetime import datetime, timedelta


def _parse_date(date_string):
    """Parse an ISO date string, supporting date-only and datetime."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_string}")


def register(mcp):
    @mcp.tool()
    def datetime_parse(date_string: str) -> str:
        """Parse an ISO date string into components."""
        try:
            dt = _parse_date(date_string)
            return json.dumps({"result": {
                "year": dt.year, "month": dt.month, "day": dt.day,
                "hour": dt.hour, "minute": dt.minute, "second": dt.second,
            }})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_format(year: int, month: int, day: int, format: str) -> str:
        """Format date components into a string using strftime format."""
        try:
            dt = datetime(year, month, day)
            return json.dumps({"result": dt.strftime(format)})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_add_days(date_string: str, days: int) -> str:
        """Add (or subtract) days from a date. Returns ISO date string."""
        try:
            dt = _parse_date(date_string)
            result = dt + timedelta(days=days)
            return json.dumps({"result": result.strftime("%Y-%m-%d")})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_diff(date_a: str, date_b: str) -> str:
        """Compute the difference in days between two dates (a - b)."""
        try:
            a = _parse_date(date_a)
            b = _parse_date(date_b)
            return json.dumps({"result": (a - b).days})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_day_of_week(date_string: str) -> str:
        """Return the weekday name for a date."""
        try:
            dt = _parse_date(date_string)
            return json.dumps({"result": dt.strftime("%A")})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_is_leap_year(year: int) -> str:
        """Check if a year is a leap year."""
        return json.dumps({"result": calendar.isleap(year)})

    @mcp.tool()
    def datetime_days_in_month(year: int, month: int) -> str:
        """Return the number of days in a given month/year."""
        try:
            return json.dumps({"result": calendar.monthrange(year, month)[1]})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_week_number(date_string: str) -> str:
        """Return the ISO week number for a date."""
        try:
            dt = _parse_date(date_string)
            return json.dumps({"result": dt.isocalendar()[1]})
        except ValueError as e:
            return json.dumps({"error": str(e)})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_datetime_tools.py -v`
Expected: All 12 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_datetime_tools.py tools/datetime_tools.py
git commit -m "feat: implement datetime tools group with tests"
```

---

## Chunk 7: Validation Tools

### Task 7: Validation tools group

**Files:**
- Create: `tests/test_validation_tools.py`
- Modify: `tools/validation_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/test_validation_tools.py`:

```python
"""Tests for validation tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.validation_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    return json.loads(result[0].text)


class TestValidationTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_is_email_valid(self):
        result = _call(self.mcp, "validation_is_email", {"text": "user@example.com"})
        self.assertTrue(result["valid"])

    def test_is_email_invalid(self):
        result = _call(self.mcp, "validation_is_email", {"text": "not-an-email"})
        self.assertFalse(result["valid"])

    def test_is_url_valid(self):
        result = _call(self.mcp, "validation_is_url", {"text": "https://example.com/path?q=1"})
        self.assertTrue(result["valid"])

    def test_is_url_invalid(self):
        result = _call(self.mcp, "validation_is_url", {"text": "not a url"})
        self.assertFalse(result["valid"])

    def test_is_ipv4_valid(self):
        result = _call(self.mcp, "validation_is_ipv4", {"text": "192.168.1.1"})
        self.assertTrue(result["valid"])

    def test_is_ipv4_invalid(self):
        result = _call(self.mcp, "validation_is_ipv4", {"text": "256.1.1.1"})
        self.assertFalse(result["valid"])

    def test_is_ipv6_valid(self):
        result = _call(self.mcp, "validation_is_ipv6", {"text": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"})
        self.assertTrue(result["valid"])

    def test_is_ipv6_invalid(self):
        result = _call(self.mcp, "validation_is_ipv6", {"text": "not-ipv6"})
        self.assertFalse(result["valid"])

    def test_is_uuid_valid(self):
        result = _call(self.mcp, "validation_is_uuid", {"text": "550e8400-e29b-41d4-a716-446655440000"})
        self.assertTrue(result["valid"])

    def test_is_uuid_invalid(self):
        result = _call(self.mcp, "validation_is_uuid", {"text": "not-a-uuid"})
        self.assertFalse(result["valid"])

    def test_is_json_valid(self):
        result = _call(self.mcp, "validation_is_json", {"text": '{"key": "value"}'})
        self.assertTrue(result["valid"])

    def test_is_json_invalid(self):
        result = _call(self.mcp, "validation_is_json", {"text": "{bad json"})
        self.assertFalse(result["valid"])

    def test_is_palindrome_true(self):
        result = _call(self.mcp, "validation_is_palindrome", {"text": "racecar"})
        self.assertTrue(result["valid"])

    def test_is_palindrome_false(self):
        result = _call(self.mcp, "validation_is_palindrome", {"text": "hello"})
        self.assertFalse(result["valid"])

    def test_matches_regex_true(self):
        result = _call(self.mcp, "validation_matches_regex", {"text": "abc123", "pattern": "^[a-z]+\\d+$"})
        self.assertTrue(result["valid"])

    def test_matches_regex_false(self):
        result = _call(self.mcp, "validation_matches_regex", {"text": "123abc", "pattern": "^[a-z]+\\d+$"})
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_validation_tools.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Implement validation tools**

Replace `tools/validation_tools.py`:

```python
"""Validation tools for MCP test server."""

import json
import re
import ipaddress
import uuid as uuid_mod
from urllib.parse import urlparse


def register(mcp):
    @mcp.tool()
    def validation_is_email(text: str) -> str:
        """Check if text is a valid email format."""
        pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        valid = bool(re.match(pattern, text))
        reason = "Valid email format" if valid else "Invalid email format"
        return json.dumps({"valid": valid, "reason": reason})

    @mcp.tool()
    def validation_is_url(text: str) -> str:
        """Check if text is a valid URL."""
        try:
            result = urlparse(text)
            valid = all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            valid = False
        reason = "Valid URL" if valid else "Invalid URL"
        return json.dumps({"valid": valid, "reason": reason})

    @mcp.tool()
    def validation_is_ipv4(text: str) -> str:
        """Check if text is a valid IPv4 address."""
        try:
            ipaddress.IPv4Address(text)
            valid = True
        except ipaddress.AddressValueError:
            valid = False
        reason = "Valid IPv4 address" if valid else "Invalid IPv4 address"
        return json.dumps({"valid": valid, "reason": reason})

    @mcp.tool()
    def validation_is_ipv6(text: str) -> str:
        """Check if text is a valid IPv6 address."""
        try:
            ipaddress.IPv6Address(text)
            valid = True
        except ipaddress.AddressValueError:
            valid = False
        reason = "Valid IPv6 address" if valid else "Invalid IPv6 address"
        return json.dumps({"valid": valid, "reason": reason})

    @mcp.tool()
    def validation_is_uuid(text: str) -> str:
        """Check if text is a valid UUID."""
        try:
            uuid_mod.UUID(text)
            valid = True
        except ValueError:
            valid = False
        reason = "Valid UUID" if valid else "Invalid UUID"
        return json.dumps({"valid": valid, "reason": reason})

    @mcp.tool()
    def validation_is_json(text: str) -> str:
        """Check if text is valid JSON."""
        try:
            json.loads(text)
            valid = True
        except (json.JSONDecodeError, TypeError):
            valid = False
        reason = "Valid JSON" if valid else "Invalid JSON"
        return json.dumps({"valid": valid, "reason": reason})

    @mcp.tool()
    def validation_is_palindrome(text: str) -> str:
        """Check if text is a palindrome (case-sensitive)."""
        valid = text == text[::-1]
        reason = "Is a palindrome" if valid else "Not a palindrome"
        return json.dumps({"valid": valid, "reason": reason})

    @mcp.tool()
    def validation_matches_regex(text: str, pattern: str) -> str:
        """Check if text matches the given regex pattern."""
        try:
            valid = bool(re.match(pattern, text))
            reason = "Pattern matches" if valid else "Pattern does not match"
        except re.error as e:
            valid = False
            reason = f"Invalid regex: {e}"
        return json.dumps({"valid": valid, "reason": reason})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_validation_tools.py -v`
Expected: All 16 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_validation_tools.py tools/validation_tools.py
git commit -m "feat: implement validation tools group with tests"
```

---

## Chunk 8: Conversion Tools

### Task 8: Conversion tools group

**Files:**
- Create: `tests/test_conversion_tools.py`
- Modify: `tools/conversion_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/test_conversion_tools.py`:

```python
"""Tests for conversion tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.conversion_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    return json.loads(result[0].text)


class TestConversionTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_celsius_to_fahrenheit(self):
        self.assertEqual(_call(self.mcp, "conversion_celsius_to_fahrenheit", {"value": 0}), {"result": 32.0})
        self.assertEqual(_call(self.mcp, "conversion_celsius_to_fahrenheit", {"value": 100}), {"result": 212.0})

    def test_fahrenheit_to_celsius(self):
        self.assertEqual(_call(self.mcp, "conversion_fahrenheit_to_celsius", {"value": 32}), {"result": 0.0})
        self.assertEqual(_call(self.mcp, "conversion_fahrenheit_to_celsius", {"value": 212}), {"result": 100.0})

    def test_km_to_miles(self):
        result = _call(self.mcp, "conversion_km_to_miles", {"value": 1})
        self.assertAlmostEqual(result["result"], 0.621371, places=5)

    def test_miles_to_km(self):
        result = _call(self.mcp, "conversion_miles_to_km", {"value": 1})
        self.assertAlmostEqual(result["result"], 1.60934, places=4)

    def test_bytes_to_human(self):
        self.assertEqual(_call(self.mcp, "conversion_bytes_to_human", {"bytes": 0}), {"result": "0 B"})
        self.assertEqual(_call(self.mcp, "conversion_bytes_to_human", {"bytes": 1024}), {"result": "1.00 KB"})
        self.assertEqual(_call(self.mcp, "conversion_bytes_to_human", {"bytes": 1048576}), {"result": "1.00 MB"})

    def test_rgb_to_hex(self):
        self.assertEqual(_call(self.mcp, "conversion_rgb_to_hex", {"r": 255, "g": 128, "b": 0}), {"result": "#ff8000"})

    def test_hex_to_rgb(self):
        self.assertEqual(_call(self.mcp, "conversion_hex_to_rgb", {"hex_color": "#ff8000"}), {"result": {"r": 255, "g": 128, "b": 0}})
        self.assertEqual(_call(self.mcp, "conversion_hex_to_rgb", {"hex_color": "ff8000"}), {"result": {"r": 255, "g": 128, "b": 0}})

    def test_decimal_to_binary(self):
        self.assertEqual(_call(self.mcp, "conversion_decimal_to_binary", {"value": 42}), {"result": "101010"})
        self.assertEqual(_call(self.mcp, "conversion_decimal_to_binary", {"value": 0}), {"result": "0"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_conversion_tools.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Implement conversion tools**

Replace `tools/conversion_tools.py`:

```python
"""Conversion tools for MCP test server."""

import json


def register(mcp):
    @mcp.tool()
    def conversion_celsius_to_fahrenheit(value: float) -> str:
        """Convert Celsius to Fahrenheit."""
        return json.dumps({"result": round(value * 9 / 5 + 32, 2)})

    @mcp.tool()
    def conversion_fahrenheit_to_celsius(value: float) -> str:
        """Convert Fahrenheit to Celsius."""
        return json.dumps({"result": round((value - 32) * 5 / 9, 2)})

    @mcp.tool()
    def conversion_km_to_miles(value: float) -> str:
        """Convert kilometers to miles."""
        return json.dumps({"result": round(value * 0.621371, 6)})

    @mcp.tool()
    def conversion_miles_to_km(value: float) -> str:
        """Convert miles to kilometers."""
        return json.dumps({"result": round(value * 1.60934, 6)})

    @mcp.tool()
    def conversion_bytes_to_human(bytes: int) -> str:
        """Convert bytes to human-readable string."""
        if bytes == 0:
            return json.dumps({"result": "0 B"})
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        value = float(bytes)
        while value >= 1024 and i < len(units) - 1:
            value /= 1024
            i += 1
        if i == 0:
            return json.dumps({"result": f"{int(value)} B"})
        return json.dumps({"result": f"{value:.2f} {units[i]}"})

    @mcp.tool()
    def conversion_rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB values (0-255) to hex color string."""
        return json.dumps({"result": f"#{r:02x}{g:02x}{b:02x}"})

    @mcp.tool()
    def conversion_hex_to_rgb(hex_color: str) -> str:
        """Convert hex color string to RGB values."""
        h = hex_color.lstrip("#")
        if len(h) != 6:
            return json.dumps({"error": "Hex color must be 6 characters (with optional # prefix)"})
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return json.dumps({"result": {"r": r, "g": g, "b": b}})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def conversion_decimal_to_binary(value: int) -> str:
        """Convert a decimal integer to binary string."""
        if value < 0:
            return json.dumps({"result": "-" + bin(-value)[2:]})
        return json.dumps({"result": bin(value)[2:]})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_conversion_tools.py -v`
Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_conversion_tools.py tools/conversion_tools.py
git commit -m "feat: implement conversion tools group with tests"
```

---

## Chunk 9: Echo Tools

### Task 9: Echo tools group

**Files:**
- Create: `tests/test_echo_tools.py`
- Modify: `tools/echo_tools.py`

- [ ] **Step 1: Write tests**

Create `tests/test_echo_tools.py`:

```python
"""Tests for echo tools."""

import json
import unittest

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.echo_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    import asyncio
    result = asyncio.run(mcp.call_tool(name, args))
    return result


def _call_json(mcp, name, args):
    result = _call(mcp, name, args)
    return json.loads(result[0].text)


class TestEchoTools(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_echo(self):
        result = _call_json(self.mcp, "echo", {"message": "hello"})
        self.assertEqual(result, {"result": "hello"})

    def test_echo_error(self):
        from mcp.server.fastmcp.exceptions import ToolError
        with self.assertRaises(ToolError):
            _call(self.mcp, "echo_error", {"message": "fail"})

    def test_echo_large(self):
        result = _call_json(self.mcp, "echo_large", {"size_kb": 2})
        text = result["result"]
        # Should be approximately 2KB
        self.assertGreaterEqual(len(text), 1800)
        self.assertLessEqual(len(text), 2200)
        # Should be deterministic
        result2 = _call_json(self.mcp, "echo_large", {"size_kb": 2})
        self.assertEqual(result, result2)

    def test_echo_nested(self):
        result = _call_json(self.mcp, "echo_nested", {"depth": 3})
        # Verify nesting depth
        inner = result["result"]
        self.assertIn("level", inner)
        self.assertEqual(inner["level"], 0)
        self.assertIn("child", inner)
        self.assertEqual(inner["child"]["level"], 1)
        self.assertEqual(inner["child"]["child"]["level"], 2)
        self.assertIsNone(inner["child"]["child"]["child"])

    def test_echo_types(self):
        result = _call_json(self.mcp, "echo_types", {})
        r = result["result"]
        self.assertIsInstance(r["string"], str)
        self.assertIsInstance(r["integer"], int)
        self.assertIsInstance(r["float"], float)
        self.assertIsInstance(r["boolean"], bool)
        self.assertIsNone(r["null"])
        self.assertIsInstance(r["array"], list)
        self.assertIsInstance(r["object"], dict)

    def test_echo_empty(self):
        result = _call_json(self.mcp, "echo_empty", {})
        self.assertEqual(result, {"result": ""})

    def test_echo_multiple(self):
        result = _call(self.mcp, "echo_multiple", {"messages": ["one", "two", "three"]})
        # Should return multiple content blocks
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "one")
        self.assertEqual(result[1].text, "two")
        self.assertEqual(result[2].text, "three")

    def test_echo_schema(self):
        args = {
            "str_param": "hello",
            "int_param": 42,
            "float_param": 3.14,
            "bool_param": True,
            "list_param": [1, 2, 3],
            "obj_param": {"key": "value"},
        }
        result = _call_json(self.mcp, "echo_schema", args)
        self.assertEqual(result["result"], args)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_echo_tools.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Implement echo tools**

Replace `tools/echo_tools.py`:

```python
"""Echo tools for MCP test server — protocol edge-case testing."""

import json

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import TextContent


def register(mcp):
    @mcp.tool()
    def echo(message: str) -> str:
        """Echo back the input message unchanged."""
        return json.dumps({"result": message})

    @mcp.tool()
    def echo_error(message: str) -> str:
        """Always raises a ToolError. For testing error handling."""
        raise ToolError(f"Intentional error: {message}")

    @mcp.tool()
    def echo_large(size_kb: int) -> str:
        """Return a deterministic string of approximately size_kb kilobytes."""
        # Deterministic: repeating pattern of printable ASCII
        pattern = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        target_bytes = size_kb * 1024
        repetitions = target_bytes // len(pattern) + 1
        text = (pattern * repetitions)[:target_bytes]
        return json.dumps({"result": text})

    @mcp.tool()
    def echo_nested(depth: int) -> str:
        """Return a JSON object nested to the given depth."""
        def build(level):
            if level >= depth:
                return {"level": level, "child": None}
            return {"level": level, "child": build(level + 1)}
        return json.dumps({"result": build(0)})

    @mcp.tool()
    def echo_types() -> str:
        """Return an object containing all JSON types."""
        return json.dumps({"result": {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, "two", False],
            "object": {"nested_key": "nested_value"},
        }})

    @mcp.tool()
    def echo_empty() -> str:
        """Return an empty string result."""
        return json.dumps({"result": ""})

    @mcp.tool()
    def echo_multiple(messages: list[str]) -> list[TextContent]:
        """Return each message as a separate content block."""
        return [TextContent(type="text", text=msg) for msg in messages]

    @mcp.tool()
    def echo_schema(
        str_param: str,
        int_param: int,
        float_param: float,
        bool_param: bool,
        list_param: list,
        obj_param: dict,
    ) -> str:
        """Echo back all parameters. Tests complex input schema."""
        return json.dumps({"result": {
            "str_param": str_param,
            "int_param": int_param,
            "float_param": float_param,
            "bool_param": bool_param,
            "list_param": list_param,
            "obj_param": obj_param,
        }})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_echo_tools.py -v`
Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_echo_tools.py tools/echo_tools.py
git commit -m "feat: implement echo tools group with tests"
```

---

## Chunk 10: Integration Verification

### Task 10: Full integration test

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
"""Integration tests for the MCP test server."""

import json
import unittest
import asyncio

from mcp.server.fastmcp import FastMCP

from tools import register_all


def _make_server():
    mcp = FastMCP(name="test")
    register_all(mcp)
    return mcp


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.mcp = _make_server()

    def test_all_64_tools_registered(self):
        """Verify exactly 64 tools are registered."""
        tools = asyncio.run(self.mcp.list_tools())
        self.assertEqual(len(tools), 64, f"Expected 64 tools, got {len(tools)}: {[t.name for t in tools]}")

    def test_tool_groups_have_8_each(self):
        """Verify each group prefix has exactly 8 tools."""
        tools = asyncio.run(self.mcp.list_tools())
        names = [t.name for t in tools]
        prefixes = ["math_", "string_", "collection_", "encoding_", "datetime_", "validation_", "conversion_", "echo_"]
        for prefix in prefixes:
            group = [n for n in names if n.startswith(prefix)]
            self.assertEqual(len(group), 8, f"Group '{prefix}' has {len(group)} tools: {group}")

    def test_all_tools_have_descriptions(self):
        """Verify every tool has a description."""
        tools = asyncio.run(self.mcp.list_tools())
        for tool in tools:
            self.assertTrue(tool.description, f"Tool {tool.name} has no description")

    def test_determinism(self):
        """Verify tools produce identical output for identical input."""
        test_cases = [
            ("math_add", {"a": 3, "b": 5}),
            ("string_reverse", {"text": "hello"}),
            ("encoding_sha256", {"text": "test"}),
            ("datetime_day_of_week", {"date_string": "2024-03-15"}),
            ("validation_is_email", {"text": "user@example.com"}),
            ("conversion_celsius_to_fahrenheit", {"value": 100}),
            ("echo_types", {}),
        ]
        for name, args in test_cases:
            r1 = asyncio.run(self.mcp.call_tool(name, args))
            r2 = asyncio.run(self.mcp.call_tool(name, args))
            self.assertEqual(r1[0].text, r2[0].text, f"Tool {name} is not deterministic")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS (approximately 95+ tests).

- [ ] **Step 3: Verify server starts with stdio**

Run: `python server.py --help`
Expected: Shows usage info.

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "feat: add integration tests — verify 64 tools registered and deterministic"
```

# Agent Contributing Guide

Instructions for AI agents contributing to this project.

## Project Overview

This is an MCP test server with 65 deterministic tools across 8 groups, exposed via MCP (stdio/SSE) and REST API. Every tool returns identical output for identical input — no randomness, no `datetime.now()`, no external state.

## Architecture

```
mcp_test_server/
  server.py      → Entry point. Creates FastMCP instance, registers tools, starts transport.
  api.py         → REST API. Data-driven endpoint registry generates Starlette routes + OpenAPI spec.
  tools/*.py     → Tool modules. Each exports register(mcp) that decorates tools with @mcp.tool().
tests/*.py       → Unit + integration tests using unittest + FastMCP's call_tool().
```

**Key pattern:** Tools are registered as closures inside `register(mcp)` via `@mcp.tool()` decorators. Helper functions live at module level.

## How to Add a New Tool

### 1. Choose the right module

| Group | File | When to use |
|-------|------|-------------|
| math | `mcp_test_server/tools/math_tools.py` | Numeric computation |
| string | `mcp_test_server/tools/string_tools.py` | String manipulation |
| collection | `mcp_test_server/tools/collection_tools.py` | Array/dict operations |
| encoding | `mcp_test_server/tools/encoding_tools.py` | Encode/decode/hash |
| datetime | `mcp_test_server/tools/datetime_tools.py` | Date computations (no current time!) |
| validation | `mcp_test_server/tools/validation_tools.py` | Input checking (returns `{valid, reason}`) |
| conversion | `mcp_test_server/tools/conversion_tools.py` | Unit/format conversions |
| echo | `mcp_test_server/tools/echo_tools.py` | Protocol testing, fixtures, misc |

If a tool doesn't fit any group, add it to `mcp_test_server/tools/echo_tools.py` (the catch-all for test fixtures).

### 2. Implement the tool

Add it inside the `register(mcp)` function in the chosen module:

```python
@mcp.tool()
def my_new_tool(param: str, count: int) -> str:
    """Clear one-line description of what the tool does."""
    result = param * count
    return json.dumps({"result": result})
```

Rules:
- **Return JSON strings** via `json.dumps({"result": ...})` for success
- **Return error objects** via `json.dumps({"error": "message"})` for expected errors
- **Raise `ToolError`** only for tools that intentionally test error handling
- **Be deterministic** — no randomness, no current time, no network calls, no file I/O
- **Use stdlib only** — no imports beyond Python stdlib + `mcp` + `requests`
- **Type-annotate all parameters** — FastMCP uses these to generate JSON schemas
- Validation tools return `json.dumps({"valid": bool, "reason": str})`

### 3. Add the REST API endpoint

In `mcp_test_server/api.py`, add an entry to the `ENDPOINTS` list:

```python
# For GET (simple scalar params):
("/api/group/my-tool", "GET", "my_new_tool",
 "Description for OpenAPI",
 [("param", "string", True, "Param description"),
  ("count", "integer", True, "Count description")]),

# For POST (complex or text-heavy params):
("/api/group/my-tool", "POST", "my_new_tool",
 "Description for OpenAPI",
 [("param", "string", True, "Param description"),
  ("count", "integer", True, "Count description")]),
```

The tuple format is: `(path, method, tool_name, summary, params)` where params is `[(name, json_schema_type, required, description), ...]`.

Use GET for simple scalar inputs. Use POST for text bodies, arrays, objects, or anything complex.

The route handler and OpenAPI spec are generated automatically from this entry.

### 4. Write tests

Add tests in the corresponding `tests/test_<group>_tools.py`:

```python
def test_my_new_tool(self):
    result = _call(self.mcp, "my_new_tool", {"param": "abc", "count": 3})
    self.assertEqual(result, {"result": "abcabcabc"})
```

Also add an API test in `tests/test_api.py`:

```python
def test_my_new_tool(self):
    r = self.client.post("/api/group/my-tool", json={"param": "abc", "count": 3})
    self.assertEqual(r.json(), {"result": "abcabcabc"})
```

### 5. Update integration test

In `tests/test_integration.py`, update the expected tool count in `test_all_65_tools_registered` and adjust group counts if applicable.

### 6. Verify

```bash
python3 -m pytest tests/ -v
```

All tests must pass. Current count: 389 tests.

## How to Add a New Tool Group

1. Create `mcp_test_server/tools/new_group_tools.py` with a `register(mcp)` function
2. Import it in `mcp_test_server/tools/__init__.py` and add to `ALL_GROUPS`
3. Add REST endpoints in `mcp_test_server/api.py` `ENDPOINTS` list
4. Create `tests/test_new_group_tools.py`
5. Update `tests/test_integration.py` tool counts and prefix checks

## Conventions

- **Tool names**: `group_action` (e.g., `math_add`, `string_reverse`)
- **API paths**: `/api/group/action-name` with kebab-case (e.g., `/api/math/add`, `/api/string/char-count`)
- **Responses**: Always JSON. Success: `{"result": ...}`. Error: `{"error": "message"}`. Validation: `{"valid": bool, "reason": str}`.
- **No external state**: Tools must be pure functions of their inputs
- **Test helpers**: Use `_make_server()` and `_call(mcp, name, args)` pattern (see existing tests)

## Running the Server

```bash
# stdio (for MCP client testing)
mcp-testkit

# SSE + REST API
mcp-testkit --transport sse

# With auth
mcp-testkit --transport sse --auth <key>
```

Default SSE port is 3001. Override with `--port`.

## Dependencies

Runtime: `mcp[cli]`, `requests`, Python stdlib.

The server must not add dependencies beyond these. Use stdlib for all tool implementations.

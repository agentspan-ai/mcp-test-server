"""HTTP REST API endpoints for MCP test server tools.

Provides /api/* REST endpoints that delegate to the same MCP tool implementations,
plus /api-docs serving the OpenAPI 3.0 spec.
"""

import json

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


# ---------------------------------------------------------------------------
# Endpoint registry — single source of truth for routes + OpenAPI generation
# ---------------------------------------------------------------------------
# (path, method, tool_name, summary, params)
#   params: list of (name, json_schema_type, required, description)

ENDPOINTS = [
    # --- Math (GET) ---
    ("/api/math/add", "GET", "math_add", "Add two numbers",
     [("a", "number", True, "First number"), ("b", "number", True, "Second number")]),
    ("/api/math/subtract", "GET", "math_subtract", "Subtract b from a",
     [("a", "number", True, "First number"), ("b", "number", True, "Number to subtract")]),
    ("/api/math/multiply", "GET", "math_multiply", "Multiply two numbers",
     [("a", "number", True, "First number"), ("b", "number", True, "Second number")]),
    ("/api/math/divide", "GET", "math_divide", "Divide a by b",
     [("a", "number", True, "Dividend"), ("b", "number", True, "Divisor")]),
    ("/api/math/modulo", "GET", "math_modulo", "Compute a modulo b",
     [("a", "number", True, "Dividend"), ("b", "number", True, "Divisor")]),
    ("/api/math/power", "GET", "math_power", "Raise base to exponent",
     [("base", "number", True, "Base"), ("exponent", "number", True, "Exponent")]),
    ("/api/math/factorial", "GET", "math_factorial", "Compute n factorial",
     [("n", "integer", True, "Non-negative integer")]),
    ("/api/math/fibonacci", "GET", "math_fibonacci", "Compute nth Fibonacci number",
     [("n", "integer", True, "Non-negative integer (0-indexed)")]),

    # --- String (POST) ---
    ("/api/string/reverse", "POST", "string_reverse", "Reverse a string",
     [("text", "string", True, "Text to reverse")]),
    ("/api/string/uppercase", "POST", "string_uppercase", "Convert to uppercase",
     [("text", "string", True, "Text to convert")]),
    ("/api/string/lowercase", "POST", "string_lowercase", "Convert to lowercase",
     [("text", "string", True, "Text to convert")]),
    ("/api/string/length", "POST", "string_length", "Get string length",
     [("text", "string", True, "Text to measure")]),
    ("/api/string/char-count", "POST", "string_char_count", "Count character occurrences",
     [("text", "string", True, "Text to search"), ("char", "string", True, "Character to count")]),
    ("/api/string/replace", "POST", "string_replace", "Replace substrings",
     [("text", "string", True, "Source text"), ("old", "string", True, "Substring to find"), ("new", "string", True, "Replacement")]),
    ("/api/string/split", "POST", "string_split", "Split string by delimiter",
     [("text", "string", True, "Text to split"), ("delimiter", "string", True, "Delimiter")]),
    ("/api/string/join", "POST", "string_join", "Join strings with delimiter",
     [("items", "array", True, "List of strings"), ("delimiter", "string", True, "Delimiter")]),

    # --- Collection (POST) ---
    ("/api/collection/sort", "POST", "collection_sort", "Sort a list",
     [("items", "array", True, "List to sort"), ("reverse", "boolean", False, "Reverse order")]),
    ("/api/collection/flatten", "POST", "collection_flatten", "Flatten nested lists",
     [("items", "array", True, "Nested list")]),
    ("/api/collection/merge", "POST", "collection_merge", "Merge two dicts",
     [("dict_a", "object", True, "Base dict"), ("dict_b", "object", True, "Override dict")]),
    ("/api/collection/filter-gt", "POST", "collection_filter_gt", "Filter numbers greater than threshold",
     [("items", "array", True, "List of numbers"), ("threshold", "number", True, "Threshold")]),
    ("/api/collection/unique", "POST", "collection_unique", "Remove duplicates preserving order",
     [("items", "array", True, "List to deduplicate")]),
    ("/api/collection/group-by", "POST", "collection_group_by", "Group objects by key",
     [("items", "array", True, "List of objects"), ("key", "string", True, "Key to group by")]),
    ("/api/collection/zip", "POST", "collection_zip", "Zip two lists into pairs",
     [("list_a", "array", True, "First list"), ("list_b", "array", True, "Second list")]),
    ("/api/collection/chunk", "POST", "collection_chunk", "Split list into chunks",
     [("items", "array", True, "List to split"), ("size", "integer", True, "Chunk size")]),

    # --- Encoding (POST) ---
    ("/api/encoding/base64-encode", "POST", "encoding_base64_encode", "Base64-encode a string",
     [("text", "string", True, "Text to encode")]),
    ("/api/encoding/base64-decode", "POST", "encoding_base64_decode", "Base64-decode a string",
     [("data", "string", True, "Base64 data to decode")]),
    ("/api/encoding/url-encode", "POST", "encoding_url_encode", "URL-encode a string",
     [("text", "string", True, "Text to encode")]),
    ("/api/encoding/url-decode", "POST", "encoding_url_decode", "URL-decode a string",
     [("text", "string", True, "URL-encoded text to decode")]),
    ("/api/encoding/hex-encode", "POST", "encoding_hex_encode", "Hex-encode a string",
     [("text", "string", True, "Text to encode")]),
    ("/api/encoding/hex-decode", "POST", "encoding_hex_decode", "Hex-decode a string",
     [("data", "string", True, "Hex data to decode")]),
    ("/api/encoding/md5", "POST", "encoding_md5", "Compute MD5 hash",
     [("text", "string", True, "Text to hash")]),
    ("/api/encoding/sha256", "POST", "encoding_sha256", "Compute SHA-256 hash",
     [("text", "string", True, "Text to hash")]),

    # --- DateTime (POST) ---
    ("/api/datetime/parse", "POST", "datetime_parse", "Parse ISO date string into components",
     [("date_string", "string", True, "ISO date string (e.g. 2024-03-15 or 2024-03-15T10:30:00)")]),
    ("/api/datetime/format", "POST", "datetime_format", "Format date components to string",
     [("year", "integer", True, "Year"), ("month", "integer", True, "Month"), ("day", "integer", True, "Day"), ("format", "string", True, "strftime format string")]),
    ("/api/datetime/add-days", "POST", "datetime_add_days", "Add days to a date",
     [("date_string", "string", True, "ISO date string"), ("days", "integer", True, "Days to add (negative to subtract)")]),
    ("/api/datetime/diff", "POST", "datetime_diff", "Compute days between two dates",
     [("date_a", "string", True, "First date"), ("date_b", "string", True, "Second date")]),
    ("/api/datetime/day-of-week", "POST", "datetime_day_of_week", "Get weekday name for a date",
     [("date_string", "string", True, "ISO date string")]),
    ("/api/datetime/is-leap-year", "POST", "datetime_is_leap_year", "Check if year is a leap year",
     [("year", "integer", True, "Year to check")]),
    ("/api/datetime/days-in-month", "POST", "datetime_days_in_month", "Get days in a month",
     [("year", "integer", True, "Year"), ("month", "integer", True, "Month (1-12)")]),
    ("/api/datetime/week-number", "POST", "datetime_week_number", "Get ISO week number",
     [("date_string", "string", True, "ISO date string")]),

    # --- Validation (POST) ---
    ("/api/validation/is-email", "POST", "validation_is_email", "Check email format",
     [("text", "string", True, "Text to validate")]),
    ("/api/validation/is-url", "POST", "validation_is_url", "Check URL format",
     [("text", "string", True, "Text to validate")]),
    ("/api/validation/is-ipv4", "POST", "validation_is_ipv4", "Check IPv4 address",
     [("text", "string", True, "Text to validate")]),
    ("/api/validation/is-ipv6", "POST", "validation_is_ipv6", "Check IPv6 address",
     [("text", "string", True, "Text to validate")]),
    ("/api/validation/is-uuid", "POST", "validation_is_uuid", "Check UUID format",
     [("text", "string", True, "Text to validate")]),
    ("/api/validation/is-json", "POST", "validation_is_json", "Check valid JSON",
     [("text", "string", True, "Text to validate")]),
    ("/api/validation/is-palindrome", "POST", "validation_is_palindrome", "Check palindrome",
     [("text", "string", True, "Text to check")]),
    ("/api/validation/matches-regex", "POST", "validation_matches_regex", "Check regex match",
     [("text", "string", True, "Text to test"), ("pattern", "string", True, "Regex pattern")]),

    # --- Conversion (GET) ---
    ("/api/conversion/celsius-to-fahrenheit", "GET", "conversion_celsius_to_fahrenheit", "Convert Celsius to Fahrenheit",
     [("value", "number", True, "Temperature in Celsius")]),
    ("/api/conversion/fahrenheit-to-celsius", "GET", "conversion_fahrenheit_to_celsius", "Convert Fahrenheit to Celsius",
     [("value", "number", True, "Temperature in Fahrenheit")]),
    ("/api/conversion/km-to-miles", "GET", "conversion_km_to_miles", "Convert kilometers to miles",
     [("value", "number", True, "Distance in kilometers")]),
    ("/api/conversion/miles-to-km", "GET", "conversion_miles_to_km", "Convert miles to kilometers",
     [("value", "number", True, "Distance in miles")]),
    ("/api/conversion/bytes-to-human", "GET", "conversion_bytes_to_human", "Convert bytes to human-readable string",
     [("bytes", "integer", True, "Number of bytes")]),
    ("/api/conversion/rgb-to-hex", "GET", "conversion_rgb_to_hex", "Convert RGB to hex color",
     [("r", "integer", True, "Red (0-255)"), ("g", "integer", True, "Green (0-255)"), ("b", "integer", True, "Blue (0-255)")]),
    ("/api/conversion/hex-to-rgb", "GET", "conversion_hex_to_rgb", "Convert hex color to RGB",
     [("hex_color", "string", True, "Hex color (with or without #)")]),
    ("/api/conversion/decimal-to-binary", "GET", "conversion_decimal_to_binary", "Convert decimal to binary",
     [("value", "integer", True, "Decimal integer")]),

    # --- Echo (mixed) ---
    ("/api/echo", "POST", "echo", "Echo back the input message",
     [("message", "string", True, "Message to echo")]),
    ("/api/echo/error", "POST", "echo_error", "Always returns an error (for testing)",
     [("message", "string", True, "Error message")]),
    ("/api/echo/large", "POST", "echo_large", "Return deterministic text of ~N KB",
     [("size_kb", "integer", True, "Approximate size in kilobytes")]),
    ("/api/echo/nested", "GET", "echo_nested", "Return nested JSON to given depth",
     [("depth", "integer", True, "Nesting depth")]),
    ("/api/echo/types", "GET", "echo_types", "Return object with all JSON types",
     []),
    ("/api/echo/empty", "GET", "echo_empty", "Return empty string",
     []),
    ("/api/echo/multiple", "POST", "echo_multiple", "Return multiple content blocks",
     [("messages", "array", True, "List of message strings")]),
    ("/api/echo/schema", "POST", "echo_schema", "Echo back all parameter types",
     [("str_param", "string", True, "String parameter"),
      ("int_param", "integer", True, "Integer parameter"),
      ("float_param", "number", True, "Float parameter"),
      ("bool_param", "boolean", True, "Boolean parameter"),
      ("list_param", "array", True, "List parameter"),
      ("obj_param", "object", True, "Object parameter")]),

    # --- Weather (GET) ---
    ("/api/weather", "GET", "get_weather", "Get weather for a city (always returns fixed 77F sunny)",
     [("city", "string", True, "City name")]),
]

# Type converters for GET query parameters
_CONVERTERS = {
    "number": float,
    "integer": int,
    "string": str,
    "boolean": lambda s: s.lower() in ("true", "1", "yes"),
}


# ---------------------------------------------------------------------------
# Handler factories
# ---------------------------------------------------------------------------

def _make_get_handler(mcp, tool_name, params):
    """Create a GET handler that extracts typed query params and calls the MCP tool."""
    param_converters = [(p[0], _CONVERTERS[p[1]]) for p in params]

    async def handler(request: Request):
        try:
            args = {}
            for name, converter in param_converters:
                val = request.query_params.get(name)
                if val is not None:
                    args[name] = converter(val)
            return JSONResponse(await _call_tool(mcp, tool_name, args))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)
    return handler


def _make_post_handler(mcp, tool_name):
    """Create a POST handler that passes the JSON body directly to the MCP tool."""
    async def handler(request: Request):
        try:
            body = await request.json()
            return JSONResponse(await _call_tool(mcp, tool_name, body))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)
    return handler


async def _call_tool(mcp, tool_name, args):
    """Call an MCP tool and return the parsed JSON result."""
    try:
        result = await mcp.call_tool(tool_name, args)
        if isinstance(result, tuple):
            result = result[0]
        if len(result) == 1:
            try:
                return json.loads(result[0].text)
            except (json.JSONDecodeError, AttributeError):
                return {"result": result[0].text}
        # Multiple content blocks (e.g., echo_multiple)
        return {"results": [r.text for r in result]}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# OpenAPI spec generation
# ---------------------------------------------------------------------------

def _build_openapi_spec():
    """Generate OpenAPI 3.0 spec from the endpoint registry."""
    paths = {}
    for path, method, _tool, summary, params in ENDPOINTS:
        method_lower = method.lower()
        operation = {
            "summary": summary,
            "operationId": _tool,
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                },
                "400": {
                    "description": "Bad request",
                    "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {"error": {"type": "string"}},
                    }}},
                },
            },
        }

        if method == "GET":
            operation["parameters"] = [
                {
                    "name": p[0],
                    "in": "query",
                    "required": p[2],
                    "description": p[3],
                    "schema": {"type": p[1]},
                }
                for p in params
            ]
        else:  # POST
            if params:
                properties = {p[0]: {"type": p[1], "description": p[3]} for p in params}
                required = [p[0] for p in params if p[2]]
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": properties,
                                "required": required,
                            }
                        }
                    },
                }

        # Group by tag (first path segment after /api/)
        tag = path.split("/")[2] if len(path.split("/")) > 2 else "other"
        operation["tags"] = [tag]

        paths.setdefault(path, {})[method_lower] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "MCP Test Server API",
            "description": "REST API for 65 deterministic MCP test tools across 8 groups.",
            "version": "1.0.0",
        },
        "paths": paths,
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                }
            }
        },
    }


_OPENAPI_SPEC = None


def _get_openapi_spec():
    """Return cached OpenAPI spec (generated once on first access)."""
    global _OPENAPI_SPEC
    if _OPENAPI_SPEC is None:
        _OPENAPI_SPEC = _build_openapi_spec()
    return _OPENAPI_SPEC


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_api_routes(mcp):
    """Create all HTTP API routes + /api-docs for the given FastMCP server."""
    routes = []
    for path, method, tool_name, _summary, params in ENDPOINTS:
        if method == "GET":
            handler = _make_get_handler(mcp, tool_name, params)
        else:
            handler = _make_post_handler(mcp, tool_name)
        routes.append(Route(path, handler, methods=[method]))

    # OpenAPI docs endpoint
    async def api_docs(request: Request):
        return JSONResponse(_get_openapi_spec())

    routes.append(Route("/api-docs", api_docs, methods=["GET"]))

    return routes

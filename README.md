# MCP Test Server

A Python MCP server with **65 deterministic tools** across 8 groups, supporting **stdio**, **SSE**, and **REST API** transports. Built for consistent, repeatable MCP protocol testing.

## Install

```bash
pip install mcp-testkit
```

Or from source:

```bash
git clone https://github.com/agentspan-dev/mcp-test-server.git
cd mcp-test-server
pip install -e .
```

## Quick Start

```bash
# stdio (default)
mcp-testkit

# SSE + REST API on port 3001
mcp-testkit --transport sse

# With bearer token authentication
mcp-testkit --transport sse --auth super_secret_key

# Custom host/port
mcp-testkit --transport sse --host 0.0.0.0 --port 8080
```

## Transports

| Transport | Command | Endpoints |
|-----------|---------|-----------|
| **stdio** | `mcp-testkit` | MCP JSON-RPC over stdin/stdout |
| **SSE** | `mcp-testkit --transport sse` | MCP at `/sse` + REST at `/api/*` + OpenAPI at `/api-docs` |

## Authentication

Pass `--auth <key>` to require a Bearer token on all requests (both MCP SSE and REST):

```bash
mcp-testkit --transport sse --auth my_secret

# Clients must include:
# Authorization: Bearer my_secret
```

## Tools (65 total)

All tools are **deterministic** — same input always produces same output. No randomness, no current time, no external state.

### Math (8 tools)

| Tool | Params | Description |
|------|--------|-------------|
| `math_add` | `a`, `b` | Add two numbers |
| `math_subtract` | `a`, `b` | Subtract b from a |
| `math_multiply` | `a`, `b` | Multiply two numbers |
| `math_divide` | `a`, `b` | Divide (errors on zero) |
| `math_modulo` | `a`, `b` | Remainder (errors on zero) |
| `math_power` | `base`, `exponent` | Exponentiation |
| `math_factorial` | `n` | n! (errors on negative) |
| `math_fibonacci` | `n` | Nth Fibonacci number (0-indexed) |

### String (8 tools)

| Tool | Params | Description |
|------|--------|-------------|
| `string_reverse` | `text` | Reverse a string |
| `string_uppercase` | `text` | Convert to uppercase |
| `string_lowercase` | `text` | Convert to lowercase |
| `string_length` | `text` | Character count |
| `string_char_count` | `text`, `char` | Count occurrences |
| `string_replace` | `text`, `old`, `new` | Replace all occurrences |
| `string_split` | `text`, `delimiter` | Split by delimiter |
| `string_join` | `items`, `delimiter` | Join list with delimiter |

### Collection (8 tools)

| Tool | Params | Description |
|------|--------|-------------|
| `collection_sort` | `items`, `reverse?` | Sort a list |
| `collection_flatten` | `items` | Recursively flatten nested lists |
| `collection_merge` | `dict_a`, `dict_b` | Merge dicts (b wins on conflict) |
| `collection_filter_gt` | `items`, `threshold` | Filter numbers > threshold |
| `collection_unique` | `items` | Remove duplicates (order preserved) |
| `collection_group_by` | `items`, `key` | Group objects by key |
| `collection_zip` | `list_a`, `list_b` | Zip into list of pairs |
| `collection_chunk` | `items`, `size` | Split into chunks |

### Encoding (8 tools)

| Tool | Params | Description |
|------|--------|-------------|
| `encoding_base64_encode` | `text` | Base64 encode |
| `encoding_base64_decode` | `data` | Base64 decode |
| `encoding_url_encode` | `text` | URL-encode |
| `encoding_url_decode` | `text` | URL-decode |
| `encoding_hex_encode` | `text` | Hex encode |
| `encoding_hex_decode` | `data` | Hex decode |
| `encoding_md5` | `text` | MD5 hash |
| `encoding_sha256` | `text` | SHA-256 hash |

### DateTime (8 tools)

All operate on provided dates — never use current time.

| Tool | Params | Description |
|------|--------|-------------|
| `datetime_parse` | `date_string` | Parse ISO date to components |
| `datetime_format` | `year`, `month`, `day`, `format` | Format date to string |
| `datetime_add_days` | `date_string`, `days` | Add/subtract days |
| `datetime_diff` | `date_a`, `date_b` | Days between two dates |
| `datetime_day_of_week` | `date_string` | Weekday name |
| `datetime_is_leap_year` | `year` | Leap year check |
| `datetime_days_in_month` | `year`, `month` | Days in month |
| `datetime_week_number` | `date_string` | ISO week number |

### Validation (8 tools)

All return `{valid: bool, reason: string}`.

| Tool | Params | Description |
|------|--------|-------------|
| `validation_is_email` | `text` | Email format check |
| `validation_is_url` | `text` | URL format check |
| `validation_is_ipv4` | `text` | IPv4 address check |
| `validation_is_ipv6` | `text` | IPv6 address check |
| `validation_is_uuid` | `text` | UUID format check |
| `validation_is_json` | `text` | Valid JSON check |
| `validation_is_palindrome` | `text` | Palindrome check |
| `validation_matches_regex` | `text`, `pattern` | Regex match check |

### Conversion (8 tools)

| Tool | Params | Description |
|------|--------|-------------|
| `conversion_celsius_to_fahrenheit` | `value` | C to F |
| `conversion_fahrenheit_to_celsius` | `value` | F to C |
| `conversion_km_to_miles` | `value` | km to miles |
| `conversion_miles_to_km` | `value` | miles to km |
| `conversion_bytes_to_human` | `bytes` | Bytes to human string |
| `conversion_rgb_to_hex` | `r`, `g`, `b` | RGB to hex color |
| `conversion_hex_to_rgb` | `hex_color` | Hex to RGB |
| `conversion_decimal_to_binary` | `value` | Decimal to binary string |

### Echo / Protocol Testing (8 tools)

| Tool | Params | Description |
|------|--------|-------------|
| `echo` | `message` | Echo input unchanged |
| `echo_error` | `message` | Always raises ToolError |
| `echo_large` | `size_kb` | Deterministic ~N KB text |
| `echo_nested` | `depth` | Nested JSON to depth N |
| `echo_types` | — | All JSON types |
| `echo_empty` | — | Empty string |
| `echo_multiple` | `messages` | Multiple TextContent blocks |
| `echo_schema` | `str_param`, `int_param`, `float_param`, `bool_param`, `list_param`, `obj_param` | Complex schema test |

### Standalone

| Tool | Params | Description |
|------|--------|-------------|
| `get_weather` | `city` | Fixed response: 77°F, sunny, always |

## REST API

When running with `--transport sse`, all tools are also available as HTTP endpoints:

```bash
# GET endpoints (math, conversion, some echo, weather)
curl "http://localhost:3001/api/math/add?a=3&b=5"
# {"result": 8.0}

curl "http://localhost:3001/api/weather?city=NYC"
# {"city":"NYC","temperature_f":77,...}

# POST endpoints (string, collection, encoding, datetime, validation, some echo)
curl -X POST "http://localhost:3001/api/string/reverse" \
  -H "Content-Type: application/json" \
  -d '{"text":"hello"}'
# {"result": "olleh"}

curl -X POST "http://localhost:3001/api/encoding/sha256" \
  -H "Content-Type: application/json" \
  -d '{"text":"hello"}'
# {"result": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"}
```

**OpenAPI spec** at `GET /api-docs` (OpenAPI 3.0.3).

With auth enabled, include `Authorization: Bearer <key>` on all requests.

## Testing

```bash
python3 -m pytest tests/ -v
```

389 tests covering all tools, REST API endpoints, auth, OpenAPI spec, and integration.

## Project Structure

```
mcp-test-server/
├── pyproject.toml              # Package config, deps, CLI entry point
├── mcp_test_server/
│   ├── __init__.py             # Package version
│   ├── server.py               # Entry point — MCP server + REST API + auth
│   ├── api.py                  # REST API routes + OpenAPI spec generation
│   └── tools/
│       ├── __init__.py         # Tool group registry
│       ├── math_tools.py
│       ├── string_tools.py
│       ├── collection_tools.py
│       ├── encoding_tools.py
│       ├── datetime_tools.py
│       ├── validation_tools.py
│       ├── conversion_tools.py
│       └── echo_tools.py      # Includes get_weather
└── tests/
    ├── test_math_tools.py
    ├── test_string_tools.py
    ├── test_collection_tools.py
    ├── test_encoding_tools.py
    ├── test_datetime_tools.py
    ├── test_validation_tools.py
    ├── test_conversion_tools.py
    ├── test_echo_tools.py
    ├── test_api.py
    └── test_integration.py
```

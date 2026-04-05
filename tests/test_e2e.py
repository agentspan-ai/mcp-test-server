"""End-to-end tests that spin up a real server process and test over HTTP."""

import os
import signal
import socket
import subprocess
import sys
import time
import unittest

import requests

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE_URL = None
AUTH_BASE_URL = None
SERVER_PROC = None
AUTH_SERVER_PROC = None


def _free_port():
    """Find a free TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(url, timeout=15):
    """Poll until the server responds or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code in (200, 401):
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.3)
    raise RuntimeError(f"Server at {url} did not start within {timeout}s")


def _start_server(port, auth_key=None):
    """Start mcp-testkit as a subprocess."""
    cmd = [sys.executable, "-m", "mcp_test_server.server", "--transport", "http", "--port", str(port)]
    if auth_key:
        cmd += ["--auth", auth_key]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )
    return proc


def _stop_server(proc):
    """Stop a server subprocess."""
    if proc and proc.poll() is None:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)


# ---------------------------------------------------------------------------
# Module-level setup: start servers once for all tests
# ---------------------------------------------------------------------------


def setUpModule():
    global BASE_URL, AUTH_BASE_URL, SERVER_PROC, AUTH_SERVER_PROC

    port = _free_port()
    auth_port = _free_port()

    SERVER_PROC = _start_server(port)
    AUTH_SERVER_PROC = _start_server(auth_port, auth_key="e2e_test_key")

    BASE_URL = f"http://127.0.0.1:{port}"
    AUTH_BASE_URL = f"http://127.0.0.1:{auth_port}"

    _wait_for_server(f"{BASE_URL}/api-docs")
    _wait_for_server(f"{AUTH_BASE_URL}/api-docs")


def tearDownModule():
    _stop_server(SERVER_PROC)
    _stop_server(AUTH_SERVER_PROC)


# ---------------------------------------------------------------------------
# Tests — No Auth Server
# ---------------------------------------------------------------------------


class TestE2EOpenAPI(unittest.TestCase):
    """OpenAPI spec served correctly over real HTTP."""

    def test_api_docs_returns_valid_spec(self):
        r = requests.get(f"{BASE_URL}/api-docs")
        self.assertEqual(r.status_code, 200)
        spec = r.json()
        self.assertEqual(spec["openapi"], "3.0.3")
        self.assertEqual(len(spec["paths"]), 65)

    def test_api_docs_content_type(self):
        r = requests.get(f"{BASE_URL}/api-docs")
        self.assertIn("application/json", r.headers["content-type"])


class TestE2EMathGET(unittest.TestCase):
    """Math tool endpoints via real HTTP GET."""

    def test_add(self):
        r = requests.get(f"{BASE_URL}/api/math/add", params={"a": 3, "b": 5})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"result": 8.0})

    def test_subtract(self):
        r = requests.get(f"{BASE_URL}/api/math/subtract", params={"a": 10, "b": 3})
        self.assertEqual(r.json(), {"result": 7.0})

    def test_multiply(self):
        r = requests.get(f"{BASE_URL}/api/math/multiply", params={"a": 4, "b": 7})
        self.assertEqual(r.json(), {"result": 28.0})

    def test_divide(self):
        r = requests.get(f"{BASE_URL}/api/math/divide", params={"a": 15, "b": 3})
        self.assertEqual(r.json(), {"result": 5.0})

    def test_divide_by_zero(self):
        r = requests.get(f"{BASE_URL}/api/math/divide", params={"a": 10, "b": 0})
        self.assertIn("error", r.json())

    def test_modulo(self):
        r = requests.get(f"{BASE_URL}/api/math/modulo", params={"a": 17, "b": 5})
        self.assertEqual(r.json(), {"result": 2.0})

    def test_power(self):
        r = requests.get(f"{BASE_URL}/api/math/power", params={"base": 2, "exponent": 10})
        self.assertEqual(r.json(), {"result": 1024.0})

    def test_factorial(self):
        r = requests.get(f"{BASE_URL}/api/math/factorial", params={"n": 6})
        self.assertEqual(r.json(), {"result": 720})

    def test_fibonacci(self):
        r = requests.get(f"{BASE_URL}/api/math/fibonacci", params={"n": 10})
        self.assertEqual(r.json(), {"result": 55})


class TestE2EStringPOST(unittest.TestCase):
    """String tool endpoints via real HTTP POST."""

    def test_reverse(self):
        r = requests.post(f"{BASE_URL}/api/string/reverse", json={"text": "hello"})
        self.assertEqual(r.json(), {"result": "olleh"})

    def test_uppercase(self):
        r = requests.post(f"{BASE_URL}/api/string/uppercase", json={"text": "hello"})
        self.assertEqual(r.json(), {"result": "HELLO"})

    def test_lowercase(self):
        r = requests.post(f"{BASE_URL}/api/string/lowercase", json={"text": "HELLO"})
        self.assertEqual(r.json(), {"result": "hello"})

    def test_length(self):
        r = requests.post(f"{BASE_URL}/api/string/length", json={"text": "hello"})
        self.assertEqual(r.json(), {"result": 5})

    def test_char_count(self):
        r = requests.post(f"{BASE_URL}/api/string/char-count", json={"text": "banana", "char": "a"})
        self.assertEqual(r.json(), {"result": 3})

    def test_replace(self):
        r = requests.post(
            f"{BASE_URL}/api/string/replace", json={"text": "hello world", "old": "world", "new": "there"}
        )
        self.assertEqual(r.json(), {"result": "hello there"})

    def test_split(self):
        r = requests.post(f"{BASE_URL}/api/string/split", json={"text": "a,b,c", "delimiter": ","})
        self.assertEqual(r.json(), {"result": ["a", "b", "c"]})

    def test_join(self):
        r = requests.post(f"{BASE_URL}/api/string/join", json={"items": ["x", "y", "z"], "delimiter": "-"})
        self.assertEqual(r.json(), {"result": "x-y-z"})


class TestE2ECollectionPOST(unittest.TestCase):
    """Collection tool endpoints via real HTTP POST."""

    def test_sort(self):
        r = requests.post(f"{BASE_URL}/api/collection/sort", json={"items": [3, 1, 2]})
        self.assertEqual(r.json(), {"result": [1, 2, 3]})

    def test_sort_reverse(self):
        r = requests.post(f"{BASE_URL}/api/collection/sort", json={"items": [3, 1, 2], "reverse": True})
        self.assertEqual(r.json(), {"result": [3, 2, 1]})

    def test_flatten(self):
        r = requests.post(f"{BASE_URL}/api/collection/flatten", json={"items": [1, [2, [3, 4]], 5]})
        self.assertEqual(r.json(), {"result": [1, 2, 3, 4, 5]})

    def test_merge(self):
        r = requests.post(f"{BASE_URL}/api/collection/merge", json={"dict_a": {"a": 1}, "dict_b": {"b": 2}})
        self.assertEqual(r.json(), {"result": {"a": 1, "b": 2}})

    def test_filter_gt(self):
        r = requests.post(f"{BASE_URL}/api/collection/filter-gt", json={"items": [1, 5, 3, 8, 2], "threshold": 3})
        self.assertEqual(r.json(), {"result": [5, 8]})

    def test_unique(self):
        r = requests.post(f"{BASE_URL}/api/collection/unique", json={"items": [1, 2, 2, 3, 1]})
        self.assertEqual(r.json(), {"result": [1, 2, 3]})

    def test_zip(self):
        r = requests.post(f"{BASE_URL}/api/collection/zip", json={"list_a": [1, 2], "list_b": ["a", "b"]})
        self.assertEqual(r.json(), {"result": [[1, "a"], [2, "b"]]})

    def test_chunk(self):
        r = requests.post(f"{BASE_URL}/api/collection/chunk", json={"items": [1, 2, 3, 4, 5], "size": 2})
        self.assertEqual(r.json(), {"result": [[1, 2], [3, 4], [5]]})


class TestE2EEncodingPOST(unittest.TestCase):
    """Encoding tool endpoints via real HTTP POST."""

    def test_base64_roundtrip(self):
        r = requests.post(f"{BASE_URL}/api/encoding/base64-encode", json={"text": "hello world"})
        encoded = r.json()["result"]
        r2 = requests.post(f"{BASE_URL}/api/encoding/base64-decode", json={"data": encoded})
        self.assertEqual(r2.json(), {"result": "hello world"})

    def test_url_roundtrip(self):
        r = requests.post(f"{BASE_URL}/api/encoding/url-encode", json={"text": "hello world&foo=bar"})
        encoded = r.json()["result"]
        r2 = requests.post(f"{BASE_URL}/api/encoding/url-decode", json={"text": encoded})
        self.assertEqual(r2.json(), {"result": "hello world&foo=bar"})

    def test_hex_roundtrip(self):
        r = requests.post(f"{BASE_URL}/api/encoding/hex-encode", json={"text": "abc"})
        encoded = r.json()["result"]
        r2 = requests.post(f"{BASE_URL}/api/encoding/hex-decode", json={"data": encoded})
        self.assertEqual(r2.json(), {"result": "abc"})

    def test_md5(self):
        r = requests.post(f"{BASE_URL}/api/encoding/md5", json={"text": "hello"})
        self.assertEqual(r.json()["result"], "5d41402abc4b2a76b9719d911017c592")

    def test_sha256(self):
        r = requests.post(f"{BASE_URL}/api/encoding/sha256", json={"text": "hello"})
        self.assertEqual(r.json()["result"], "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")


class TestE2EDatetimePOST(unittest.TestCase):
    """DateTime tool endpoints via real HTTP POST."""

    def test_parse(self):
        r = requests.post(f"{BASE_URL}/api/datetime/parse", json={"date_string": "2024-03-15"})
        d = r.json()["result"]
        self.assertEqual(d["year"], 2024)
        self.assertEqual(d["month"], 3)
        self.assertEqual(d["day"], 15)

    def test_add_days(self):
        r = requests.post(f"{BASE_URL}/api/datetime/add-days", json={"date_string": "2024-03-15", "days": 10})
        self.assertEqual(r.json()["result"], "2024-03-25")

    def test_diff(self):
        r = requests.post(f"{BASE_URL}/api/datetime/diff", json={"date_a": "2024-03-15", "date_b": "2024-03-20"})
        self.assertEqual(r.json()["result"], -5)

    def test_day_of_week(self):
        r = requests.post(f"{BASE_URL}/api/datetime/day-of-week", json={"date_string": "2024-03-15"})
        self.assertEqual(r.json(), {"result": "Friday"})

    def test_is_leap_year(self):
        r = requests.post(f"{BASE_URL}/api/datetime/is-leap-year", json={"year": 2024})
        self.assertEqual(r.json(), {"result": True})

    def test_days_in_month(self):
        r = requests.post(f"{BASE_URL}/api/datetime/days-in-month", json={"year": 2024, "month": 2})
        self.assertEqual(r.json(), {"result": 29})


class TestE2EValidationPOST(unittest.TestCase):
    """Validation tool endpoints via real HTTP POST."""

    def test_is_email_valid(self):
        r = requests.post(f"{BASE_URL}/api/validation/is-email", json={"text": "user@example.com"})
        self.assertTrue(r.json()["valid"])

    def test_is_email_invalid(self):
        r = requests.post(f"{BASE_URL}/api/validation/is-email", json={"text": "not-an-email"})
        self.assertFalse(r.json()["valid"])

    def test_is_url_valid(self):
        r = requests.post(f"{BASE_URL}/api/validation/is-url", json={"text": "https://example.com"})
        self.assertTrue(r.json()["valid"])

    def test_is_ipv4_valid(self):
        r = requests.post(f"{BASE_URL}/api/validation/is-ipv4", json={"text": "192.168.1.1"})
        self.assertTrue(r.json()["valid"])

    def test_is_uuid_valid(self):
        r = requests.post(f"{BASE_URL}/api/validation/is-uuid", json={"text": "550e8400-e29b-41d4-a716-446655440000"})
        self.assertTrue(r.json()["valid"])

    def test_is_json_valid(self):
        r = requests.post(f"{BASE_URL}/api/validation/is-json", json={"text": '{"key": "val"}'})
        self.assertTrue(r.json()["valid"])

    def test_is_palindrome(self):
        r = requests.post(f"{BASE_URL}/api/validation/is-palindrome", json={"text": "racecar"})
        self.assertTrue(r.json()["valid"])

    def test_matches_regex(self):
        r = requests.post(
            f"{BASE_URL}/api/validation/matches-regex", json={"text": "abc123", "pattern": r"^[a-z]+\d+$"}
        )
        self.assertTrue(r.json()["valid"])


class TestE2EConversionGET(unittest.TestCase):
    """Conversion tool endpoints via real HTTP GET."""

    def test_celsius_to_fahrenheit(self):
        r = requests.get(f"{BASE_URL}/api/conversion/celsius-to-fahrenheit", params={"value": 100})
        self.assertEqual(r.json(), {"result": 212.0})

    def test_fahrenheit_to_celsius(self):
        r = requests.get(f"{BASE_URL}/api/conversion/fahrenheit-to-celsius", params={"value": 212})
        self.assertEqual(r.json(), {"result": 100.0})

    def test_km_to_miles(self):
        r = requests.get(f"{BASE_URL}/api/conversion/km-to-miles", params={"value": 10})
        self.assertAlmostEqual(r.json()["result"], 6.2137, places=3)

    def test_miles_to_km(self):
        r = requests.get(f"{BASE_URL}/api/conversion/miles-to-km", params={"value": 10})
        self.assertAlmostEqual(r.json()["result"], 16.0934, places=3)

    def test_bytes_to_human(self):
        r = requests.get(f"{BASE_URL}/api/conversion/bytes-to-human", params={"bytes": 1048576})
        self.assertEqual(r.json()["result"], "1.00 MB")

    def test_rgb_to_hex(self):
        r = requests.get(f"{BASE_URL}/api/conversion/rgb-to-hex", params={"r": 255, "g": 0, "b": 128})
        self.assertEqual(r.json(), {"result": "#ff0080"})

    def test_hex_to_rgb(self):
        r = requests.get(f"{BASE_URL}/api/conversion/hex-to-rgb", params={"hex_color": "#ff0080"})
        self.assertEqual(r.json(), {"result": {"r": 255, "g": 0, "b": 128}})

    def test_decimal_to_binary(self):
        r = requests.get(f"{BASE_URL}/api/conversion/decimal-to-binary", params={"value": 42})
        self.assertEqual(r.json(), {"result": "101010"})


class TestE2EEchoMixed(unittest.TestCase):
    """Echo tool endpoints via real HTTP."""

    def test_echo(self):
        r = requests.post(f"{BASE_URL}/api/echo", json={"message": "hello e2e"})
        self.assertEqual(r.json(), {"result": "hello e2e"})

    def test_echo_error(self):
        r = requests.post(f"{BASE_URL}/api/echo/error", json={"message": "boom"})
        self.assertIn("error", r.json())

    def test_echo_nested(self):
        r = requests.get(f"{BASE_URL}/api/echo/nested", params={"depth": 3})
        data = r.json()["result"]
        self.assertEqual(data["level"], 0)
        self.assertEqual(data["child"]["child"]["level"], 2)

    def test_echo_types(self):
        r = requests.get(f"{BASE_URL}/api/echo/types")
        data = r.json()
        self.assertIn("string", data)
        self.assertIn("integer", data)
        self.assertIn("boolean", data)
        self.assertIn("null", data)

    def test_echo_empty(self):
        r = requests.get(f"{BASE_URL}/api/echo/empty")
        self.assertEqual(r.json(), {"result": ""})

    def test_echo_multiple(self):
        r = requests.post(f"{BASE_URL}/api/echo/multiple", json={"messages": ["a", "b"]})
        self.assertEqual(r.json(), {"results": ["a", "b"]})

    def test_echo_schema(self):
        body = {
            "str_param": "test",
            "int_param": 99,
            "float_param": 1.5,
            "bool_param": False,
            "list_param": [1, 2, 3],
            "obj_param": {"nested": True},
        }
        r = requests.post(f"{BASE_URL}/api/echo/schema", json=body)
        self.assertEqual(r.json(), body)

    def test_echo_large(self):
        r = requests.post(f"{BASE_URL}/api/echo/large", json={"size_kb": 1})
        self.assertGreater(len(r.text), 500)


class TestE2EWeatherGET(unittest.TestCase):
    """Weather endpoint via real HTTP GET."""

    def test_weather(self):
        r = requests.get(f"{BASE_URL}/api/weather", params={"city": "San Francisco"})
        data = r.json()
        self.assertEqual(data["city"], "San Francisco")
        self.assertEqual(data["temperature_f"], 77)
        self.assertEqual(data["condition"], "sunny")

    def test_weather_different_cities_same_result(self):
        r1 = requests.get(f"{BASE_URL}/api/weather", params={"city": "NYC"})
        r2 = requests.get(f"{BASE_URL}/api/weather", params={"city": "London"})
        self.assertEqual(r1.json()["temperature_f"], r2.json()["temperature_f"])


class TestE2EDeterminism(unittest.TestCase):
    """Verify same request returns same response across calls."""

    def test_repeated_get_is_identical(self):
        for _ in range(3):
            r = requests.get(f"{BASE_URL}/api/math/fibonacci", params={"n": 15})
            self.assertEqual(r.json(), {"result": 610})

    def test_repeated_post_is_identical(self):
        body = {"text": "deterministic"}
        results = []
        for _ in range(3):
            r = requests.post(f"{BASE_URL}/api/encoding/sha256", json=body)
            results.append(r.json()["result"])
        self.assertTrue(all(r == results[0] for r in results), "SHA256 results differ across calls")


# ---------------------------------------------------------------------------
# Tests — Auth Server
# ---------------------------------------------------------------------------


class TestE2EAuth(unittest.TestCase):
    """Authentication behavior over real HTTP."""

    def test_no_token_returns_401(self):
        r = requests.get(f"{AUTH_BASE_URL}/api/math/add", params={"a": 1, "b": 2})
        self.assertEqual(r.status_code, 401)

    def test_wrong_token_returns_401(self):
        r = requests.get(
            f"{AUTH_BASE_URL}/api/math/add",
            params={"a": 1, "b": 2},
            headers={"Authorization": "Bearer wrong_key"},
        )
        self.assertEqual(r.status_code, 401)

    def test_correct_token_get(self):
        r = requests.get(
            f"{AUTH_BASE_URL}/api/math/add",
            params={"a": 1, "b": 2},
            headers={"Authorization": "Bearer e2e_test_key"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"result": 3.0})

    def test_correct_token_post(self):
        r = requests.post(
            f"{AUTH_BASE_URL}/api/string/reverse",
            json={"text": "auth"},
            headers={"Authorization": "Bearer e2e_test_key"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"result": "htua"})

    def test_api_docs_requires_auth(self):
        r = requests.get(f"{AUTH_BASE_URL}/api-docs")
        self.assertEqual(r.status_code, 401)

    def test_api_docs_with_auth(self):
        r = requests.get(
            f"{AUTH_BASE_URL}/api-docs",
            headers={"Authorization": "Bearer e2e_test_key"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["openapi"], "3.0.3")


class TestE2EAllEndpointsReachable(unittest.TestCase):
    """Verify every registered endpoint returns a non-500 response."""

    def test_all_65_endpoints_respond(self):
        from mcp_test_server.api import ENDPOINTS

        # Minimal valid payloads per type
        type_defaults = {
            "number": 1.0,
            "integer": 1,
            "string": "test",
            "boolean": True,
            "array": [1, 2],
            "object": {"key": "val"},
        }

        for path, method, _tool, _summary, params in ENDPOINTS:
            url = f"{BASE_URL}{path}"
            if method == "GET":
                query = {p[0]: type_defaults[p[1]] for p in params}
                r = requests.get(url, params=query)
            else:
                body = {p[0]: type_defaults[p[1]] for p in params}
                r = requests.post(url, json=body)
            self.assertLess(
                r.status_code,
                500,
                f"{method} {path} returned {r.status_code}: {r.text[:200]}",
            )


if __name__ == "__main__":
    unittest.main()

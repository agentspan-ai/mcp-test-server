"""Tests for datetime_tools module."""

import json
import asyncio

from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.datetime_tools import register
    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    # call_tool returns (content_list, metadata); extract text from first content item
    content_list = result[0] if isinstance(result, tuple) else result
    return json.loads(content_list[0].text)


# ---------- datetime_parse ----------

class TestDatetimeParse:
    def test_parse_date_only(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_parse", {"date_string": "2024-03-15"})
        assert result["result"] == {
            "year": 2024, "month": 3, "day": 15,
            "hour": 0, "minute": 0, "second": 0,
        }

    def test_parse_datetime(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_parse", {"date_string": "2024-03-15T14:30:45"})
        assert result["result"] == {
            "year": 2024, "month": 3, "day": 15,
            "hour": 14, "minute": 30, "second": 45,
        }

    def test_parse_invalid(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_parse", {"date_string": "not-a-date"})
        assert "error" in result

    def test_parse_midnight(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_parse", {"date_string": "2024-01-01T00:00:00"})
        assert result["result"]["hour"] == 0
        assert result["result"]["minute"] == 0
        assert result["result"]["second"] == 0


# ---------- datetime_format ----------

class TestDatetimeFormat:
    def test_format_iso(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_format", {
            "year": 2024, "month": 3, "day": 15, "format": "%Y-%m-%d"
        })
        assert result["result"] == "2024-03-15"

    def test_format_human_readable(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_format", {
            "year": 2024, "month": 3, "day": 15, "format": "%B %d, %Y"
        })
        assert result["result"] == "March 15, 2024"

    def test_format_custom(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_format", {
            "year": 2024, "month": 1, "day": 5, "format": "%d/%m/%Y"
        })
        assert result["result"] == "05/01/2024"

    def test_format_invalid_date(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_format", {
            "year": 2024, "month": 13, "day": 1, "format": "%Y-%m-%d"
        })
        assert "error" in result


# ---------- datetime_add_days ----------

class TestDatetimeAddDays:
    def test_add_days_basic(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_add_days", {
            "date_string": "2024-03-15", "days": 5
        })
        assert result["result"] == "2024-03-20"

    def test_add_days_leap_year(self):
        """2024-02-28 + 1 day = 2024-02-29 (leap year)."""
        mcp = _make_server()
        result = _call(mcp, "datetime_add_days", {
            "date_string": "2024-02-28", "days": 1
        })
        assert result["result"] == "2024-02-29"

    def test_add_days_non_leap_year(self):
        """2023-02-28 + 1 day = 2023-03-01 (not a leap year)."""
        mcp = _make_server()
        result = _call(mcp, "datetime_add_days", {
            "date_string": "2023-02-28", "days": 1
        })
        assert result["result"] == "2023-03-01"

    def test_add_negative_days(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_add_days", {
            "date_string": "2024-03-01", "days": -1
        })
        assert result["result"] == "2024-02-29"

    def test_add_days_cross_year(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_add_days", {
            "date_string": "2024-12-31", "days": 1
        })
        assert result["result"] == "2025-01-01"

    def test_add_zero_days(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_add_days", {
            "date_string": "2024-06-15", "days": 0
        })
        assert result["result"] == "2024-06-15"

    def test_add_days_invalid_date(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_add_days", {
            "date_string": "bad-date", "days": 1
        })
        assert "error" in result


# ---------- datetime_diff ----------

class TestDatetimeDiff:
    def test_diff_positive(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_diff", {
            "date_a": "2024-03-20", "date_b": "2024-03-15"
        })
        assert result["result"] == 5

    def test_diff_negative(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_diff", {
            "date_a": "2024-03-15", "date_b": "2024-03-20"
        })
        assert result["result"] == -5

    def test_diff_same_date(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_diff", {
            "date_a": "2024-03-15", "date_b": "2024-03-15"
        })
        assert result["result"] == 0

    def test_diff_cross_year(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_diff", {
            "date_a": "2025-01-01", "date_b": "2024-12-31"
        })
        assert result["result"] == 1

    def test_diff_invalid_date(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_diff", {
            "date_a": "2024-03-15", "date_b": "invalid"
        })
        assert "error" in result


# ---------- datetime_day_of_week ----------

class TestDatetimeDayOfWeek:
    def test_friday(self):
        """2024-03-15 is a Friday."""
        mcp = _make_server()
        result = _call(mcp, "datetime_day_of_week", {"date_string": "2024-03-15"})
        assert result["result"] == "Friday"

    def test_monday(self):
        """2024-03-11 is a Monday."""
        mcp = _make_server()
        result = _call(mcp, "datetime_day_of_week", {"date_string": "2024-03-11"})
        assert result["result"] == "Monday"

    def test_sunday(self):
        """2024-03-17 is a Sunday."""
        mcp = _make_server()
        result = _call(mcp, "datetime_day_of_week", {"date_string": "2024-03-17"})
        assert result["result"] == "Sunday"

    def test_new_years_day_2025(self):
        """2025-01-01 is a Wednesday."""
        mcp = _make_server()
        result = _call(mcp, "datetime_day_of_week", {"date_string": "2025-01-01"})
        assert result["result"] == "Wednesday"

    def test_invalid_date(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_day_of_week", {"date_string": "nope"})
        assert "error" in result


# ---------- datetime_is_leap_year ----------

class TestDatetimeIsLeapYear:
    def test_2024_is_leap(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_is_leap_year", {"year": 2024})
        assert result["result"] is True

    def test_2023_not_leap(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_is_leap_year", {"year": 2023})
        assert result["result"] is False

    def test_1900_not_leap(self):
        """1900 is divisible by 100 but not 400 — not a leap year."""
        mcp = _make_server()
        result = _call(mcp, "datetime_is_leap_year", {"year": 1900})
        assert result["result"] is False

    def test_2000_is_leap(self):
        """2000 is divisible by 400 — leap year."""
        mcp = _make_server()
        result = _call(mcp, "datetime_is_leap_year", {"year": 2000})
        assert result["result"] is True

    def test_2100_not_leap(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_is_leap_year", {"year": 2100})
        assert result["result"] is False


# ---------- datetime_days_in_month ----------

class TestDatetimeDaysInMonth:
    def test_feb_leap_year(self):
        """Feb 2024 has 29 days."""
        mcp = _make_server()
        result = _call(mcp, "datetime_days_in_month", {"year": 2024, "month": 2})
        assert result["result"] == 29

    def test_feb_non_leap_year(self):
        """Feb 2023 has 28 days."""
        mcp = _make_server()
        result = _call(mcp, "datetime_days_in_month", {"year": 2023, "month": 2})
        assert result["result"] == 28

    def test_january(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_days_in_month", {"year": 2024, "month": 1})
        assert result["result"] == 31

    def test_april(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_days_in_month", {"year": 2024, "month": 4})
        assert result["result"] == 30

    def test_december(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_days_in_month", {"year": 2024, "month": 12})
        assert result["result"] == 31

    def test_invalid_month(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_days_in_month", {"year": 2024, "month": 13})
        assert "error" in result

    def test_invalid_month_zero(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_days_in_month", {"year": 2024, "month": 0})
        assert "error" in result


# ---------- datetime_week_number ----------

class TestDatetimeWeekNumber:
    def test_first_week(self):
        """2024-01-01 is in ISO week 1."""
        mcp = _make_server()
        result = _call(mcp, "datetime_week_number", {"date_string": "2024-01-01"})
        assert result["result"] == 1

    def test_mid_year(self):
        """2024-06-15 is in ISO week 24."""
        mcp = _make_server()
        result = _call(mcp, "datetime_week_number", {"date_string": "2024-06-15"})
        assert result["result"] == 24

    def test_last_day_of_year(self):
        """2024-12-31 — ISO week 1 of 2025."""
        mcp = _make_server()
        result = _call(mcp, "datetime_week_number", {"date_string": "2024-12-31"})
        assert result["result"] == 1

    def test_known_week(self):
        """2024-03-15 is in ISO week 11."""
        mcp = _make_server()
        result = _call(mcp, "datetime_week_number", {"date_string": "2024-03-15"})
        assert result["result"] == 11

    def test_invalid_date(self):
        mcp = _make_server()
        result = _call(mcp, "datetime_week_number", {"date_string": "bad"})
        assert "error" in result

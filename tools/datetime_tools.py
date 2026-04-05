"""DateTime tools for MCP test server."""

import json
import calendar
from datetime import datetime, timedelta


def _parse_date(date_string: str) -> datetime:
    """Parse a date string supporting ISO formats with and without time."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date string: {date_string}")


def register(mcp):
    @mcp.tool()
    def datetime_parse(date_string: str) -> str:
        """Parse an ISO date string and return its components {year, month, day, hour, minute, second}."""
        try:
            dt = _parse_date(date_string)
            return json.dumps({"result": {
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": dt.hour,
                "minute": dt.minute,
                "second": dt.second,
            }})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_format(year: int, month: int, day: int, format: str) -> str:
        """Format a date to a string using a strftime format specifier."""
        try:
            dt = datetime(year, month, day)
            return json.dumps({"result": dt.strftime(format)})
        except (ValueError, TypeError) as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_add_days(date_string: str, days: int) -> str:
        """Add N days to a date and return the resulting ISO date string."""
        try:
            dt = _parse_date(date_string)
            result = dt + timedelta(days=days)
            return json.dumps({"result": result.strftime("%Y-%m-%d")})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_diff(date_a: str, date_b: str) -> str:
        """Return the number of days between two dates (a - b)."""
        try:
            dt_a = _parse_date(date_a)
            dt_b = _parse_date(date_b)
            delta = dt_a - dt_b
            return json.dumps({"result": delta.days})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_day_of_week(date_string: str) -> str:
        """Return the weekday name (e.g., 'Friday') for a given date."""
        try:
            dt = _parse_date(date_string)
            return json.dumps({"result": dt.strftime("%A")})
        except ValueError as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_is_leap_year(year: int) -> str:
        """Return whether the given year is a leap year."""
        return json.dumps({"result": calendar.isleap(year)})

    @mcp.tool()
    def datetime_days_in_month(year: int, month: int) -> str:
        """Return the number of days in the given month and year."""
        try:
            if month < 1 or month > 12:
                return json.dumps({"error": f"Invalid month: {month}"})
            _, days = calendar.monthrange(year, month)
            return json.dumps({"result": days})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def datetime_week_number(date_string: str) -> str:
        """Return the ISO week number for the given date."""
        try:
            dt = _parse_date(date_string)
            return json.dumps({"result": dt.isocalendar()[1]})
        except ValueError as e:
            return json.dumps({"error": str(e)})

"""Weather forecast tools for MCP test server.

API flow:
  1. zippopotam.us              — zip code → lat/lon
  2. api.weather.gov/points     — lat/lon → forecast grid URL
  3. api.weather.gov/gridpoints — forecast grid URL → forecast periods
"""
import json
import urllib.request
import urllib.error

USER_AGENT = "ZipCodeWeatherAgent/1.0 (your@email.com)"


def _get(url: str, accept: str = "application/json") -> tuple[int, str]:
    """Perform a GET request and return (status_code, body)."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": accept},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def register(mcp):
    @mcp.tool()
    def weather_convert_zip(zip_code: str) -> str:
        """Convert a US zip code to latitude, longitude, city, and state.

        Args:
            zip_code: A 5-digit US zip code, e.g. '10013'.

        Returns:
            JSON with 'lat', 'lon', 'city', and 'state', or an 'error' key on failure.
        """
        status, body = _get(f"https://api.zippopotam.us/us/{zip_code}")

        if status == 404:
            return json.dumps({"error": f"Zip code {zip_code} not found."})
        if status != 200:
            return json.dumps({"error": f"Geocoding failed with status {status}."})

        try:
            data = json.loads(body)
            place = data["places"][0]
            return json.dumps({
                "lat": place["latitude"],
                "lon": place["longitude"],
                "city": place["place name"],
                "state": place["state abbreviation"],
            })
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return json.dumps({"error": f"Failed to parse geocoding response: {e}"})

    @mcp.tool()
    def weather_get_grid(lat: str, lon: str) -> str:
        """Given a latitude and longitude, call the NWS /points API to retrieve
        the forecast grid URL for that location.

        Args:
            lat: Latitude as a string, e.g. '40.7128'.
            lon: Longitude as a string, e.g. '-74.0060'.

        Returns:
            JSON with 'forecast_url', 'forecast_hourly_url', 'city', and 'state',
            or an 'error' key on failure. Note: only US locations are supported.
        """
        status, body = _get(
            f"https://api.weather.gov/points/{lat},{lon}",
            accept="application/geo+json",
        )

        if status != 200:
            return json.dumps({
                "error": (
                    f"NWS /points call failed with status {status}. "
                    "This location may be outside NWS coverage (US only)."
                )
            })

        try:
            props = json.loads(body)["properties"]
            rel = props.get("relativeLocation", {}).get("properties", {})
            return json.dumps({
                "forecast_url": props["forecast"],
                "forecast_hourly_url": props["forecastHourly"],
                "city": rel.get("city", ""),
                "state": rel.get("state", ""),
            })
        except (KeyError, json.JSONDecodeError) as e:
            return json.dumps({"error": f"Failed to parse NWS grid response: {e}"})

    @mcp.tool()
    def weather_get_forecast(forecast_url: str) -> str:
        """Fetch the multi-day weather forecast from an NWS forecast URL.
        Returns a human-readable summary of the next 6 forecast periods (~3 days).

        Args:
            forecast_url: The NWS forecast URL returned by weather_get_grid,
                          e.g. 'https://api.weather.gov/gridpoints/OKX/33,37/forecast'.

        Returns:
            JSON with a 'forecast' list of period objects (name, temperature,
            temperature_unit, short_forecast, detailed_forecast), or an 'error' key.
        """
        status, body = _get(forecast_url, accept="application/geo+json")

        if status != 200:
            return json.dumps({"error": f"Forecast fetch failed with status {status}."})

        try:
            periods = json.loads(body)["properties"]["periods"]
        except (KeyError, json.JSONDecodeError) as e:
            return json.dumps({"error": f"Failed to parse forecast response: {e}"})

        results = []
        for period in periods[:6]:  # First 6 periods ≈ 3 days of day/night
            results.append({
                "name": period.get("name", ""),
                "temperature": period.get("temperature"),
                "temperature_unit": period.get("temperatureUnit", "F"),
                "short_forecast": period.get("shortForecast", ""),
                "detailed_forecast": period.get("detailedForecast", ""),
            })

        return json.dumps({"forecast": results})

    @mcp.tool()
    def weather_forecast_by_zip(zip_code: str) -> str:
        """End-to-end convenience tool: get the full weather forecast for a US zip code.

        Chains weather_convert_zip → weather_get_grid → weather_get_forecast
        in a single call.

        Args:
            zip_code: A 5-digit US zip code, e.g. '10013'.

        Returns:
            JSON with 'city', 'state', and a 'forecast' list of period objects,
            or an 'error' key if any step fails.
        """
        # Step 1: zip → lat/lon
        geo = json.loads(weather_convert_zip(zip_code))
        if "error" in geo:
            return json.dumps(geo)

        # Step 2: lat/lon → grid/forecast URL
        grid = json.loads(weather_get_grid(geo["lat"], geo["lon"]))
        if "error" in grid:
            return json.dumps(grid)

        # Step 3: forecast URL → periods
        forecast = json.loads(weather_get_forecast(grid["forecast_url"]))
        if "error" in forecast:
            return json.dumps(forecast)

        return json.dumps({
            "city": grid.get("city") or geo.get("city", ""),
            "state": grid.get("state") or geo.get("state", ""),
            "forecast": forecast["forecast"],
        })
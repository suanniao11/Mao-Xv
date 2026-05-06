"""LangChain tool for current weather and forecast lookups."""

import httpx
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.config import settings


class WeatherInput(BaseModel):
    location: str = Field(
        ...,
        description="City name or 'city,country_code' (e.g. 'Paris' or 'Paris,FR').",
    )


class ForecastInput(BaseModel):
    location: str = Field(
        ...,
        description="City name or 'city,country_code' (e.g. 'Tokyo' or 'Tokyo,JP').",
    )
    days: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of forecast days to return (1–5).",
    )


class WeatherTool(BaseTool):
    """Tool that fetches current weather conditions for a given location."""

    name: str = "weather_tool"
    description: str = (
        "Useful for finding the current weather conditions at a given city or location. "
        "Returns temperature, humidity, wind speed, and a short description."
    )
    args_schema: type[BaseModel] = WeatherInput

    def _run(self, location: str) -> str:
        """Fetch current weather using the OpenWeatherMap API."""
        if not settings.weather_api_key:
            return (
                "Weather API key is not configured. "
                "Set WEATHER_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.weather_api_base_url}/weather"
        params = {
            "q": location,
            "appid": settings.weather_api_key,
            "units": "metric",
        }

        try:
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return _format_current_weather(data)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return f"Location '{location}' not found. Please check the city name."
            return f"Weather API request failed: {exc}"
        except httpx.HTTPError as exc:
            return f"Weather API request failed: {exc}"

    async def _arun(self, location: str) -> str:
        """Async current weather fetch using the OpenWeatherMap API."""
        if not settings.weather_api_key:
            return (
                "Weather API key is not configured. "
                "Set WEATHER_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.weather_api_base_url}/weather"
        params = {
            "q": location,
            "appid": settings.weather_api_key,
            "units": "metric",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                return _format_current_weather(data)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    return f"Location '{location}' not found. Please check the city name."
                return f"Weather API request failed: {exc}"
            except httpx.HTTPError as exc:
                return f"Weather API request failed: {exc}"


class WeatherForecastTool(BaseTool):
    """Tool that fetches a multi-day weather forecast for a given location."""

    name: str = "weather_forecast_tool"
    description: str = (
        "Useful for getting a multi-day weather forecast (up to 5 days) for a city. "
        "Returns daily temperature ranges and conditions."
    )
    args_schema: type[BaseModel] = ForecastInput

    def _run(self, location: str, days: int = 3) -> str:
        """Fetch weather forecast using the OpenWeatherMap API."""
        if not settings.weather_api_key:
            return (
                "Weather API key is not configured. "
                "Set WEATHER_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.weather_api_base_url}/forecast"
        params = {
            "q": location,
            "appid": settings.weather_api_key,
            "units": "metric",
            "cnt": days * 8,  # API returns data in 3-hour intervals
        }

        try:
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return _format_forecast(data, days)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return f"Location '{location}' not found. Please check the city name."
            return f"Weather API request failed: {exc}"
        except httpx.HTTPError as exc:
            return f"Weather API request failed: {exc}"

    async def _arun(self, location: str, days: int = 3) -> str:
        """Async weather forecast fetch using the OpenWeatherMap API."""
        if not settings.weather_api_key:
            return (
                "Weather API key is not configured. "
                "Set WEATHER_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.weather_api_base_url}/forecast"
        params = {
            "q": location,
            "appid": settings.weather_api_key,
            "units": "metric",
            "cnt": days * 8,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                return _format_forecast(data, days)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    return f"Location '{location}' not found. Please check the city name."
                return f"Weather API request failed: {exc}"
            except httpx.HTTPError as exc:
                return f"Weather API request failed: {exc}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_current_weather(data: dict) -> str:
    city = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")
    temp = data.get("main", {}).get("temp", "N/A")
    feels_like = data.get("main", {}).get("feels_like", "N/A")
    humidity = data.get("main", {}).get("humidity", "N/A")
    wind_speed = data.get("wind", {}).get("speed", "N/A")
    description = data.get("weather", [{}])[0].get("description", "N/A")

    return (
        f"Current weather in {city}, {country}:\n"
        f"  Condition:  {description.capitalize()}\n"
        f"  Temperature: {temp}°C (feels like {feels_like}°C)\n"
        f"  Humidity:    {humidity}%\n"
        f"  Wind speed:  {wind_speed} m/s"
    )


def _format_forecast(data: dict, days: int) -> str:
    city_info = data.get("city", {})
    city = city_info.get("name", "Unknown")
    country = city_info.get("country", "")

    items = data.get("list", [])
    if not items:
        return "No forecast data available."

    # Group by date (first 3-hour slot of each date)
    seen_dates: dict[str, dict] = {}
    for item in items:
        date = item["dt_txt"].split(" ")[0]
        if date not in seen_dates:
            seen_dates[date] = item
        if len(seen_dates) >= days:
            break

    lines = [f"{days}-day forecast for {city}, {country}:"]
    for date, item in seen_dates.items():
        temp = item.get("main", {}).get("temp", "N/A")
        temp_min = item.get("main", {}).get("temp_min", "N/A")
        temp_max = item.get("main", {}).get("temp_max", "N/A")
        description = item.get("weather", [{}])[0].get("description", "N/A")
        lines.append(
            f"  {date}: {description.capitalize()}, "
            f"{temp_min}°C – {temp_max}°C (avg {temp}°C)"
        )

    return "\n".join(lines)

"""LangChain tool for Map / geocoding / directions lookups."""

import httpx
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.config import settings


class PlaceSearchInput(BaseModel):
    query: str = Field(..., description="The place or address to search for.")


class DirectionsInput(BaseModel):
    origin: str = Field(..., description="Starting location for directions.")
    destination: str = Field(..., description="Destination location for directions.")
    mode: str = Field(
        default="driving",
        description="Travel mode: driving, walking, bicycling, or transit.",
    )


class MapTool(BaseTool):
    """Tool that queries the Maps API for place information and directions."""

    name: str = "map_tool"
    description: str = (
        "Useful for finding information about places, addresses, landmarks, or "
        "getting directions between two locations. "
        "Input should describe the place to search or the route needed."
    )
    args_schema: type[BaseModel] = PlaceSearchInput

    def _run(self, query: str) -> str:
        """Search for a place using the Google Maps API."""
        if not settings.map_api_key:
            return (
                "Map API key is not configured. "
                "Set MAP_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.map_api_base_url}/place/textsearch/json"
        params = {"query": query, "key": settings.map_api_key}

        try:
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                return f"No places found for query: {query}"

            top = results[0]
            name = top.get("name", "Unknown")
            address = top.get("formatted_address", "Address not available")
            rating = top.get("rating", "N/A")
            return (
                f"Place: {name}\n"
                f"Address: {address}\n"
                f"Rating: {rating}\n"
                f"Additional results: {len(results) - 1} more found."
            )
        except httpx.HTTPError as exc:
            return f"Map API request failed: {exc}"

    async def _arun(self, query: str) -> str:
        """Async search for a place using the Google Maps API."""
        if not settings.map_api_key:
            return (
                "Map API key is not configured. "
                "Set MAP_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.map_api_base_url}/place/textsearch/json"
        params = {"query": query, "key": settings.map_api_key}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                if not results:
                    return f"No places found for query: {query}"

                top = results[0]
                name = top.get("name", "Unknown")
                address = top.get("formatted_address", "Address not available")
                rating = top.get("rating", "N/A")
                return (
                    f"Place: {name}\n"
                    f"Address: {address}\n"
                    f"Rating: {rating}\n"
                    f"Additional results: {len(results) - 1} more found."
                )
            except httpx.HTTPError as exc:
                return f"Map API request failed: {exc}"


class DirectionsTool(BaseTool):
    """Tool that retrieves driving/walking/transit directions between two locations."""

    name: str = "directions_tool"
    description: str = (
        "Useful for getting directions or travel time between two locations. "
        "Provide an origin and a destination. "
        "Optionally specify a travel mode: driving (default), walking, bicycling, or transit."
    )
    args_schema: type[BaseModel] = DirectionsInput

    def _run(self, origin: str, destination: str, mode: str = "driving") -> str:
        """Get directions using the Google Maps API."""
        if not settings.map_api_key:
            return (
                "Map API key is not configured. "
                "Set MAP_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.map_api_base_url}/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": settings.map_api_key,
        }

        try:
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            routes = data.get("routes", [])
            if not routes:
                return f"No route found from '{origin}' to '{destination}'."

            leg = routes[0]["legs"][0]
            distance = leg.get("distance", {}).get("text", "unknown distance")
            duration = leg.get("duration", {}).get("text", "unknown duration")
            start = leg.get("start_address", origin)
            end = leg.get("end_address", destination)

            return (
                f"Route ({mode}):\n"
                f"From: {start}\n"
                f"To:   {end}\n"
                f"Distance: {distance}\n"
                f"Duration: {duration}"
            )
        except httpx.HTTPError as exc:
            return f"Map API request failed: {exc}"

    async def _arun(self, origin: str, destination: str, mode: str = "driving") -> str:
        """Async directions lookup using the Google Maps API."""
        if not settings.map_api_key:
            return (
                "Map API key is not configured. "
                "Set MAP_API_KEY in your environment to enable this tool."
            )

        url = f"{settings.map_api_base_url}/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": settings.map_api_key,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                routes = data.get("routes", [])
                if not routes:
                    return f"No route found from '{origin}' to '{destination}'."

                leg = routes[0]["legs"][0]
                distance = leg.get("distance", {}).get("text", "unknown distance")
                duration = leg.get("duration", {}).get("text", "unknown duration")
                start = leg.get("start_address", origin)
                end = leg.get("end_address", destination)

                return (
                    f"Route ({mode}):\n"
                    f"From: {start}\n"
                    f"To:   {end}\n"
                    f"Distance: {distance}\n"
                    f"Duration: {duration}"
                )
            except httpx.HTTPError as exc:
                return f"Map API request failed: {exc}"

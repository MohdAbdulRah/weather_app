# app/services.py
import os
import requests
from typing import Tuple, Dict, Any
from urllib.parse import quote_plus

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY") or None

BASE_GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
REVERSE_GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/reverse"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"  # 5 day / 3 hour

OPEN_METEO_HIST_URL = "https://archive-api.open-meteo.com/v1/archive"

class OpenWeatherError(Exception):
    pass

def check_api_key():
    if not OPENWEATHER_KEY:
        raise OpenWeatherError("OPENWEATHER_API_KEY not set. Put it into .env and restart the server.")

def geocode_from_query(query: str, limit: int = 3) -> list:
    check_api_key()
    params = {"q": query, "limit": limit, "appid": OPENWEATHER_KEY}
    resp = requests.get(BASE_GEOCODE_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise OpenWeatherError(f"Geocoding failed: {resp.status_code} {resp.text}")
    return resp.json()

def geocode_from_latlon(lat: float, lon: float) -> list:
    check_api_key()
    params = {"lat": lat, "lon": lon, "limit": 1, "appid": OPENWEATHER_KEY}
    resp = requests.get(REVERSE_GEOCODE_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise OpenWeatherError(f"Reverse geocoding failed: {resp.status_code} {resp.text}")
    return resp.json()

def fetch_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    check_api_key()
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"}
    resp = requests.get(CURRENT_WEATHER_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise OpenWeatherError(f"Current weather failed: {resp.status_code} {resp.text}")
    return resp.json()

def fetch_5day_forecast(lat: float, lon: float) -> Dict[str, Any]:
    check_api_key()
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"}
    resp = requests.get(FORECAST_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise OpenWeatherError(f"Forecast fetch failed: {resp.status_code} {resp.text}")
    return resp.json()

def fetch_historical_temperatures(lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Uses Open-Meteo archive API to fetch daily temps between start_date and end_date.
    start_date & end_date must be YYYY-MM-DD.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean",
        "timezone": "UTC"
    }
    resp = requests.get(OPEN_METEO_HIST_URL, params=params, timeout=20)
    if resp.status_code != 200:
        raise OpenWeatherError(f"Open-Meteo failed: {resp.status_code} {resp.text}")
    return resp.json()

def parse_location_input(location_input: dict) -> Tuple[float, float, str]:
    query = location_input.get("query")
    lat = location_input.get("lat")
    lon = location_input.get("lon")

    if lat is not None and lon is not None:
        try:
            res = geocode_from_latlon(lat, lon)
            if isinstance(res, list) and res:
                first = res[0]
                parts = []
                if first.get("name"):
                    parts.append(first["name"])
                if first.get("state"):
                    parts.append(first["state"])
                if first.get("country"):
                    parts.append(first["country"])
                pretty = ", ".join(parts) if parts else f"{lat},{lon}"
                return lat, lon, pretty
        except OpenWeatherError:
            pass
        return lat, lon, f"{lat},{lon}"

    if query:
        q = query.strip()
        if "," in q:
            pieces = [p.strip() for p in q.split(",")]
            try:
                la = float(pieces[0]); lo = float(pieces[1])
                return parse_location_input({"lat": la, "lon": lo})
            except Exception:
                pass
        matches = geocode_from_query(q, limit=1)
        if not matches:
            raise OpenWeatherError(f"No geocoding matches found for query: {q}")
        m = matches[0]
        name = m.get("name", q)
        if m.get("state"):
            name = f"{name}, {m.get('state')}"
        if m.get("country"):
            name = f"{name}, {m.get('country')}"
        return float(m["lat"]), float(m["lon"]), name

    raise OpenWeatherError("Invalid location input. Provide query or lat+lon.")

# Helpers for UI links
def youtube_search_url_for_location(location_name: str) -> str:
    q = f"{location_name} travel vlog"
    return f"https://www.youtube.com/results?search_query={quote_plus(q)}"

def google_maps_embed_url(lat: float, lon: float, zoom: int = 16) -> str:
    # Adds a pinpoint marker at the exact lat/lon location
    return f"https://www.google.com/maps?q={lat},{lon}&ll={lat},{lon}&z={zoom}&output=embed"



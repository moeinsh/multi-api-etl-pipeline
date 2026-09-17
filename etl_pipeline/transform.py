"""Transform stage: pure functions, no I/O.

Raw API payloads go in, clean flat dicts come out. Missing values stay
None (never invented) so downstream can see exactly what failed.
"""

from datetime import datetime, timedelta, timezone

# WMO weather-code -> short human label (subset used by Open-Meteo current).
WEATHER_LABELS = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm + slight hail",
    99: "Thunderstorm + heavy hail",
}


def weather_label(code):
    """Human label for a WMO weather code; None stays None."""
    if code is None:
        return None
    return WEATHER_LABELS.get(int(code), f"Code {code}")


def _nested(item, *keys):
    """Safe nested dict lookup: returns None instead of raising."""
    for key in keys:
        if not isinstance(item, dict):
            return None
        item = item.get(key)
    return item


def normalize_country(wb_item, population, geo, capital, updated_at):
    """Join World Bank metadata + population + geocoding into one row."""
    return {
        "iso3": wb_item.get("id"),
        "country_name": wb_item.get("name"),
        "region": _nested(wb_item, "region", "value"),
        "income_level": _nested(wb_item, "incomeLevel", "value"),
        "capital": capital,
        "population_2024": population,           # None if the API had none
        "latitude": (geo or {}).get("latitude"),
        "longitude": (geo or {}).get("longitude"),
        "timezone": (geo or {}).get("timezone"),
        "updated_at": updated_at,
    }


def normalize_weather(location):
    """Flatten one Open-Meteo location block into a row dict."""
    current = location.get("current", {}) if isinstance(location, dict) else {}
    return {
        "observed_at_utc": current.get("time"),
        "temp_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "weather_label": weather_label(current.get("weather_code")),
        "utc_offset_seconds": (location or {}).get("utc_offset_seconds"),
    }


def local_time_str(observed_at_utc, utc_offset_seconds):
    """Local time at the capital, derived from Open-Meteo's utc_offset.

    Falls back to the raw UTC timestamp when the offset is unknown.
    """
    if not observed_at_utc:
        return None
    try:
        dt = datetime.fromisoformat(observed_at_utc).replace(tzinfo=timezone.utc)
        if utc_offset_seconds is None:
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        local = dt + timedelta(seconds=int(utc_offset_seconds))
        return local.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return observed_at_utc

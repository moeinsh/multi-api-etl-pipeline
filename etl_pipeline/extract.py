"""Extract stage: pull raw JSON from the four free, key-less API endpoints.

Every function returns plain Python data structures and raises
RuntimeError (via http.get_json) when a source is unreachable after
retries. The orchestrator in main.py decides per-source whether a
failure is fatal or degradable.
"""

import logging

import config
from etl_pipeline import http

log = logging.getLogger("etl.extract")


def fetch_world_bank_meta(session):
    """Country metadata for all capitals in ONE request (semicolon list)."""
    codes = ";".join(c["iso3"] for c in config.CAPITALS)
    url = config.WORLD_BANK_META_URL.format(codes=codes)
    payload = http.get_json(session, url, label="World Bank metadata")
    # payload = [paging_info, [country, ...]]
    items = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    log.info("World Bank metadata: %d countries", len(items))
    return items


def fetch_populations(session):
    """2024 total population per ISO3, one batched indicator request."""
    codes = ";".join(c["iso3"] for c in config.CAPITALS)
    url = config.WORLD_BANK_POP_URL.format(codes=codes)
    payload = http.get_json(session, url, label="World Bank population")
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    pops = {r["countryiso3code"]: r["value"] for r in rows if r.get("value")}
    log.info("World Bank population: %d values", len(pops))
    return pops


def fetch_geocoding(session, capital):
    """Coordinates + IANA timezone for one capital city."""
    params = {"name": capital, "count": 1, "language": "en", "format": "json"}
    payload = http.get_json(session, config.GEOCODING_URL, params=params,
                            label=f"geocoding({capital})")
    results = payload.get("results") or []
    if not results:
        raise RuntimeError(f"geocoding({capital}): no results")
    r = results[0]
    return {
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
        "timezone": r.get("timezone"),
        "country_code": r.get("country_code"),
    }


def fetch_forecast(session, coords):
    """Current weather for many coordinates in ONE request.

    coords: list of (latitude, longitude). Returns a list aligned with
    the input order: [{time, temperature_2m, ...}, ...].
    """
    lats = ",".join(f"{lat:.4f}" for lat, _ in coords)
    lons = ",".join(f"{lon:.4f}" for _, lon in coords)
    params = {
        "latitude": lats,
        "longitude": lons,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh",
        "timezone": "UTC",
    }
    payload = http.get_json(session, config.FORECAST_URL, params=params,
                            label="Open-Meteo forecast")
    locations = payload if isinstance(payload, list) else [payload]
    out = [
        {
            "current": loc.get("current", {}),
            "utc_offset_seconds": loc.get("utc_offset_seconds"),
        }
        for loc in locations
    ]
    log.info("Open-Meteo forecast: %d locations", len(out))
    return out


def fetch_fx_rates(session, currencies):
    """USD -> currency rates for the distinct currency list.

    Returns (rates_dict, fx_date). Raises RuntimeError on failure.
    """
    params = {"base": "USD", "symbols": ",".join(sorted(set(currencies)))}
    payload = http.get_json(session, config.FRANKFURTER_URL, params=params,
                            label="Frankfurter FX rates")
    rates = payload.get("rates", {})
    fx_date = payload.get("date")
    missing = sorted(set(currencies) - set(rates))
    if missing:
        log.warning("FX rates missing for: %s", ", ".join(missing))
    log.info("Frankfurter FX: %d rates (date %s)", len(rates), fx_date)
    return rates, fx_date

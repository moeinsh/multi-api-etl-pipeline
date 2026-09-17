"""Unit tests for the transform stage (pure functions, no network).

Run:  python tests/test_transform.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl_pipeline import transform


def test_weather_label_known():
    assert transform.weather_label(0) == "Clear sky"
    assert transform.weather_label(95) == "Thunderstorm"


def test_weather_label_unknown_and_none():
    assert transform.weather_label(12345) == "Code 12345"
    assert transform.weather_label(None) is None


def test_normalize_country_joins_sources():
    wb = {"id": "DEU", "name": "Germany",
          "region": {"value": "Europe & Central Asia"},
          "incomeLevel": {"value": "High income"}}
    geo = {"latitude": 52.52, "longitude": 13.41, "timezone": "Europe/Berlin"}
    row = transform.normalize_country(wb, 83516593, geo, "Berlin", "2026-01-01")
    assert row["iso3"] == "DEU"
    assert row["region"] == "Europe & Central Asia"
    assert row["population_2024"] == 83516593
    assert row["timezone"] == "Europe/Berlin"


def test_normalize_country_missing_everything_is_none_not_crash():
    row = transform.normalize_country({}, None, None, "Nowhere", "2026-01-01")
    assert row["iso3"] is None
    assert row["population_2024"] is None
    assert row["latitude"] is None


def test_normalize_weather_flattens():
    loc = {"current": {"time": "2026-09-17T10:00", "temperature_2m": 17.9,
                       "relative_humidity_2m": 62, "wind_speed_10m": 11.8,
                       "weather_code": 3},
           "utc_offset_seconds": 7200}
    row = transform.normalize_weather(loc)
    assert row["temp_c"] == 17.9
    assert row["weather_label"] == "Overcast"
    assert row["utc_offset_seconds"] == 7200


def test_local_time_str_uses_offset():
    s = transform.local_time_str("2026-09-17T10:00", 7200)
    assert s == "2026-09-17 12:00", s


def test_local_time_str_without_offset_falls_back_to_utc():
    s = transform.local_time_str("2026-09-17T10:00", None)
    assert s.endswith("UTC"), s
    assert transform.local_time_str(None, 7200) is None


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_")]
    for t in tests:
        t()
    print(f"OK — {len(tests)} transform tests passed")

"""Static configuration for the Multi-API ETL pipeline.

Everything the pipeline needs to know lives here: which APIs to call,
which capitals to cover, and polite-crawling / retry settings.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
DB_PATH = DATA_DIR / "pipeline.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

# ---------------------------------------------------------------------------
# Coverage: 12 world capitals across 6 continents.
#
# CURRENCY is static reference data (ISO 4217 codes for the World Bank
# country). It is kept here on purpose, in the open: none of the APIs used
# in this pipeline returns currency codes, so instead of hiding a mapping
# inside code it lives in config where anyone can see and audit it.
# ---------------------------------------------------------------------------
CAPITALS = [
    {"capital": "Berlin",      "iso3": "DEU", "currency": "EUR"},
    {"capital": "Paris",       "iso3": "FRA", "currency": "EUR"},
    {"capital": "London",      "iso3": "GBR", "currency": "GBP"},
    {"capital": "Tokyo",       "iso3": "JPN", "currency": "JPY"},
    {"capital": "Canberra",    "iso3": "AUS", "currency": "AUD"},
    {"capital": "Ottawa",      "iso3": "CAN", "currency": "CAD"},
    {"capital": "Mexico City", "iso3": "MEX", "currency": "MXN"},
    {"capital": "Brasilia",    "iso3": "BRA", "currency": "BRL"},
    {"capital": "New Delhi",   "iso3": "IND", "currency": "INR"},
    {"capital": "Stockholm",   "iso3": "SWE", "currency": "SEK"},
    {"capital": "Singapore",   "iso3": "SGP", "currency": "SGD"},
    {"capital": "Pretoria",    "iso3": "ZAF", "currency": "ZAR"},
]

# ---------------------------------------------------------------------------
# Sources — all free, no API key required.
#   1. World Bank API      — country metadata + 2024 population
#   2. Open-Meteo Geocoding — capital coordinates + IANA timezone
#   3. Open-Meteo Forecast  — current weather per capital
#   4. Frankfurter API      — USD -> local currency rates
# ---------------------------------------------------------------------------
WORLD_BANK_META_URL = (
    "https://api.worldbank.org/v2/country/{codes}?format=json&per_page=25"
)
WORLD_BANK_POP_URL = (
    "https://api.worldbank.org/v2/country/{codes}/indicator/SP.POP.TOTL"
    "?format=json&date=2024&per_page=25"
)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"

# ---------------------------------------------------------------------------
# HTTP behaviour
# ---------------------------------------------------------------------------
HTTP_TIMEOUT = 20          # seconds per request
MAX_RETRIES = 4           # total attempts per request
BACKOFF_FACTOR = 1.5      # exponential backoff base
REQUEST_DELAY = 0.4       # polite pause between calls (seconds)
USER_AGENT = "multi-api-etl-pipeline/1.0 (personal demo project)"

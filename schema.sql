-- SQLite schema for the Multi-API ETL pipeline.
-- Reruns are idempotent: countries are upserted by ISO3 code, and
-- weather/fx snapshots are keyed by (run_id, iso3) so re-running the
-- same day replaces rather than duplicates rows.

CREATE TABLE IF NOT EXISTS countries (
    iso3           TEXT PRIMARY KEY,
    country_name   TEXT NOT NULL,
    region         TEXT,
    income_level   TEXT,
    capital        TEXT NOT NULL,
    population_2024 INTEGER,
    latitude       REAL,
    longitude      REAL,
    timezone       TEXT,
    updated_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_observations (
    run_id          TEXT NOT NULL,
    iso3            TEXT NOT NULL,
    observed_at_utc TEXT,
    temp_c          REAL,
    humidity_pct    REAL,
    wind_kmh        REAL,
    weather_code    INTEGER,
    weather_label   TEXT,
    utc_offset_seconds INTEGER,
    PRIMARY KEY (run_id, iso3)
);

CREATE TABLE IF NOT EXISTS fx_rates (
    run_id          TEXT NOT NULL,
    iso3            TEXT NOT NULL,
    currency        TEXT NOT NULL,
    usd_to_currency REAL,
    fx_date         TEXT,
    PRIMARY KEY (run_id, iso3)
);

-- Denormalized reporting view used by the Excel export.
CREATE VIEW IF NOT EXISTS v_capital_report AS
SELECT
    c.capital,
    c.country_name,
    c.region,
    c.income_level,
    c.population_2024,
    c.latitude,
    c.longitude,
    c.timezone,
    w.observed_at_utc,
    w.temp_c,
    w.humidity_pct,
    w.wind_kmh,
    w.weather_code,
    w.weather_label,
    f.currency,
    f.usd_to_currency,
    f.fx_date,
    w.run_id
FROM countries c
LEFT JOIN weather_observations w
    ON w.iso3 = c.iso3
LEFT JOIN fx_rates f
    ON f.iso3 = c.iso3 AND f.run_id = w.run_id;

"""Orchestrator: extract -> transform -> load, with honest failure handling.

Failure policy:
  * World Bank metadata ......... FATAL (nothing to join against without it)
  * geocoding / forecast / FX ... DEGRADED (row keeps NULLs, warning logged)
A run is idempotent: re-running the same UTC day replaces that day's
weather/FX snapshots instead of duplicating them.
"""

import logging
import sys
from datetime import datetime, timezone

import config
from etl_pipeline import extract, http, load, transform
from etl_pipeline.logging_setup import setup_logging

log = logging.getLogger("etl")


def main():
    setup_logging()
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log.info("=== ETL run %s started ===", run_id)

    failures = []  # (capital, stage, error) — reported at the end
    session = http.make_session()

    # --- Extract: World Bank (fatal if it fails) ---------------------------
    try:
        meta_items = extract.fetch_world_bank_meta(session)
        populations = extract.fetch_populations(session)
    except RuntimeError as exc:
        log.critical("FATAL: %s — aborting run, nothing was loaded.", exc)
        return 1
    meta_by_iso3 = {m.get("id"): m for m in meta_items}

    # --- Extract: geocoding, one capital at a time (degradable) ------------
    geo_by_iso3 = {}
    for cap in config.CAPITALS:
        try:
            geo_by_iso3[cap["iso3"]] = extract.fetch_geocoding(
                session, cap["capital"])
            log.info("geocoded %-12s -> %s",
                     cap["capital"], geo_by_iso3[cap["iso3"]]["timezone"])
        except RuntimeError as exc:
            failures.append((cap["capital"], "geocoding", str(exc)))
            log.warning("%s: geocoding failed, continuing without coords",
                        cap["capital"])

    # --- Extract: weather, single batched request (degradable) -------------
    with_coords = [c for c in config.CAPITALS if c["iso3"] in geo_by_iso3
                   and geo_by_iso3[c["iso3"]].get("latitude") is not None]
    weather_by_iso3 = {}
    try:
        coords = [(geo_by_iso3[c["iso3"]]["latitude"],
                   geo_by_iso3[c["iso3"]]["longitude"]) for c in with_coords]
        locations = extract.fetch_forecast(session, coords)
        for cap, loc in zip(with_coords, locations):
            weather_by_iso3[cap["iso3"]] = loc
    except RuntimeError as exc:
        failures.append(("ALL", "forecast", str(exc)))
        log.warning("forecast failed for all capitals: %s", exc)

    # --- Extract: FX rates (degradable) ------------------------------------
    fx_rates, fx_date = {}, None
    try:
        fx_rates, fx_date = extract.fetch_fx_rates(
            session, [c["currency"] for c in config.CAPITALS])
    except RuntimeError as exc:
        failures.append(("ALL", "fx", str(exc)))
        log.warning("FX rates unavailable: %s", exc)

    # --- Transform ----------------------------------------------------------
    country_rows, weather_rows, fx_rows = [], [], []
    for cap in config.CAPITALS:
        iso3 = cap["iso3"]
        wb_item = meta_by_iso3.get(iso3, {})
        country_rows.append(transform.normalize_country(
            wb_item, populations.get(iso3),
            geo_by_iso3.get(iso3), cap["capital"], updated_at))
        if iso3 in weather_by_iso3:
            w = transform.normalize_weather(weather_by_iso3[iso3])
            w["iso3"] = iso3
            weather_rows.append(w)
        else:
            failures.append((cap["capital"], "weather", "no data"))
        rate = fx_rates.get(cap["currency"])
        fx_rows.append({"iso3": iso3, "currency": cap["currency"],
                        "usd_to_currency": rate, "fx_date": fx_date})
    log.info("transformed: %d countries, %d weather rows, %d fx rows",
             len(country_rows), len(weather_rows), len(fx_rows))

    # --- Load ---------------------------------------------------------------
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    conn = load.init_db()
    load.upsert_countries(conn, country_rows)
    load.replace_weather(conn, run_id, weather_rows)
    load.replace_fx(conn, run_id, fx_rows)
    conn.close()

    xlsx_path = config.DATA_DIR / f"capitals_dashboard_{run_id}.xlsx"
    n = load.export_excel(config.DB_PATH, xlsx_path, run_id)

    # --- Summary ------------------------------------------------------------
    log.info("=== ETL run %s finished: %d capitals in report ===", run_id, n)
    if failures:
        log.warning("degraded items (%d):", len(failures))
        for capital, stage, err in failures:
            log.warning("  - %s [%s]: %s", capital, stage, err)
    else:
        log.info("no failures — all sources returned data")
    return 0


if __name__ == "__main__":
    sys.exit(main())

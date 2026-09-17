# Multi-API ETL Data Pipeline

> **Personal demo / sample project** — built to demonstrate ETL and API-integration
> skills. Not a client project; there are no clients, reviews, or business
> results attached to it.

A real, runnable ETL pipeline in Python. Every run it:

1. **Extracts** live data from 4 free, key-less public API endpoints covering
   12 world capitals,
2. **Transforms** the JSON into clean, joined rows (missing values stay
   `NULL` — never invented),
3. **Loads** them into SQLite (`schema.sql`), then exports a formatted Excel
   report with openpyxl — styled headers, totals/averages, a temperature bar
   chart and a region-share pie chart.

## Sources (all free, no API key)

| # | Provider | Endpoint | What it gives |
|---|----------|----------|---------------|
| 1 | World Bank API | `/v2/country/{codes}` + `/indicator/SP.POP.TOTL` | Country name, region, income level, capital, 2024 population |
| 2 | Open-Meteo Geocoding | `/v1/search` | Capital coordinates + IANA timezone |
| 3 | Open-Meteo Forecast | `/v1/forecast` (batched multi-coordinate) | Current temp, humidity, wind, weather code |
| 4 | Frankfurter API | `/v1/latest?base=USD` | USD → local currency rates |

**API swap note (build-time, 2026-09-17):** the original plan used
restcountries.com, but its API now only returns a deprecation notice
(even the "v5" endpoint redirects to a legacy JSON saying the version is
deprecated), so it was replaced with the World Bank API. WorldTimeAPI was
also evaluated but returned empty responses, so local capital times are
derived from Open-Meteo's `utc_offset_seconds` instead — one less moving
part. Currency codes are not returned by any of these APIs, so the small
ISO-4217 mapping lives openly in `config.py` as documented static
reference data.

## The real run (2026-09-17)

The committed `data/` outputs and `docs/run-output.txt` are from a real
execution — nothing was faked:

- 12/12 capitals extracted, transformed and loaded; **zero failures**
- SQLite: 12 countries, 12 weather observations, 12 FX rates
  (idempotent — the run was executed twice and row counts stayed at 12)
- One transient `RemoteDisconnected` on the World Bank population call was
  absorbed by the retry logic (visible in the log)
- Sample rows: Berlin 17.9 °C Overcast · Brasilia 21.5 °C Clear sky ·
  Germany population 83,516,593 · USD→EUR 0.86678 (FX date 2026-09-16)

## Run it yourself

```bash
pip install -r requirements.txt
python tests/test_transform.py   # 7 unit tests, no network needed
python main.py                   # full pipeline, ~30 seconds
```

Outputs land in `data/`:
`pipeline.db`, `capitals_dashboard_YYYY-MM-DD.xlsx`; the console log can be
kept with `python main.py | tee docs/run-output.txt`.

## Reliability features

- Retries with exponential backoff on every request (urllib3 `Retry`)
- Polite crawling: real `User-Agent`, small delay between calls
- Structured logging to stdout
- Idempotent reruns — same UTC day replaces that day's snapshots
- Honest degradation: a failed source leaves `NULL`s + a warning in the log,
  never fabricated rows (fatal only if the World Bank metadata itself fails,
  since there is nothing to join against)

## Project layout

```
main.py                 orchestrator (extract -> transform -> load)
config.py               capitals, API URLs, retry/crawl settings
schema.sql              SQLite tables + reporting view
etl_pipeline/
  extract.py            one function per API endpoint
  transform.py          pure functions (unit-tested), no I/O
  load.py               SQLite upserts + openpyxl Excel export
  http.py               session with retries/backoff
  logging_setup.py
tests/test_transform.py 7 unit tests
data/                   pipeline.db + .xlsx from the real run
docs/run-output.txt     real console log of the 2026-09-17 run
cover.png               portfolio cover
site-listings.md        ready-to-paste metadata for freelance sites
```

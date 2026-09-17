# Site listings — Multi-API ETL Data Pipeline

Ready-to-paste metadata for the three freelance sites. The project is a
**personal demo / sample project** — no client names or results anywhere.

---

## Fiverr (portfolio project)

- **Title:** Multi-API ETL Pipeline: Live Data → SQLite → Excel Report
- **Industry:** Data Analytics
- **Project category:** Data Processing
- **Project duration:** 7–30 days
- **Price range:** $50–$100
- **Description (2–3 sentences):**
  Personal sample project: a Python ETL pipeline that pulls live data from
  four free public API endpoints (World Bank, Open-Meteo, Frankfurter),
  joins 12 world capitals' country facts, current weather and FX rates into
  a normalized SQLite database, and exports a styled Excel dashboard with
  totals, charts and a region summary. Source code:
  https://github.com/moeinsh/multi-api-etl-pipeline

---

## Upwork (portfolio item)

- **Title (≤70 chars):** Multi-API ETL Pipeline — Live Data to SQLite & Excel
- **Role:** Python Developer
- **Description (≤600 chars):**
  Sample project: an end-to-end ETL pipeline in Python. It extracts live
  data from four free key-less API endpoints (World Bank country data and
  population, Open-Meteo geocoding and current weather, Frankfurter FX
  rates), transforms the JSON into clean joined rows, and loads them into
  SQLite with a reporting view — then exports a formatted Excel dashboard
  (styled tables, totals/averages, temperature bar chart, region pie chart).
  Built with retries + backoff, structured logging and idempotent reruns;
  7 unit tests included. GitHub:
  https://github.com/moeinsh/multi-api-etl-pipeline
- **Skills (5):** Python, ETL, API Integration, SQLite, Microsoft Excel

---

## Freelancer.com (portfolio item)

- **Title (≤36 chars):** Multi-API ETL Data Pipeline
- **Description (≤2000 chars):**
  Personal sample project: a real, runnable ETL data pipeline in Python.

  Extract — live data from four free public API endpoints (no API keys):
  World Bank (country metadata + 2024 population), Open-Meteo geocoding
  (capital coordinates + timezone) and forecast (current temperature,
  humidity, wind, weather code), and Frankfurter (USD to local currency
  rates). Covers 12 world capitals.

  Transform — the JSON is normalized, cleaned and joined into one coherent
  dataset. Missing values stay NULL and are logged; nothing is fabricated.

  Load — into SQLite (normalized tables plus a reporting view, see
  schema.sql), then a formatted Excel report is generated with openpyxl:
  styled headers, filters, totals/averages row, a temperature-by-capital
  bar chart and a population-by-region pie chart.

  Engineering touches: retries with exponential backoff, polite crawling
  (User-Agent + delays), structured logging, idempotent daily reruns
  (re-running the same day replaces that day's snapshots), and 7 unit
  tests for the transform stage.

  The repository includes the real outputs of the 2026-09-17 run: the
  SQLite database, the generated .xlsx report and the full console log.

  Source code: https://github.com/moeinsh/multi-api-etl-pipeline
- **Tags:** python, etl, api, sqlite, excel, data-pipeline, automation

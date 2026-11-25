# Automated Weather ETL Pipeline (Medallion Architecture)

An end-to-end data engineering pipeline that extracts multi-city hourly weather forecasts from the Open-Meteo REST API, validates data quality, and transforms raw JSON payloads into analytics-ready SQL tables and Parquet files using **Python**, **Pandas**, and **DuckDB**.

## Architecture Overview

This pipeline follows the **Medallion Architecture** pattern to separate raw ingestion from cleaned and aggregated datasets:

1. **Extract (`Bronze Layer`):** Polls the Open-Meteo API for 5 global cities (Johannesburg, Cape Town, Durban, London, New York) using exponential backoff retries (`tenacity`) and stores immutable raw JSON responses in `data/bronze/`.
2. **Transform & Validate (`Silver Layer`):** Parses nested JSON arrays into typed tabular DataFrames (`pandas`), drops null temperature records, runs automated data quality assertions (`quality.py`), and persists structured records to both **DuckDB** (`silver_weather_hourly`) and **Parquet** (`data/silver/`).
3. **Load & Aggregate (`Gold Layer`):** Executes analytical SQL queries inside **DuckDB** to build `gold_daily_summary` (daily min/max/average temperatures, total precipitation) and `gold_latest_reading` (using `QUALIFY ROW_NUMBER()` window functions).
4. **Orchestration:** Automated daily execution via **GitHub Actions** (`.github/workflows/daily_etl.yml`).

## Project Structure

```text
weather-etl-pipeline/
├── .github/workflows/
│   └── daily_etl.yml        # Automated CI/CD scheduled pipeline run
├── config/
│   └── settings.py          # Directory paths, API endpoints, and target coordinates
├── sql/
│   └── create_tables.sql    # Database DDL definitions
├── src/
│   ├── extract.py           # API ingestion with retry/backoff error handling
│   ├── transform.py         # JSON-to-DataFrame parsing and type casting
│   ├── quality.py           # Schema, null, and range validation checks
│   ├── load.py              # DuckDB & Parquet persistence + Gold SQL aggregations
│   └── pipeline.py          # Main ETL orchestrator with file and stream logging
├── requirements.txt         # Project dependencies
└── .gitignore               # Excludes local databases, logs, and raw data files
```

## Tech Stack
* **Language:** Python 3.11+
* **Data Processing:** Pandas
* **Analytical Database & Storage:** DuckDB, Apache Parquet
* **Ingestion & Resilience:** Requests, Tenacity (retry/backoff)
* **Automation:** GitHub Actions

## Setup & Local Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd weather-etl-pipeline
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the pipeline:**
   ```bash
   python src/pipeline.py
   ```

import duckdb
import pandas as pd
from pathlib import Path
import logging

from config.settings import DB_PATH, SILVER_DIR, GOLD_DIR

logger = logging.getLogger(__name__)

def get_connection():
    return duckdb.connect(str(DB_PATH))

def load_to_silver(df: pd.DataFrame, location: str):
    """Load cleaned data into silver layer (DuckDB + parquet)."""
    table_name = "silver_weather_hourly"
    
    with get_connection() as conn:
        # Create table if not exists
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                location VARCHAR,
                timestamp TIMESTAMP,
                temperature_c DOUBLE,
                humidity_pct DOUBLE,
                precipitation_mm DOUBLE,
                wind_speed_kmh DOUBLE,
                extracted_at TIMESTAMP
            )
        """)
        
        # Insert data
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
        
    # Also save as parquet for easy inspection
    parquet_path = SILVER_DIR / f"{location.lower().replace(' ', '_')}_silver.parquet"
    df.to_parquet(parquet_path, index=False)
    logger.info(f"Loaded {len(df)} rows into silver for {location}")

def build_gold_layer():
    """Create analytics-ready gold tables."""
    with get_connection() as conn:
        # Daily summary per location
        conn.execute("""
            CREATE OR REPLACE TABLE gold_daily_summary AS
            SELECT
                location,
                CAST(timestamp AS DATE) AS date,
                ROUND(AVG(temperature_c), 2) AS avg_temp_c,
                ROUND(MIN(temperature_c), 2) AS min_temp_c,
                ROUND(MAX(temperature_c), 2) AS max_temp_c,
                ROUND(SUM(precipitation_mm), 2) AS total_precipitation_mm,
                ROUND(AVG(humidity_pct), 1) AS avg_humidity_pct,
                ROUND(AVG(wind_speed_kmh), 1) AS avg_wind_speed_kmh,
                COUNT(*) AS hours_recorded
            FROM silver_weather_hourly
            GROUP BY 1, 2
            ORDER BY 1, 2
        """)
        
        # Latest snapshot
        conn.execute("""
            CREATE OR REPLACE TABLE gold_latest_reading AS
            SELECT *
            FROM silver_weather_hourly
            QUALIFY ROW_NUMBER() OVER (PARTITION BY location ORDER BY timestamp DESC) = 1
        """)
        
    logger.info("Gold layer tables built successfully")
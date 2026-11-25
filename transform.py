import json
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def transform_bronze_to_silver(bronze_file: Path) -> pd.DataFrame:
    """Turn raw Open-Meteo JSON into a clean tabular format."""
    with open(bronze_file) as f:
        raw = json.load(f)
    
    location = raw.get("location_name", "unknown")
    extracted_at = raw.get("extracted_at")
    
    hourly = raw.get("hourly", {})
    times = hourly.get("time", [])
    
    df = pd.DataFrame({
        "location": location,
        "timestamp": times,
        "temperature_c": hourly.get("temperature_2m"),
        "humidity_pct": hourly.get("relative_humidity_2m"),
        "precipitation_mm": hourly.get("precipitation"),
        "wind_speed_kmh": hourly.get("wind_speed_10m"),
        "extracted_at": extracted_at
    })
    
    # Basic cleaning
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["extracted_at"] = pd.to_datetime(df["extracted_at"])
    
    # Remove rows with no temperature (rare but possible)
    df = df.dropna(subset=["temperature_c"])
    
    logger.info(f"Transformed {len(df)} rows for {location}")
    return df
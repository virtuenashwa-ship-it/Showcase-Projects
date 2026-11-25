import requests
import json
from datetime import datetime
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from config.settings import BRONZE_DIR, LOCATIONS, BASE_URL

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_weather(lat: float, lon: float, location_name: str) -> dict:
    """Fetch weather data from Open-Meteo with retries."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": "auto",
        "forecast_days": 3
    }
    
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    data["location_name"] = location_name
    data["extracted_at"] = datetime.utcnow().isoformat()
    return data

def extract_all_locations() -> list[Path]:
    """Extract weather for all configured locations and save raw JSON to bronze."""
    saved_files = []
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    for loc in LOCATIONS:
        try:
            logger.info(f"Extracting weather for {loc['name']}...")
            data = fetch_weather(loc["lat"], loc["lon"], loc["name"])
            
            filename = BRONZE_DIR / f"{loc['name'].lower().replace(' ', '_')}_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            
            saved_files.append(filename)
            logger.info(f"Saved raw data → {filename.name}")
            
        except Exception as e:
            logger.error(f"Failed to extract {loc['name']}: {e}")
            # Continue with other locations even if one fails
            
    return saved_files
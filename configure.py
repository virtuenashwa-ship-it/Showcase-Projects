from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
DB_PATH = DATA_DIR / "weather.duckdb"

# Create directories if they don't exist
for path in [BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Locations to pull weather for (you can add more)
LOCATIONS = [
    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473},
    {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241},
    {"name": "Durban", "lat": -29.8587, "lon": 31.0218},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
]

# Open-Meteo API (free, no key required)
BASE_URL = "https://api.open-meteo.com/v1/forecast"
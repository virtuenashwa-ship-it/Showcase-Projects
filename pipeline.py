import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.extract import extract_all_locations
from src.transform import transform_bronze_to_silver
from src.quality import run_quality_checks
from src.load import load_to_silver, build_gold_layer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log")
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("=== Starting Weather ETL Pipeline ===")
    
    # 1. Extract
    bronze_files = extract_all_locations()
    if not bronze_files:
        logger.error("No data extracted. Exiting.")
        return
    
    # 2. Transform + Quality + Load to Silver
    for file in bronze_files:
        try:
            df = transform_bronze_to_silver(file)
            location = df["location"].iloc[0]
            
            if run_quality_checks(df, location):
                load_to_silver(df, location)
            else:
                logger.warning(f"Skipping load for {location} due to quality failures")
                
        except Exception as e:
            logger.error(f"Failed processing {file.name}: {e}")
    
    # 3. Build Gold layer
    build_gold_layer()
    
    logger.info("=== Pipeline completed successfully ===")

if __name__ == "__main__":
    run_pipeline()
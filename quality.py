import pandas as pd
import logging

logger = logging.getLogger(__name__)

def run_quality_checks(df: pd.DataFrame, location: str) -> bool:
    """Simple but useful data quality checks."""
    checks_passed = True
    
    # 1. Not empty
    if df.empty:
        logger.error(f"[{location}] Quality Fail: Empty dataframe")
        return False
    
    # 2. Required columns present
    required = ["location", "timestamp", "temperature_c"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"[{location}] Quality Fail: Missing columns {missing}")
        checks_passed = False
    
    # 3. Temperature range sanity (-50°C to 60°C)
    if "temperature_c" in df.columns:
        invalid_temp = df[(df["temperature_c"] < -50) | (df["temperature_c"] > 60)]
        if not invalid_temp.empty:
            logger.warning(f"[{location}] Quality Warning: {len(invalid_temp)} unrealistic temperatures")
    
    # 4. No future timestamps way ahead (simple check)
    if "timestamp" in df.columns:
        future = df[df["timestamp"] > pd.Timestamp.utcnow() + pd.Timedelta(days=10)]
        if not future.empty:
            logger.warning(f"[{location}] Quality Warning: {len(future)} timestamps too far in future")
    
    if checks_passed:
        logger.info(f"[{location}] Quality checks passed ({len(df)} rows)")
    
    return checks_passed
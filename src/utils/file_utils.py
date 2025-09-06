"""
Shared file utilities for YMCA volunteer data processing
"""
import os
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def load_excel_data(file_path: str) -> Optional[pd.DataFrame]:
    """Load data from Excel file with error handling"""
    try:
        df = pd.read_excel(file_path)
        logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"❌ Error loading file: {e}")
        return None


def save_excel_data(df: pd.DataFrame, filename: str, output_dir: str = "data/processed") -> str:
    """Save DataFrame to Excel with consistent naming and directory structure"""
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate full file path
    filepath = os.path.join(output_dir, filename)
    
    # Save to Excel
    df.to_excel(filepath, index=False)
    logger.info(f"✅ Saved: {filepath} | rows: {len(df)}")
    
    return filepath


def find_latest_file(pattern: str, directory: str = ".") -> Optional[Path]:
    """Find the most recent file matching a pattern"""
    files = list(Path(directory).glob(pattern))
    if not files:
        return None
    
    return max(files, key=os.path.getctime)
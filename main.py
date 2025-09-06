#!/usr/bin/env python3
"""
YMCA Volunteer Data Processing Pipeline

This is the main entry point for the YMCA volunteer data processing system.
It orchestrates the three-step process:

1. Data Extraction (volunteer_history_extractor.py)
2. Data Preparation (data_preparation.py) 
3. Statistical Analysis (project_statistics.py)
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def main():
    """Main entry point for YMCA volunteer data processing"""
    logger.info("🏊‍♂️ YMCA Volunteer Data Processing Pipeline")
    logger.info("=" * 60)
    
    print("\nAvailable processing steps:")
    print("1. Extract volunteer data (src/extractors/volunteer_history_extractor.py)")
    print("2. Prepare data (src/processors/data_preparation.py)")
    print("3. Generate statistics (src/processors/project_statistics.py)")
    print("4. Create plots from XLSX files")
    print("5. Validate data quality (data_quality_validator_main.py)")
    print("6. Quick metrics summary (python tools/reporting/quick_metrics_summary.py)")
    print("7. Review generated Excel files in data/processed/")
    
    print("\nDirectory structure:")
    print("├── src/")
    print("│   ├── extractors/    # Data extraction scripts")
    print("│   ├── processors/    # Data processing and analysis")
    print("│   ├── tests/         # Validation and testing")
    print("│   └── utils/         # Shared utilities")
    print("├── data/")
    print("│   ├── raw/           # Raw extracted data")
    print("│   ├── processed/     # Processed and analyzed data")
    print("│   └── plots/         # Generated scatter plots")
    print("├── docs/              # Documentation")
    print("└── logs/              # Application logs")
    
    logger.info("Pipeline setup complete. Run individual scripts as needed.")


if __name__ == "__main__":
    main()
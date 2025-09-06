# YMCA Volunteer Data Processing System

This repository contains a comprehensive data processing pipeline for YMCA volunteer statistics and reporting.

## Directory Structure

```
├── src/
│   ├── extractors/           # Data extraction from external APIs
│   │   └── volunteer_history_extractor.py
│   ├── processors/           # Data cleaning and statistical analysis
│   │   ├── data_preparation.py
│   │   └── project_statistics.py
│   ├── tests/               # Validation and testing scripts
│   │   └── test_validation.py
│   └── utils/               # Shared utilities and configurations
│       ├── logging_config.py
│       └── file_utils.py
├── data/
│   ├── raw/                 # Raw extracted data files
│   └── processed/           # Cleaned and analyzed data
├── docs/                    # Documentation files
├── logs/                    # Application logs
├── main.py                  # Main entry point
└── requirements.txt         # Python dependencies
```

## Processing Pipeline

The system follows a three-step process:

### 1. Data Extraction
**Script:** `src/extractors/volunteer_history_extractor.py`
- Extracts volunteer data from VolunteerMatters API
- Handles pagination and error recovery
- Saves raw data to `data/raw/`

### 2. Data Preparation  
**Script:** `src/processors/data_preparation.py`
- Cleans raw data (removes 0-hour entries)
- Provides deduplication options
- Generates summary reports
- Saves processed data to `data/processed/`

### 3. Statistical Analysis
**Script:** `src/processors/project_statistics.py` 
- Creates pivot tables for hours, volunteers, and projects
- Applies manual adjustments for special programs
- Generates Excel reports for PowerPoint integration

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the main entry point:**
   ```bash
   python main.py
   ```

3. **Or run individual steps:**
   ```bash
   # Step 1: Extract data
   python src/extractors/volunteer_history_extractor.py
   
   # Step 2: Prepare data
   python src/processors/data_preparation.py
   
   # Step 3: Generate statistics
   python src/processors/project_statistics.py
   ```

## Configuration

- API credentials are configured in `src/extractors/volunteer_history_extractor.py`
- Logging configuration is centralized in `src/utils/logging_config.py`
- File handling utilities are in `src/utils/file_utils.py`

## Dependencies

- `pandas>=1.5.0` - Data manipulation and analysis
- `requests>=2.28.0` - HTTP requests for API calls  
- `openpyxl>=3.0.0` - Excel file handling

## Notes

- Each processing step can be run independently
- Log files are automatically created in the `logs/` directory
- Data files follow consistent naming conventions with timestamps
- The system handles various deduplication methods based on reporting needs
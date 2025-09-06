# Data Quality Validation Tool

## Overview

A comprehensive data quality validation tool that checks Excel files for common data quality issues and generates detailed quality reports. Built specifically for the YMCA Volunteer Data Processing Pipeline but designed to be reusable for any dataset.

## Features

### ✅ Data Quality Checks
- **Duplicate Record Detection**: Identifies complete duplicates and key-field duplicates
- **Missing Field Validation**: Checks for missing required fields and calculates completeness percentages
- **Date Validation**: Detects invalid date formats, future dates, and very old dates
- **Data Consistency**: Identifies formatting inconsistencies and unusual characters
- **Numeric Range Validation**: Flags negative values in inappropriate fields and statistical outliers
- **Text Quality Assessment**: Detects very short text values and encoding issues

### 📊 Quality Scoring System
- Assigns a quality score from 0-100 based on issue severity
- Provides quality ratings: Excellent (90+), Good (80-89), Fair (70-79), Poor (50-69), Very Poor (<50)
- Categorizes issues by severity: High, Medium, Low

### 📋 Comprehensive Reporting
- **Text Reports (.txt)**: Human-readable executive summaries with detailed findings and recommendations
- **Excel Reports (.xlsx)**: Multi-sheet workbooks with summary, issues, data profile, field analysis, and recommendations
- **JSON Reports (.json)**: Machine-readable format for programmatic access

## Files Created

### Core Modules
- `src/processors/data_quality_validator.py` - Main validation engine
- `src/processors/data_quality_reporter.py` - Report generation system
- `data_quality_validator_main.py` - Command-line interface
- `example_data_quality_validation.py` - Usage examples and demonstrations
- `test_data_quality_tool.py` - Mock test and feature demonstration

### Configuration
- `requirements.txt` - Updated with jsonschema dependency
- `main.py` - Updated to include data quality validation step

## Usage Examples

### Basic Usage
```bash
# Validate a specific file
python data_quality_validator_main.py data/raw/volunteers.xlsx

# Auto-detect latest file in data/raw/
python data_quality_validator_main.py --auto

# Get help
python data_quality_validator_main.py --help
```

### Advanced Usage
```bash
# Validate with required fields check
python data_quality_validator_main.py data/raw/volunteers.xlsx --required-fields name email date

# Validate all Excel files in directory
python data_quality_validator_main.py --directory data/raw/

# Custom output directory
python data_quality_validator_main.py data/raw/volunteers.xlsx --output reports/quality/
```

### Programmatic Usage
```python
from src.processors.data_quality_validator import DataQualityValidator
from src.processors.data_quality_reporter import DataQualityReporter

# Initialize validator
validator = DataQualityValidator(required_fields=['name', 'email', 'date'])

# Run validation
results = validator.validate_data(df, 'my_data.xlsx')

# Generate reports
reporter = DataQualityReporter()
txt_report = reporter.generate_comprehensive_report(results)
excel_report = reporter.generate_excel_report(results, df)
json_report = reporter.generate_json_report(results)
```

## Integration with YMCA Pipeline

The data quality validation tool is fully integrated into the existing YMCA Volunteer Data Processing Pipeline:

1. **Step 1**: Extract volunteer data
2. **Step 2**: Prepare data (existing)
3. **Step 3**: Generate statistics (existing)
4. **Step 4**: Create plots (existing)
5. **Step 5**: **Validate data quality** (NEW)
6. **Step 6**: Review generated files

## Sample Output

### Quality Score Example
```
🎯 VALIDATION SUMMARY
Quality Score: 87/100
Quality Rating: Good
Total Issues: 8

Issue Breakdown:
🔴 High Priority: 1
🟡 Medium Priority: 3  
🟢 Low Priority: 1
```

### Issue Detection Example
```
🔍 DETAILED FINDINGS
🟡 Found 15 complete duplicate rows
🔴 Field 'Hours' has 23 missing values (1.8%)
🟡 Field 'volunteerDate' has 7 invalid date formats
🟡 Field 'Hours' has 3 negative values
🟢 Field 'assignment' has 12 values with inconsistent formatting
```

## Dependencies

- pandas>=1.5.0
- numpy>=1.21.0
- openpyxl>=3.0.0
- jsonschema>=4.0.0

## Installation

1. Install dependencies: `pip install -r requirements.txt`
2. Run validation: `python data_quality_validator_main.py --auto`
3. Review reports in `data/processed/reports/`

## Benefits

- **Proactive Quality Assurance**: Catch data issues before analysis
- **Comprehensive Coverage**: Multiple validation strategies ensure thorough checking
- **Actionable Insights**: Specific recommendations for each issue type
- **Multiple Report Formats**: Choose the format that best fits your workflow
- **Integration Ready**: Seamlessly integrates with existing data pipelines
- **Extensible Design**: Easy to add new validation rules and report formats

## Next Steps

1. Test with real data from your Excel files
2. Customize required fields based on your data requirements
3. Integrate into regular data processing workflow
4. Set up automated quality monitoring
5. Train team on interpreting quality reports
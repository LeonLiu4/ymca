# CSV Export Feature for YMCA Volunteer Reports

## Overview

The YMCA Volunteer Data Processing Pipeline now supports CSV export for all Excel reports, making it easier to share data and create backups. This feature is available through a simple `--format csv` command-line flag.

## Usage

### Method 1: Using the Unified Reports Generator (Recommended)

```bash
# Generate all reports in CSV format
python generate_reports.py --format csv

# Generate specific report types in CSV format
python generate_reports.py --format csv --type statistics

# Generate reports in Excel format (default)
python generate_reports.py --format excel
```

### Method 2: Using Individual Report Scripts

```bash
# Generate volunteer statistics in CSV format
python src/processors/project_statistics.py --format csv

# Generate statistics with custom output directory
python src/processors/project_statistics.py --format csv --output-dir custom_output
```

## Output Files

When using `--format csv`, the system creates multiple CSV files instead of a single Excel file:

### Statistics Reports CSV Output
- `Y_Volunteer_2025_Hours_Statistics_TIMESTAMP.csv` - Project hours data
- `Y_Volunteer_2025_Volunteers_Statistics_TIMESTAMP.csv` - Volunteer participation data  
- `Y_Volunteer_2025_Projects_Statistics_TIMESTAMP.csv` - Project categories data
- `Y_Volunteer_2025_Summary_TIMESTAMP.csv` - Summary metrics
- `Y_Volunteer_2025_Manual_Adjustments_TIMESTAMP.csv` - Manual adjustments (if applicable)

### File Locations
- Default output directory: `data/processed/`
- Custom directory: Use `--output-dir` flag
- Files include timestamp for version control

## Advantages of CSV Format

### Data Sharing
- ✅ Easy to share via email or cloud storage
- ✅ Smaller file sizes compared to Excel
- ✅ Universal format readable by all spreadsheet applications

### Data Integration
- ✅ Import into Google Sheets, Excel, LibreOffice
- ✅ Use with automated data processing scripts
- ✅ Compatible with data analysis tools (R, Python, etc.)

### Backup & Archival
- ✅ Plain text format for long-term storage
- ✅ Version control friendly (Git, SVN)
- ✅ No proprietary format concerns

## Examples

### Basic Usage
```bash
# Generate CSV reports for data sharing
python generate_reports.py --format csv

# Output will create files like:
# data/processed/Y_Volunteer_2025_Hours_Statistics_20250906_213147.csv
# data/processed/Y_Volunteer_2025_Volunteers_Statistics_20250906_213147.csv
# data/processed/Y_Volunteer_2025_Projects_Statistics_20250906_213147.csv
```

### Advanced Usage
```bash
# Generate CSV reports in a custom directory
python generate_reports.py --format csv --output-dir backup/monthly_reports

# Generate verbose output for troubleshooting
python generate_reports.py --format csv --verbose
```

## Integration with Existing Workflow

The CSV export feature integrates seamlessly with your existing workflow:

1. **Existing Excel Workflow** (default behavior preserved)
   ```bash
   python generate_reports.py  # Creates Excel files as before
   ```

2. **New CSV Workflow** (for data sharing)
   ```bash
   python generate_reports.py --format csv  # Creates CSV files
   ```

3. **Both Formats** (generate both for different purposes)
   ```bash
   python generate_reports.py --format excel  # For presentations
   python generate_reports.py --format csv    # For data sharing
   ```

## Technical Details

### CSV Format Specifications
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Line Endings**: Platform appropriate
- **Headers**: First row contains column names
- **Quoting**: Automatic for fields containing commas or quotes

### File Naming Convention
- Pattern: `{ReportName}_{Timestamp}.csv`
- Timestamp format: `YYYYMMDD_HHMMSS`
- Special characters in names are replaced with underscores
- Each Excel sheet becomes a separate CSV file

## Troubleshooting

### Common Issues
1. **Permission Errors**: Ensure write access to output directory
2. **Missing Data**: Verify `Raw_Data_*.xlsx` files exist in `data/processed/`
3. **Import Problems**: Check CSV encoding (UTF-8) in your target application

### Getting Help
```bash
# View available options
python generate_reports.py --help
python src/processors/project_statistics.py --help
```

## Backward Compatibility

This feature maintains full backward compatibility:
- All existing scripts continue to work unchanged
- Excel format remains the default
- No breaking changes to existing functionality
- All command-line options preserved

## Next Steps

1. Test CSV export with your data
2. Share CSV files with stakeholders  
3. Set up automated backup using CSV format
4. Integrate with your preferred data analysis tools
# Quick Volunteer Metrics Summary CLI Tool

## Overview

The Quick Volunteer Metrics Summary CLI tool provides a fast, one-page text summary of key volunteer metrics without running the full processing pipeline. It reads from existing processed data files to extract essential information like total hours, volunteer count, and top branches.

## Usage

### Basic Commands

```bash
# Quick summary (fastest)
python quick_metrics_summary.py

# Using shell wrapper
./quick-summary

# Detailed summary with raw data analysis
python quick_metrics_summary.py --details

# Save to file
python quick_metrics_summary.py --output my_summary.txt

# Quiet mode (suppress logs)
python quick_metrics_summary.py --quiet
```

### Command-Line Options

- `--details`: Include detailed analysis from raw data (slower, requires pandas)
- `--output OUTPUT` or `-o OUTPUT`: Save output to file instead of console
- `--quiet` or `-q`: Suppress log output, show only summary
- `--help` or `-h`: Show help message

## Features

### Quick Mode (Default)
- Parses existing summary report for fastest results
- Shows key metrics: total hours, records, volunteers
- Displays top branches by hours and volunteers  
- Shows processing status
- Works without pandas dependency

### Detailed Mode
- Reads raw Excel data files for comprehensive analysis
- Provides more granular metrics
- Shows date ranges and activity breakdowns
- Requires pandas and other dependencies

## Sample Output

```
🏊‍♂️ YMCA VOLUNTEER METRICS - QUICK SUMMARY
=======================================================
Generated: 2025-09-06 21:30:00

📊 KEY METRICS (from latest processing)
---------------------------------------------
Total Volunteer Hours: 6,644.8
Total Activity Records: 990
Active Volunteers: 411

🏢 TOP BRANCHES BY HOURS:
  • R.C. Durr YMCA: 1,756.5 hours

👥 TOP BRANCHES BY VOLUNTEERS:
  • Camp Ernst: 77 volunteers

🔧 PROCESSING STATUS
---------------------------------------------
Statistics File: ✅ Available
Branch Breakdown: ✅ Available
Summary Report: ✅ Available

📋 NEXT STEPS
---------------------------------------------
• For detailed analysis, run: python main.py
• For branch breakdowns, check data/processed/ directory
• For charts and visualizations, run specific generators
```

## Dependencies

### Minimal Dependencies (Quick Mode)
- Python 3.6+
- Standard library only

### Full Dependencies (Detailed Mode)
- All packages in `requirements.txt`
- pandas, openpyxl for Excel file processing

## Integration

The tool is integrated into the main pipeline:
- Referenced in `main.py` as processing step 6
- Can be run independently without full pipeline setup
- Uses existing processed data files when available

## Performance

- **Quick mode**: ~1-2 seconds (reads text summary)
- **Detailed mode**: ~5-10 seconds (processes Excel files)
- Memory usage: Minimal in quick mode, moderate in detailed mode

## Error Handling

- Graceful fallback when dependencies missing
- Clear error messages for missing data files
- Continues operation with available data sources
- Logs warnings for troubleshooting

## Files Used

The tool reads from these data sources in order of preference:
1. `data/processed/YMCA_Volunteer_Summary_Report.txt` (fastest)
2. `data/processed/Raw_Data_*.xlsx` (detailed mode)
3. `data/processed/Y_Volunteer_*Statistics*.xlsx`
4. `data/processed/Y_Volunteer_*Branch_Breakdown*.xlsx`
# Reporting Tools

Advanced reporting and data export tools for the YMCA Volunteer Data Processing System.

## 📊 **Available Tools:**

### **Custom Date Range Reports**
- **File**: `generate_custom_date_range_reports.py`
- **Purpose**: Generate reports for any custom date range
- **Usage**: `python generate_custom_date_range_reports.py --start 2025-01-01 --end 2025-06-30`

### **Quick Metrics Summary**
- **File**: `quick_metrics_summary.py`
- **Purpose**: Command-line tool for quick data summaries
- **Usage**: `python quick_metrics_summary.py` or `./quick-summary`

### **Flexible Report Generator**
- **File**: `flexible_report_generator.py`
- **Purpose**: Advanced report generation with multiple formats
- **Usage**: `python flexible_report_generator.py`

### **General Report Generator**
- **File**: `generate_reports.py`
- **Purpose**: Generate standard reports
- **Usage**: `python generate_reports.py`

### **Date Range Processor**
- **File**: `date_range_processor.py`
- **Purpose**: Process data for specific date ranges
- **Usage**: `python date_range_processor.py`

### **Export Utilities**
- **File**: `export_utils.py`
- **Purpose**: Export data to various formats (CSV, Excel, JSON)
- **Usage**: Import as module in other scripts

### **Test Validation**
- **File**: `test_date_range_validation.py`
- **Purpose**: Test date range validation functionality
- **Usage**: `python test_date_range_validation.py`

## 🚀 **Quick Start:**

1. **Generate Custom Date Range Report:**
   ```bash
   python generate_custom_date_range_reports.py --start 2025-01-01 --end 2025-06-30
   ```

2. **Get Quick Summary:**
   ```bash
   python quick_metrics_summary.py
   ```

3. **Generate Flexible Reports:**
   ```bash
   python flexible_report_generator.py
   ```

## 📋 **Features:**

- **Custom Date Ranges**: Generate reports for any date period
- **Multiple Output Formats**: CSV, Excel, JSON, HTML
- **Quick Metrics**: Fast command-line data summaries
- **Flexible Configuration**: Customizable report parameters
- **Data Validation**: Built-in date range validation
- **Export Utilities**: Reusable export functions

## 📚 **Documentation:**

- `docs/FLEXIBLE_DATE_RANGE_REPORT_GENERATOR.md` - Detailed custom date range documentation
- `docs/QUICK_SUMMARY_CLI.md` - Quick metrics summary guide
- `docs/CSV_EXPORT_USAGE.md` - CSV export functionality

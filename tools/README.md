# YMCA Volunteer Data Processing Tools

This directory contains additional tools and utilities that extend the core volunteer data processing system.

## 📁 **Directory Structure:**

### **📊 `reporting/`**
Advanced reporting and data export tools:
- **Custom Date Range Reports**: Generate reports for any date range
- **Quick Metrics Summary**: Command-line tool for quick data summaries
- **Flexible Report Generator**: Advanced report generation with multiple formats
- **CSV Export Utilities**: Export data to CSV format

### **⏰ `scheduling/`**
Automated scheduling and pipeline management:
- **Schedule Manager**: Manage automated report generation
- **Pipeline Runner**: Execute the full data processing pipeline
- **Cron Scheduler**: Linux/Mac scheduling support
- **Windows Scheduler**: Windows task scheduling support

### **📈 `comparison/`**
Data comparison and analysis tools:
- **Monthly Volunteer Comparison**: Compare volunteer data across months
- **Example Comparison Scripts**: Sample comparison implementations
- **Comparison Results**: Output files from comparison analyses

### **🌐 `web_dashboard/`**
Web-based dashboard and interface:
- **Flask Web App**: Web interface for data visualization
- **Dashboard Templates**: HTML templates for the web interface
- **Web Dashboard Runner**: Script to launch the web dashboard

## 🚀 **Quick Start:**

### **Generate Custom Reports:**
```bash
cd tools/reporting
python generate_custom_date_range_reports.py
```

### **Run Scheduled Pipeline:**
```bash
cd tools/scheduling
python run_scheduled_pipeline.py
```

### **Compare Monthly Data:**
```bash
cd tools/comparison
python monthly_volunteer_comparison.py
```

### **Launch Web Dashboard:**
```bash
cd tools/web_dashboard
./run_web_dashboard.sh
```

## 📋 **Documentation:**

Each tool directory contains its own README with detailed usage instructions. See the main `docs/` directory for comprehensive documentation:

- `docs/CSV_EXPORT_USAGE.md` - CSV export functionality
- `docs/FLEXIBLE_DATE_RANGE_REPORT_GENERATOR.md` - Custom date range reports
- `docs/QUICK_SUMMARY_CLI.md` - Quick metrics summary tool
- `docs/SCHEDULER_README.md` - Scheduling and automation
- `docs/WEB_DASHBOARD_README.md` - Web dashboard interface

## 🎯 **Features:**

- **Flexible Date Ranges**: Generate reports for any custom date period
- **Automated Scheduling**: Set up automated report generation
- **Data Comparison**: Compare volunteer data across different time periods
- **Web Interface**: Browser-based dashboard for data visualization
- **Multiple Export Formats**: CSV, Excel, JSON, HTML outputs
- **Quick Metrics**: Command-line tool for fast data summaries

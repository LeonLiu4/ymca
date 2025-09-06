# YMCA Volunteer Data Processing System

This repository contains a comprehensive data processing pipeline for YMCA volunteer statistics and reporting, designed to generate data for the **Y Monthly Statistics Report 8.31.2025** PowerPoint presentation.

## 📁 **File-to-Page Mapping:**

### **📥 Step 1: Data Extraction**
- **File**: `src/extractors/volunteer_history_extractor.py`
- **Output**: `data/raw/VolunteerHistory_YYYYMMDD_HHMMSS.xlsx`
- **Purpose**: Downloads volunteer data from VolunteerMatters API (Jan 1, 2025 to current date)

### **🧹 Step 2: Data Preparation**
- **File**: `src/processors/data_preparation.py`
- **Output**: `data/processed/Raw_Data_YYYYMMDD_HHMMSS.xlsx`
- **Purpose**: Removes 0-hour entries, saves clean "Raw Data" for all subsequent analysis

### **📊 Step 3: Page 1 - Project Category Statistics**
- **File**: `src/processors/project_statistics.py`
- **Output**: `data/processed/Y_Volunteer_2025_Statistics_YYYYMMDD_HHMMSS.xlsx`
- **Purpose**: 
  - Hours by PROJECT TAG (no deduplication)
  - Volunteers by PROJECT CATALOG (deduplicated by ASSIGNEE, PROJECT CATALOG, BRANCH)
  - Projects by PROJECT TAG vs PROJECT (with manual adjustments for Competitive Swim/Gymnastics)

### **📊 Pages 2-5: Branch/Site Breakdown**
- **File**: `src/processors/branch_breakdown.py`
- **Output**: `data/processed/Y_Volunteer_2025_Branch_Breakdown_YYYYMMDD_HHMMSS.xlsx`
- **Purpose**:
  - Branch Hours (no deduplication)
  - Active Volunteers (deduplicated by ASSIGNEE, BRANCH)
  - Member Volunteers (filtered by "Yes" for YMCA membership)

### **📊 Page 6: Youth Development & Education**
- **File**: `src/processors/yde_breakdown.py`
- **Output**: `data/processed/Y_Volunteer_2025_YDE_Breakdown_YYYYMMDD_HHMMSS.xlsx`
- **Purpose**:
  - YDE - Community Services (includes Music Resource Center)
  - YDE - Early Learning Centers
  - YDE - Out of School Time
  - Hours, Volunteers, and Project numbers for each category

### **📊 Page 7: YMCA & Senior Centers**
- **File**: `src/processors/senior_centers_breakdown.py`
- **Output**: `data/processed/Y_Volunteer_2025_Senior_Centers_YYYYMMDD_HHMMSS.xlsx`
- **Purpose**:
  - Clippard YMCA + Clippard Senior Center
  - R.C. Durr YMCA + Kentucky Senior Center
  - Combined data for ease of reading

### **📋 Consolidated Summary Report**
- **File**: `data/processed/YMCA_Volunteer_Summary_Report.txt`
- **Purpose**: Single comprehensive report containing summaries from all processing steps

## Directory Structure

```
├── src/
│   ├── extractors/           # Data extraction from external APIs
│   │   └── volunteer_history_extractor.py
│   ├── processors/           # Data cleaning and statistical analysis
│   │   ├── data_preparation.py
│   │   ├── project_statistics.py
│   │   ├── branch_breakdown.py
│   │   ├── yde_breakdown.py
│   │   └── senior_centers_breakdown.py
│   └── utils/               # Shared utilities and configurations
│       ├── logging_config.py
│       └── file_utils.py
├── data/
│   ├── raw/                 # Raw extracted data files
│   └── processed/           # Cleaned and analyzed data
├── docs/                    # Documentation files
│   ├── README.md            # Main documentation
│   ├── BAR_CHART_USAGE.md   # Bar chart usage guide
│   ├── LINE_GRAPH_README.md # Line graph documentation
│   ├── PIE_CHARTS_README.md # Pie chart documentation
│   ├── data_quality_dashboard.html # Data quality dashboard
│   └── frontend/            # Frontend guidelines
├── visualization_tools/     # Data visualization tools
│   ├── README.md            # Visualization tools documentation
│   ├── generate_*.py        # Chart generation scripts
│   ├── create_*.py          # Chart creation scripts
│   ├── visualizations/      # Visualization modules
│   ├── visualizers/         # Visualizer modules
│   ├── charts/              # Generated chart outputs
│   └── final_charts/        # Final processed charts
├── tools/                   # Additional tools and utilities
│   ├── README.md            # Tools overview documentation
│   ├── reporting/           # Advanced reporting tools
│   ├── scheduling/          # Automated scheduling tools
│   ├── comparison/          # Data comparison tools
│   └── web_dashboard/       # Web-based dashboard
├── logs/                    # Application logs
├── main.py                  # Main entry point
└── requirements.txt         # Python dependencies
```

## 🚀 **Execution Order:**

1. **Run Data Extraction**: `python src/extractors/volunteer_history_extractor.py`
2. **Run Data Preparation**: `python src/processors/data_preparation.py`
3. **Run Project Statistics**: `python src/processors/project_statistics.py`
4. **Run Branch Breakdown**: `python src/processors/branch_breakdown.py`
5. **Run YDE Breakdown**: `python src/processors/yde_breakdown.py`
6. **Run Senior Centers**: `python src/processors/senior_centers_breakdown.py`

## 📊 **Data Visualization Tools:**

The system includes comprehensive visualization tools located in the `visualization_tools/` directory:

### **Available Chart Types:**
- **Bar Charts**: `python visualization_tools/generate_bar_charts.py`
- **Line Graphs**: `python visualization_tools/generate_line_graphs.py`
- **Pie Charts**: `python visualization_tools/create_pie_charts.py`
- **Scatter Plots**: `python visualization_tools/create_scatter_plots.py`
- **Histograms**: `python visualization_tools/generate_histograms.py`

### **Features:**
- Automatic data detection from Excel files
- Professional styling with seaborn
- Multiple output formats (PNG, HTML, JSON)
- Flexible time period aggregation
- Trend line overlays

### **Documentation:**
- `visualization_tools/README.md` - Complete visualization tools guide
- `docs/BAR_CHART_USAGE.md` - Bar chart usage instructions
- `docs/LINE_GRAPH_README.md` - Line graph documentation
- `docs/PIE_CHARTS_README.md` - Pie chart documentation

## 🛠 **Additional Tools:**

The system includes comprehensive additional tools located in the `tools/` directory:

### **📊 Reporting Tools:**
- **Custom Date Range Reports**: `python tools/reporting/generate_custom_date_range_reports.py`
- **Quick Metrics Summary**: `python tools/reporting/quick_metrics_summary.py`
- **Flexible Report Generator**: `python tools/reporting/flexible_report_generator.py`

### **⏰ Scheduling Tools:**
- **Schedule Manager**: `python tools/scheduling/schedule_manager.py`
- **Pipeline Runner**: `python tools/scheduling/run_scheduled_pipeline.py`
- **Automated Scheduling**: Cross-platform scheduling support

### **📈 Comparison Tools:**
- **Monthly Comparison**: `python tools/comparison/monthly_volunteer_comparison.py`
- **Data Analysis**: Compare volunteer data across time periods
- **Trend Analysis**: Identify patterns and growth trends

### **🌐 Web Dashboard:**
- **Web Interface**: `./tools/web_dashboard/run_web_dashboard.sh`
- **Browser Access**: View data and reports in web browser
- **Interactive Dashboard**: Real-time data visualization

### **Documentation:**
- `tools/README.md` - Complete tools overview
- `docs/CSV_EXPORT_USAGE.md` - CSV export functionality
- `docs/FLEXIBLE_DATE_RANGE_REPORT_GENERATOR.md` - Custom date range reports
- `docs/QUICK_SUMMARY_CLI.md` - Quick metrics summary
- `docs/SCHEDULER_README.md` - Scheduling and automation
- `docs/WEB_DASHBOARD_README.md` - Web dashboard interface

## 📊 **PowerPoint Integration:**
All Excel files are formatted for direct import into your **Y Monthly Statistics Report 8.31.2025** presentation, with each page having its own dedicated Excel file containing the specific pivot tables and summaries you need.

The system automatically handles:
- ✅ Date filtering (Jan 1, 2025 to current)
- ✅ 0-hour entry removal
- ✅ Proper deduplication strategies
- ✅ Manual adjustments for Competitive Swim/Gymnastics
- ✅ Music Resource Center inclusion in YDE - Community Services
- ✅ Senior Center combinations
- ✅ Monthly data validation preparation

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
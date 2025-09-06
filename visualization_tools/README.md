# Visualization Tools

This directory contains all the data visualization tools and utilities for the YMCA Volunteer Data Processing System.

## 📊 **Chart Generators**

### **Bar Charts**
- `generate_bar_charts.py` - Main bar chart generator
- `visualizations/bar_chart_generator.py` - Core bar chart functionality

### **Line Graphs**
- `generate_line_graphs.py` - Main line graph generator
- `visualizers/line_graph_generator.py` - Core line graph functionality
- `visualizers/simple_line_graph_generator.py` - Simplified line graph generator
- `run_line_graph_generator.sh` - Shell script for line graph generation
- `line_graph_requirements.txt` - Dependencies for line graphs

### **Pie Charts**
- `create_pie_charts.py` - Main pie chart creator
- `simple_pie_charts.py` - Simplified pie chart generator
- `xlsx_to_pie_charts.py` - Excel to pie chart converter
- `generate_pie_chart_reports.py` - Pie chart report generator

### **Scatter Plots**
- `create_scatter_plots.py` - Main scatter plot creator
- `generate_scatterplot_reports.py` - Scatter plot report generator
- `scatter_plot_generator.py` - Core scatter plot functionality

### **Histograms**
- `generate_histograms.py` - Main histogram generator
- `histogram_generator.py` - Core histogram functionality

## 📈 **Report Generators**

- `line_graph_report_generator.py` - Line graph report generation
- `pie_chart_report_generator.py` - Pie chart report generation
- `scatterplot_report_generator.py` - Scatter plot report generation
- `histogram_report.py` - Histogram report generation
- `report_generator.py` - General report generation
- `simple_line_graph_report.py` - Simple line graph reports

## 🔧 **Utilities**

- `basic_xlsx_analyzer.py` - Excel file analysis utility
- `example_usage.py` - Example usage demonstrations
- `test_histogram_generator.py` - Histogram generator tests
- `test_pie_chart_reports.py` - Pie chart report tests

## 📁 **Output Directories**

- `charts/` - Generated chart files
- `final_charts/` - Final processed chart outputs

## 🚀 **Quick Start**

1. **Generate Bar Charts:**
   ```bash
   python generate_bar_charts.py
   ```

2. **Create Line Graphs:**
   ```bash
   python generate_line_graphs.py
   ```

3. **Make Pie Charts:**
   ```bash
   python create_pie_charts.py
   ```

4. **Generate Scatter Plots:**
   ```bash
   python create_scatter_plots.py
   ```

5. **Create Histograms:**
   ```bash
   python generate_histograms.py
   ```

## 📋 **Documentation**

For detailed usage instructions, see the documentation files in the `docs/` directory:
- `docs/BAR_CHART_USAGE.md`
- `docs/LINE_GRAPH_README.md`
- `docs/PIE_CHARTS_README.md`

## 🎯 **Features**

- **Automatic Data Detection**: Finds date and numeric columns automatically
- **Multiple Graph Types**: Bar charts, line graphs, pie charts, scatter plots, histograms
- **Professional Styling**: Uses seaborn styling for publication-ready graphs
- **Flexible Time Periods**: Supports daily, weekly, monthly, quarterly, and yearly aggregation
- **Trend Lines**: Optional trend line overlay for pattern analysis
- **Multiple Output Formats**: JSON, PNG, HTML, Excel

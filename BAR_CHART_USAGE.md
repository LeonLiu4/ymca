# Bar Chart Generator for XLSX Files

This repository now includes a comprehensive bar chart generator that can create visualizations from XLSX files automatically.

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Charts from All XLSX Files**:
   ```bash
   python generate_bar_charts.py
   ```

3. **Run Example with Sample Data**:
   ```bash
   python example_usage.py
   ```

## 📁 File Structure

```
├── generate_bar_charts.py          # Main script to generate charts
├── example_usage.py                # Example with sample data
├── src/visualizations/
│   └── bar_chart_generator.py      # Core chart generation module
├── data/
│   ├── processed/                  # Input XLSX files
│   └── visualizations/             # Generated chart images
└── requirements.txt                # Updated with visualization dependencies
```

## 🎯 Features

### Automatic Chart Generation
- **Auto-Detection**: Automatically detects numeric and categorical columns
- **Multiple Chart Types**: Creates vertical bars, horizontal bars, and grouped charts
- **Smart Formatting**: Handles long category names and large datasets elegantly
- **High Quality**: Saves charts as high-resolution PNG files (300 DPI)

### Chart Types Generated
1. **Vertical Bar Charts**: Standard bar charts for comparing categories
2. **Horizontal Bar Charts**: Better for datasets with many categories or long names
3. **Grouped Bar Charts**: When multiple categorical columns are available

### Data Processing
- **Flexible Input**: Works with any XLSX file structure
- **Smart Aggregation**: Sums numeric values or counts occurrences automatically
- **Error Handling**: Gracefully handles missing data and formatting issues

## 📊 Example Output

The generator will create charts like:
- `bar_chart_Hours_Contributed_by_Branch_20250906_143022.png`
- `horizontal_bar_chart_Hours_Contributed_by_Assignment_20250906_143023.png`
- `grouped_bar_chart_Hours_Contributed_by_Branch_Grouped_by_Assignment_20250906_143024.png`

## 🛠️ Usage Options

### Basic Usage (Recommended)
```bash
python generate_bar_charts.py
```
Processes all XLSX files in `data/processed/` and saves charts to `data/visualizations/`

### Programmatic Usage
```python
from src.visualizations.bar_chart_generator import generate_bar_charts_from_xlsx

# Generate charts from a specific file
charts = generate_bar_charts_from_xlsx('path/to/your/file.xlsx')
print(f"Generated {len(charts)} charts")
```

### Custom Chart Creation
```python
from src.visualizations.bar_chart_generator import create_bar_chart, load_xlsx_file

# Load data
df = load_xlsx_file('your_file.xlsx')

# Create specific chart
chart_path = create_bar_chart(df, 'category_column', 'value_column', 
                             title='My Custom Chart')
```

## 📋 Column Detection Logic

### Numeric Columns (for chart values)
- Columns with int64 or float64 data types
- Columns with names containing 'hour', 'count', 'total'
- Convertible text columns with numeric values

### Categorical Columns (for chart categories)
- Columns with fewer than 20 unique values
- Columns where unique values are less than 10% of total records
- Columns with names containing 'branch', 'location', 'assignment', 'category', 'type'

## 🎨 Customization

### Chart Styling
Charts use a modern style with:
- Seaborn color palette
- Grid lines for better readability
- Value labels on bars
- Professional fonts and spacing

### Output Customization
- Charts are saved with timestamps to avoid overwrites
- File names are automatically generated from chart titles
- Output directory can be customized

## 🔧 Dependencies

The following packages have been added to `requirements.txt`:
- `matplotlib>=3.5.0` - Core plotting functionality
- `seaborn>=0.11.0` - Enhanced styling and color palettes
- `numpy>=1.21.0` - Numerical computations

Existing dependencies:
- `pandas>=1.5.0` - Data manipulation and analysis
- `openpyxl>=3.0.0` - Excel file reading
- `requests>=2.28.0` - HTTP requests (existing functionality)

## 🚨 Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```
   ModuleNotFoundError: No module named 'matplotlib'
   ```
   **Solution**: Run `pip install -r requirements.txt`

2. **No Charts Generated**:
   - Check if XLSX files exist in `data/processed/`
   - Verify XLSX files contain data with detectable columns
   - Check the console output for specific error messages

3. **Permission Errors**:
   - Ensure write permissions for `data/visualizations/` directory
   - Close any Excel files that might be open

### Debugging
Enable detailed logging by checking the log files:
- `bar_chart_generator.log` - Chart generation details
- Console output shows progress and any issues

## 💡 Tips for Best Results

1. **Data Preparation**: Ensure your XLSX files have clear column headers
2. **File Location**: Place XLSX files in `data/processed/` for automatic processing
3. **Column Names**: Use descriptive names like 'Hours', 'Branch', 'Activity' for better charts
4. **Data Quality**: Remove or fix any corrupted data before running the generator

## 🔄 Integration with Existing Workflow

This bar chart generator integrates seamlessly with the existing YMCA data processing pipeline:
- Uses the same logging system (`src/utils/logging_config.py`)
- Follows the same file organization patterns
- Compatible with existing data processing scripts

## 📈 Future Enhancements

Potential improvements that could be added:
- Interactive charts with plotly
- PDF report generation
- More chart types (pie charts, line graphs, scatter plots)
- Web dashboard integration
- Automated report scheduling
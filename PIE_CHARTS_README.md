# XLSX to Pie Charts Generator

This collection of scripts can create pie charts from XLSX files with different levels of functionality based on available Python packages.

## Quick Start

```bash
# Process all XLSX files in the data directory
python3 xlsx_to_pie_charts.py

# Process a specific file
python3 xlsx_to_pie_charts.py --file data/example.xlsx

# Check what functionality is available
python3 xlsx_to_pie_charts.py --info
```

## Scripts Included

### 1. `xlsx_to_pie_charts.py` (Main Script)
- **Purpose**: Main entry point that automatically selects the best available method
- **Features**: Auto-detects dependencies and uses the most capable generator available
- **Usage**: Recommended for all users

### 2. `basic_xlsx_analyzer.py` (Standard Library Only)
- **Purpose**: Works with only Python standard library (no pip installs needed)
- **Features**: 
  - Reads XLSX files using zipfile and XML parsing
  - Creates text-based pie chart visualizations
  - Generates JSON data for further processing
- **Limitations**: No visual charts, text output only

### 3. `create_pie_charts.py` (Full Featured)
- **Purpose**: Full-featured with pandas and matplotlib
- **Requirements**: `pip install pandas matplotlib openpyxl`
- **Features**: 
  - Advanced data processing with pandas
  - High-quality PNG chart generation
  - Automatic data type detection

### 4. `simple_pie_charts.py` (Minimal Dependencies)
- **Purpose**: Basic charts with minimal dependencies
- **Requirements**: `pip install matplotlib openpyxl`
- **Features**: Direct XLSX reading, matplotlib charts

## Output Files

The scripts generate several types of output in the `charts/` directory:

- **PNG files**: Visual pie charts (if matplotlib available)
- **JSON files**: Structured data for programmatic use
- **TXT files**: Text-based visualizations and summaries

## Example Output

```
Column_4 Distribution
=====================
1                    |██████████████████████████████████████  766 ( 76.6%)
0                    |███████████                234 ( 23.4%)
```

## Data Requirements

The scripts work best with:
- **Categorical columns**: Text data with 2-50 unique values
- **Categorical numeric**: Numeric codes with few unique values (like 0/1, status codes)
- **Clean data**: Non-empty values, consistent formatting

## Supported File Types

- `.xlsx` files (Excel format)
- Multiple sheets (processes first sheet by default)
- Various data types (text, numbers, dates)

## Installation Options

### Option 1: Standard Library Only (No Installation)
```bash
python3 xlsx_to_pie_charts.py  # Uses basic functionality
```

### Option 2: Full Functionality
```bash
pip install pandas matplotlib openpyxl
python3 xlsx_to_pie_charts.py  # Uses full functionality
```

### Option 3: Minimal Charts
```bash
pip install matplotlib openpyxl
python3 xlsx_to_pie_charts.py  # Uses simple functionality
```

## Command Line Options

```bash
python3 xlsx_to_pie_charts.py [options]

Options:
  --input-dir DIR     Directory with XLSX files (default: data)
  --output-dir DIR    Output directory (default: charts)
  --file FILE         Process single file instead of directory
  --info             Show dependency information
  --help             Show help message
```

## Examples

```bash
# Process all files in current directory
python3 xlsx_to_pie_charts.py --input-dir .

# Process specific file, save to custom location
python3 xlsx_to_pie_charts.py --file report.xlsx --output-dir results

# Check what's available on your system
python3 xlsx_to_pie_charts.py --info
```

## Troubleshooting

- **No charts generated**: Check that your data has categorical columns with 2-50 unique values
- **Import errors**: Install required packages or use `--info` to see what's missing
- **Empty output**: Verify XLSX files contain data and aren't corrupted
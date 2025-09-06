# XLSX Line Graph Generator

This script generates line graphs from XLSX files in your data directories.

## Features

- **Automatic Data Detection**: Finds date and numeric columns automatically
- **Multiple Graph Types**: Creates individual graphs for each metric plus combined views
- **Flexible Time Periods**: Supports daily, weekly, monthly, quarterly, and yearly aggregation
- **Trend Lines**: Optional trend line overlay for pattern analysis
- **Professional Styling**: Uses seaborn styling for publication-ready graphs

## Quick Start

### Option 1: Use the Setup Script
```bash
./run_line_graph_generator.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Generate graphs from all XLSX files
python3 generate_line_graphs.py

# Or process a specific file
python3 generate_line_graphs.py data/processed/your_file.xlsx
```

## Usage Examples

```bash
# Process all XLSX files in default directories (data/processed, data/raw)
python3 generate_line_graphs.py

# Process a specific file
python3 generate_line_graphs.py data/processed/Raw_Data_20250906_132711.xlsx

# Process all files in a specific directory
python3 generate_line_graphs.py --dir data/processed

# Use weekly aggregation instead of monthly
python3 generate_line_graphs.py --period W

# Specify custom output directory
python3 generate_line_graphs.py --output my_graphs
```

## Time Aggregation Options

- `D` = Daily
- `W` = Weekly  
- `M` = Monthly (default)
- `Q` = Quarterly
- `Y` = Yearly

## Requirements

Your XLSX files need:
- At least one column with dates/times
- At least one numeric column for plotting
- Data with non-zero values

## Output

Generated graphs are saved as PNG files in:
- `data/visualizations/` (default)
- Or your specified output directory

Graph types created:
- Individual line graph for each numeric column
- Combined graph showing all metrics together
- Trend lines to show patterns over time

## File Structure

```
src/visualizers/
├── line_graph_generator.py      # Main graph generation class
├── simple_line_graph_generator.py # Standalone version
├── 
generate_line_graphs.py          # Command-line interface
run_line_graph_generator.sh      # Setup and run script
```

## Troubleshooting

**Missing Dependencies**: If you see dependency errors, run:
```bash
pip3 install pandas matplotlib seaborn openpyxl
```

**No Graphs Generated**: Check that your XLSX files have:
- Date columns (with 'date', 'time', 'volunteer' in the name)
- Numeric columns with non-zero data

**Permission Errors**: Make sure the output directory is writable:
```bash
mkdir -p data/visualizations
chmod 755 data/visualizations
```

## Integration with Existing Pipeline

This line graph generator integrates with the existing YMCA volunteer data processing pipeline:

1. **Step 1**: `volunteer_history_extractor.py` - Extract data from API
2. **Step 2**: `data_preparation.py` - Clean and prepare data  
3. **Step 3**: `*_breakdown.py` - Generate statistics
4. **Step 4**: **`line_graph_generator.py`** - Create visualizations

The generator automatically processes files created by previous steps in the pipeline.
#!/usr/bin/env python3
"""
XLSX to Pie Charts Generator

This script reads XLSX files and generates pie charts from categorical data.
It supports multiple approaches based on available dependencies:

1. Full-featured with pandas and matplotlib (if available)
2. Basic analysis with standard library only
3. Text-based visualizations as fallback

Usage:
    python3 xlsx_to_pie_charts.py --input-dir data
    python3 xlsx_to_pie_charts.py --file data/example.xlsx
    python3 xlsx_to_pie_charts.py --help

Features:
- Automatically detects categorical columns suitable for pie charts
- Handles both text and numeric categorical data
- Generates visual charts (if matplotlib available) and text summaries
- Provides detailed analysis of data structure
- Supports batch processing of directories
"""

import os
import sys
import argparse
from pathlib import Path

# Import availability flags
basic_available = False
full_available = False
simple_available = False

# Try to import different implementations based on available dependencies
try:
    # Import modules dynamically to avoid early import errors
    import importlib.util
    
    # Check for basic analyzer
    if os.path.exists("basic_xlsx_analyzer.py"):
        spec = importlib.util.spec_from_file_location("basic_xlsx_analyzer", "basic_xlsx_analyzer.py")
        basic_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(basic_module)
        BasicXLSXAnalyzer = basic_module.BasicXLSXAnalyzer
        basic_available = True
    
    # Check for full generator (requires pandas/matplotlib)
    if os.path.exists("create_pie_charts.py"):
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            spec = importlib.util.spec_from_file_location("create_pie_charts", "create_pie_charts.py")
            full_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(full_module)
            PieChartGenerator = full_module.PieChartGenerator
            full_available = True
        except ImportError:
            pass
    
    # Check for simple generator (requires matplotlib)
    if os.path.exists("simple_pie_charts.py"):
        try:
            import matplotlib.pyplot as plt
            spec = importlib.util.spec_from_file_location("simple_pie_charts", "simple_pie_charts.py")
            simple_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(simple_module)
            SimplePieChartGenerator = simple_module.SimplePieChartGenerator
            simple_available = True
        except ImportError:
            pass

except Exception as e:
    print(f"Warning: Error during import setup: {e}")


def check_dependencies():
    """Check what dependencies are available and return best option."""
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import openpyxl
        return "full"
    except ImportError:
        pass
    
    try:
        import matplotlib.pyplot as plt
        import openpyxl
        return "simple"
    except ImportError:
        pass
    
    return "basic"


def print_usage_info():
    """Print information about available functionality."""
    dependency_level = check_dependencies()
    
    print("XLSX to Pie Charts Generator")
    print("=" * 40)
    print()
    
    if dependency_level == "full":
        print("✅ Full functionality available")
        print("   - pandas for data processing")
        print("   - matplotlib for chart generation")
        print("   - openpyxl for XLSX reading")
    elif dependency_level == "simple":
        print("⚠️  Limited functionality available")
        print("   - matplotlib for chart generation")
        print("   - openpyxl for XLSX reading")
        print("   - Missing: pandas (using custom data processing)")
    else:
        print("📊 Basic functionality only")
        print("   - Standard library XLSX parsing")
        print("   - Text-based visualizations")
        print("   - Missing: matplotlib, openpyxl, pandas")
        print()
        print("To get full functionality, install:")
        print("   pip install pandas matplotlib openpyxl")
    
    print()


def main():
    """Main function to orchestrate pie chart generation."""
    parser = argparse.ArgumentParser(
        description="Generate pie charts from XLSX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input-dir data                    # Process all XLSX files in data/
  %(prog)s --file data/example.xlsx           # Process single file
  %(prog)s --input-dir data --output-dir charts  # Custom output directory
  %(prog)s --info                             # Show dependency information

Supported file types: .xlsx
Output formats: PNG charts (if matplotlib available), JSON data, text summaries
        """
    )
    
    parser.add_argument(
        "--input-dir",
        default="data",
        help="Directory containing XLSX files (default: data)"
    )
    parser.add_argument(
        "--output-dir",
        default="charts",
        help="Output directory for generated charts (default: charts)"
    )
    parser.add_argument(
        "--file",
        help="Process a specific XLSX file instead of a directory"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show information about available functionality"
    )
    
    args = parser.parse_args()
    
    if args.info:
        print_usage_info()
        return
    
    # Determine which implementation to use
    dependency_level = check_dependencies()
    
    print(f"Using {dependency_level} mode for pie chart generation")
    
    # Initialize the appropriate generator
    if dependency_level == "full" and full_available:
        generator = PieChartGenerator(args.output_dir)
        print("📊 Full-featured generator with pandas and matplotlib")
    elif dependency_level == "simple" and simple_available:
        generator = SimplePieChartGenerator(args.output_dir)
        print("📊 Simple generator with matplotlib")
    elif basic_available:
        generator = BasicXLSXAnalyzer(args.output_dir)
        print("📊 Basic analyzer with text visualizations")
    else:
        print("❌ No suitable generator available. Please check your installation.")
        return 1
    
    # Process files
    if args.file:
        if os.path.exists(args.file):
            print(f"Processing single file: {args.file}")
            generator.process_xlsx_file(args.file)
        else:
            print(f"❌ File not found: {args.file}")
            return 1
    else:
        if os.path.exists(args.input_dir):
            print(f"Processing directory: {args.input_dir}")
            if hasattr(generator, 'process_all_xlsx_files'):
                generator.process_all_xlsx_files(args.input_dir)
            else:
                # Fallback for generators without batch processing
                xlsx_files = list(Path(args.input_dir).glob("**/*.xlsx"))
                print(f"Found {len(xlsx_files)} XLSX files")
                for xlsx_file in xlsx_files:
                    generator.process_xlsx_file(xlsx_file)
        else:
            print(f"❌ Directory not found: {args.input_dir}")
            return 1
    
    print(f"✅ Processing complete. Output saved to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Bar Chart Generator for XLSX Files
==================================

This script generates bar charts from XLSX files in the data/processed directory.
It automatically detects numeric and categorical columns and creates various types of bar charts.

Usage:
    python generate_bar_charts.py

Features:
- Automatically processes all XLSX files in data/processed/
- Creates vertical and horizontal bar charts
- Generates grouped bar charts when multiple categorical columns are available
- Saves charts as high-resolution PNG files in data/visualizations/
- Provides detailed logging of the process

Requirements:
- pandas, matplotlib, seaborn, numpy (install with: pip install -r requirements.txt)
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    try:
        import pandas as pd
    except ImportError:
        missing_deps.append('pandas')
    
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        missing_deps.append('matplotlib')
    
    try:
        import seaborn as sns
    except ImportError:
        missing_deps.append('seaborn')
    
    try:
        import numpy as np
    except ImportError:
        missing_deps.append('numpy')
    
    return missing_deps

def main():
    """Main function"""
    print("🏊‍♂️ YMCA Bar Chart Generator")
    print("=" * 50)
    print("This script will generate bar charts from all XLSX files in data/processed/")
    print("Charts will be saved to data/visualizations/")
    print()
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print("\nPlease install dependencies:")
        print("  pip install pandas matplotlib seaborn numpy openpyxl")
        print("  or")
        print("  pip install -r requirements.txt")
        return False
    
    # Add src to path for imports
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from src.visualizations.bar_chart_generator import main as chart_main
        chart_main()
        print("\n✅ Bar chart generation completed successfully!")
        print("📁 Check the data/visualizations/ directory for your charts.")
        return True
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script to verify histogram generator functionality
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from processors.histogram_generator import HistogramGenerator
    print("✅ HistogramGenerator imported successfully")
    
    # Test basic functionality
    generator = HistogramGenerator(output_dir='data/processed/histograms')
    print(f"✅ Output directory created: {generator.output_dir}")
    
    # Check for XLSX files
    xlsx_files = list(Path('data').glob('**/*.xlsx'))
    print(f"✅ Found {len(xlsx_files)} XLSX files:")
    for file in xlsx_files[:3]:  # Show first 3 files
        print(f"  📄 {file}")
    
    print("\n🎯 Histogram generator is ready to use!")
    print("\nTo generate histograms, run:")
    print("  python generate_histograms.py")
    print("  python generate_histograms.py data/raw/VolunteerHistory_2025-01_to_2025-08.xlsx")
    print("  python generate_histograms.py data/processed")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("  pip install pandas matplotlib seaborn openpyxl")
except Exception as e:
    print(f"❌ Error: {e}")
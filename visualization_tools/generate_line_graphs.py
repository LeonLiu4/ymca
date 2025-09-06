#!/usr/bin/env python3
"""
Command-line script to generate line graphs from XLSX files.

Usage:
    python generate_line_graphs.py                    # Process all XLSX files in data/ directories
    python generate_line_graphs.py file.xlsx          # Process a specific file
    python generate_line_graphs.py --dir /path/       # Process all XLSX files in a directory
    python generate_line_graphs.py --period W         # Use weekly aggregation instead of monthly
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.visualizers.line_graph_generator import LineGraphGenerator
from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, 'generate_line_graphs_cli.log')


def main():
    parser = argparse.ArgumentParser(
        description="Generate line graphs from XLSX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_line_graphs.py
  python generate_line_graphs.py data/processed/Raw_Data_20250906_132711.xlsx
  python generate_line_graphs.py --dir data/processed
  python generate_line_graphs.py --period W --dir data/raw
  
Aggregation periods:
  D = Daily, W = Weekly, M = Monthly (default), Q = Quarterly, Y = Yearly
        """
    )
    
    parser.add_argument('file', nargs='?', help='Specific XLSX file to process')
    parser.add_argument('--dir', '--directory', help='Directory containing XLSX files')
    parser.add_argument('--period', choices=['D', 'W', 'M', 'Q', 'Y'], default='M',
                       help='Time aggregation period (default: M for Monthly)')
    parser.add_argument('--output', help='Output directory for graphs (default: data/visualizations)')
    
    args = parser.parse_args()
    
    # Initialize generator
    output_dir = args.output or "data/visualizations"
    generator = LineGraphGenerator(output_dir=output_dir)
    
    saved_files = []
    
    try:
        if args.file:
            # Process a specific file
            if not os.path.exists(args.file):
                print(f"❌ File not found: {args.file}")
                sys.exit(1)
            
            if not args.file.endswith('.xlsx'):
                print(f"❌ File must be an XLSX file: {args.file}")
                sys.exit(1)
            
            print(f"📊 Processing file: {args.file}")
            saved_files = generator.process_xlsx_file(args.file, period=args.period)
            
        elif args.dir:
            # Process a specific directory
            if not os.path.exists(args.dir):
                print(f"❌ Directory not found: {args.dir}")
                sys.exit(1)
            
            print(f"📁 Processing directory: {args.dir}")
            saved_files = generator.process_directory(args.dir, "*.xlsx", period=args.period)
            
        else:
            # Process default directories
            print("📁 Processing default directories: data/processed and data/raw")
            
            # Process data/processed
            if os.path.exists("data/processed"):
                processed_files = generator.process_directory("data/processed", "*.xlsx", period=args.period)
                saved_files.extend(processed_files)
            
            # Process data/raw  
            if os.path.exists("data/raw"):
                raw_files = generator.process_directory("data/raw", "*.xlsx", period=args.period)
                saved_files.extend(raw_files)
            
            if not os.path.exists("data/processed") and not os.path.exists("data/raw"):
                print("❌ No data directories found. Please specify --file or --dir")
                sys.exit(1)
        
        # Summary
        if saved_files:
            print(f"\n🎉 Successfully generated {len(saved_files)} line graphs!")
            print(f"📁 Output directory: {output_dir}")
            print(f"📈 Aggregation period: {args.period} ({'Daily' if args.period=='D' else 'Weekly' if args.period=='W' else 'Monthly' if args.period=='M' else 'Quarterly' if args.period=='Q' else 'Yearly'})")
            print("\nGenerated files:")
            for file in saved_files:
                print(f"  • {os.path.basename(file)}")
        else:
            print("❌ No line graphs were generated.")
            print("💡 Make sure your XLSX files contain:")
            print("   • At least one date/time column")
            print("   • At least one numeric column") 
            print("   • Data with non-zero values")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
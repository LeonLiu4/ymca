#!/usr/bin/env python3
"""
Command-line script to create scatter plots from XLSX files

Usage:
    python create_scatter_plots.py                    # Process all XLSX files in data/
    python create_scatter_plots.py file.xlsx          # Process specific file
    python create_scatter_plots.py file.xlsx x y      # Create specific x vs y plot
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.scatter_plot_generator import ScatterPlotGenerator
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Generate scatter plots from XLSX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                   # Process all XLSX files
  %(prog)s data/raw/file.xlsx                # Process specific file
  %(prog)s data/raw/file.xlsx col1 col2      # Plot col1 vs col2
  %(prog)s --output plots/                   # Specify output directory
        """
    )
    
    parser.add_argument('file', nargs='?', 
                       help='XLSX file to process (default: process all in data/)')
    parser.add_argument('x_column', nargs='?', 
                       help='X-axis column name (requires y_column)')
    parser.add_argument('y_column', nargs='?', 
                       help='Y-axis column name (requires x_column)')
    parser.add_argument('--output', '-o', default='data/plots',
                       help='Output directory for plots (default: data/plots)')
    parser.add_argument('--max-plots', '-m', type=int, default=10,
                       help='Maximum number of auto-generated plots (default: 10)')
    parser.add_argument('--list-columns', '-l', action='store_true',
                       help='List available columns in the file and exit')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.x_column and not args.y_column:
        parser.error("y_column is required when x_column is specified")
    if args.y_column and not args.x_column:
        parser.error("x_column is required when y_column is specified")
    
    # Initialize generator
    generator = ScatterPlotGenerator(output_dir=args.output)
    
    # Determine files to process
    if args.file:
        # Process specific file
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        xlsx_files = [file_path]
    else:
        # Process all XLSX files in data directory
        data_dir = Path("data")
        xlsx_files = []
        for pattern in ["**/*.xlsx", "**/*.xls"]:
            xlsx_files.extend(data_dir.glob(pattern))
        
        if not xlsx_files:
            logger.error("❌ No XLSX files found in data/ directory")
            sys.exit(1)
    
    logger.info(f"🎯 Found {len(xlsx_files)} file(s) to process")
    
    # Process files
    all_saved_plots = []
    
    for xlsx_file in xlsx_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 Processing: {xlsx_file}")
        
        # List columns if requested
        if args.list_columns:
            df = generator.load_excel_file(str(xlsx_file))
            if df is not None:
                logger.info(f"📋 Available columns in {xlsx_file.name}:")
                numeric_cols = generator.detect_numeric_columns(df)
                for i, col in enumerate(df.columns, 1):
                    marker = "🔢" if col in numeric_cols else "📝"
                    logger.info(f"  {i:2d}. {marker} {col}")
            continue
        
        # Generate plots
        if args.x_column and args.y_column:
            # Create specific plot
            saved_plots = generator.process_xlsx_file(
                str(xlsx_file), 
                auto_detect=False,
                x_col=args.x_column,
                y_col=args.y_column
            )
        else:
            # Auto-generate plots
            saved_plots = generator.process_xlsx_file(str(xlsx_file), auto_detect=True)
        
        all_saved_plots.extend(saved_plots)
    
    # Don't show summary if just listing columns
    if args.list_columns:
        return
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ COMPLETE: Generated {len(all_saved_plots)} scatter plot(s)")
    
    if all_saved_plots:
        logger.info(f"📁 Plots saved to: {Path(args.output).absolute()}")
        logger.info("📊 Generated plots:")
        for plot_file in all_saved_plots:
            logger.info(f"  • {Path(plot_file).name}")
    else:
        logger.warning("⚠️ No plots were generated. Check your data for numeric columns.")
        logger.info("💡 Use --list-columns to see available columns in your files")


if __name__ == "__main__":
    main()
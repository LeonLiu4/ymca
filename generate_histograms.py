#!/usr/bin/env python3
"""
YMCA Volunteer Data Histogram Generator - Command Line Interface

This script generates histograms from XLSX files in the repository.
It can process individual files or entire directories.

Usage:
    python generate_histograms.py                    # Process all XLSX files in data/ directories
    python generate_histograms.py file.xlsx          # Process specific file
    python generate_histograms.py path/to/directory  # Process all XLSX files in directory
"""

import sys
import os
from pathlib import Path
import argparse

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from processors.histogram_generator import HistogramGenerator
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Generate histograms from XLSX files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_histograms.py                           # Process all data directories
  python generate_histograms.py data/raw/volunteer.xlsx   # Process specific file
  python generate_histograms.py data/processed            # Process directory
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to XLSX file or directory (optional, defaults to data directories)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data/processed/histograms',
        help='Output directory for histograms (default: data/processed/histograms)'
    )
    
    args = parser.parse_args()
    
    logger.info("📊 YMCA Volunteer Data Histogram Generator")
    logger.info("=" * 50)
    
    generator = HistogramGenerator(output_dir=args.output_dir)
    
    if args.path:
        path = Path(args.path)
        
        if not path.exists():
            logger.error(f"❌ Path does not exist: {args.path}")
            sys.exit(1)
        
        if path.is_file() and path.suffix.lower() == '.xlsx':
            # Process single file
            logger.info(f"Processing single file: {path}")
            generated_files = generator.process_xlsx_file(path)
        elif path.is_dir():
            # Process directory
            logger.info(f"Processing directory: {path}")
            generated_files = generator.process_directory(path)
        else:
            logger.error(f"❌ Path must be an XLSX file or directory: {args.path}")
            sys.exit(1)
    else:
        # Process default data directories
        logger.info("Processing default data directories...")
        data_dirs = ['data/raw', 'data/processed']
        generated_files = []
        
        for data_dir in data_dirs:
            if Path(data_dir).exists():
                logger.info(f"🔍 Processing directory: {data_dir}")
                files = generator.process_directory(data_dir)
                generated_files.extend(files)
            else:
                logger.info(f"Directory not found: {data_dir}")
    
    # Summary
    logger.info(f"\n✅ Histogram generation complete!")
    logger.info(f"Generated {len(generated_files)} histogram files")
    logger.info(f"Output directory: {generator.output_dir}")
    
    if generated_files:
        logger.info("\nGenerated files:")
        for file_path in generated_files:
            logger.info(f"  📈 {file_path}")
    else:
        logger.warning("No histograms were generated. Check that XLSX files contain numeric data.")


if __name__ == "__main__":
    main()
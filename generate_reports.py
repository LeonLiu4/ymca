#!/usr/bin/env python3
"""
YMCA Volunteer Reports Generator - Unified Command Line Interface

This script provides a unified interface to generate all types of volunteer reports
with support for both Excel and CSV formats using the --format csv flag.

Usage:
    python generate_reports.py                           # Generate Excel reports (default)
    python generate_reports.py --format csv              # Generate CSV reports for data sharing
    python generate_reports.py --format excel            # Generate Excel reports explicitly
    python generate_reports.py --type statistics         # Generate only statistics reports
    python generate_reports.py --type all --format csv   # Generate all report types in CSV format
"""

import sys
import os
import argparse
from pathlib import Path
import datetime as dt

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import setup_logger
from utils.export_utils import add_format_argument, get_output_format_description
from processors.project_statistics import main as generate_statistics

logger = setup_logger(__name__)


def main():
    """Main command-line interface for generating volunteer reports"""
    parser = argparse.ArgumentParser(
        description='Generate YMCA Volunteer Reports in Excel or CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_reports.py                           # Generate Excel reports (default)
  python generate_reports.py --format csv              # Generate CSV reports for data sharing
  python generate_reports.py --format excel            # Generate Excel reports explicitly
  python generate_reports.py --type statistics         # Generate only statistics reports
  python generate_reports.py --type all --format csv   # Generate all report types in CSV format

Output formats:
  excel: Single Excel file with multiple sheets (default)
  csv:   Multiple CSV files for easier data sharing and backup purposes

Report types:
  statistics: Volunteer statistics reports (hours, volunteers, projects)
  all:        All available report types (currently statistics only)
        """
    )
    
    # Add format argument using utility function
    parser = add_format_argument(parser)
    
    parser.add_argument(
        '--type',
        choices=['statistics', 'all'],
        default='all',
        help='Type of reports to generate (default: all)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data/processed',
        help='Output directory for reports (default: data/processed)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Print header
    logger.info("🏊‍♂️ YMCA Volunteer Reports Generator")
    logger.info("=" * 60)
    
    # Get format description
    format_info = get_output_format_description(args.format)
    logger.info(f"📊 Output format: {format_info['name']} ({format_info['description']})")
    logger.info(f"📁 Output directory: {args.output_dir}")
    logger.info(f"📋 Report type: {args.type.title()}")
    
    # Ensure output directory exists
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    generated_reports = []
    
    try:
        if args.type in ['statistics', 'all']:
            logger.info("\n🔢 Generating Statistics Reports...")
            
            # Temporarily modify sys.argv to pass arguments to project_statistics
            original_argv = sys.argv.copy()
            sys.argv = ['project_statistics.py', '--format', args.format, '--output-dir', args.output_dir]
            
            try:
                # Import and run statistics generation
                stats_result = generate_statistics()
                if stats_result and 'report_file' in stats_result:
                    generated_reports.append({
                        'type': 'Statistics',
                        'files': stats_result['report_file'] if isinstance(stats_result['report_file'], list) 
                                else [stats_result['report_file']],
                        'format': stats_result.get('format', args.format)
                    })
                    logger.info("✅ Statistics reports generated successfully")
                else:
                    logger.warning("⚠️ Statistics report generation returned no results")
            finally:
                # Restore original sys.argv
                sys.argv = original_argv
        
        # Summary
        logger.info("\n🎯 Report Generation Summary")
        logger.info("=" * 40)
        
        if generated_reports:
            logger.info(f"✅ Successfully generated {len(generated_reports)} report type(s)")
            
            for report in generated_reports:
                logger.info(f"\n📊 {report['type']} Report:")
                logger.info(f"   Format: {report['format'].upper()}")
                logger.info(f"   Files: {len(report['files'])}")
                
                for file_path in report['files']:
                    if isinstance(file_path, str):
                        logger.info(f"   • {os.path.basename(file_path)}")
            
            logger.info(f"\n📁 All reports saved to: {os.path.abspath(args.output_dir)}")
            
            # Format-specific next steps
            if args.format.lower() == "csv":
                logger.info("\n📋 Next Steps for CSV Reports:")
                logger.info("1. CSV files are ready for data sharing and backup")
                logger.info("2. Import into Excel, Google Sheets, or other analysis tools")
                logger.info("3. Use for automated data processing and integration")
                logger.info("4. Share easily with stakeholders who need raw data")
            else:
                logger.info("\n📋 Next Steps for Excel Reports:")
                logger.info("1. Review Excel files for accuracy")
                logger.info("2. Import data into PowerPoint presentations")
                logger.info("3. Use for comprehensive data analysis")
                logger.info("4. Share workbooks with stakeholders")
                
        else:
            logger.error("❌ No reports were generated")
            logger.error("   Check that data files exist in the data/processed directory")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Error generating reports: {e}")
        if args.verbose:
            import traceback
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
        return 1
    
    logger.info("\n🎉 Report generation complete!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
YMCA Custom Date Range Report Generator

Command-line interface for generating volunteer reports with flexible date ranges.
Supports various date formats and provides comprehensive validation.
"""

import argparse
import sys
import os
from datetime import date, datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from processors.flexible_report_generator import FlexibleReportGenerator
from processors.date_range_processor import DateRangeProcessor
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate YMCA volunteer reports for custom date ranges',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --start "2025-01-01" --end "2025-03-31"
  %(prog)s --start "January 1, 2025" --end "March 31, 2025" 
  %(prog)s --start "01/01/2025" --end "03/31/2025"
  %(prog)s --start "30 days ago" --end "today"
  %(prog)s --preset "Last Month"
  %(prog)s --list-presets
  %(prog)s --show-available-data

Supported date formats:
  - ISO format: 2025-01-15
  - US format: 01/15/2025, 01-15-2025
  - European: 15/01/2025  
  - Written: January 15, 2025, Jan 15, 2025
  - Month only: 2025-01, 01/2025
  - Relative: today, yesterday, 30 days ago, 2 weeks ago
        ''')
    
    # Date range options
    date_group = parser.add_mutually_exclusive_group(required=False)
    date_group.add_argument('--start', '-s', help='Start date (various formats supported)')
    date_group.add_argument('--preset', '-p', help='Use a preset date range')
    
    parser.add_argument('--end', '-e', help='End date (required with --start)')
    
    # Options
    parser.add_argument('--allow-future', action='store_true',
                       help='Allow future dates in the range')
    parser.add_argument('--max-days', type=int, default=1095,
                       help='Maximum allowed range in days (default: 1095)')
    parser.add_argument('--data-dir', default='data/raw',
                       help='Directory containing source data files')
    parser.add_argument('--output-dir', default='data/processed',
                       help='Directory for output reports')
    
    # Information options
    info_group = parser.add_mutually_exclusive_group(required=False)
    info_group.add_argument('--list-presets', action='store_true',
                           help='List available preset date ranges')
    info_group.add_argument('--show-available-data', action='store_true', 
                           help='Show available date ranges in data files')
    info_group.add_argument('--validate-date', 
                           help='Validate a date string without generating reports')
    
    # Verbosity
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress non-error output')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    return parser.parse_args()


def setup_logging_level(verbose: bool, quiet: bool):
    """Configure logging level based on command line options"""
    if quiet:
        import logging
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)


def print_presets(generator: FlexibleReportGenerator):
    """Print available preset date ranges"""
    print("Available Preset Date Ranges:")
    print("=" * 40)
    
    suggestions = generator.date_processor.suggest_common_ranges()
    for i, (name, (start_date, end_date)) in enumerate(suggestions.items(), 1):
        days = (end_date - start_date).days + 1
        description = generator.date_processor.get_period_description(start_date, end_date)
        print(f"{i:2d}. {name}")
        print(f"    Range: {start_date} to {end_date} ({days} days)")
        print(f"    Description: {description}")
        print()


def print_available_data(generator: FlexibleReportGenerator, data_dir: str):
    """Print information about available data files and date ranges"""
    print("Available Data Analysis:")
    print("=" * 30)
    
    available = generator.get_available_date_ranges(data_dir)
    
    print(f"Files found: {available['files_found']}")
    print(f"Files analyzed: {available['files_analyzed']}")
    
    if available['overall_range']:
        overall = available['overall_range']
        print(f"Overall date range: {overall['min_date']} to {overall['max_date']}")
        print(f"Total records: {overall['total_records']:,}")
    else:
        print("No date ranges could be determined from data files.")
        return
    
    print("\nIndividual File Analysis:")
    print("-" * 25)
    for i, file_info in enumerate(available['date_ranges'], 1):
        print(f"{i}. {file_info['file']}")
        print(f"   Date range: {file_info['min_date']} to {file_info['max_date']}")
        print(f"   Records: {file_info['total_records']:,}")
        print(f"   Date column: {file_info['date_column']}")
        print()


def validate_single_date(date_str: str, processor: DateRangeProcessor):
    """Validate and show information about a single date string"""
    print(f"Validating date string: '{date_str}'")
    print("=" * 40)
    
    parsed_date = processor.parse_date_string(date_str)
    
    if parsed_date:
        print(f"✅ Successfully parsed: {parsed_date}")
        print(f"   ISO format: {parsed_date.isoformat()}")
        print(f"   Day of week: {parsed_date.strftime('%A')}")
        print(f"   Formatted: {parsed_date.strftime('%B %d, %Y')}")
        
        # Show relative information
        today = date.today()
        days_diff = (parsed_date - today).days
        
        if days_diff == 0:
            print("   Relative: Today")
        elif days_diff == 1:
            print("   Relative: Tomorrow")
        elif days_diff == -1:
            print("   Relative: Yesterday")
        elif days_diff > 0:
            print(f"   Relative: {days_diff} days in the future")
        else:
            print(f"   Relative: {abs(days_diff)} days ago")
        
    else:
        print("❌ Failed to parse date string")
        print("\nSupported formats:")
        for fmt in processor.supported_formats:
            example_date = datetime(2025, 1, 15)
            try:
                example = example_date.strftime(fmt)
                print(f"   {fmt} → {example}")
            except:
                print(f"   {fmt}")


def resolve_preset_dates(preset_name: str, generator: FlexibleReportGenerator) -> tuple:
    """Resolve a preset name to start and end dates"""
    suggestions = generator.date_processor.suggest_common_ranges()
    
    # Case-insensitive lookup
    preset_lower = preset_name.lower()
    for name, (start_date, end_date) in suggestions.items():
        if name.lower() == preset_lower:
            return start_date, end_date
    
    # Try partial matching
    matches = []
    for name, dates in suggestions.items():
        if preset_lower in name.lower():
            matches.append((name, dates))
    
    if len(matches) == 1:
        return matches[0][1]
    elif len(matches) > 1:
        print(f"Ambiguous preset '{preset_name}'. Multiple matches found:")
        for name, _ in matches:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print(f"Preset '{preset_name}' not found.")
        print("Use --list-presets to see available options.")
        sys.exit(1)


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Setup logging
    setup_logging_level(args.verbose, args.quiet)
    
    # Create generator
    generator = FlexibleReportGenerator(args.output_dir)
    
    # Handle information requests
    if args.list_presets:
        print_presets(generator)
        return
    
    if args.show_available_data:
        print_available_data(generator, args.data_dir)
        return
    
    if args.validate_date:
        validate_single_date(args.validate_date, generator.date_processor)
        return
    
    # Determine date range
    start_date_str = None
    end_date_str = None
    
    if args.preset:
        if not args.quiet:
            print(f"Using preset: {args.preset}")
        start_date, end_date = resolve_preset_dates(args.preset, generator)
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
    elif args.start:
        if not args.end:
            print("Error: --end is required when using --start")
            sys.exit(1)
        start_date_str = args.start
        end_date_str = args.end
    else:
        print("Error: Either --start and --end, or --preset is required")
        print("Use --help for usage information")
        sys.exit(1)
    
    # Generate the report
    if not args.quiet:
        print("🚀 Generating custom date range report...")
        print(f"📅 Date range: {start_date_str} to {end_date_str}")
        print(f"📂 Source data: {args.data_dir}")
        print(f"📁 Output directory: {args.output_dir}")
    
    try:
        result = generator.generate_custom_date_range_report(
            start_date_str, 
            end_date_str,
            allow_future=args.allow_future,
            max_range_days=args.max_days,
            source_data_dir=args.data_dir
        )
        
        if result['success']:
            if not args.quiet:
                print("\n✅ Report generation completed successfully!")
                print(f"📋 Executive Summary: {os.path.basename(result['executive_summary_file'])}")
                print(f"📊 Detailed Analysis: {os.path.basename(result['detailed_analysis_file'])}")
                print(f"📈 Period: {result['date_range']['description']}")
                print(f"📊 Records processed: {result['data_stats']['total_records']:,}")
                print(f"📅 Actual range: {result['data_stats']['date_range_actual']['start']} to {result['data_stats']['date_range_actual']['end']}")
            else:
                # Quiet mode - just print file paths
                print(result['executive_summary_file'])
                print(result['detailed_analysis_file'])
        else:
            print(f"❌ Report generation failed: {result['error']}")
            if args.verbose and 'date_validation' in result:
                validation = result['date_validation']
                if validation and 'errors' in validation:
                    for error in validation['errors']:
                        print(f"   • {error}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Report generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
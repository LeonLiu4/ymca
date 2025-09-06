#!/usr/bin/env python3
"""
Data Quality Validation Tool

This tool performs comprehensive data quality validation on Excel files,
checking for common issues like duplicate records, invalid dates, missing 
required fields, and generating detailed quality reports.

Usage:
    python data_quality_validator_main.py [file_path] [options]
    
Features:
    • Duplicate record detection
    • Missing field validation
    • Date format validation
    • Data consistency checks
    • Comprehensive reporting (TXT, Excel, JSON)
    • Quality scoring system
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import setup_logger
from utils.file_utils import load_excel_data, find_latest_file
from processors.data_quality_validator import DataQualityValidator
from processors.data_quality_reporter import DataQualityReporter

logger = setup_logger(__name__, 'data_quality_main.log')


def validate_file(file_path: str, required_fields: Optional[List[str]] = None,
                 output_dir: str = "data/processed/reports") -> bool:
    """Validate a single file and generate reports"""
    logger.info(f"\n🏊‍♂️ Data Quality Validation Tool")
    logger.info("=" * 60)
    logger.info(f"📁 Processing file: {file_path}")
    
    # Load data
    df = load_excel_data(file_path)
    if df is None:
        logger.error(f"❌ Failed to load file: {file_path}")
        return False
    
    logger.info(f"📊 Loaded {len(df)} records with {len(df.columns)} columns")
    
    # Initialize validator
    validator = DataQualityValidator(required_fields=required_fields)
    
    # Run validation
    filename = os.path.basename(file_path)
    validation_results = validator.validate_data(df, filename)
    
    # Generate reports
    reporter = DataQualityReporter()
    
    try:
        # Generate text report
        txt_report = reporter.generate_comprehensive_report(validation_results, output_dir)
        logger.info(f"📄 Text report: {txt_report}")
        
        # Generate Excel report  
        excel_report = reporter.generate_excel_report(validation_results, df, output_dir)
        logger.info(f"📊 Excel report: {excel_report}")
        
        # Generate JSON report
        json_report = reporter.generate_json_report(validation_results, output_dir)
        logger.info(f"🔧 JSON report: {json_report}")
        
        # Display summary
        display_validation_summary(validation_results)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating reports: {e}")
        return False


def validate_directory(directory_path: str, file_pattern: str = "*.xlsx",
                      required_fields: Optional[List[str]] = None,
                      output_dir: str = "data/processed/reports") -> bool:
    """Validate all matching files in a directory"""
    logger.info(f"\n🏊‍♂️ Data Quality Validation - Directory Mode")
    logger.info("=" * 60)
    logger.info(f"📁 Processing directory: {directory_path}")
    logger.info(f"🔍 File pattern: {file_pattern}")
    
    # Find all matching files
    import glob
    pattern_path = os.path.join(directory_path, file_pattern)
    files = glob.glob(pattern_path)
    
    if not files:
        logger.error(f"❌ No files found matching pattern: {pattern_path}")
        return False
    
    logger.info(f"📋 Found {len(files)} files to process")
    
    success_count = 0
    for file_path in files:
        logger.info(f"\n--- Processing {os.path.basename(file_path)} ---")
        if validate_file(file_path, required_fields, output_dir):
            success_count += 1
        else:
            logger.error(f"❌ Failed to process: {file_path}")
    
    logger.info(f"\n✅ Successfully processed {success_count}/{len(files)} files")
    return success_count == len(files)


def display_validation_summary(validation_results: dict):
    """Display validation summary to console"""
    print(f"\n🎯 VALIDATION SUMMARY")
    print("-" * 40)
    print(f"Quality Score: {validation_results.get('quality_score', 0)}/100")
    print(f"Quality Rating: {validation_results.get('quality_rating', 'Unknown')}")
    print(f"Total Issues: {validation_results.get('total_issues', 0)}")
    
    issues = validation_results.get('issues', [])
    if issues:
        high_issues = len([i for i in issues if i.get('severity') == 'high'])
        medium_issues = len([i for i in issues if i.get('severity') == 'medium']) 
        low_issues = len([i for i in issues if i.get('severity') == 'low'])
        
        print(f"\nIssue Breakdown:")
        print(f"🔴 High Priority: {high_issues}")
        print(f"🟡 Medium Priority: {medium_issues}")
        print(f"🟢 Low Priority: {low_issues}")
        
        if high_issues > 0:
            print(f"\n⚠️ Immediate attention required for high-priority issues!")
        elif medium_issues > 0:
            print(f"\n💡 Consider addressing medium-priority issues for improved quality.")
        else:
            print(f"\n✅ No critical issues found!")
    else:
        print(f"\n✅ No data quality issues detected!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Data Quality Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a specific file
  python data_quality_validator_main.py data/raw/volunteers.xlsx
  
  # Validate with required fields check
  python data_quality_validator_main.py data/raw/volunteers.xlsx --required-fields name email date
  
  # Validate all Excel files in a directory
  python data_quality_validator_main.py --directory data/raw/
  
  # Validate with custom output directory
  python data_quality_validator_main.py data/raw/volunteers.xlsx --output reports/quality/
        """)
    
    parser.add_argument('file_path', nargs='?', 
                       help='Path to Excel file to validate (optional if using --directory)')
    parser.add_argument('--directory', '-d',
                       help='Validate all Excel files in this directory')
    parser.add_argument('--pattern', '-p', default='*.xlsx',
                       help='File pattern to match in directory mode (default: *.xlsx)')
    parser.add_argument('--required-fields', '-r', nargs='+',
                       help='List of required fields to validate')
    parser.add_argument('--output', '-o', default='data/processed/reports',
                       help='Output directory for reports (default: data/processed/reports)')
    parser.add_argument('--auto', '-a', action='store_true',
                       help='Auto-detect latest file in data/raw/ directory')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file_path and not args.directory and not args.auto:
        print("❌ Error: Must specify either a file path, --directory, or --auto")
        parser.print_help()
        return False
    
    try:
        success = False
        
        if args.auto:
            # Auto-detect latest file
            latest_file = find_latest_file("*.xlsx", "data/raw")
            if latest_file:
                logger.info(f"🔍 Auto-detected file: {latest_file}")
                success = validate_file(latest_file, args.required_fields, args.output)
            else:
                logger.error("❌ No Excel files found in data/raw/ directory")
                return False
                
        elif args.directory:
            # Directory mode
            success = validate_directory(args.directory, args.pattern, 
                                       args.required_fields, args.output)
        else:
            # Single file mode
            if not os.path.exists(args.file_path):
                logger.error(f"❌ File not found: {args.file_path}")
                return False
            success = validate_file(args.file_path, args.required_fields, args.output)
        
        if success:
            print(f"\n✅ Data quality validation completed successfully!")
            print(f"📁 Reports saved to: {args.output}")
        else:
            print(f"\n❌ Data quality validation failed!")
            return False
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Validation interrupted by user")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Example usage of the Data Quality Validation Tool

This script demonstrates how to use the data quality validation system
to check Excel files for common data quality issues and generate reports.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import setup_logger
from utils.file_utils import load_excel_data, find_latest_file
from processors.data_quality_validator import DataQualityValidator
from processors.data_quality_reporter import DataQualityReporter

logger = setup_logger(__name__, 'data_quality_example.log')


def example_basic_validation():
    """Example 1: Basic data quality validation"""
    logger.info("\n🎯 Example 1: Basic Data Quality Validation")
    logger.info("=" * 50)
    
    # Find the latest file in raw data
    latest_file = find_latest_file("*.xlsx", "data/raw")
    if not latest_file:
        logger.error("❌ No Excel files found in data/raw/")
        return False
    
    logger.info(f"📁 Using file: {latest_file}")
    
    # Load data
    df = load_excel_data(latest_file)
    if df is None:
        return False
    
    # Create validator
    validator = DataQualityValidator()
    
    # Run validation
    filename = os.path.basename(latest_file)
    validation_results = validator.validate_data(df, filename)
    
    # Display results
    print(f"\n📊 Validation Results:")
    print(f"Quality Score: {validation_results.get('quality_score', 0)}/100")
    print(f"Quality Rating: {validation_results.get('quality_rating', 'Unknown')}")
    print(f"Issues Found: {validation_results.get('total_issues', 0)}")
    
    return True


def example_custom_validation():
    """Example 2: Custom validation with required fields"""
    logger.info("\n🎯 Example 2: Custom Validation with Required Fields")
    logger.info("=" * 50)
    
    # Define required fields for volunteer data
    required_fields = ['volunteerDate', 'assignment', 'Hours']
    
    # Find the latest file
    latest_file = find_latest_file("*.xlsx", "data/raw")
    if not latest_file:
        logger.error("❌ No Excel files found in data/raw/")
        return False
    
    # Load data
    df = load_excel_data(latest_file)
    if df is None:
        return False
    
    # Create validator with required fields
    validator = DataQualityValidator(required_fields=required_fields)
    
    # Run validation
    filename = os.path.basename(latest_file)
    validation_results = validator.validate_data(df, filename)
    
    # Show specific issues
    issues = validation_results.get('issues', [])
    print(f"\n📋 Found {len(issues)} data quality issues:")
    for issue in issues[:5]:  # Show first 5 issues
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get('severity', 'low'), "🟢")
        print(f"  {severity_icon} {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}")
    
    return True


def example_comprehensive_reporting():
    """Example 3: Comprehensive reporting with all formats"""
    logger.info("\n🎯 Example 3: Comprehensive Reporting")
    logger.info("=" * 50)
    
    # Find the latest file
    latest_file = find_latest_file("*.xlsx", "data/raw")
    if not latest_file:
        logger.error("❌ No Excel files found in data/raw/")
        return False
    
    # Load data
    df = load_excel_data(latest_file)
    if df is None:
        return False
    
    # Create validator
    validator = DataQualityValidator()
    
    # Run validation
    filename = os.path.basename(latest_file)
    validation_results = validator.validate_data(df, filename)
    
    # Create reporter and generate all report types
    reporter = DataQualityReporter()
    
    output_dir = "data/processed/reports/examples"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Generate text report
        txt_report = reporter.generate_comprehensive_report(validation_results, output_dir)
        print(f"📄 Text report: {txt_report}")
        
        # Generate Excel report
        excel_report = reporter.generate_excel_report(validation_results, df, output_dir)
        print(f"📊 Excel report: {excel_report}")
        
        # Generate JSON report
        json_report = reporter.generate_json_report(validation_results, output_dir)
        print(f"🔧 JSON report: {json_report}")
        
        print(f"\n✅ All reports generated successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating reports: {e}")
        return False


def example_processed_data_validation():
    """Example 4: Validate processed data files"""
    logger.info("\n🎯 Example 4: Validate Processed Data Files")
    logger.info("=" * 50)
    
    # Find processed files
    processed_dir = "data/processed"
    if not os.path.exists(processed_dir):
        logger.error(f"❌ Processed data directory not found: {processed_dir}")
        return False
    
    import glob
    processed_files = glob.glob(os.path.join(processed_dir, "*.xlsx"))
    
    if not processed_files:
        logger.error(f"❌ No processed Excel files found in {processed_dir}")
        return False
    
    logger.info(f"📋 Found {len(processed_files)} processed files to validate")
    
    validator = DataQualityValidator()
    results_summary = []
    
    for file_path in processed_files[:3]:  # Validate first 3 files
        filename = os.path.basename(file_path)
        logger.info(f"🔍 Validating: {filename}")
        
        df = load_excel_data(file_path)
        if df is None:
            continue
        
        validation_results = validator.validate_data(df, filename)
        
        results_summary.append({
            'file': filename,
            'quality_score': validation_results.get('quality_score', 0),
            'issues': validation_results.get('total_issues', 0)
        })
        
        print(f"  📊 {filename}: {validation_results.get('quality_score', 0)}/100 ({validation_results.get('total_issues', 0)} issues)")
    
    # Show summary
    print(f"\n📈 Validation Summary:")
    avg_score = sum([r['quality_score'] for r in results_summary]) / len(results_summary) if results_summary else 0
    total_issues = sum([r['issues'] for r in results_summary])
    
    print(f"Average Quality Score: {avg_score:.1f}/100")
    print(f"Total Issues Across All Files: {total_issues}")
    
    return True


def main():
    """Run all examples"""
    logger.info("🏊‍♂️ Data Quality Validation Tool - Examples")
    logger.info("=" * 60)
    
    examples = [
        example_basic_validation,
        example_custom_validation, 
        example_comprehensive_reporting,
        example_processed_data_validation
    ]
    
    success_count = 0
    for i, example_func in enumerate(examples, 1):
        try:
            if example_func():
                success_count += 1
            else:
                logger.warning(f"⚠️ Example {i} completed with warnings")
        except Exception as e:
            logger.error(f"❌ Example {i} failed: {e}")
    
    print(f"\n🎯 Examples completed: {success_count}/{len(examples)} successful")
    
    if success_count > 0:
        print(f"\n💡 To run the data quality validator manually:")
        print(f"   python data_quality_validator_main.py --auto")
        print(f"   python data_quality_validator_main.py data/raw/your_file.xlsx")
        print(f"   python data_quality_validator_main.py --directory data/raw/")


if __name__ == "__main__":
    main()
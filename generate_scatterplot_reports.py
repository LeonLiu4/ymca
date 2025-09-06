#!/usr/bin/env python3
"""
YMCA Volunteer Data - Scatterplot Report Generator

This script generates comprehensive reports from volunteer data by:
1. Creating multiple types of scatterplots from volunteer data
2. Analyzing the scatterplots to extract insights
3. Generating detailed reports in multiple formats

Usage:
    python generate_scatterplot_reports.py

Requirements:
    - Raw volunteer data must be processed first (run data_preparation.py)
    - Raw_Data_*.xlsx file must exist in data/processed/

Output:
    - Scatterplot images in data/processed/scatterplots/
    - Excel analysis report with multiple worksheets
    - Text report with detailed findings
    - Updated comprehensive summary report
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import setup_logger
from processors.scatterplot_report_generator import main as generate_reports

logger = setup_logger(__name__)

def check_prerequisites():
    """Check if all prerequisites are met before running"""
    logger.info("🔍 Checking prerequisites...")
    
    # Check if processed data exists
    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        logger.error("❌ data/processed directory not found")
        logger.error("Please run data extraction and preparation first")
        return False
    
    # Check for Raw_Data files
    raw_data_files = list(processed_dir.glob("Raw_Data_*.xlsx"))
    if not raw_data_files:
        logger.error("❌ No Raw_Data_*.xlsx files found in data/processed/")
        logger.error("Please run data_preparation.py first to create processed data")
        return False
    
    logger.info(f"✅ Found {len(raw_data_files)} processed data file(s)")
    
    # Check if required packages are installed
    try:
        import pandas
        import matplotlib
        import seaborn
        logger.info("✅ All required packages are available")
    except ImportError as e:
        logger.error(f"❌ Missing required package: {e}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main entry point for scatterplot report generation"""
    logger.info("🏊‍♂️ YMCA Volunteer Scatterplot Report Generator")
    logger.info("=" * 70)
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("❌ Prerequisites not met. Exiting.")
        return False
    
    try:
        # Generate reports
        results = generate_reports()
        
        if results:
            logger.info("\n🎉 SUCCESS! Scatterplot reports generated successfully")
            logger.info("\n📁 Generated Files:")
            
            # List scatterplot files
            scatterplot_dir = Path("data/processed/scatterplots")
            if scatterplot_dir.exists():
                scatterplot_files = list(scatterplot_dir.glob("*.png"))
                logger.info(f"📊 Scatterplots ({len(scatterplot_files)} files):")
                for plot_file in scatterplot_files:
                    logger.info(f"   • {plot_file.name}")
            
            # List report files
            processed_dir = Path("data/processed")
            recent_files = [
                f for f in processed_dir.glob("YMCA_Scatterplot_Analysis_Report_*.xlsx")
            ] + [
                f for f in processed_dir.glob("YMCA_Scatterplot_Analysis_Report_*.txt")
            ]
            
            if recent_files:
                logger.info("\n📝 Report Files:")
                for report_file in sorted(recent_files, key=lambda x: x.stat().st_mtime, reverse=True)[:2]:
                    logger.info(f"   • {report_file.name}")
            
            logger.info("\n📋 What to do next:")
            logger.info("1. Review the scatterplot images for visual insights")
            logger.info("2. Open the Excel report for detailed analysis")
            logger.info("3. Read the text report for key findings and recommendations")
            logger.info("4. Use visualizations in presentations and reports")
            
            return True
        else:
            logger.error("❌ Report generation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during report generation: {e}")
        logger.error("Please check the logs for more details")
        return False

def show_help():
    """Show help information"""
    help_text = """
🏊‍♂️ YMCA Volunteer Scatterplot Report Generator Help

DESCRIPTION:
    This script generates comprehensive analytical reports from volunteer data
    by creating and analyzing multiple types of scatterplots.

PREREQUISITES:
    1. Install dependencies: pip install -r requirements.txt
    2. Run data extraction: python src/extractors/volunteer_history_extractor.py
    3. Run data preparation: python src/processors/data_preparation.py

USAGE:
    python generate_scatterplot_reports.py

OUTPUT FILES:
    • Scatterplot Images: data/processed/scatterplots/*.png
    • Excel Report: data/processed/YMCA_Scatterplot_Analysis_Report_*.xlsx
    • Text Report: data/processed/YMCA_Scatterplot_Analysis_Report_*.txt
    • Summary Update: data/processed/YMCA_Volunteer_Summary_Report.txt

SCATTERPLOTS GENERATED:
    1. Hours vs Time: Monthly volunteer activity trends
    2. Volunteers vs Projects: Project popularity and impact analysis
    3. Efficiency Analysis: Hours per session by project
    4. Monthly Trends: Seasonal patterns across all projects

REPORT CONTENTS:
    • Executive summary with key metrics
    • Project impact analysis (top performers, underutilized projects)
    • Temporal analysis (peak months, seasonal trends)
    • Efficiency analysis (most/least efficient projects)
    • Actionable recommendations based on data insights

For issues or questions, check the logs or review the documentation.
    """
    print(help_text)

if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        sys.exit(0)
    
    # Run the main process
    success = main()
    sys.exit(0 if success else 1)
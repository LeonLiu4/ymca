#!/usr/bin/env python3
"""
Command-line interface for generating pie chart reports from YMCA volunteer data

Usage:
    python generate_pie_chart_reports.py [data_file_path]

If no data file is provided, the script will automatically find the most recent
Raw_Data_*.xlsx file in the data/processed directory.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from processors.pie_chart_report_generator import PieChartReportGenerator
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    """Main CLI function"""
    print("🥧 YMCA Volunteer Data - Pie Chart Report Generator")
    print("=" * 60)
    
    # Check if data file path is provided
    data_file_path = None
    if len(sys.argv) > 1:
        data_file_path = sys.argv[1]
        if not os.path.exists(data_file_path):
            print(f"❌ Error: Data file not found: {data_file_path}")
            return 1
        print(f"📁 Using provided data file: {data_file_path}")
    else:
        print("🔍 No data file provided, will auto-detect latest file...")
    
    # Create report generator
    generator = PieChartReportGenerator(data_file_path)
    
    try:
        # Generate all reports
        results = generator.generate_all_reports()
        
        if results:
            print("\n🎉 SUCCESS! Pie chart reports generated successfully!")
            print("\n📁 Generated Files:")
            print(f"  📊 Pie Charts: {len(results['charts'])} files")
            for chart in results['charts']:
                print(f"    • {os.path.basename(chart)}")
            print(f"  📝 Text Report: {os.path.basename(results['text_report'])}")
            print(f"  📈 Excel Summary: {os.path.basename(results['excel_summary'])}")
            
            print("\n📊 Analysis Summary:")
            if 'hours_by_branch' in results['charts_data']:
                hours_data = results['charts_data']['hours_by_branch']
                print(f"  • Total Hours: {hours_data['total_hours']:.1f}")
                print(f"  • Active Branches: {hours_data['branch_count']}")
                print(f"  • Top Branch: {hours_data['top_branch']}")
            
            if 'volunteers_by_project' in results['charts_data']:
                proj_data = results['charts_data']['volunteers_by_project']
                print(f"  • Total Assignments: {proj_data['total_assignments']}")
                print(f"  • Unique Projects: {proj_data['unique_projects']}")
            
            if 'monthly_activity' in results['charts_data']:
                month_data = results['charts_data']['monthly_activity']
                print(f"  • Active Months: {month_data['active_months']}")
                print(f"  • Peak Month: {month_data['peak_month']}")
            
            print(f"\n📁 All files saved in: data/processed/")
            print("\n✅ Ready for PowerPoint integration and stakeholder review!")
            return 0
        else:
            print("❌ Failed to generate pie chart reports")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Error generating reports: {e}")
        print(f"❌ Error: {e}")
        return 1

def show_help():
    """Show help information"""
    print(__doc__)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        show_help()
        sys.exit(0)
    
    sys.exit(main())
#!/usr/bin/env python3
"""
Quick Volunteer Metrics Summary CLI Tool

Generates a one-page text summary of key volunteer metrics (total hours, 
volunteer count, top branches) without running the full processing pipeline.
Reads from existing processed data files.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Try to import dependencies with graceful fallback
try:
    from utils.file_utils import find_latest_file, load_excel_data
    from utils.logging_config import setup_logger
    logger = setup_logger(__name__, 'quick_metrics.log')
    HAVE_FULL_DEPS = True
except ImportError as e:
    # Fallback logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Some dependencies not available: {e}")
    HAVE_FULL_DEPS = False


def find_latest_file_fallback(pattern: str, directory: str = ".") -> Optional[Path]:
    """Fallback file finder when utils are not available"""
    try:
        files = list(Path(directory).glob(pattern))
        if not files:
            return None
        return max(files, key=os.path.getctime)
    except Exception as e:
        logger.warning(f"Error finding files: {e}")
        return None


def find_latest_processed_data() -> Optional[Path]:
    """Find the latest processed raw data file"""
    if HAVE_FULL_DEPS:
        return find_latest_file("Raw_Data_*.xlsx", "data/processed")
    else:
        return find_latest_file_fallback("Raw_Data_*.xlsx", "data/processed")


def find_branch_breakdown_file() -> Optional[Path]:
    """Find the latest branch breakdown file"""
    if HAVE_FULL_DEPS:
        return find_latest_file("Y_Volunteer_*Branch_Breakdown*.xlsx", "data/processed")
    else:
        return find_latest_file_fallback("Y_Volunteer_*Branch_Breakdown*.xlsx", "data/processed")


def find_statistics_file() -> Optional[Path]:
    """Find the latest statistics file"""
    if HAVE_FULL_DEPS:
        return find_latest_file("Y_Volunteer_*Statistics*.xlsx", "data/processed")
    else:
        return find_latest_file_fallback("Y_Volunteer_*Statistics*.xlsx", "data/processed")


def read_summary_report() -> Optional[str]:
    """Read existing summary report if available"""
    report_path = Path("data/processed/YMCA_Volunteer_Summary_Report.txt")
    if report_path.exists():
        with open(report_path, 'r') as f:
            return f.read()
    return None


def extract_basic_metrics(df) -> Dict:
    """Extract basic metrics from raw volunteer data"""
    if df is None or df.empty:
        return {}
    
    metrics = {}
    
    # Total records and hours
    metrics['total_records'] = len(df)
    if 'creditedHours' in df.columns:
        metrics['total_hours'] = df['creditedHours'].sum()
        metrics['average_hours'] = df['creditedHours'].mean()
        metrics['min_hours'] = df['creditedHours'].min()
        metrics['max_hours'] = df['creditedHours'].max()
    
    # Date range
    if 'volunteerDate' in df.columns:
        df['volunteerDate'] = pd.to_datetime(df['volunteerDate'], errors='coerce')
        metrics['date_range'] = {
            'start': df['volunteerDate'].min(),
            'end': df['volunteerDate'].max()
        }
    
    # Unique volunteers (approximated by unique volunteer sessions)
    metrics['unique_volunteers'] = df.drop_duplicates(subset=['volunteerDate']).shape[0] if 'volunteerDate' in df.columns else 'N/A'
    
    # Top activities/assignments
    if 'assignment' in df.columns:
        top_assignments = df['assignment'].value_counts().head(5)
        metrics['top_assignments'] = top_assignments.to_dict()
        metrics['unique_assignments'] = df['assignment'].nunique()
    
    return metrics


def extract_branch_metrics(branch_file: Path) -> Dict:
    """Extract branch-specific metrics from branch breakdown file"""
    try:
        # Read Hours sheet
        hours_df = pd.read_excel(branch_file, sheet_name='Branch_Hours')
        volunteers_df = pd.read_excel(branch_file, sheet_name='Active_Volunteers')
        
        branch_metrics = {
            'total_branches': len(hours_df),
            'top_branches_by_hours': hours_df.head(5).to_dict('records'),
            'top_branches_by_volunteers': volunteers_df.head(5).to_dict('records')
        }
        
        return branch_metrics
    except Exception as e:
        logger.warning(f"Could not extract branch metrics: {e}")
        return {}


def parse_summary_report(report_content: str) -> Dict:
    """Extract key metrics from existing summary report"""
    metrics = {}
    
    if not report_content:
        return metrics
    
    lines = report_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Extract total hours
        if 'Total Hours:' in line and 'Total Hours: 6644.' in line:
            try:
                hours = float(line.split('Total Hours: ')[1].split()[0])
                metrics['summary_total_hours'] = hours
            except:
                pass
        
        # Extract total records
        if 'Total Records:' in line:
            try:
                records = int(line.split('Total Records: ')[1])
                metrics['summary_total_records'] = records
            except:
                pass
        
        # Extract volunteer counts
        if 'Total Active Volunteers:' in line:
            try:
                volunteers = int(line.split('Total Active Volunteers: ')[1])
                metrics['summary_active_volunteers'] = volunteers
            except:
                pass
        
        # Extract top branches
        if '• R.C. Durr YMCA:' in line and 'hours' in line:
            try:
                hours = float(line.split(': ')[1].split(' hours')[0])
                if 'top_branches_hours' not in metrics:
                    metrics['top_branches_hours'] = {}
                metrics['top_branches_hours']['R.C. Durr YMCA'] = hours
            except:
                pass
        
        if '• Camp Ernst:' in line and 'volunteers' in line:
            try:
                volunteers = int(line.split(': ')[1].split(' volunteers')[0])
                if 'top_branches_volunteers' not in metrics:
                    metrics['top_branches_volunteers'] = {}
                metrics['top_branches_volunteers']['Camp Ernst'] = volunteers
            except:
                pass
    
    return metrics


def generate_quick_summary(include_details: bool = False) -> str:
    """Generate a quick one-page summary of volunteer metrics"""
    
    summary = []
    summary.append("🏊‍♂️ YMCA VOLUNTEER METRICS - QUICK SUMMARY")
    summary.append("=" * 55)
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    # Try to get data from summary report first (fastest method)
    report_content = read_summary_report()
    parsed_metrics = parse_summary_report(report_content) if report_content else {}
    
    if parsed_metrics:
        summary.append("📊 KEY METRICS (from latest processing)")
        summary.append("-" * 45)
        
        if 'summary_total_hours' in parsed_metrics:
            summary.append(f"Total Volunteer Hours: {parsed_metrics['summary_total_hours']:,.1f}")
        
        if 'summary_total_records' in parsed_metrics:
            summary.append(f"Total Activity Records: {parsed_metrics['summary_total_records']:,}")
        
        if 'summary_active_volunteers' in parsed_metrics:
            summary.append(f"Active Volunteers: {parsed_metrics['summary_active_volunteers']:,}")
        
        summary.append("")
        
        # Top branches by hours
        if 'top_branches_hours' in parsed_metrics:
            summary.append("🏢 TOP BRANCHES BY HOURS:")
            for branch, hours in parsed_metrics['top_branches_hours'].items():
                summary.append(f"  • {branch}: {hours:,.1f} hours")
            summary.append("")
        
        # Top branches by volunteers  
        if 'top_branches_volunteers' in parsed_metrics:
            summary.append("👥 TOP BRANCHES BY VOLUNTEERS:")
            for branch, volunteers in parsed_metrics['top_branches_volunteers'].items():
                summary.append(f"  • {branch}: {volunteers:,} volunteers")
            summary.append("")
    
    # If we want more details or summary report parsing failed, try reading raw data
    if include_details or not parsed_metrics:
        if HAVE_FULL_DEPS:
            try:
                import pandas as pd
                
                # Find and load latest raw data
                latest_file = find_latest_processed_data()
                
                if latest_file:
                    summary.append("📋 DETAILED ANALYSIS (from raw data)")
                    summary.append("-" * 45)
                    summary.append(f"Data Source: {latest_file.name}")
                    summary.append("")
                    
                    df = load_excel_data(str(latest_file))
                    basic_metrics = extract_basic_metrics(df)
                    
                    if basic_metrics:
                        if 'total_hours' in basic_metrics:
                            summary.append(f"Total Hours: {basic_metrics['total_hours']:,.1f}")
                        
                        if 'total_records' in basic_metrics:
                            summary.append(f"Total Records: {basic_metrics['total_records']:,}")
                        
                        if 'unique_volunteers' in basic_metrics:
                            summary.append(f"Unique Volunteer Sessions: {basic_metrics['unique_volunteers']:,}")
                        
                        if 'unique_assignments' in basic_metrics:
                            summary.append(f"Unique Activities: {basic_metrics['unique_assignments']:,}")
                        
                        summary.append("")
                        
                        # Date range
                        if 'date_range' in basic_metrics:
                            dr = basic_metrics['date_range']
                            summary.append(f"Date Range: {dr['start'].strftime('%Y-%m-%d')} to {dr['end'].strftime('%Y-%m-%d')}")
                            summary.append("")
                        
                        # Top assignments
                        if 'top_assignments' in basic_metrics:
                            summary.append("🎯 TOP 5 ACTIVITIES:")
                            for assignment, count in list(basic_metrics['top_assignments'].items())[:5]:
                                # Truncate long assignment names
                                display_name = (assignment[:50] + "...") if len(str(assignment)) > 50 else assignment
                                summary.append(f"  • {display_name}: {count} records")
                            summary.append("")
                else:
                    summary.append("⚠️  No processed data files found")
                    summary.append("   Run the full processing pipeline first to generate data")
                    summary.append("")
            
            except Exception as e:
                logger.warning(f"Error reading detailed metrics: {e}")
                summary.append(f"⚠️  Error reading detailed data: {e}")
                summary.append("")
        else:
            summary.append("⚠️  pandas not available - install requirements.txt for detailed analysis")
            summary.append("   Showing available data from summary report only")
            summary.append("")
    
    # Processing status
    summary.append("🔧 PROCESSING STATUS")
    summary.append("-" * 45)
    
    # Check for various processed files
    stats_file = find_statistics_file()
    branch_file = find_branch_breakdown_file()
    
    summary.append(f"Statistics File: {'✅ Available' if stats_file else '❌ Missing'}")
    summary.append(f"Branch Breakdown: {'✅ Available' if branch_file else '❌ Missing'}")
    summary.append(f"Summary Report: {'✅ Available' if report_content else '❌ Missing'}")
    summary.append("")
    
    summary.append("📋 NEXT STEPS")
    summary.append("-" * 45)
    summary.append("• For detailed analysis, run: python main.py")
    summary.append("• For branch breakdowns, check data/processed/ directory")
    summary.append("• For charts and visualizations, run specific generators")
    summary.append("")
    
    return "\n".join(summary)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate quick volunteer metrics summary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Quick summary
  %(prog)s --details          # Detailed summary with raw data analysis
  %(prog)s --output report.txt # Save to file
        """
    )
    
    parser.add_argument(
        '--details', 
        action='store_true',
        help='Include detailed analysis from raw data (slower)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save output to file instead of printing to console'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress log output, only show summary'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.quiet:
        logger.setLevel(logging.ERROR)
    
    try:
        logger.info("Generating quick volunteer metrics summary...")
        
        # Generate the summary
        summary_text = generate_quick_summary(include_details=args.details)
        
        # Output the summary
        if args.output:
            # Save to file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(summary_text)
            
            print(f"Summary saved to: {args.output}")
            if not args.quiet:
                logger.info(f"Summary saved to: {args.output}")
        else:
            # Print to console
            print(summary_text)
        
        logger.info("Quick summary generation completed successfully")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
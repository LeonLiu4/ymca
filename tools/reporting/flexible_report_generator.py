#!/usr/bin/env python3
"""
Flexible Report Generator with Custom Date Range Support

This module extends the existing report generation capabilities to support
flexible date ranges, allowing users to generate reports for any custom
date range instead of just standard monthly periods.
"""

import pandas as pd
import datetime as dt
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import find_latest_file
from src.processors.date_range_processor import DateRangeProcessor
from src.processors.report_generator import ReportGenerator

logger = setup_logger(__name__, 'flexible_report_generator.log')


class FlexibleReportGenerator(ReportGenerator):
    """Extended report generator with flexible date range support"""
    
    def __init__(self, data_dir: str = "data/processed"):
        super().__init__(data_dir)
        self.date_processor = DateRangeProcessor()
        self.filtered_data = {}
        self.date_range_info = None
        
    def load_and_filter_data_by_date_range(self, start_date: dt.date, end_date: dt.date,
                                         source_data_dir: str = "data/raw") -> bool:
        """
        Load raw data and filter by the specified date range
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            source_data_dir: Directory containing raw data files
            
        Returns:
            True if data was successfully loaded and filtered
        """
        logger.info(f"📅 Loading and filtering data for date range: {start_date} to {end_date}")
        
        # Store date range info
        self.date_range_info = {
            'start_date': start_date,
            'end_date': end_date,
            'description': self.date_processor.get_period_description(start_date, end_date),
            'range_days': (end_date - start_date).days + 1
        }
        
        # Find the most recent volunteer history file
        volunteer_files = []
        import glob
        patterns = [
            os.path.join(source_data_dir, "VolunteerHistory_*.xlsx"),
            os.path.join(source_data_dir, "VolunteerHistory_*.csv")
        ]
        
        for pattern in patterns:
            volunteer_files.extend(glob.glob(pattern))
        
        if not volunteer_files:
            logger.error(f"❌ No volunteer history files found in {source_data_dir}")
            return False
        
        # Use the most recent file
        latest_file = max(volunteer_files, key=os.path.getmtime)
        logger.info(f"📂 Loading data from: {os.path.basename(latest_file)}")
        
        try:
            # Load the raw data
            if latest_file.endswith('.xlsx'):
                df = pd.read_excel(latest_file)
            else:
                df = pd.read_csv(latest_file)
            
            logger.info(f"📊 Loaded {len(df)} total records")
            
            # Find date columns (common names)
            date_columns = []
            for col in df.columns:
                if any(date_term in col.lower() for date_term in ['date', 'datetime', 'time']):
                    date_columns.append(col)
            
            if not date_columns:
                logger.warning("⚠️ No date columns found - using all data without date filtering")
                self.raw_data = df
                return True
            
            logger.info(f"🔍 Found date columns: {date_columns}")
            
            # Convert date columns to datetime
            for col in date_columns:
                try:
                    df[col] = pd.to_datetime(df[col]).dt.date
                    logger.debug(f"Converted {col} to date format")
                except Exception as e:
                    logger.warning(f"Could not convert {col} to date: {e}")
            
            # Filter by date range using the primary date column
            primary_date_col = self._identify_primary_date_column(date_columns, df)
            if primary_date_col:
                logger.info(f"📅 Filtering by {primary_date_col}: {start_date} to {end_date}")
                
                # Filter the data
                mask = (df[primary_date_col] >= start_date) & (df[primary_date_col] <= end_date)
                filtered_df = df[mask]
                
                logger.info(f"✅ Filtered to {len(filtered_df)} records ({len(df) - len(filtered_df)} excluded)")
                
                if len(filtered_df) == 0:
                    logger.warning("⚠️ No records found in the specified date range")
                    return False
                
                self.raw_data = filtered_df
                
                # Log date range statistics
                actual_start = filtered_df[primary_date_col].min()
                actual_end = filtered_df[primary_date_col].max()
                logger.info(f"📈 Actual data range: {actual_start} to {actual_end}")
                
            else:
                logger.warning("⚠️ Could not identify primary date column - using all data")
                self.raw_data = df
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            return False
    
    def _identify_primary_date_column(self, date_columns: List[str], df: pd.DataFrame) -> Optional[str]:
        """Identify the primary date column for filtering"""
        # Prioritize common volunteer date column names
        priority_names = ['volunteerdate', 'volunteer_date', 'date', 'activity_date', 'session_date']
        
        for priority in priority_names:
            for col in date_columns:
                if priority in col.lower():
                    logger.debug(f"Selected {col} as primary date column (priority match)")
                    return col
        
        # Fallback to first date column with most non-null values
        if date_columns:
            best_col = max(date_columns, key=lambda col: df[col].notna().sum())
            logger.debug(f"Selected {best_col} as primary date column (most data)")
            return best_col
        
        return None
    
    def process_filtered_data_for_reporting(self) -> bool:
        """Process the filtered raw data into reporting format"""
        if not hasattr(self, 'raw_data') or self.raw_data is None:
            logger.error("❌ No raw data available - call load_and_filter_data_by_date_range first")
            return False
        
        logger.info("🔄 Processing filtered data for reporting...")
        
        try:
            # Simulate the data processing steps that would normally be done
            # by the data preparation pipeline, but for our filtered dataset
            df = self.raw_data.copy()
            
            # Create statistics data similar to the existing pipeline
            # This is a simplified version - in a real implementation,
            # you'd want to use the actual data preparation logic
            
            stats_sheets = {}
            
            # Hours statistics
            if 'hours' in df.columns:
                hours_by_project = df.groupby('project').agg({
                    'hours': 'sum'
                }).reset_index()
                hours_by_project.columns = ['PROJECT_TAG', 'TOTAL_HOURS']
                hours_by_project = hours_by_project.sort_values('TOTAL_HOURS', ascending=False)
                stats_sheets['Hours_Statistics'] = hours_by_project
            
            # Volunteer statistics
            if 'volunteerName' in df.columns or 'volunteer_name' in df.columns:
                volunteer_col = 'volunteerName' if 'volunteerName' in df.columns else 'volunteer_name'
                project_col = 'project' if 'project' in df.columns else 'PROJECT_TAG'
                
                volunteers_by_project = df.groupby(project_col)[volunteer_col].nunique().reset_index()
                volunteers_by_project.columns = ['PROJECT_CATALOG', 'UNIQUE_VOLUNTEERS']
                volunteers_by_project = volunteers_by_project.sort_values('UNIQUE_VOLUNTEERS', ascending=False)
                stats_sheets['Volunteers_Statistics'] = volunteers_by_project
            
            # Project statistics
            project_col = 'project' if 'project' in df.columns else 'PROJECT_TAG'
            if project_col in df.columns:
                projects = df[project_col].unique()
                project_stats = pd.DataFrame({'PROJECT_TAG': projects})
                stats_sheets['Projects_Statistics'] = project_stats
            
            # Store the processed statistics data
            self.statistics_data = stats_sheets
            
            logger.info(f"✅ Processed data into {len(stats_sheets)} statistical sheets")
            for sheet_name, sheet_df in stats_sheets.items():
                logger.info(f"  • {sheet_name}: {len(sheet_df)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing filtered data: {e}")
            return False
    
    def generate_custom_date_range_report(self, start_date_str: str, end_date_str: str,
                                        allow_future: bool = False, max_range_days: int = 1095,
                                        source_data_dir: str = "data/raw") -> Dict[str, Any]:
        """
        Generate a comprehensive report for a custom date range
        
        Args:
            start_date_str: Start date as string
            end_date_str: End date as string
            allow_future: Whether to allow future dates
            max_range_days: Maximum allowed range in days (default: 3 years)
            source_data_dir: Directory containing raw data files
            
        Returns:
            Dictionary with report generation results
        """
        logger.info("🚀 YMCA Flexible Date Range Report Generator")
        logger.info("=" * 60)
        
        # Parse and validate date range
        date_result = self.date_processor.create_date_range_from_strings(
            start_date_str, end_date_str, allow_future, max_range_days
        )
        
        if not date_result['success']:
            logger.error(f"❌ Date range validation failed: {date_result['error_message']}")
            return {
                'success': False,
                'error': date_result['error_message'],
                'date_validation': date_result['validation']
            }
        
        start_date = date_result['start_date']
        end_date = date_result['end_date']
        validation = date_result['validation']
        
        logger.info(f"📅 Generating report for: {start_date} to {end_date}")
        logger.info(f"📊 Period: {validation['range_type']} ({validation['range_days']} days)")
        
        # Load and filter data by date range
        if not self.load_and_filter_data_by_date_range(start_date, end_date, source_data_dir):
            return {
                'success': False,
                'error': 'Failed to load and filter data for the specified date range',
                'date_validation': validation
            }
        
        # Process the filtered data
        if not self.process_filtered_data_for_reporting():
            return {
                'success': False,
                'error': 'Failed to process filtered data for reporting',
                'date_validation': validation
            }
        
        # Generate analyses using the parent class methods
        hours_analysis = self.analyze_hours_statistics()
        volunteers_analysis = self.analyze_volunteer_statistics()
        projects_analysis = self.analyze_project_statistics()
        
        # Generate custom reports with date range context
        executive_summary = self.generate_custom_executive_summary(
            hours_analysis, volunteers_analysis, projects_analysis, validation
        )
        
        detailed_analysis = self.generate_custom_detailed_analysis(
            hours_analysis, volunteers_analysis, projects_analysis, validation
        )
        
        # Save reports with date range in filename
        exec_file, detail_file = self.save_custom_reports(
            executive_summary, detailed_analysis, validation
        )
        
        # Return comprehensive results
        results = {
            'success': True,
            'executive_summary_file': exec_file,
            'detailed_analysis_file': detail_file,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'description': self.date_range_info['description'],
                'days': validation['range_days'],
                'type': validation['range_type']
            },
            'data_stats': {
                'total_records': len(self.raw_data) if hasattr(self, 'raw_data') else 0,
                'date_range_actual': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            },
            'analyses': {
                'hours_analysis': hours_analysis,
                'volunteers_analysis': volunteers_analysis,
                'projects_analysis': projects_analysis
            },
            'date_validation': validation,
            'generation_timestamp': dt.datetime.now().isoformat()
        }
        
        logger.info("🎯 Custom Date Range Report Generation Complete!")
        logger.info(f"📋 Executive Summary: {os.path.basename(exec_file)}")
        logger.info(f"📊 Detailed Analysis: {os.path.basename(detail_file)}")
        logger.info(f"📈 Period: {self.date_range_info['description']}")
        
        return results
    
    def generate_custom_executive_summary(self, hours_analysis: Dict, volunteers_analysis: Dict,
                                        projects_analysis: Dict, validation: Dict) -> str:
        """Generate executive summary with custom date range context"""
        date_info = self.date_range_info
        
        summary_lines = [
            "=" * 80,
            "YMCA VOLUNTEER PROGRAM - CUSTOM DATE RANGE REPORT",
            "=" * 80,
            f"Generated: {dt.datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"Reporting Period: {date_info['description']}",
            f"Date Range: {date_info['start_date']} to {date_info['end_date']} ({date_info['range_days']} days)",
            f"Report Type: {validation['range_type'].title()} Analysis",
            "",
            "CUSTOM DATE RANGE METRICS OVERVIEW",
            "-" * 45,
            f"📊 Total Volunteer Hours: {hours_analysis.get('total_hours', 0):,.1f} hours",
            f"👥 Total Unique Volunteers: {volunteers_analysis.get('total_unique_volunteers', 0):,}",
            f"🏗️ Total Project Categories: {projects_analysis.get('total_unique_projects', 0)}",
            f"📈 Average Hours per Project: {hours_analysis.get('average_hours_per_project', 0):,.1f} hours",
            f"👨‍👩‍👧‍👦 Average Volunteers per Category: {volunteers_analysis.get('average_volunteers_per_category', 0):,.1f}",
            "",
            f"PERIOD-SPECIFIC INSIGHTS ({date_info['description']})",
            "-" * 50
        ]
        
        # Add period-specific insights
        total_hours = hours_analysis.get('total_hours', 0)
        total_volunteers = volunteers_analysis.get('total_unique_volunteers', 0)
        days = date_info['range_days']
        
        if total_hours > 0 and days > 0:
            daily_avg_hours = total_hours / days
            summary_lines.extend([
                f"• Daily Average Hours: {daily_avg_hours:.1f} hours per day",
                f"• Period Intensity: {total_hours / days:.1f} hours/day across {days} days"
            ])
        
        if total_volunteers > 0 and days > 0:
            volunteer_engagement = total_volunteers / days if days <= 365 else total_volunteers / (days / 365)
            summary_lines.append(f"• Volunteer Engagement Rate: {volunteer_engagement:.1f} unique volunteers per day")
        
        # Add standard content from parent class
        summary_lines.extend([
            "",
            "TOP PERFORMING PROJECTS BY VOLUNTEER HOURS",
            "-" * 50
        ])
        
        for i, project in enumerate(hours_analysis.get('top_projects_by_hours', []), 1):
            summary_lines.append(f"{i:2d}. {project['PROJECT_TAG']}: {project['TOTAL_HOURS']:,.1f} hours")
        
        summary_lines.extend([
            "",
            "DATE RANGE VALIDATION SUMMARY",
            "-" * 35,
            f"• Validation Status: {'✅ Passed' if validation['is_valid'] else '❌ Failed'}",
            f"• Range Type: {validation['range_type'].title()}",
            f"• Total Days: {validation['range_days']} days"
        ])
        
        if validation['warnings']:
            summary_lines.append("• Warnings:")
            for warning in validation['warnings']:
                summary_lines.append(f"  - {warning}")
        
        summary_lines.extend([
            "",
            "=" * 80,
            f"End of Custom Date Range Report ({date_info['description']})",
            "=" * 80
        ])
        
        return "\n".join(summary_lines)
    
    def generate_custom_detailed_analysis(self, hours_analysis: Dict, volunteers_analysis: Dict,
                                        projects_analysis: Dict, validation: Dict) -> str:
        """Generate detailed analysis with custom date range context"""
        date_info = self.date_range_info
        
        # Use parent class method and extend with custom content
        standard_report = self.generate_detailed_analysis_report(
            hours_analysis, volunteers_analysis, projects_analysis, {}
        )
        
        # Replace the header with custom date range info
        lines = standard_report.split('\n')
        custom_lines = [
            "=" * 90,
            "YMCA VOLUNTEER PROGRAM - CUSTOM DATE RANGE DETAILED ANALYSIS",
            "=" * 90,
            f"Generated: {dt.datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"Custom Period: {date_info['description']}",
            f"Date Range: {date_info['start_date']} to {date_info['end_date']}",
            f"Analysis Duration: {date_info['range_days']} days ({validation['range_type']} period)",
            f"Data Source: Filtered volunteer data for specified date range",
        ]
        
        # Find where the original content starts (after the header)
        content_start = 0
        for i, line in enumerate(lines):
            if line.startswith("SECTION 1:"):
                content_start = i
                break
        
        # Combine custom header with original content
        custom_lines.extend(lines[content_start:])
        
        return "\n".join(custom_lines)
    
    def save_custom_reports(self, executive_summary: str, detailed_analysis: str,
                          validation: Dict, output_dir: str = None) -> Tuple[str, str]:
        """Save reports with custom date range in filename"""
        if output_dir is None:
            output_dir = self.data_dir
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        date_range_str = self.date_processor.format_date_range_for_filename(
            self.date_range_info['start_date'], self.date_range_info['end_date']
        )
        
        # Save executive summary
        exec_filename = f"YMCA_Executive_Summary_{date_range_str}_{timestamp}.txt"
        exec_filepath = os.path.join(output_dir, exec_filename)
        
        with open(exec_filepath, 'w') as f:
            f.write(executive_summary)
        
        # Save detailed analysis
        detail_filename = f"YMCA_Detailed_Analysis_{date_range_str}_{timestamp}.txt"
        detail_filepath = os.path.join(output_dir, detail_filename)
        
        with open(detail_filepath, 'w') as f:
            f.write(detailed_analysis)
        
        logger.info(f"✅ Custom executive summary saved: {exec_filepath}")
        logger.info(f"✅ Custom detailed analysis saved: {detail_filepath}")
        
        return exec_filepath, detail_filepath
    
    def get_available_date_ranges(self, source_data_dir: str = "data/raw") -> Dict[str, Any]:
        """Get information about available date ranges in the data"""
        logger.info("🔍 Analyzing available date ranges in data files...")
        
        # Find data files
        import glob
        data_files = glob.glob(os.path.join(source_data_dir, "VolunteerHistory_*.xlsx"))
        data_files.extend(glob.glob(os.path.join(source_data_dir, "VolunteerHistory_*.csv")))
        
        if not data_files:
            return {'files_found': 0, 'date_ranges': []}
        
        available_ranges = []
        
        for file_path in data_files:
            try:
                # Load file
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    df = pd.read_csv(file_path)
                
                # Find date columns
                date_cols = [col for col in df.columns 
                           if any(term in col.lower() for term in ['date', 'datetime', 'time'])]
                
                if date_cols:
                    primary_date_col = date_cols[0]  # Use first date column
                    df[primary_date_col] = pd.to_datetime(df[primary_date_col]).dt.date
                    
                    min_date = df[primary_date_col].min()
                    max_date = df[primary_date_col].max()
                    
                    available_ranges.append({
                        'file': os.path.basename(file_path),
                        'min_date': min_date.isoformat(),
                        'max_date': max_date.isoformat(),
                        'total_records': len(df),
                        'date_column': primary_date_col
                    })
                    
            except Exception as e:
                logger.warning(f"Could not analyze {os.path.basename(file_path)}: {e}")
        
        # Calculate overall date range
        overall_min = None
        overall_max = None
        total_records = 0
        
        for range_info in available_ranges:
            min_date = dt.date.fromisoformat(range_info['min_date'])
            max_date = dt.date.fromisoformat(range_info['max_date'])
            
            if overall_min is None or min_date < overall_min:
                overall_min = min_date
            if overall_max is None or max_date > overall_max:
                overall_max = max_date
            
            total_records += range_info['total_records']
        
        result = {
            'files_found': len(data_files),
            'files_analyzed': len(available_ranges),
            'date_ranges': available_ranges,
            'overall_range': {
                'min_date': overall_min.isoformat() if overall_min else None,
                'max_date': overall_max.isoformat() if overall_max else None,
                'total_records': total_records
            } if overall_min and overall_max else None,
            'common_suggestions': self.date_processor.suggest_common_ranges()
        }
        
        logger.info(f"📊 Found {result['files_analyzed']} analyzable files with date ranges")
        if result['overall_range']:
            logger.info(f"📅 Overall data spans: {result['overall_range']['min_date']} to {result['overall_range']['max_date']}")
        
        return result


def main():
    """Example usage of FlexibleReportGenerator"""
    generator = FlexibleReportGenerator()
    
    print("🗓️ YMCA Flexible Date Range Report Generator")
    print("=" * 50)
    
    # Show available data ranges
    available = generator.get_available_date_ranges()
    print(f"\n📊 Available Data Analysis:")
    print(f"  Files found: {available['files_found']}")
    print(f"  Files analyzed: {available['files_analyzed']}")
    
    if available['overall_range']:
        print(f"  Date range: {available['overall_range']['min_date']} to {available['overall_range']['max_date']}")
        print(f"  Total records: {available['overall_range']['total_records']:,}")
    
    # Show common range suggestions
    print("\n💡 Common Date Range Suggestions:")
    suggestions = available['common_suggestions']
    for i, (name, (start, end)) in enumerate(list(suggestions.items())[:5]):
        print(f"  {i+1}. {name}: {start} to {end}")
    
    # Example report generation (commented out to avoid running without user input)
    # print("\n🚀 Example: Generating Last 30 Days Report...")
    # result = generator.generate_custom_date_range_report("30 days ago", "today")
    # if result['success']:
    #     print(f"✅ Report generated successfully!")
    #     print(f"📋 Executive Summary: {os.path.basename(result['executive_summary_file'])}")
    # else:
    #     print(f"❌ Report generation failed: {result['error']}")


if __name__ == "__main__":
    main()
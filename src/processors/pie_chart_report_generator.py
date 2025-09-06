#!/usr/bin/env python3
"""
Pie Chart Report Generator for YMCA Volunteer Data

This script generates comprehensive reports from pie chart visualizations,
analyzing volunteer data across different dimensions like branches, projects,
and volunteer demographics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import os
import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, find_latest_file

logger = setup_logger(__name__, 'pie_chart_reports.log')

class PieChartReportGenerator:
    """Generate comprehensive reports from pie chart data analysis"""
    
    def __init__(self, data_file_path=None):
        """Initialize the pie chart report generator"""
        self.data_file_path = data_file_path
        self.df = None
        self.charts_data = {}
        self.reports = {}
        
    def load_data(self):
        """Load volunteer data for analysis"""
        if not self.data_file_path:
            # Find the most recent processed file
            self.data_file_path = find_latest_file("Raw_Data_*.xlsx", "data/processed")
            if not self.data_file_path:
                logger.error("❌ No data file found")
                return False
        
        logger.info(f"📁 Loading data from: {self.data_file_path}")
        self.df = load_excel_data(self.data_file_path)
        
        if self.df is None:
            logger.error("❌ Failed to load data")
            return False
            
        logger.info(f"✅ Loaded {len(self.df)} records for pie chart analysis")
        return True
    
    def extract_branch_info(self):
        """Extract branch information from assignment data"""
        import ast
        branches = []
        
        for idx, assignment in enumerate(self.df['assignment']):
            try:
                if isinstance(assignment, str):
                    assignment_data = ast.literal_eval(assignment)
                else:
                    assignment_data = assignment
                
                if ('need' in assignment_data and 
                    'project' in assignment_data['need'] and 
                    'branch' in assignment_data['need']['project']):
                    branch_name = assignment_data['need']['project']['branch']['name']
                    branches.append(branch_name)
                else:
                    branches.append('Unknown Branch')
                    
            except Exception as e:
                logger.warning(f"Error parsing assignment at row {idx}: {e}")
                branches.append('Unknown Branch')
        
        self.df['branch'] = branches
        logger.info(f"✅ Extracted branch information for {len(branches)} records")
        
    def generate_hours_by_branch_pie_chart(self, save_path="data/processed/charts"):
        """Generate pie chart for volunteer hours by branch"""
        logger.info("\n📊 Generating Hours by Branch Pie Chart...")
        
        # Ensure we have branch information
        if 'branch' not in self.df.columns:
            self.extract_branch_info()
        
        # Group hours by branch
        hours_by_branch = self.df.groupby('branch')['creditedHours'].sum().sort_values(ascending=False)
        
        # Store data for report generation
        self.charts_data['hours_by_branch'] = {
            'data': hours_by_branch,
            'total_hours': hours_by_branch.sum(),
            'branch_count': len(hours_by_branch),
            'top_branch': hours_by_branch.index[0] if len(hours_by_branch) > 0 else 'N/A',
            'top_branch_hours': hours_by_branch.iloc[0] if len(hours_by_branch) > 0 else 0
        }
        
        # Create the pie chart
        plt.figure(figsize=(12, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(hours_by_branch)))
        
        wedges, texts, autotexts = plt.pie(
            hours_by_branch.values, 
            labels=hours_by_branch.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        plt.title('Volunteer Hours Distribution by Branch', fontsize=16, fontweight='bold')
        
        # Enhance readability
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        # Save the chart
        Path(save_path).mkdir(parents=True, exist_ok=True)
        chart_filename = f"{save_path}/hours_by_branch_pie_chart_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ Hours by Branch pie chart saved: {chart_filename}")
        return chart_filename
    
    def generate_volunteers_by_project_pie_chart(self, save_path="data/processed/charts"):
        """Generate pie chart for volunteer count by project assignment"""
        logger.info("\n📊 Generating Volunteers by Project Pie Chart...")
        
        # Group volunteers by assignment (project)
        volunteers_by_project = self.df['assignment'].value_counts().head(10)  # Top 10 for readability
        
        # Store data for report generation
        self.charts_data['volunteers_by_project'] = {
            'data': volunteers_by_project,
            'total_assignments': len(self.df),
            'unique_projects': len(self.df['assignment'].unique()),
            'top_project': volunteers_by_project.index[0] if len(volunteers_by_project) > 0 else 'N/A',
            'top_project_count': volunteers_by_project.iloc[0] if len(volunteers_by_project) > 0 else 0
        }
        
        # Create the pie chart
        plt.figure(figsize=(14, 10))
        colors = plt.cm.Set1(np.linspace(0, 1, len(volunteers_by_project)))
        
        wedges, texts, autotexts = plt.pie(
            volunteers_by_project.values, 
            labels=[str(label)[:50] + '...' if len(str(label)) > 50 else str(label) for label in volunteers_by_project.index],
            autopct='%1.1f%%',
            colors=colors,
            startangle=45
        )
        
        plt.title('Top 10 Volunteer Assignments Distribution', fontsize=16, fontweight='bold')
        
        # Enhance readability
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # Save the chart
        Path(save_path).mkdir(parents=True, exist_ok=True)
        chart_filename = f"{save_path}/volunteers_by_project_pie_chart_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ Volunteers by Project pie chart saved: {chart_filename}")
        return chart_filename
    
    def generate_monthly_activity_pie_chart(self, save_path="data/processed/charts"):
        """Generate pie chart for volunteer activity by month"""
        logger.info("\n📊 Generating Monthly Activity Pie Chart...")
        
        # Extract month from volunteerDate
        self.df['volunteer_month'] = pd.to_datetime(self.df['volunteerDate']).dt.strftime('%B %Y')
        monthly_activity = self.df['volunteer_month'].value_counts().sort_index()
        
        # Store data for report generation
        self.charts_data['monthly_activity'] = {
            'data': monthly_activity,
            'total_records': len(self.df),
            'active_months': len(monthly_activity),
            'peak_month': monthly_activity.idxmax() if len(monthly_activity) > 0 else 'N/A',
            'peak_month_count': monthly_activity.max() if len(monthly_activity) > 0 else 0
        }
        
        # Create the pie chart
        plt.figure(figsize=(12, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(monthly_activity)))
        
        wedges, texts, autotexts = plt.pie(
            monthly_activity.values, 
            labels=monthly_activity.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        plt.title('Volunteer Activity Distribution by Month', fontsize=16, fontweight='bold')
        
        # Enhance readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Save the chart
        Path(save_path).mkdir(parents=True, exist_ok=True)
        chart_filename = f"{save_path}/monthly_activity_pie_chart_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ Monthly Activity pie chart saved: {chart_filename}")
        return chart_filename
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive text report from all pie chart data"""
        logger.info("\n📝 Generating Comprehensive Pie Chart Report...")
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("YMCA VOLUNTEER DATA - PIE CHART ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Report Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Data Source: {os.path.basename(self.data_file_path)}")
        report_lines.append(f"Total Records Analyzed: {len(self.df)}")
        report_lines.append("")
        
        # Hours by Branch Analysis
        if 'hours_by_branch' in self.charts_data:
            data = self.charts_data['hours_by_branch']
            report_lines.append("📊 VOLUNTEER HOURS BY BRANCH ANALYSIS")
            report_lines.append("-" * 50)
            report_lines.append(f"Total Volunteer Hours: {data['total_hours']:.1f} hours")
            report_lines.append(f"Number of Active Branches: {data['branch_count']}")
            report_lines.append(f"Top Performing Branch: {data['top_branch']}")
            report_lines.append(f"Hours at Top Branch: {data['top_branch_hours']:.1f} hours")
            report_lines.append("")
            
            report_lines.append("Branch Distribution:")
            for branch, hours in data['data'].head(10).items():
                percentage = (hours / data['total_hours']) * 100
                report_lines.append(f"  • {branch}: {hours:.1f} hours ({percentage:.1f}%)")
            report_lines.append("")
        
        # Volunteers by Project Analysis
        if 'volunteers_by_project' in self.charts_data:
            data = self.charts_data['volunteers_by_project']
            report_lines.append("👥 VOLUNTEER ASSIGNMENTS BY PROJECT ANALYSIS")
            report_lines.append("-" * 50)
            report_lines.append(f"Total Volunteer Assignments: {data['total_assignments']}")
            report_lines.append(f"Unique Projects: {data['unique_projects']}")
            report_lines.append(f"Most Popular Project: {str(data['top_project'])[:100]}")
            report_lines.append(f"Assignments for Top Project: {data['top_project_count']}")
            report_lines.append("")
            
            report_lines.append("Top Project Distribution:")
            for i, (project, count) in enumerate(data['data'].head(10).items(), 1):
                percentage = (count / data['total_assignments']) * 100
                project_short = str(project)[:60] + "..." if len(str(project)) > 60 else str(project)
                report_lines.append(f"  {i}. {project_short}: {count} assignments ({percentage:.1f}%)")
            report_lines.append("")
        
        # Monthly Activity Analysis
        if 'monthly_activity' in self.charts_data:
            data = self.charts_data['monthly_activity']
            report_lines.append("📅 MONTHLY VOLUNTEER ACTIVITY ANALYSIS")
            report_lines.append("-" * 50)
            report_lines.append(f"Total Activity Records: {data['total_records']}")
            report_lines.append(f"Active Months: {data['active_months']}")
            report_lines.append(f"Peak Activity Month: {data['peak_month']}")
            report_lines.append(f"Peak Month Activity: {data['peak_month_count']} records")
            report_lines.append("")
            
            report_lines.append("Monthly Distribution:")
            for month, count in data['data'].items():
                percentage = (count / data['total_records']) * 100
                report_lines.append(f"  • {month}: {count} activities ({percentage:.1f}%)")
            report_lines.append("")
        
        # Summary Insights
        report_lines.append("🔍 KEY INSIGHTS FROM PIE CHART ANALYSIS")
        report_lines.append("-" * 50)
        
        if 'hours_by_branch' in self.charts_data:
            hours_data = self.charts_data['hours_by_branch']
            top_branch_percentage = (hours_data['top_branch_hours'] / hours_data['total_hours']) * 100
            report_lines.append(f"• Branch Concentration: {hours_data['top_branch']} accounts for {top_branch_percentage:.1f}% of all hours")
        
        if 'volunteers_by_project' in self.charts_data:
            proj_data = self.charts_data['volunteers_by_project']
            top_proj_percentage = (proj_data['top_project_count'] / proj_data['total_assignments']) * 100
            report_lines.append(f"• Project Popularity: Top project represents {top_proj_percentage:.1f}% of all assignments")
        
        if 'monthly_activity' in self.charts_data:
            month_data = self.charts_data['monthly_activity']
            peak_percentage = (month_data['peak_month_count'] / month_data['total_records']) * 100
            report_lines.append(f"• Seasonal Pattern: {month_data['peak_month']} had {peak_percentage:.1f}% of all activity")
        
        report_lines.append("")
        report_lines.append("📈 RECOMMENDATIONS")
        report_lines.append("-" * 50)
        report_lines.append("• Focus resources on high-performing branches for maximum impact")
        report_lines.append("• Consider expanding popular project types to other branches")
        report_lines.append("• Plan recruitment and retention strategies around peak activity periods")
        report_lines.append("• Investigate low-performing areas for improvement opportunities")
        report_lines.append("")
        
        # Save the report
        report_content = "\n".join(report_lines)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"data/processed/Pie_Chart_Analysis_Report_{timestamp}.txt"
        
        Path("data/processed").mkdir(parents=True, exist_ok=True)
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        logger.info(f"✅ Comprehensive pie chart report saved: {report_filename}")
        return report_filename
    
    def generate_excel_summary(self):
        """Generate Excel summary of all pie chart analyses"""
        logger.info("\n📊 Generating Excel Summary from Pie Chart Data...")
        
        # Create summary data for each chart
        summary_sheets = {}
        
        # Hours by Branch Summary
        if 'hours_by_branch' in self.charts_data:
            hours_data = self.charts_data['hours_by_branch']['data']
            hours_df = pd.DataFrame({
                'Branch': hours_data.index,
                'Total_Hours': hours_data.values,
                'Percentage': (hours_data.values / hours_data.sum()) * 100
            })
            summary_sheets['Hours_by_Branch'] = hours_df
        
        # Volunteers by Project Summary  
        if 'volunteers_by_project' in self.charts_data:
            proj_data = self.charts_data['volunteers_by_project']['data']
            proj_df = pd.DataFrame({
                'Project': [str(p)[:100] for p in proj_data.index],  # Truncate long project names
                'Assignment_Count': proj_data.values,
                'Percentage': (proj_data.values / proj_data.sum()) * 100
            })
            summary_sheets['Top_Projects'] = proj_df
        
        # Monthly Activity Summary
        if 'monthly_activity' in self.charts_data:
            month_data = self.charts_data['monthly_activity']['data']
            month_df = pd.DataFrame({
                'Month': month_data.index,
                'Activity_Count': month_data.values,
                'Percentage': (month_data.values / month_data.sum()) * 100
            })
            summary_sheets['Monthly_Activity'] = month_df
        
        # Create Excel file
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"data/processed/Pie_Chart_Summary_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            for sheet_name, df in summary_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"✅ Excel summary saved: {excel_filename}")
        return excel_filename
    
    def generate_all_reports(self):
        """Generate all pie charts and reports"""
        logger.info("\n🚀 Generating All Pie Chart Reports...")
        
        if not self.load_data():
            return None
        
        # Generate all pie charts
        chart_files = []
        chart_files.append(self.generate_hours_by_branch_pie_chart())
        chart_files.append(self.generate_volunteers_by_project_pie_chart())
        chart_files.append(self.generate_monthly_activity_pie_chart())
        
        # Generate reports
        text_report = self.generate_comprehensive_report()
        excel_summary = self.generate_excel_summary()
        
        logger.info("\n🎯 PIE CHART ANALYSIS COMPLETE")
        logger.info("=" * 50)
        logger.info(f"📊 Charts Generated: {len(chart_files)}")
        logger.info(f"📝 Text Report: {text_report}")
        logger.info(f"📈 Excel Summary: {excel_summary}")
        
        return {
            'charts': chart_files,
            'text_report': text_report,
            'excel_summary': excel_summary,
            'charts_data': self.charts_data
        }


def main():
    """Main function to run pie chart report generation"""
    logger.info("📊 YMCA Volunteer Data - Pie Chart Report Generator")
    logger.info("=" * 70)
    
    # Create report generator
    generator = PieChartReportGenerator()
    
    # Generate all reports
    results = generator.generate_all_reports()
    
    if results:
        logger.info("\n✅ SUCCESS: All pie chart reports generated successfully!")
        logger.info("\nFiles created:")
        for chart in results['charts']:
            logger.info(f"  📊 Chart: {chart}")
        logger.info(f"  📝 Report: {results['text_report']}")
        logger.info(f"  📈 Excel: {results['excel_summary']}")
        
        logger.info("\n📋 Next Steps:")
        logger.info("1. Review generated pie charts for visual insights")
        logger.info("2. Read comprehensive text report for detailed analysis")
        logger.info("3. Use Excel summary for PowerPoint integration")
        logger.info("4. Share findings with YMCA leadership team")
    else:
        logger.error("❌ FAILED: Could not generate pie chart reports")
    
    return results


if __name__ == "__main__":
    results = main()
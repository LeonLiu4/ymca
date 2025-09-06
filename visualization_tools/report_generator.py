#!/usr/bin/env python3
"""
YMCA Volunteer Data Report Generator

This script generates comprehensive reports from bar graph data created by the 
volunteer data processing pipeline. It analyzes statistics from Excel files
and creates formatted reports suitable for presentations and stakeholder reviews.
"""

import pandas as pd
import datetime as dt
import os
from pathlib import Path
import sys
import glob
from typing import Dict, List, Tuple, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import find_latest_file

logger = setup_logger(__name__, 'report_generator.log')


class ReportGenerator:
    """Generate reports from YMCA volunteer bar graph data"""
    
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = data_dir
        self.statistics_data = {}
        self.branch_data = {}
        self.breakdown_data = {}
        
    def load_statistics_data(self) -> bool:
        """Load statistics data from Excel files"""
        logger.info("📊 Loading volunteer statistics data...")
        
        # Find the latest statistics file
        stats_file = find_latest_file("Y_Volunteer_2025_Statistics_*.xlsx", self.data_dir)
        if not stats_file:
            logger.error("❌ No statistics Excel file found")
            return False
            
        try:
            # Load all sheets from statistics file
            excel_data = pd.read_excel(stats_file, sheet_name=None)
            self.statistics_data = excel_data
            
            logger.info(f"✅ Loaded statistics data from: {os.path.basename(stats_file)}")
            logger.info(f"Available sheets: {list(excel_data.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading statistics data: {e}")
            return False
    
    def load_branch_data(self) -> bool:
        """Load branch breakdown data from Excel files"""
        logger.info("🏢 Loading branch breakdown data...")
        
        # Find the latest branch breakdown file
        branch_file = find_latest_file("Y_Volunteer_2025_Branch_Breakdown_*.xlsx", self.data_dir)
        if not branch_file:
            logger.warning("⚠️ No branch breakdown Excel file found")
            return False
            
        try:
            # Load all sheets from branch file
            excel_data = pd.read_excel(branch_file, sheet_name=None)
            self.branch_data = excel_data
            
            logger.info(f"✅ Loaded branch data from: {os.path.basename(branch_file)}")
            logger.info(f"Available sheets: {list(excel_data.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading branch data: {e}")
            return False
    
    def analyze_hours_statistics(self) -> Dict:
        """Analyze hours statistics from bar graph data"""
        logger.info("\n📈 Analyzing Hours Statistics...")
        
        if 'Hours_Statistics' not in self.statistics_data:
            logger.warning("⚠️ Hours statistics data not found")
            return {}
            
        hours_df = self.statistics_data['Hours_Statistics']
        
        analysis = {
            'total_projects': len(hours_df),
            'total_hours': hours_df['TOTAL_HOURS'].sum(),
            'average_hours_per_project': hours_df['TOTAL_HOURS'].mean(),
            'top_projects_by_hours': hours_df.head(5).to_dict('records'),
            'hours_distribution': {
                'high_impact': len(hours_df[hours_df['TOTAL_HOURS'] >= hours_df['TOTAL_HOURS'].quantile(0.8)]),
                'medium_impact': len(hours_df[(hours_df['TOTAL_HOURS'] >= hours_df['TOTAL_HOURS'].quantile(0.4)) & 
                                            (hours_df['TOTAL_HOURS'] < hours_df['TOTAL_HOURS'].quantile(0.8))]),
                'low_impact': len(hours_df[hours_df['TOTAL_HOURS'] < hours_df['TOTAL_HOURS'].quantile(0.4)])
            }
        }
        
        logger.info(f"  • Total Projects: {analysis['total_projects']}")
        logger.info(f"  • Total Hours: {analysis['total_hours']:.1f}")
        logger.info(f"  • Average Hours per Project: {analysis['average_hours_per_project']:.1f}")
        
        return analysis
    
    def analyze_volunteer_statistics(self) -> Dict:
        """Analyze volunteer statistics from bar graph data"""
        logger.info("\n👥 Analyzing Volunteer Statistics...")
        
        if 'Volunteers_Statistics' not in self.statistics_data:
            logger.warning("⚠️ Volunteer statistics data not found")
            return {}
            
        volunteers_df = self.statistics_data['Volunteers_Statistics']
        
        analysis = {
            'total_project_categories': len(volunteers_df),
            'total_unique_volunteers': volunteers_df['UNIQUE_VOLUNTEERS'].sum(),
            'average_volunteers_per_category': volunteers_df['UNIQUE_VOLUNTEERS'].mean(),
            'top_categories_by_volunteers': volunteers_df.head(5).to_dict('records'),
            'volunteer_engagement': {
                'highly_engaged': len(volunteers_df[volunteers_df['UNIQUE_VOLUNTEERS'] >= volunteers_df['UNIQUE_VOLUNTEERS'].quantile(0.8)]),
                'moderately_engaged': len(volunteers_df[(volunteers_df['UNIQUE_VOLUNTEERS'] >= volunteers_df['UNIQUE_VOLUNTEERS'].quantile(0.4)) & 
                                                       (volunteers_df['UNIQUE_VOLUNTEERS'] < volunteers_df['UNIQUE_VOLUNTEERS'].quantile(0.8))]),
                'low_engaged': len(volunteers_df[volunteers_df['UNIQUE_VOLUNTEERS'] < volunteers_df['UNIQUE_VOLUNTEERS'].quantile(0.4)])
            }
        }
        
        logger.info(f"  • Total Project Categories: {analysis['total_project_categories']}")
        logger.info(f"  • Total Unique Volunteers: {analysis['total_unique_volunteers']}")
        logger.info(f"  • Average Volunteers per Category: {analysis['average_volunteers_per_category']:.1f}")
        
        return analysis
    
    def analyze_project_statistics(self) -> Dict:
        """Analyze project statistics from bar graph data"""
        logger.info("\n🏗️ Analyzing Project Statistics...")
        
        if 'Projects_Statistics' not in self.statistics_data:
            logger.warning("⚠️ Project statistics data not found")
            return {}
            
        projects_df = self.statistics_data['Projects_Statistics']
        
        analysis = {
            'total_unique_projects': len(projects_df),
            'project_categories': projects_df['PROJECT_TAG'].tolist(),
            'project_distribution': projects_df.to_dict('records')
        }
        
        logger.info(f"  • Total Unique Projects: {analysis['total_unique_projects']}")
        logger.info(f"  • Project Categories: {', '.join(analysis['project_categories'][:5])}")
        
        return analysis
    
    def analyze_branch_breakdown(self) -> Dict:
        """Analyze branch breakdown data if available"""
        logger.info("\n🏢 Analyzing Branch Breakdown...")
        
        if not self.branch_data:
            logger.warning("⚠️ Branch breakdown data not available")
            return {}
            
        # Try to find branch statistics in the data
        branch_analysis = {}
        
        for sheet_name, df in self.branch_data.items():
            if 'branch' in sheet_name.lower():
                logger.info(f"  • Processing sheet: {sheet_name}")
                branch_analysis[sheet_name] = {
                    'total_records': len(df),
                    'columns': list(df.columns),
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                }
        
        return branch_analysis
    
    def generate_executive_summary(self, hours_analysis: Dict, volunteers_analysis: Dict, 
                                 projects_analysis: Dict) -> str:
        """Generate executive summary report"""
        logger.info("\n📋 Generating Executive Summary...")
        
        summary_lines = [
            "=" * 80,
            "YMCA VOLUNTEER PROGRAM - EXECUTIVE SUMMARY REPORT",
            "=" * 80,
            f"Generated: {dt.datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"Reporting Period: January - August 2025",
            "",
            "KEY METRICS OVERVIEW",
            "-" * 40,
            f"📊 Total Volunteer Hours: {hours_analysis.get('total_hours', 0):,.1f} hours",
            f"👥 Total Unique Volunteers: {volunteers_analysis.get('total_unique_volunteers', 0):,}",
            f"🏗️ Total Project Categories: {projects_analysis.get('total_unique_projects', 0)}",
            f"📈 Average Hours per Project: {hours_analysis.get('average_hours_per_project', 0):,.1f} hours",
            f"👨‍👩‍👧‍👦 Average Volunteers per Category: {volunteers_analysis.get('average_volunteers_per_category', 0):,.1f}",
            "",
            "TOP PERFORMING PROJECTS BY VOLUNTEER HOURS",
            "-" * 50
        ]
        
        # Add top projects by hours
        for i, project in enumerate(hours_analysis.get('top_projects_by_hours', []), 1):
            summary_lines.append(f"{i:2d}. {project['PROJECT_TAG']}: {project['TOTAL_HOURS']:,.1f} hours")
        
        summary_lines.extend([
            "",
            "TOP PROJECT CATEGORIES BY VOLUNTEER PARTICIPATION",
            "-" * 55
        ])
        
        # Add top categories by volunteers
        for i, category in enumerate(volunteers_analysis.get('top_categories_by_volunteers', []), 1):
            summary_lines.append(f"{i:2d}. {category['PROJECT_CATALOG']}: {category['UNIQUE_VOLUNTEERS']:,} volunteers")
        
        summary_lines.extend([
            "",
            "PROJECT IMPACT DISTRIBUTION",
            "-" * 30,
            "Hours Impact Distribution:",
        ])
        
        hours_dist = hours_analysis.get('hours_distribution', {})
        summary_lines.extend([
            f"  • High Impact Projects (Top 20%): {hours_dist.get('high_impact', 0)} projects",
            f"  • Medium Impact Projects (40-80%): {hours_dist.get('medium_impact', 0)} projects", 
            f"  • Developing Projects (Bottom 40%): {hours_dist.get('low_impact', 0)} projects",
            "",
            "Volunteer Engagement Distribution:",
        ])
        
        volunteer_dist = volunteers_analysis.get('volunteer_engagement', {})
        summary_lines.extend([
            f"  • Highly Engaged Categories (Top 20%): {volunteer_dist.get('highly_engaged', 0)} categories",
            f"  • Moderately Engaged Categories (40-80%): {volunteer_dist.get('moderately_engaged', 0)} categories",
            f"  • Growing Categories (Bottom 40%): {volunteer_dist.get('low_engaged', 0)} categories",
            "",
            "INSIGHTS & RECOMMENDATIONS",
            "-" * 35,
        ])
        
        # Generate insights based on data
        total_hours = hours_analysis.get('total_hours', 0)
        total_volunteers = volunteers_analysis.get('total_unique_volunteers', 0)
        
        if total_hours > 0 and total_volunteers > 0:
            avg_hours_per_volunteer = total_hours / total_volunteers
            summary_lines.extend([
                f"• Average volunteer contribution: {avg_hours_per_volunteer:.1f} hours per volunteer",
                f"• Community impact: {total_hours:,.0f} hours of service delivered",
            ])
            
            if avg_hours_per_volunteer > 10:
                summary_lines.append("• Strong volunteer retention and engagement indicated")
            else:
                summary_lines.append("• Opportunity to increase volunteer engagement and retention")
        
        # Add project diversity insights
        num_projects = projects_analysis.get('total_unique_projects', 0)
        if num_projects >= 6:
            summary_lines.append("• Strong program diversity with comprehensive service offerings")
        elif num_projects >= 3:
            summary_lines.append("• Good program foundation with opportunity for expansion")
        else:
            summary_lines.append("• Focused program approach with potential for diversification")
        
        summary_lines.extend([
            "",
            "NEXT STEPS",
            "-" * 15,
            "1. Review top-performing projects for best practice replication",
            "2. Analyze growth opportunities in lower-engagement categories", 
            "3. Consider volunteer recognition programs for high-contributing individuals",
            "4. Evaluate resource allocation based on project impact metrics",
            "5. Plan expansion strategies for successful program models",
            "",
            "=" * 80,
            "End of Executive Summary Report",
            "=" * 80
        ])
        
        return "\n".join(summary_lines)
    
    def generate_detailed_analysis_report(self, hours_analysis: Dict, volunteers_analysis: Dict,
                                        projects_analysis: Dict, branch_analysis: Dict) -> str:
        """Generate detailed analysis report"""
        logger.info("\n📊 Generating Detailed Analysis Report...")
        
        report_lines = [
            "=" * 90,
            "YMCA VOLUNTEER PROGRAM - DETAILED ANALYSIS REPORT",
            "=" * 90,
            f"Generated: {dt.datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"Data Source: Processed volunteer statistics and bar graph data",
            f"Analysis Period: January - August 2025",
            "",
            "SECTION 1: VOLUNTEER HOURS ANALYSIS",
            "=" * 45,
            ""
        ]
        
        # Detailed hours analysis
        if hours_analysis:
            report_lines.extend([
                f"Total Volunteer Hours Contributed: {hours_analysis.get('total_hours', 0):,.2f} hours",
                f"Number of Project Categories: {hours_analysis.get('total_projects', 0)}",
                f"Average Hours per Project Category: {hours_analysis.get('average_hours_per_project', 0):,.2f} hours",
                "",
                "Top 5 Projects by Total Hours:",
                "-" * 35
            ])
            
            for i, project in enumerate(hours_analysis.get('top_projects_by_hours', []), 1):
                hours = project.get('TOTAL_HOURS', 0)
                percentage = (hours / hours_analysis.get('total_hours', 1)) * 100
                report_lines.append(f"{i}. {project.get('PROJECT_TAG', 'N/A')}")
                report_lines.append(f"   Hours: {hours:,.1f} ({percentage:.1f}% of total)")
                report_lines.append("")
        
        # Detailed volunteer analysis
        report_lines.extend([
            "",
            "SECTION 2: VOLUNTEER PARTICIPATION ANALYSIS", 
            "=" * 50,
            ""
        ])
        
        if volunteers_analysis:
            report_lines.extend([
                f"Total Unique Volunteers: {volunteers_analysis.get('total_unique_volunteers', 0):,}",
                f"Number of Project Categories: {volunteers_analysis.get('total_project_categories', 0)}",
                f"Average Volunteers per Category: {volunteers_analysis.get('average_volunteers_per_category', 0):,.1f}",
                "",
                "Top 5 Categories by Volunteer Count:",
                "-" * 40
            ])
            
            for i, category in enumerate(volunteers_analysis.get('top_categories_by_volunteers', []), 1):
                volunteers = category.get('UNIQUE_VOLUNTEERS', 0)
                percentage = (volunteers / volunteers_analysis.get('total_unique_volunteers', 1)) * 100
                report_lines.append(f"{i}. {category.get('PROJECT_CATALOG', 'N/A')}")
                report_lines.append(f"   Volunteers: {volunteers:,} ({percentage:.1f}% of total)")
                report_lines.append("")
        
        # Project diversity analysis
        report_lines.extend([
            "",
            "SECTION 3: PROJECT DIVERSITY ANALYSIS",
            "=" * 45,
            ""
        ])
        
        if projects_analysis:
            report_lines.extend([
                f"Total Unique Projects: {projects_analysis.get('total_unique_projects', 0)}",
                "",
                "Project Categories:",
                "-" * 20
            ])
            
            for i, category in enumerate(projects_analysis.get('project_categories', []), 1):
                report_lines.append(f"{i}. {category}")
        
        # Branch analysis if available
        if branch_analysis:
            report_lines.extend([
                "",
                "SECTION 4: BRANCH BREAKDOWN ANALYSIS",
                "=" * 45,
                ""
            ])
            
            for sheet_name, data in branch_analysis.items():
                report_lines.extend([
                    f"Data Source: {sheet_name}",
                    f"Total Records: {data.get('total_records', 0):,}",
                    f"Available Columns: {', '.join(data.get('columns', []))}",
                    ""
                ])
        
        # Statistical insights
        report_lines.extend([
            "",
            "SECTION 5: STATISTICAL INSIGHTS",
            "=" * 40,
            ""
        ])
        
        if hours_analysis and volunteers_analysis:
            total_hours = hours_analysis.get('total_hours', 0)
            total_volunteers = volunteers_analysis.get('total_unique_volunteers', 0)
            
            if total_volunteers > 0:
                hours_per_volunteer = total_hours / total_volunteers
                report_lines.extend([
                    f"Average Hours per Volunteer: {hours_per_volunteer:.2f} hours",
                    f"Volunteer Productivity Index: {hours_per_volunteer:.1f}",
                    ""
                ])
                
                # Efficiency metrics
                if hours_per_volunteer > 15:
                    efficiency_rating = "High"
                elif hours_per_volunteer > 8:
                    efficiency_rating = "Moderate"
                else:
                    efficiency_rating = "Developing"
                
                report_lines.append(f"Program Efficiency Rating: {efficiency_rating}")
        
        report_lines.extend([
            "",
            "=" * 90,
            "End of Detailed Analysis Report",
            "=" * 90
        ])
        
        return "\n".join(report_lines)
    
    def save_reports(self, executive_summary: str, detailed_analysis: str, 
                     output_dir: str = None) -> Tuple[str, str]:
        """Save generated reports to files"""
        if output_dir is None:
            output_dir = self.data_dir
            
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save executive summary
        exec_filename = f"YMCA_Executive_Summary_{timestamp}.txt"
        exec_filepath = os.path.join(output_dir, exec_filename)
        
        with open(exec_filepath, 'w') as f:
            f.write(executive_summary)
        
        # Save detailed analysis
        detail_filename = f"YMCA_Detailed_Analysis_{timestamp}.txt"
        detail_filepath = os.path.join(output_dir, detail_filename)
        
        with open(detail_filepath, 'w') as f:
            f.write(detailed_analysis)
        
        logger.info(f"✅ Executive summary saved: {exec_filepath}")
        logger.info(f"✅ Detailed analysis saved: {detail_filepath}")
        
        return exec_filepath, detail_filepath
    
    def generate_bar_graph_report(self) -> Dict:
        """Main method to generate comprehensive bar graph reports"""
        logger.info("🚀 YMCA Volunteer Data - Bar Graph Report Generator")
        logger.info("=" * 70)
        
        # Load all data sources
        stats_loaded = self.load_statistics_data()
        branch_loaded = self.load_branch_data()
        
        if not stats_loaded:
            logger.error("❌ Cannot generate reports without statistics data")
            return {}
        
        # Perform analyses
        hours_analysis = self.analyze_hours_statistics()
        volunteers_analysis = self.analyze_volunteer_statistics() 
        projects_analysis = self.analyze_project_statistics()
        branch_analysis = self.analyze_branch_breakdown() if branch_loaded else {}
        
        # Generate reports
        executive_summary = self.generate_executive_summary(
            hours_analysis, volunteers_analysis, projects_analysis
        )
        
        detailed_analysis = self.generate_detailed_analysis_report(
            hours_analysis, volunteers_analysis, projects_analysis, branch_analysis
        )
        
        # Save reports
        exec_file, detail_file = self.save_reports(executive_summary, detailed_analysis)
        
        # Return results
        results = {
            'executive_summary_file': exec_file,
            'detailed_analysis_file': detail_file,
            'hours_analysis': hours_analysis,
            'volunteers_analysis': volunteers_analysis, 
            'projects_analysis': projects_analysis,
            'branch_analysis': branch_analysis,
            'generation_timestamp': dt.datetime.now().isoformat()
        }
        
        logger.info("\n🎯 Report Generation Complete!")
        logger.info(f"📋 Executive Summary: {os.path.basename(exec_file)}")
        logger.info(f"📊 Detailed Analysis: {os.path.basename(detail_file)}")
        logger.info("📈 Reports ready for stakeholder review and presentation")
        
        return results


def main():
    """Main function to run the report generator"""
    generator = ReportGenerator()
    results = generator.generate_bar_graph_report()
    
    if results:
        logger.info("\n✅ Bar graph reports generated successfully!")
        logger.info("📁 Check the data/processed directory for report files")
    else:
        logger.error("❌ Failed to generate reports")


if __name__ == "__main__":
    main()
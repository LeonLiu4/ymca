#!/usr/bin/env python3
"""
YMCA Volunteer Line Graph Report Generator

This script generates line graph reports from the processed volunteer data.
It creates visual reports showing trends in volunteer hours, participation,
and activity across different time periods and categories.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import seaborn as sns

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, find_latest_file

logger = setup_logger(__name__, 'line_graph_report.log')

# Set matplotlib style for better-looking graphs
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_processed_data():
    """Load the latest processed volunteer data"""
    logger.info("📊 Loading processed volunteer data...")
    
    # Find the most recent raw data file
    latest_file = find_latest_file("Raw_Data_*.xlsx", "data/processed")
    if not latest_file:
        logger.error("❌ No Raw_Data_*.xlsx files found in data/processed directory")
        return None
    
    logger.info(f"📁 Using file: {latest_file}")
    df = load_excel_data(latest_file)
    
    if df is not None:
        # Convert volunteerDate to datetime
        df['volunteerDate'] = pd.to_datetime(df['volunteerDate'])
        logger.info(f"✅ Loaded {len(df)} records from {df['volunteerDate'].min()} to {df['volunteerDate'].max()}")
    
    return df

def create_daily_hours_trend(df, output_dir="data/processed/reports"):
    """Generate line graph showing daily volunteer hours trend"""
    logger.info("📈 Creating daily volunteer hours trend line graph...")
    
    # Group by date and sum hours
    daily_hours = df.groupby('volunteerDate')['creditedHours'].sum().reset_index()
    daily_hours = daily_hours.sort_values('volunteerDate')
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_hours['volunteerDate'], daily_hours['creditedHours'], 
            marker='o', linewidth=2, markersize=4, color='#2E8B57')
    
    # Formatting
    ax.set_title('Daily Volunteer Hours Trend', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Total Hours', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45)
    
    # Add statistics text
    total_hours = daily_hours['creditedHours'].sum()
    avg_daily = daily_hours['creditedHours'].mean()
    max_day = daily_hours.loc[daily_hours['creditedHours'].idxmax()]
    
    stats_text = f'Total Hours: {total_hours:.1f}\nAvg Daily: {avg_daily:.1f}\nPeak Day: {max_day["volunteerDate"].strftime("%m/%d")} ({max_day["creditedHours"]:.1f}h)'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = f"daily_hours_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Daily hours trend graph saved: {filepath}")
    return filepath

def create_weekly_volunteer_participation(df, output_dir="data/processed/reports"):
    """Generate line graph showing weekly volunteer participation"""
    logger.info("📈 Creating weekly volunteer participation line graph...")
    
    # Add week column
    df['week'] = df['volunteerDate'].dt.to_period('W')
    
    # Count unique volunteers per week (deduplicated)
    weekly_volunteers = df.groupby('week')['volunteerDate'].count().reset_index()
    weekly_volunteers['week_start'] = weekly_volunteers['week'].dt.start_time
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(weekly_volunteers['week_start'], weekly_volunteers['volunteerDate'], 
            marker='s', linewidth=2, markersize=6, color='#4169E1')
    
    # Formatting
    ax.set_title('Weekly Volunteer Participation', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Week Starting', fontsize=12)
    ax.set_ylabel('Number of Volunteer Sessions', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45)
    
    # Add statistics
    total_sessions = weekly_volunteers['volunteerDate'].sum()
    avg_weekly = weekly_volunteers['volunteerDate'].mean()
    peak_week = weekly_volunteers.loc[weekly_volunteers['volunteerDate'].idxmax()]
    
    stats_text = f'Total Sessions: {total_sessions}\nAvg Weekly: {avg_weekly:.1f}\nPeak Week: {peak_week["week_start"].strftime("%m/%d")} ({peak_week["volunteerDate"]} sessions)'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    filename = f"weekly_participation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Weekly participation graph saved: {filepath}")
    return filepath

def create_top_projects_trend(df, top_n=5, output_dir="data/processed/reports"):
    """Generate line graph showing trends for top N projects by total hours"""
    logger.info(f"📈 Creating top {top_n} projects trend line graph...")
    
    # Find top projects by total hours
    top_projects = df.groupby('assignment')['creditedHours'].sum().nlargest(top_n).index.tolist()
    
    # Filter data for top projects
    df_top = df[df['assignment'].isin(top_projects)].copy()
    df_top['week'] = df_top['volunteerDate'].dt.to_period('W')
    
    # Group by week and project
    weekly_project_hours = df_top.groupby(['week', 'assignment'])['creditedHours'].sum().unstack(fill_value=0)
    weekly_project_hours.index = weekly_project_hours.index.to_timestamp()
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot line for each project
    for project in weekly_project_hours.columns:
        ax.plot(weekly_project_hours.index, weekly_project_hours[project], 
                marker='o', linewidth=2, markersize=4, label=project[:30] + '...' if len(project) > 30 else project)
    
    # Formatting
    ax.set_title(f'Weekly Hours Trend - Top {top_n} Projects', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Week Starting', fontsize=12)
    ax.set_ylabel('Weekly Hours', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save the plot
    filename = f"top_projects_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Top projects trend graph saved: {filepath}")
    return filepath

def create_cumulative_hours_report(df, output_dir="data/processed/reports"):
    """Generate cumulative hours line graph over time"""
    logger.info("📈 Creating cumulative hours report line graph...")
    
    # Sort by date and calculate cumulative hours
    df_sorted = df.sort_values('volunteerDate')
    daily_hours = df_sorted.groupby('volunteerDate')['creditedHours'].sum().reset_index()
    daily_hours['cumulative_hours'] = daily_hours['creditedHours'].cumsum()
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_hours['volunteerDate'], daily_hours['cumulative_hours'], 
            linewidth=3, color='#DC143C')
    ax.fill_between(daily_hours['volunteerDate'], daily_hours['cumulative_hours'], 
                    alpha=0.3, color='#DC143C')
    
    # Formatting
    ax.set_title('Cumulative Volunteer Hours Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Hours', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45)
    
    # Add milestone markers
    total_hours = daily_hours['cumulative_hours'].max()
    milestones = [1000, 2500, 5000, total_hours * 0.5, total_hours * 0.75]
    
    for milestone in milestones:
        if milestone <= total_hours:
            milestone_date = daily_hours[daily_hours['cumulative_hours'] >= milestone].iloc[0]['volunteerDate']
            ax.axhline(y=milestone, color='gray', linestyle='--', alpha=0.5)
            ax.axvline(x=milestone_date, color='gray', linestyle='--', alpha=0.5)
            ax.text(milestone_date, milestone, f'{milestone:.0f}h', 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    
    # Save the plot
    filename = f"cumulative_hours_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Cumulative hours graph saved: {filepath}")
    return filepath

def generate_summary_report(df, graph_files, output_dir="data/processed/reports"):
    """Generate a text summary report with graph references"""
    logger.info("📝 Generating summary report with line graph analysis...")
    
    # Calculate key metrics
    total_records = len(df)
    total_hours = df['creditedHours'].sum()
    date_range = f"{df['volunteerDate'].min().strftime('%Y-%m-%d')} to {df['volunteerDate'].max().strftime('%Y-%m-%d')}"
    unique_projects = df['assignment'].nunique()
    
    # Daily statistics
    daily_hours = df.groupby('volunteerDate')['creditedHours'].sum()
    avg_daily_hours = daily_hours.mean()
    peak_day = daily_hours.idxmax()
    peak_hours = daily_hours.max()
    
    # Weekly statistics
    df['week'] = df['volunteerDate'].dt.to_period('W')
    weekly_sessions = df.groupby('week').size()
    avg_weekly_sessions = weekly_sessions.mean()
    
    # Top projects
    top_projects = df.groupby('assignment')['creditedHours'].sum().nlargest(5)
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"line_graph_analysis_report_{timestamp}.txt"
    report_filepath = os.path.join(output_dir, report_filename)
    
    with open(report_filepath, 'w') as f:
        f.write("🏊‍♂️ YMCA Volunteer Line Graph Analysis Report\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data Period: {date_range}\n\n")
        
        f.write("📊 SUMMARY STATISTICS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Records: {total_records:,}\n")
        f.write(f"Total Hours: {total_hours:,.1f}\n")
        f.write(f"Unique Projects: {unique_projects}\n")
        f.write(f"Average Daily Hours: {avg_daily_hours:.1f}\n")
        f.write(f"Average Weekly Sessions: {avg_weekly_sessions:.1f}\n")
        f.write(f"Peak Day: {peak_day.strftime('%Y-%m-%d')} ({peak_hours:.1f} hours)\n\n")
        
        f.write("📈 GENERATED LINE GRAPHS\n")
        f.write("-" * 30 + "\n")
        for i, graph_file in enumerate(graph_files, 1):
            graph_name = os.path.basename(graph_file)
            f.write(f"{i}. {graph_name}\n")
            f.write(f"   Path: {graph_file}\n")
        f.write("\n")
        
        f.write("🏆 TOP 5 PROJECTS BY HOURS\n")
        f.write("-" * 30 + "\n")
        for i, (project, hours) in enumerate(top_projects.items(), 1):
            f.write(f"{i}. {project[:50]}{'...' if len(project) > 50 else ''}\n")
            f.write(f"   Total Hours: {hours:.1f}\n")
        f.write("\n")
        
        f.write("📋 REPORT USAGE NOTES\n")
        f.write("-" * 30 + "\n")
        f.write("• Line graphs provide visual trends and patterns in volunteer data\n")
        f.write("• Daily trends show activity fluctuations over time\n")
        f.write("• Weekly participation reveals engagement patterns\n")
        f.write("• Project trends identify high-impact activities\n")
        f.write("• Cumulative hours show overall program growth\n")
        f.write("• All graphs are saved in PNG format for presentations\n")
        f.write("• Use these visualizations in PowerPoint reports and dashboards\n")
    
    logger.info(f"✅ Summary report saved: {report_filepath}")
    return report_filepath

def main():
    """Main function to generate all line graph reports"""
    logger.info("📊 YMCA Volunteer Line Graph Report Generator")
    logger.info("=" * 60)
    
    # Load data
    df = load_processed_data()
    if df is None:
        logger.error("❌ Failed to load data. Exiting.")
        return
    
    # Create output directory
    output_dir = "data/processed/reports"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate all line graphs
    graph_files = []
    
    try:
        # Daily hours trend
        graph_file = create_daily_hours_trend(df, output_dir)
        graph_files.append(graph_file)
        
        # Weekly participation
        graph_file = create_weekly_volunteer_participation(df, output_dir)
        graph_files.append(graph_file)
        
        # Top projects trend
        graph_file = create_top_projects_trend(df, top_n=5, output_dir=output_dir)
        graph_files.append(graph_file)
        
        # Cumulative hours
        graph_file = create_cumulative_hours_report(df, output_dir)
        graph_files.append(graph_file)
        
        # Generate summary report
        summary_report = generate_summary_report(df, graph_files, output_dir)
        
        logger.info("\n🎯 LINE GRAPH REPORT GENERATION COMPLETE")
        logger.info(f"📁 Reports saved to: {output_dir}")
        logger.info(f"📊 Generated {len(graph_files)} line graphs")
        logger.info(f"📝 Summary report: {summary_report}")
        
        logger.info("\n📋 GENERATED FILES:")
        for graph_file in graph_files:
            logger.info(f"  • {os.path.basename(graph_file)}")
        logger.info(f"  • {os.path.basename(summary_report)}")
        
        return {
            'graph_files': graph_files,
            'summary_report': summary_report,
            'output_dir': output_dir
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating line graph reports: {str(e)}")
        return None

if __name__ == "__main__":
    results = main()
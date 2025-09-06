import pandas as pd
import datetime as dt
import os
from pathlib import Path
import sys
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import find_latest_file
from src.processors.scatterplot_generator import generate_all_scatterplots, load_volunteer_data

logger = setup_logger(__name__, 'scatterplot_report_generator.log')

def analyze_scatterplot_data(scatterplot_data):
    """Analyze data extracted from scatterplots to generate insights"""
    logger.info("\n🔍 Analyzing scatterplot data for insights...")
    
    insights = {
        'executive_summary': {},
        'project_analysis': {},
        'temporal_analysis': {},
        'efficiency_analysis': {},
        'recommendations': []
    }
    
    # Extract data components
    project_data = scatterplot_data['data']['project_volunteers']
    efficiency_data = scatterplot_data['data']['efficiency']
    monthly_data = scatterplot_data['data']['monthly_trends']
    
    # Executive Summary Analysis
    total_projects = len(project_data)
    total_sessions = project_data['volunteer_sessions'].sum()
    total_hours = project_data['total_hours'].sum()
    avg_hours_per_project = total_hours / total_projects if total_projects > 0 else 0
    
    insights['executive_summary'] = {
        'total_projects': total_projects,
        'total_volunteer_sessions': int(total_sessions),
        'total_hours_logged': round(total_hours, 1),
        'average_hours_per_project': round(avg_hours_per_project, 1),
        'most_active_months': monthly_data.groupby('month')['total_hours'].sum().nlargest(3).to_dict()
    }
    
    # Project Analysis
    top_projects_by_hours = project_data.nlargest(5, 'total_hours')[['assignment', 'total_hours', 'volunteer_sessions']]
    top_projects_by_sessions = project_data.nlargest(5, 'volunteer_sessions')[['assignment', 'volunteer_sessions', 'total_hours']]
    
    insights['project_analysis'] = {
        'highest_impact_projects': top_projects_by_hours.to_dict('records'),
        'most_popular_projects': top_projects_by_sessions.to_dict('records'),
        'underutilized_projects': project_data.nsmallest(3, 'volunteer_sessions')[['assignment', 'volunteer_sessions', 'total_hours']].to_dict('records')
    }
    
    # Temporal Analysis
    monthly_totals = monthly_data.groupby('month').agg({
        'total_hours': 'sum',
        'volunteer_count': 'sum'
    }).round(1)
    
    peak_month = monthly_totals['total_hours'].idxmax()
    low_month = monthly_totals['total_hours'].idxmin()
    
    insights['temporal_analysis'] = {
        'peak_activity_month': int(peak_month),
        'peak_month_hours': round(monthly_totals.loc[peak_month, 'total_hours'], 1),
        'lowest_activity_month': int(low_month),
        'low_month_hours': round(monthly_totals.loc[low_month, 'total_hours'], 1),
        'monthly_breakdown': monthly_totals.to_dict('index')
    }
    
    # Efficiency Analysis
    most_efficient = efficiency_data.nlargest(3, 'avg_hours_per_session')[['assignment', 'avg_hours_per_session', 'total_sessions']]
    least_efficient = efficiency_data.nsmallest(3, 'avg_hours_per_session')[['assignment', 'avg_hours_per_session', 'total_sessions']]
    
    insights['efficiency_analysis'] = {
        'most_efficient_projects': most_efficient.to_dict('records'),
        'least_efficient_projects': least_efficient.to_dict('records'),
        'average_efficiency': round(efficiency_data['avg_hours_per_session'].mean(), 2)
    }
    
    # Generate Recommendations
    recommendations = []
    
    # Recommendation 1: Focus on high-impact projects
    if len(top_projects_by_hours) > 0:
        top_project = top_projects_by_hours.iloc[0]
        recommendations.append(f"Continue prioritizing '{top_project['assignment']}' - it generated {top_project['total_hours']} hours from {top_project['volunteer_sessions']} sessions")
    
    # Recommendation 2: Address underutilized projects
    if len(insights['project_analysis']['underutilized_projects']) > 0:
        underutilized = insights['project_analysis']['underutilized_projects'][0]
        recommendations.append(f"Review '{underutilized['assignment']}' project - only {underutilized['volunteer_sessions']} sessions logged")
    
    # Recommendation 3: Seasonal planning
    peak_month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][peak_month - 1]
    recommendations.append(f"Plan major initiatives around {peak_month_name} when volunteer engagement peaks")
    
    # Recommendation 4: Efficiency improvements
    if insights['efficiency_analysis']['average_efficiency'] < 5:
        recommendations.append("Average session efficiency is low (<5 hours/session) - consider longer commitment programs")
    
    insights['recommendations'] = recommendations
    
    logger.info(f"✅ Generated {len(recommendations)} recommendations from scatterplot analysis")
    return insights

def create_scatterplot_report_excel(insights, scatterplot_data, output_dir="data/processed"):
    """Create comprehensive Excel report from scatterplot analysis"""
    logger.info("\n📊 Creating Excel report from scatterplot analysis...")
    
    # Generate filename
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"YMCA_Scatterplot_Analysis_Report_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        
        # Executive Summary Sheet
        exec_summary = pd.DataFrame([
            ['Total Projects Analyzed', insights['executive_summary']['total_projects']],
            ['Total Volunteer Sessions', insights['executive_summary']['total_volunteer_sessions']],
            ['Total Hours Logged', insights['executive_summary']['total_hours_logged']],
            ['Average Hours per Project', insights['executive_summary']['average_hours_per_project']],
            ['Report Generated', dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ], columns=['Metric', 'Value'])
        exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        # Project Analysis Sheet
        project_df = pd.DataFrame(insights['project_analysis']['highest_impact_projects'])
        project_df.to_excel(writer, sheet_name='Top_Projects_by_Impact', index=False)
        
        popular_df = pd.DataFrame(insights['project_analysis']['most_popular_projects'])
        popular_df.to_excel(writer, sheet_name='Most_Popular_Projects', index=False)
        
        # Efficiency Analysis Sheet
        efficiency_df = pd.DataFrame(insights['efficiency_analysis']['most_efficient_projects'])
        efficiency_df.to_excel(writer, sheet_name='Most_Efficient_Projects', index=False)
        
        # Monthly Trends Sheet
        monthly_df = pd.DataFrame.from_dict(insights['temporal_analysis']['monthly_breakdown'], orient='index')
        monthly_df.reset_index(inplace=True)
        monthly_df.columns = ['Month', 'Total_Hours', 'Volunteer_Count']
        monthly_df.to_excel(writer, sheet_name='Monthly_Trends', index=False)
        
        # Recommendations Sheet
        recommendations_df = pd.DataFrame(insights['recommendations'], columns=['Recommendation'])
        recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        # Raw Scatterplot Data
        if 'project_volunteers' in scatterplot_data['data']:
            scatterplot_data['data']['project_volunteers'].to_excel(writer, sheet_name='Project_Data', index=False)
        
        if 'efficiency' in scatterplot_data['data']:
            scatterplot_data['data']['efficiency'].to_excel(writer, sheet_name='Efficiency_Data', index=False)
    
    logger.info(f"✅ Excel report saved: {filepath}")
    return filepath

def create_scatterplot_text_report(insights, output_dir="data/processed"):
    """Create comprehensive text report from scatterplot analysis"""
    logger.info("\n📝 Creating text report from scatterplot analysis...")
    
    # Generate filename
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"YMCA_Scatterplot_Analysis_Report_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write("🏊‍♂️ YMCA Volunteer Scatterplot Analysis Report\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Executive Summary
        f.write("📊 EXECUTIVE SUMMARY\n")
        f.write("-" * 30 + "\n")
        exec_sum = insights['executive_summary']
        f.write(f"Total Projects Analyzed: {exec_sum['total_projects']}\n")
        f.write(f"Total Volunteer Sessions: {exec_sum['total_volunteer_sessions']}\n")
        f.write(f"Total Hours Logged: {exec_sum['total_hours_logged']}\n")
        f.write(f"Average Hours per Project: {exec_sum['average_hours_per_project']}\n\n")
        
        # Project Analysis
        f.write("🎯 PROJECT IMPACT ANALYSIS\n")
        f.write("-" * 30 + "\n")
        f.write("Top 3 Projects by Total Hours:\n")
        for i, project in enumerate(insights['project_analysis']['highest_impact_projects'][:3], 1):
            f.write(f"  {i}. {project['assignment']}: {project['total_hours']} hours ({project['volunteer_sessions']} sessions)\n")
        
        f.write("\nMost Popular Projects (by sessions):\n")
        for i, project in enumerate(insights['project_analysis']['most_popular_projects'][:3], 1):
            f.write(f"  {i}. {project['assignment']}: {project['volunteer_sessions']} sessions ({project['total_hours']} hours)\n")
        
        f.write("\nUnderutilized Projects:\n")
        for i, project in enumerate(insights['project_analysis']['underutilized_projects'], 1):
            f.write(f"  {i}. {project['assignment']}: {project['volunteer_sessions']} sessions ({project['total_hours']} hours)\n")
        f.write("\n")
        
        # Temporal Analysis
        f.write("📅 TEMPORAL ANALYSIS\n")
        f.write("-" * 30 + "\n")
        temp_analysis = insights['temporal_analysis']
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        peak_month = month_names[temp_analysis['peak_activity_month'] - 1]
        low_month = month_names[temp_analysis['lowest_activity_month'] - 1]
        
        f.write(f"Peak Activity Month: {peak_month} ({temp_analysis['peak_month_hours']} hours)\n")
        f.write(f"Lowest Activity Month: {low_month} ({temp_analysis['low_month_hours']} hours)\n\n")
        
        # Efficiency Analysis
        f.write("⚡ EFFICIENCY ANALYSIS\n")
        f.write("-" * 30 + "\n")
        eff_analysis = insights['efficiency_analysis']
        f.write(f"Average Session Efficiency: {eff_analysis['average_efficiency']} hours/session\n\n")
        
        f.write("Most Efficient Projects:\n")
        for i, project in enumerate(eff_analysis['most_efficient_projects'], 1):
            f.write(f"  {i}. {project['assignment']}: {project['avg_hours_per_session']} hrs/session\n")
        f.write("\n")
        
        # Recommendations
        f.write("💡 RECOMMENDATIONS\n")
        f.write("-" * 30 + "\n")
        for i, rec in enumerate(insights['recommendations'], 1):
            f.write(f"{i}. {rec}\n")
        f.write("\n")
        
        # Data Sources
        f.write("📋 DATA SOURCES\n")
        f.write("-" * 30 + "\n")
        f.write("• Scatterplot 1: Hours vs Time (Monthly trends)\n")
        f.write("• Scatterplot 2: Volunteers vs Projects (Popularity analysis)\n")
        f.write("• Scatterplot 3: Efficiency Analysis (Hours per session)\n")
        f.write("• Scatterplot 4: Monthly Trends (Temporal patterns)\n\n")
        
        f.write("📈 VISUALIZATIONS GENERATED\n")
        f.write("-" * 30 + "\n")
        f.write("• hours_vs_time_scatterplot.png\n")
        f.write("• volunteers_vs_projects_scatterplot.png\n")
        f.write("• efficiency_scatterplot.png\n")
        f.write("• monthly_trends_scatterplot.png\n")
    
    logger.info(f"✅ Text report saved: {filepath}")
    return filepath

def update_comprehensive_summary_report(insights, output_dir="data/processed"):
    """Add scatterplot analysis to the comprehensive summary report"""
    logger.info("\n📝 Adding scatterplot analysis to comprehensive summary report...")
    
    summary_file = os.path.join(output_dir, "YMCA_Volunteer_Summary_Report.txt")
    
    with open(summary_file, 'a') as f:
        f.write(f"\nScatterplot Analysis Report\n")
        f.write("-" * 50 + "\n")
        f.write(f"Completed: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Key findings
        exec_sum = insights['executive_summary']
        f.write("🎯 Key Findings from Visual Analysis:\n")
        f.write(f"  • {exec_sum['total_projects']} projects analyzed across {exec_sum['total_volunteer_sessions']} sessions\n")
        f.write(f"  • Total volunteer effort: {exec_sum['total_hours_logged']} hours\n")
        f.write(f"  • Average project impact: {exec_sum['average_hours_per_project']} hours per project\n\n")
        
        # Top insights
        if insights['project_analysis']['highest_impact_projects']:
            top_project = insights['project_analysis']['highest_impact_projects'][0]
            f.write(f"📊 Highest Impact Project: {top_project['assignment']} ({top_project['total_hours']} hours)\n")
        
        temp_analysis = insights['temporal_analysis']
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        peak_month = month_names[temp_analysis['peak_activity_month'] - 1]
        f.write(f"📅 Peak Activity Period: {peak_month}\n")
        f.write(f"⚡ Average Session Efficiency: {insights['efficiency_analysis']['average_efficiency']} hours/session\n\n")
        
        # Visualizations created
        f.write("📈 Scatterplot Visualizations Created:\n")
        f.write("  • Hours vs Time trends\n")
        f.write("  • Project popularity analysis\n")
        f.write("  • Efficiency metrics\n")
        f.write("  • Monthly activity patterns\n\n")
    
    logger.info(f"✅ Comprehensive summary updated: {summary_file}")
    return summary_file

def main():
    """Main function to generate reports from scatterplots"""
    logger.info("📊 YMCA Volunteer Data - Scatterplot Report Generation")
    logger.info("=" * 70)
    
    # Find the most recent raw data file
    latest_file = find_latest_file("Raw_Data_*.xlsx", "data/processed")
    if not latest_file:
        logger.error("❌ No Raw_Data_*.xlsx files found in data/processed directory")
        return
    logger.info(f"📁 Using file: {latest_file}")
    
    # Load data
    df = load_volunteer_data(latest_file)
    if df is None:
        return
    
    # Generate scatterplots first
    logger.info("🎨 Step 1: Generating scatterplots...")
    scatterplot_results = generate_all_scatterplots(df)
    
    # Analyze scatterplot data
    logger.info("🔍 Step 2: Analyzing scatterplot data...")
    insights = analyze_scatterplot_data(scatterplot_results)
    
    # Create reports
    logger.info("📝 Step 3: Creating reports...")
    excel_report = create_scatterplot_report_excel(insights, scatterplot_results)
    text_report = create_scatterplot_text_report(insights)
    comprehensive_summary = update_comprehensive_summary_report(insights)
    
    # Final summary
    logger.info("\n🎯 SCATTERPLOT ANALYSIS COMPLETE")
    logger.info("=" * 50)
    logger.info(f"📊 Scatterplots Generated: {len(scatterplot_results['plots'])}")
    logger.info(f"📈 Excel Report: {os.path.basename(excel_report)}")
    logger.info(f"📝 Text Report: {os.path.basename(text_report)}")
    logger.info(f"📋 Summary Updated: {os.path.basename(comprehensive_summary)}")
    
    # Display key insights
    exec_sum = insights['executive_summary']
    logger.info(f"\n📊 Key Insights:")
    logger.info(f"  • Analyzed {exec_sum['total_projects']} projects")
    logger.info(f"  • Processed {exec_sum['total_volunteer_sessions']} volunteer sessions")
    logger.info(f"  • Total impact: {exec_sum['total_hours_logged']} hours")
    logger.info(f"  • Generated {len(insights['recommendations'])} actionable recommendations")
    
    logger.info("\n📋 Files Ready for Review:")
    logger.info("1. Scatterplot images in data/processed/scatterplots/")
    logger.info("2. Excel analysis report with multiple worksheets")
    logger.info("3. Text report with detailed findings")
    logger.info("4. Updated comprehensive summary report")
    
    return {
        'scatterplots': scatterplot_results,
        'insights': insights,
        'reports': {
            'excel': excel_report,
            'text': text_report,
            'summary': comprehensive_summary
        }
    }

if __name__ == "__main__":
    results = main()
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, find_latest_file

logger = setup_logger(__name__, 'scatterplot_generator.log')

def load_volunteer_data(file_path):
    """Load volunteer data from Excel file"""
    return load_excel_data(file_path)

def prepare_scatterplot_data(df):
    """Prepare data for scatterplot generation"""
    logger.info("\n📊 Preparing data for scatterplot generation...")
    
    # Extract date components for time-based analysis
    df['month'] = pd.to_datetime(df['volunteerDate']).dt.month
    df['day_of_month'] = pd.to_datetime(df['volunteerDate']).dt.day
    df['weekday'] = pd.to_datetime(df['volunteerDate']).dt.dayofweek
    
    # Create numeric mapping for assignments
    unique_assignments = df['assignment'].unique()
    assignment_mapping = {assignment: idx for idx, assignment in enumerate(unique_assignments)}
    df['assignment_numeric'] = df['assignment'].map(assignment_mapping)
    
    logger.info(f"Data prepared with {len(df)} records for visualization")
    return df, assignment_mapping

def create_hours_vs_time_scatterplot(df, output_dir):
    """Create scatterplot: Hours vs Time (by month)"""
    plt.figure(figsize=(12, 8))
    
    # Group data by month for better visualization
    monthly_data = df.groupby(['month', 'assignment'])['creditedHours'].sum().reset_index()
    
    # Create scatterplot
    sns.scatterplot(data=monthly_data, x='month', y='creditedHours', 
                   hue='assignment', size='creditedHours', sizes=(50, 400), alpha=0.7)
    
    plt.title('Volunteer Hours Distribution by Month and Project', fontsize=16, fontweight='bold')
    plt.xlabel('Month (2025)', fontsize=12)
    plt.ylabel('Total Credited Hours', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    filename = 'hours_vs_time_scatterplot.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Saved scatterplot: {filepath}")
    return filepath

def create_volunteers_vs_projects_scatterplot(df, output_dir):
    """Create scatterplot: Number of Volunteers vs Project Type"""
    plt.figure(figsize=(14, 10))
    
    # Calculate volunteers per project
    project_volunteers = df.groupby('assignment').agg({
        'volunteerDate': 'count',  # Total volunteer sessions
        'creditedHours': ['sum', 'mean']  # Total and average hours
    }).round(2)
    
    project_volunteers.columns = ['volunteer_sessions', 'total_hours', 'avg_hours_per_session']
    project_volunteers = project_volunteers.reset_index()
    
    # Create scatterplot
    scatter = plt.scatter(project_volunteers['volunteer_sessions'], 
                         project_volunteers['total_hours'],
                         s=project_volunteers['avg_hours_per_session'] * 50,
                         c=range(len(project_volunteers)), 
                         cmap='viridis', 
                         alpha=0.7,
                         edgecolors='black',
                         linewidth=1)
    
    # Add labels for each point
    for i, row in project_volunteers.iterrows():
        plt.annotate(row['assignment'][:20] + ('...' if len(row['assignment']) > 20 else ''), 
                    (row['volunteer_sessions'], row['total_hours']),
                    xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.8)
    
    plt.title('Project Analysis: Volunteer Sessions vs Total Hours\n(Bubble size = Average hours per session)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Number of Volunteer Sessions', fontsize=12)
    plt.ylabel('Total Hours', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Project Index', fontsize=10)
    
    plt.tight_layout()
    
    # Save plot
    filename = 'volunteers_vs_projects_scatterplot.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Saved scatterplot: {filepath}")
    return filepath, project_volunteers

def create_efficiency_scatterplot(df, output_dir):
    """Create scatterplot: Project Efficiency (Hours per session vs Total sessions)"""
    plt.figure(figsize=(12, 8))
    
    # Calculate efficiency metrics
    efficiency_data = df.groupby('assignment').agg({
        'volunteerDate': 'count',
        'creditedHours': ['sum', 'mean']
    }).round(2)
    
    efficiency_data.columns = ['total_sessions', 'total_hours', 'avg_hours_per_session']
    efficiency_data = efficiency_data.reset_index()
    
    # Create scatterplot
    sns.scatterplot(data=efficiency_data, 
                   x='total_sessions', 
                   y='avg_hours_per_session',
                   size='total_hours',
                   hue='assignment',
                   sizes=(100, 1000),
                   alpha=0.7)
    
    plt.title('Project Efficiency Analysis\n(Size = Total Hours)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Total Volunteer Sessions', fontsize=12)
    plt.ylabel('Average Hours per Session', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    filename = 'efficiency_scatterplot.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Saved scatterplot: {filepath}")
    return filepath, efficiency_data

def create_monthly_trends_scatterplot(df, output_dir):
    """Create scatterplot: Monthly trends across all projects"""
    plt.figure(figsize=(14, 8))
    
    # Prepare monthly aggregated data
    monthly_trends = df.groupby(['month', 'assignment']).agg({
        'creditedHours': 'sum',
        'volunteerDate': 'count'
    }).reset_index()
    
    monthly_trends.columns = ['month', 'assignment', 'total_hours', 'volunteer_count']
    
    # Create scatterplot
    sns.scatterplot(data=monthly_trends,
                   x='month',
                   y='total_hours',
                   hue='assignment',
                   size='volunteer_count',
                   sizes=(50, 500),
                   alpha=0.7)
    
    plt.title('Monthly Volunteer Activity Trends by Project', fontsize=16, fontweight='bold')
    plt.xlabel('Month (2025)', fontsize=12)
    plt.ylabel('Total Hours', fontsize=12)
    plt.xticks(range(1, 13))
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    filename = 'monthly_trends_scatterplot.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Saved scatterplot: {filepath}")
    return filepath, monthly_trends

def generate_all_scatterplots(df, output_dir="data/processed/scatterplots"):
    """Generate all scatterplots from volunteer data"""
    logger.info("\n🎨 Generating scatterplots from volunteer data...")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Prepare data
    df_prepared, assignment_mapping = prepare_scatterplot_data(df)
    
    # Generate all scatterplots
    plots_generated = []
    
    # 1. Hours vs Time
    plot1 = create_hours_vs_time_scatterplot(df_prepared, output_dir)
    plots_generated.append(plot1)
    
    # 2. Volunteers vs Projects
    plot2, project_data = create_volunteers_vs_projects_scatterplot(df_prepared, output_dir)
    plots_generated.append(plot2)
    
    # 3. Efficiency Analysis
    plot3, efficiency_data = create_efficiency_scatterplot(df_prepared, output_dir)
    plots_generated.append(plot3)
    
    # 4. Monthly Trends
    plot4, monthly_data = create_monthly_trends_scatterplot(df_prepared, output_dir)
    plots_generated.append(plot4)
    
    logger.info(f"✅ Generated {len(plots_generated)} scatterplots in {output_dir}")
    
    return {
        'plots': plots_generated,
        'data': {
            'project_volunteers': project_data,
            'efficiency': efficiency_data,
            'monthly_trends': monthly_data,
            'assignment_mapping': assignment_mapping
        }
    }

def main():
    """Main function to generate scatterplots from volunteer data"""
    logger.info("🎨 YMCA Volunteer Data - Scatterplot Generation")
    logger.info("=" * 60)
    
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
    
    # Generate scatterplots
    results = generate_all_scatterplots(df)
    
    logger.info("\n📊 Scatterplot Generation Complete:")
    for i, plot_path in enumerate(results['plots'], 1):
        logger.info(f"  {i}. {os.path.basename(plot_path)}")
    
    logger.info("\n📋 Next Steps:")
    logger.info("1. Review generated scatterplots for insights")
    logger.info("2. Run the report generator to create comprehensive analysis")
    logger.info("3. Use plots for presentations and documentation")
    
    return results

if __name__ == "__main__":
    results = main()
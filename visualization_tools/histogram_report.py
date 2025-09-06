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

logger = setup_logger(__name__, 'histogram_report.log')

plt.style.use('default')
sns.set_palette("husl")

def load_data_for_histograms(file_path):
    """Load processed volunteer data for histogram generation"""
    logger.info(f"📊 Loading data for histogram generation: {file_path}")
    return load_excel_data(file_path)

def create_hours_distribution_histogram(df, output_dir="data/processed"):
    """Create histogram showing distribution of volunteer hours"""
    logger.info("\n📊 Creating Hours Distribution Histogram...")
    
    # Find hours column
    hours_col = None
    for col in df.columns:
        if 'hour' in col.lower():
            hours_col = col
            break
    
    if hours_col is None:
        logger.error("❌ No hours column found for histogram")
        return None
    
    plt.figure(figsize=(12, 8))
    
    # Create histogram
    plt.hist(df[hours_col], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('Distribution of Volunteer Hours', fontsize=16, fontweight='bold')
    plt.xlabel('Hours', fontsize=12)
    plt.ylabel('Number of Records', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics text
    mean_hours = df[hours_col].mean()
    median_hours = df[hours_col].median()
    total_hours = df[hours_col].sum()
    
    stats_text = f'Mean: {mean_hours:.1f} hours\nMedian: {median_hours:.1f} hours\nTotal: {total_hours:.1f} hours'
    plt.text(0.7, 0.9, stats_text, transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             verticalalignment='top', fontsize=10)
    
    # Save histogram
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Histogram_Hours_Distribution_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Hours distribution histogram saved: {filepath}")
    return filepath

def create_projects_histogram(df, output_dir="data/processed"):
    """Create histogram showing volunteer hours by project/assignment"""
    logger.info("\n📊 Creating Projects Histogram...")
    
    # Find assignment and hours columns
    assignment_col = 'assignment' if 'assignment' in df.columns else None
    hours_col = None
    
    for col in df.columns:
        if 'hour' in col.lower():
            hours_col = col
            break
    
    if assignment_col is None or hours_col is None:
        logger.error("❌ Required columns not found for projects histogram")
        return None
    
    # Aggregate hours by project
    project_hours = df.groupby(assignment_col)[hours_col].sum().sort_values(ascending=True)
    
    plt.figure(figsize=(14, 8))
    
    # Create horizontal bar chart (better for long project names)
    bars = plt.barh(range(len(project_hours)), project_hours.values, 
                    color=plt.cm.viridis(range(len(project_hours))))
    
    plt.yticks(range(len(project_hours)), project_hours.index)
    plt.xlabel('Total Hours', fontsize=12)
    plt.ylabel('Projects/Assignments', fontsize=12)
    plt.title('Total Volunteer Hours by Project', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, project_hours.values)):
        plt.text(bar.get_width() + max(project_hours.values) * 0.01, bar.get_y() + bar.get_height()/2, 
                f'{value:.0f}h', ha='left', va='center', fontsize=9)
    
    # Save histogram
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Histogram_Projects_Hours_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Projects histogram saved: {filepath}")
    return filepath

def create_monthly_trends_histogram(df, output_dir="data/processed"):
    """Create histogram showing volunteer activity trends over months"""
    logger.info("\n📊 Creating Monthly Trends Histogram...")
    
    # Find date and hours columns
    date_col = None
    hours_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'date' in col_lower:
            date_col = col
        elif 'hour' in col_lower:
            hours_col = col
    
    if date_col is None or hours_col is None:
        logger.error("❌ Required columns not found for monthly trends histogram")
        return None
    
    # Convert date column to datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Extract month and aggregate
    df['month'] = df[date_col].dt.to_period('M')
    monthly_hours = df.groupby('month')[hours_col].sum()
    
    plt.figure(figsize=(12, 8))
    
    # Create bar chart
    bars = plt.bar(range(len(monthly_hours)), monthly_hours.values, 
                   color='coral', alpha=0.7, edgecolor='black')
    
    plt.xticks(range(len(monthly_hours)), [str(month) for month in monthly_hours.index], 
               rotation=45)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Total Hours', fontsize=12)
    plt.title('Monthly Volunteer Hours Trend', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, value in zip(bars, monthly_hours.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(monthly_hours.values) * 0.01, 
                f'{value:.0f}', ha='center', va='bottom', fontsize=10)
    
    # Save histogram
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Histogram_Monthly_Trends_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Monthly trends histogram saved: {filepath}")
    return filepath

def create_volunteer_frequency_histogram(df, output_dir="data/processed"):
    """Create histogram showing volunteer participation frequency"""
    logger.info("\n📊 Creating Volunteer Frequency Histogram...")
    
    # Find date column to count volunteer sessions
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break
    
    if date_col is None:
        logger.error("❌ No date column found for volunteer frequency histogram")
        return None
    
    # Count volunteer sessions (assuming each row is a volunteer session)
    session_counts = df.groupby(date_col).size()
    
    plt.figure(figsize=(12, 8))
    
    # Create histogram of session counts
    plt.hist(session_counts.values, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
    plt.title('Distribution of Daily Volunteer Sessions', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Volunteer Sessions per Day', fontsize=12)
    plt.ylabel('Number of Days', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_sessions = session_counts.mean()
    median_sessions = session_counts.median()
    max_sessions = session_counts.max()
    
    stats_text = f'Mean: {mean_sessions:.1f} sessions/day\nMedian: {median_sessions:.1f} sessions/day\nMax: {max_sessions} sessions/day'
    plt.text(0.7, 0.9, stats_text, transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
             verticalalignment='top', fontsize=10)
    
    # Save histogram
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Histogram_Volunteer_Frequency_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Volunteer frequency histogram saved: {filepath}")
    return filepath

def create_comprehensive_histogram_report(df, output_dir="data/processed"):
    """Create a comprehensive report with multiple histograms"""
    logger.info("\n📊 Creating Comprehensive Histogram Report...")
    
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('YMCA Volunteer Data - Histogram Report', fontsize=20, fontweight='bold')
    
    # Find required columns
    hours_col = None
    assignment_col = 'assignment' if 'assignment' in df.columns else None
    date_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'hour' in col_lower:
            hours_col = col
        elif 'date' in col_lower:
            date_col = col
    
    # Histogram 1: Hours distribution
    if hours_col:
        axes[0,0].hist(df[hours_col], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0,0].set_title('Hours Distribution')
        axes[0,0].set_xlabel('Hours')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].grid(True, alpha=0.3)
    
    # Histogram 2: Top projects by hours
    if assignment_col and hours_col:
        project_hours = df.groupby(assignment_col)[hours_col].sum().sort_values(ascending=False).head(8)
        axes[0,1].barh(range(len(project_hours)), project_hours.values, color='coral')
        axes[0,1].set_yticks(range(len(project_hours)))
        axes[0,1].set_yticklabels([name[:20] + '...' if len(name) > 20 else name for name in project_hours.index])
        axes[0,1].set_title('Top Projects by Hours')
        axes[0,1].set_xlabel('Total Hours')
    
    # Histogram 3: Monthly trends
    if date_col and hours_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['month'] = df[date_col].dt.to_period('M')
        monthly_hours = df.groupby('month')[hours_col].sum()
        axes[1,0].bar(range(len(monthly_hours)), monthly_hours.values, color='lightgreen', alpha=0.7)
        axes[1,0].set_xticks(range(len(monthly_hours)))
        axes[1,0].set_xticklabels([str(month) for month in monthly_hours.index], rotation=45)
        axes[1,0].set_title('Monthly Hours Trend')
        axes[1,0].set_ylabel('Total Hours')
    
    # Histogram 4: Daily session frequency
    if date_col:
        session_counts = df.groupby(date_col).size()
        axes[1,1].hist(session_counts.values, bins=15, alpha=0.7, color='gold', edgecolor='black')
        axes[1,1].set_title('Daily Session Distribution')
        axes[1,1].set_xlabel('Sessions per Day')
        axes[1,1].set_ylabel('Number of Days')
        axes[1,1].grid(True, alpha=0.3)
    
    # Save comprehensive report
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Comprehensive_Histogram_Report_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✅ Comprehensive histogram report saved: {filepath}")
    return filepath

def create_summary_text_report(histograms, df, output_dir="data/processed"):
    """Create a text summary report of the histogram analysis"""
    logger.info("\n📝 Creating Histogram Analysis Summary...")
    
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Histogram_Analysis_Summary_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Calculate key statistics
    hours_col = None
    assignment_col = 'assignment' if 'assignment' in df.columns else None
    date_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'hour' in col_lower:
            hours_col = col
        elif 'date' in col_lower:
            date_col = col
    
    with open(filepath, 'w') as f:
        f.write("YMCA Volunteer Data - Histogram Analysis Summary\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Generated Histograms:\n")
        f.write("-" * 20 + "\n")
        for i, hist_file in enumerate(histograms, 1):
            if hist_file:
                f.write(f"{i}. {os.path.basename(hist_file)}\n")
        f.write("\n")
        
        if hours_col:
            f.write("Hours Analysis:\n")
            f.write("-" * 15 + "\n")
            f.write(f"Total Hours: {df[hours_col].sum():.1f}\n")
            f.write(f"Average Hours per Record: {df[hours_col].mean():.1f}\n")
            f.write(f"Median Hours: {df[hours_col].median():.1f}\n")
            f.write(f"Max Hours in Single Record: {df[hours_col].max():.1f}\n")
            f.write(f"Min Hours in Single Record: {df[hours_col].min():.1f}\n\n")
        
        if assignment_col and hours_col:
            project_hours = df.groupby(assignment_col)[hours_col].sum().sort_values(ascending=False)
            f.write("Top Projects by Hours:\n")
            f.write("-" * 22 + "\n")
            for i, (project, hours) in enumerate(project_hours.head(5).items(), 1):
                f.write(f"{i}. {project}: {hours:.1f} hours\n")
            f.write("\n")
        
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            date_range = f"{df[date_col].min().strftime('%Y-%m-%d')} to {df[date_col].max().strftime('%Y-%m-%d')}"
            f.write(f"Data Period: {date_range}\n")
            f.write(f"Total Records: {len(df)}\n")
            f.write(f"Unique Dates: {df[date_col].nunique()}\n\n")
        
        f.write("Histogram Insights:\n")
        f.write("-" * 18 + "\n")
        f.write("• Hours Distribution: Shows the frequency of different volunteer hour commitments\n")
        f.write("• Projects Analysis: Identifies which programs receive the most volunteer support\n")
        f.write("• Monthly Trends: Reveals seasonal patterns in volunteer activity\n")
        f.write("• Session Frequency: Shows daily volunteer participation patterns\n\n")
        
        f.write("Usage Notes:\n")
        f.write("-" * 12 + "\n")
        f.write("• All histogram images are saved in PNG format at 300 DPI\n")
        f.write("• Images are suitable for reports and presentations\n")
        f.write("• Data is based on processed volunteer records with zero hours removed\n")
        f.write("• Comprehensive report combines all visualizations in one image\n")
    
    logger.info(f"✅ Histogram analysis summary saved: {filepath}")
    return filepath

def clean_output_directory(output_dir="data/processed"):
    """Clean output directory of previous histogram files"""
    logger.info(f"🧹 Cleaning histogram files from: {output_dir}")
    
    import glob
    patterns_to_clean = [
        "Histogram_*.png",
        "Comprehensive_Histogram_Report_*.png",
        "Histogram_Analysis_Summary_*.txt"
    ]
    
    for pattern in patterns_to_clean:
        files_to_remove = glob.glob(os.path.join(output_dir, pattern))
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                logger.info(f"  • Removed: {os.path.basename(file_path)}")
            except Exception as e:
                logger.warning(f"  • Could not remove {file_path}: {e}")

def main():
    """Main function for histogram report generation"""
    logger.info("📊 YMCA Volunteer Data - Histogram Report Generator")
    logger.info("=" * 60)
    
    # Clean output directory first
    clean_output_directory()
    
    # Find the most recent processed data file
    latest_file = find_latest_file("Raw_Data_*.xlsx", "data/processed")
    if not latest_file:
        logger.error("❌ No Raw_Data_*.xlsx files found in data/processed directory")
        logger.info("💡 Run data extraction and preparation steps first")
        return
    
    logger.info(f"📁 Using data file: {latest_file}")
    
    # Load data
    df = load_data_for_histograms(latest_file)
    if df is None:
        return
    
    logger.info(f"📊 Loaded {len(df)} records for histogram generation")
    
    # Create output directory
    output_dir = "data/processed"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate individual histograms
    histogram_files = []
    
    # 1. Hours distribution histogram
    hours_hist = create_hours_distribution_histogram(df, output_dir)
    histogram_files.append(hours_hist)
    
    # 2. Projects histogram
    projects_hist = create_projects_histogram(df, output_dir)
    histogram_files.append(projects_hist)
    
    # 3. Monthly trends histogram
    monthly_hist = create_monthly_trends_histogram(df, output_dir)
    histogram_files.append(monthly_hist)
    
    # 4. Volunteer frequency histogram
    frequency_hist = create_volunteer_frequency_histogram(df, output_dir)
    histogram_files.append(frequency_hist)
    
    # 5. Comprehensive report
    comprehensive_hist = create_comprehensive_histogram_report(df, output_dir)
    histogram_files.append(comprehensive_hist)
    
    # 6. Generate summary text report
    summary_report = create_summary_text_report(histogram_files, df, output_dir)
    
    # Final summary
    logger.info("\n🎯 Histogram Report Generation Complete!")
    logger.info("=" * 45)
    logger.info("Generated Files:")
    
    for i, hist_file in enumerate(histogram_files, 1):
        if hist_file:
            logger.info(f"  {i}. {os.path.basename(hist_file)}")
    
    if summary_report:
        logger.info(f"  📝 {os.path.basename(summary_report)}")
    
    logger.info(f"\n📁 All files saved to: {output_dir}")
    logger.info("🖼️  Histogram images are ready for presentations and reports")
    
    return {
        'histogram_files': histogram_files,
        'summary_report': summary_report,
        'data_file_used': latest_file,
        'records_processed': len(df)
    }

if __name__ == "__main__":
    results = main()
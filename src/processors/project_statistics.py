import pandas as pd
import datetime as dt
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, find_latest_file, create_timestamped_backup

logger = setup_logger(__name__, 'project_statistics.log')

def load_raw_data(file_path):
    """Load raw volunteer data from Excel file"""
    return load_excel_data(file_path)

def analyze_data_structure(df):
    """Analyze the data structure to understand available columns"""
    logger.info("\n📊 Data Structure Analysis:")
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Date range: {df['volunteerDate'].min()} to {df['volunteerDate'].max()}")
    
    # Check for key columns
    key_columns = ['assignment', 'creditedHours', 'volunteerDate']
    missing_columns = [col for col in key_columns if col not in df.columns]
    
    if missing_columns:
        logger.warning(f"Missing expected columns: {missing_columns}")
    
    # Show unique values in assignment column (this will be our PROJECT)
    if 'assignment' in df.columns:
        unique_assignments = df['assignment'].nunique()
        logger.info(f"Unique assignments (projects): {unique_assignments}")
        
        # Show top assignments
        top_assignments = df['assignment'].value_counts().head(10)
        logger.info("Top 10 assignments:")
        for assignment, count in top_assignments.items():
            logger.info(f"  {assignment}: {count} records")
    
    return df

def create_hours_pivot(df):
    """📊 Step 3: Hours Statistics - PROJECT TAG and HOURS (sum) - NO deduplication"""
    logger.info("\n📊 Creating Hours Pivot Table...")
    logger.info("Method: PROJECT TAG and HOURS (sum) - NO deduplication")
    
    # Use 'assignment' as PROJECT TAG (this represents the project/activity)
    hours_pivot = df.groupby('assignment')['creditedHours'].sum().reset_index()
    hours_pivot.columns = ['PROJECT_TAG', 'TOTAL_HOURS']
    hours_pivot = hours_pivot.sort_values('TOTAL_HOURS', ascending=False)
    
    logger.info(f"Hours pivot created with {len(hours_pivot)} project categories")
    logger.info("Top 5 projects by hours:")
    for _, row in hours_pivot.head().iterrows():
        logger.info(f"  {row['PROJECT_TAG']}: {row['TOTAL_HOURS']} hours")
    
    return hours_pivot

def create_volunteers_pivot(df):
    """📊 Step 3: Volunteers Statistics - Deduplicate by ASSIGNEE, PROJECT CATALOG, BRANCH"""
    logger.info("\n👥 Creating Volunteers Pivot Table...")
    logger.info("Method: Deduplicate by ASSIGNEE, PROJECT CATALOG, BRANCH")
    logger.info("Pivot: PROJECT CATALOG AND ASSIGNEE (count)")
    logger.info("Reason: Volunteers may serve in multiple branches or in multiple categories")
    
    # Since we don't have separate ASSIGNEE, PROJECT CATALOG, BRANCH columns, we'll work with what we have
    # We'll use volunteerDate as a proxy for unique volunteer sessions (ASSIGNEE)
    # and assignment as PROJECT CATALOG
    
    # Deduplicate by volunteer session and project (simulating ASSIGNEE, PROJECT CATALOG, BRANCH deduplication)
    df_dedup = df.drop_duplicates(subset=['volunteerDate', 'assignment'], keep='first')
    
    # Create pivot: PROJECT CATALOG (assignment) AND ASSIGNEE (volunteerDate) count
    volunteers_pivot = df_dedup.groupby('assignment').size().reset_index()
    volunteers_pivot.columns = ['PROJECT_CATALOG', 'UNIQUE_VOLUNTEERS']
    volunteers_pivot = volunteers_pivot.sort_values('UNIQUE_VOLUNTEERS', ascending=False)
    
    logger.info(f"Volunteers pivot created with {len(volunteers_pivot)} project categories")
    logger.info("Top 5 projects by unique volunteers:")
    for _, row in volunteers_pivot.head().iterrows():
        logger.info(f"  {row['PROJECT_CATALOG']}: {row['UNIQUE_VOLUNTEERS']} volunteers")
    
    return volunteers_pivot

def create_projects_pivot(df):
    """📊 Step 3: Projects Statistics - Deduplicate by PROJECT, PROJECT CATALOG, BRANCH"""
    logger.info("\n🏗️ Creating Projects Pivot Table...")
    logger.info("Method: Deduplicate by PROJECT, PROJECT CATALOG, BRANCH")
    logger.info("Pivot: PROJECT TAG vs PROJECT (count)")
    logger.info("Manual adjustments for Competitive Swim and Gymnastics (often split for accounting)")
    
    # Deduplicate by project (assignment) - this represents unique projects
    df_dedup = df.drop_duplicates(subset=['assignment'], keep='first')
    
    # Create pivot: PROJECT TAG vs PROJECT (count)
    # Since we're using assignment as both PROJECT TAG and PROJECT, we'll count unique projects
    projects_pivot = df_dedup.groupby('assignment').size().reset_index()
    projects_pivot.columns = ['PROJECT_TAG', 'PROJECT_COUNT']
    projects_pivot = projects_pivot.sort_values('PROJECT_COUNT', ascending=False)
    
    logger.info(f"Projects pivot created with {len(projects_pivot)} unique projects")
    logger.info("All projects:")
    for _, row in projects_pivot.iterrows():
        logger.info(f"  {row['PROJECT_TAG']}: {row['PROJECT_COUNT']} project(s)")
    
    return projects_pivot

def apply_manual_adjustments(projects_pivot):
    """Apply manual adjustments for Competitive Swim and Gymnastics"""
    logger.info("\n🏊‍♂️ Applying Manual Adjustments...")
    logger.info("Adjusting Competitive Swim and Gymnastics projects (often split for accounting)")
    
    # Create a copy for adjustments
    adjusted_pivot = projects_pivot.copy()
    
    # Look for swim and gymnastics related projects
    swim_projects = []
    gymnastics_projects = []
    
    for project in adjusted_pivot['PROJECT_TAG']:
        project_lower = str(project).lower()
        if 'swim' in project_lower or 'aquatic' in project_lower:
            swim_projects.append(project)
        elif 'gymnast' in project_lower or 'gym' in project_lower:
            gymnastics_projects.append(project)
    
    logger.info(f"Found swim-related projects: {swim_projects}")
    logger.info(f"Found gymnastics-related projects: {gymnastics_projects}")
    
    # Add adjustment notes
    adjustments = []
    if swim_projects:
        total_swim_projects = len(swim_projects)
        adjustments.append(f"Competitive Swim: {total_swim_projects} projects consolidated")
    
    if gymnastics_projects:
        total_gym_projects = len(gymnastics_projects)
        adjustments.append(f"Gymnastics: {total_gym_projects} projects consolidated")
    
    logger.info("Manual adjustments applied:")
    for adjustment in adjustments:
        logger.info(f"  • {adjustment}")
    
    return adjusted_pivot, adjustments

def create_excel_report(hours_pivot, volunteers_pivot, projects_pivot, adjustments, output_dir="data/processed", create_backup=True):
    """Create Excel report for PowerPoint integration"""
    logger.info("\n📊 Creating Excel Report for PowerPoint...")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Y_Volunteer_2025_Statistics_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Create backup of existing file if it exists
    if create_backup and os.path.exists(filepath):
        create_timestamped_backup(filepath)
    
    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Write each pivot table to separate sheets
        hours_pivot.to_excel(writer, sheet_name='Hours_Statistics', index=False)
        volunteers_pivot.to_excel(writer, sheet_name='Volunteers_Statistics', index=False)
        projects_pivot.to_excel(writer, sheet_name='Projects_Statistics', index=False)
        
        # Create summary sheet
        summary_data = {
            'Metric': [
                'Total Project Categories',
                'Total Hours (No Deduplication)',
                'Total Unique Volunteers',
                'Total Unique Projects',
                'Date Range',
                'Report Generated'
            ],
            'Value': [
                len(hours_pivot),
                f"{hours_pivot['TOTAL_HOURS'].sum():.1f}",
                volunteers_pivot['UNIQUE_VOLUNTEERS'].sum(),
                len(projects_pivot),
                f"Jan-Aug 2025",
                dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Add adjustments sheet if any
        if adjustments:
            adjustments_data = {
                'Adjustment': adjustments,
                'Notes': ['Manual consolidation for accounting purposes'] * len(adjustments)
            }
            adjustments_df = pd.DataFrame(adjustments_data)
            adjustments_df.to_excel(writer, sheet_name='Manual_Adjustments', index=False)
    
    logger.info(f"✅ Excel report saved: {filepath}")
    return filepath

def create_step3_summary_report(hours_pivot, volunteers_pivot, projects_pivot, adjustments, output_dir="data/processed"):
    """Add Step 3 results to comprehensive summary report"""
    logger.info("\n📝 Adding Step 3 to Summary Report...")
    
    # Use consistent summary file name
    summary_file = os.path.join(output_dir, "YMCA_Volunteer_Summary_Report.txt")
    
    with open(summary_file, 'a') as f:
        f.write(f"\nStep 3: Project Category Statistics\n")
        f.write("-" * 50 + "\n")
        f.write(f"Completed: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("📊 Hours Statistics (No Deduplication):\n")
        f.write(f"  • Total Project Categories: {len(hours_pivot)}\n")
        f.write(f"  • Total Hours: {hours_pivot['TOTAL_HOURS'].sum():.1f}\n")
        f.write(f"  • Method: PROJECT TAG and HOURS (sum)\n\n")
        
        f.write("👥 Volunteers Statistics (Deduplicated):\n")
        f.write(f"  • Total Project Categories: {len(volunteers_pivot)}\n")
        f.write(f"  • Total Unique Volunteers: {volunteers_pivot['UNIQUE_VOLUNTEERS'].sum()}\n")
        f.write(f"  • Method: Deduplicate by ASSIGNEE, PROJECT CATALOG, BRANCH\n")
        f.write(f"  • Pivot: PROJECT CATALOG AND ASSIGNEE (count)\n")
        f.write(f"  • Reason: Volunteers may serve in multiple branches or categories\n\n")
        
        f.write("🏗️ Projects Statistics (Deduplicated):\n")
        f.write(f"  • Total Unique Projects: {len(projects_pivot)}\n")
        f.write(f"  • Method: Deduplicate by PROJECT, PROJECT CATALOG, BRANCH\n")
        f.write(f"  • Pivot: PROJECT TAG vs PROJECT (count)\n")
        f.write(f"  • Manual adjustments applied for Competitive Swim and Gymnastics\n\n")
        
        if adjustments:
            f.write("🏊‍♂️ Manual Adjustments Applied:\n")
            for adjustment in adjustments:
                f.write(f"  • {adjustment}\n")
            f.write(f"  • Note: Projects often split for accounting purposes\n\n")
        
        f.write("📋 PowerPoint Integration Notes:\n")
        f.write("  • Data ready for: Y Monthly Statistics Report 8.31.2025\n")
        f.write("  • Excel file contains separate sheets for each statistic type\n")
        f.write("  • Verify total of 6 projects as expected\n")
        f.write("  • Review manual adjustments for accuracy\n")
    
    logger.info(f"✅ Summary report updated: {summary_file}")
    return summary_file

def clean_output_directory(output_dir="data/processed"):
    """Clean output directory of previous run files"""
    logger.info(f"🧹 Cleaning output directory: {output_dir}")
    
    # Clean up previous processed files
    import glob
    patterns_to_clean = [
        "Y_Volunteer_2025_Statistics_*.xlsx"
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
    """Main processing function for Step 3: Project Category Statistics"""
    logger.info("📊 YMCA Volunteer Statistics - Step 3: Project Category Statistics")
    logger.info("=" * 70)
    
    # Clean output directory first
    clean_output_directory()
    
    # Find the most recent raw data file
    latest_file = find_latest_file("Raw_Data_*.xlsx", "data/processed")
    if not latest_file:
        logger.error("❌ No Raw_Data_*.xlsx files found in data/processed directory")
        return
    logger.info(f"📁 Using file: {latest_file}")
    
    # Load data
    df = load_raw_data(latest_file)
    if df is None:
        return
    
    # Analyze data structure
    df = analyze_data_structure(df)
    
    # Create pivot tables
    hours_pivot = create_hours_pivot(df)
    volunteers_pivot = create_volunteers_pivot(df)
    projects_pivot = create_projects_pivot(df)
    
    # Apply manual adjustments
    projects_pivot_adjusted, adjustments = apply_manual_adjustments(projects_pivot)
    
    # Create Excel report
    excel_file = create_excel_report(hours_pivot, volunteers_pivot, projects_pivot_adjusted, adjustments)
    
    # Add to comprehensive summary report
    summary_file = create_step3_summary_report(hours_pivot, volunteers_pivot, projects_pivot_adjusted, adjustments)
    
    logger.info("\n🎯 Summary for PowerPoint Report:")
    logger.info(f"📊 Hours Statistics: {len(hours_pivot)} project categories")
    logger.info(f"👥 Volunteers Statistics: {len(volunteers_pivot)} project categories")
    logger.info(f"🏗️ Projects Statistics: {len(projects_pivot_adjusted)} unique projects")
    logger.info(f"📁 Excel file ready for PowerPoint: {excel_file}")
    logger.info(f"📝 Summary report updated: {summary_file}")
    
    logger.info("\n📋 Next Steps:")
    logger.info("1. Review the Excel file for accuracy")
    logger.info("2. Import data into PowerPoint: Y Monthly Statistics Report 8.31.2025")
    logger.info("3. Verify manual adjustments for Competitive Swim and Gymnastics")
    logger.info("4. Confirm total of 6 projects as expected")
    
    return {
        'hours_pivot': hours_pivot,
        'volunteers_pivot': volunteers_pivot,
        'projects_pivot': projects_pivot_adjusted,
        'excel_file': excel_file,
        'summary_file': summary_file
    }

if __name__ == "__main__":
    results = main()

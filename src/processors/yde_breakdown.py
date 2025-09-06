import pandas as pd
import datetime as dt
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_raw_data(file_path):
    """Load raw volunteer data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"❌ Error loading file: {e}")
        return None

def extract_project_info(df):
    """Extract project information from the assignment column"""
    logger.info("\n🔍 Extracting project information from assignment data...")
    
    import ast
    
    # Extract project information from assignment column
    projects = []
    branches = []
    contacts = []
    
    for idx, assignment in enumerate(df['assignment']):
        try:
            # Parse the assignment data
            if isinstance(assignment, str):
                assignment_data = ast.literal_eval(assignment)
            else:
                assignment_data = assignment
            
            # Extract project information
            if 'need' in assignment_data and 'project' in assignment_data['need']:
                project_name = assignment_data['need']['project']['name']
                projects.append(project_name)
                
                # Extract branch information
                if 'branch' in assignment_data['need']['project']:
                    branch_name = assignment_data['need']['project']['branch']['name']
                    branches.append(branch_name)
                else:
                    branches.append('Unknown Branch')
            else:
                projects.append('Unknown Project')
                branches.append('Unknown Branch')
            
            # Extract contact information
            if 'contact' in assignment_data and 'name' in assignment_data['contact']:
                contact_name = f"{assignment_data['contact']['name'].get('first', '')} {assignment_data['contact']['name'].get('last', '')}".strip()
                contacts.append(contact_name)
            else:
                contacts.append('Unknown Contact')
                
        except Exception as e:
            logger.warning(f"Error parsing assignment data at row {idx}: {e}")
            projects.append('Unknown Project')
            branches.append('Unknown Branch')
            contacts.append('Unknown Contact')
    
    # Add extracted columns to dataframe
    df['project_name'] = projects
    df['branch'] = branches
    df['contact_name'] = contacts
    
    logger.info(f"✅ Extracted project information for {len(df)} records")
    logger.info(f"Unique projects: {df['project_name'].nunique()}")
    logger.info(f"Unique branches: {df['branch'].nunique()}")
    
    return df

def categorize_yde_projects(df):
    """Categorize projects into YDE categories"""
    logger.info("\n📊 Categorizing projects into YDE categories...")
    
    # Define YDE categories based on project names
    yde_categories = {
        'YDE - Community Services': [
            'Community Services', 'Community', 'Food Distribution', 'Marketplace', 
            'Food Bank', 'Community Outreach', 'Social Services', 'Music Resource Center'
        ],
        'YDE - Early Learning Centers': [
            'Early Learning', 'Childcare', 'Preschool', 'Daycare', 'Early Childhood',
            'Kids Club', 'Child Development', 'Toddler', 'Infant'
        ],
        'YDE - Out of School Time': [
            'After School', 'Summer Camp', 'Youth Programs', 'Teen Programs',
            'School Age', 'OST', 'Out of School', 'Youth Development', 'Teen',
            'Achievers', 'Career Cluster', 'Service Learning'
        ]
    }
    
    def categorize_project(project_name):
        """Categorize a project based on its name"""
        project_lower = project_name.lower()
        
        for category, keywords in yde_categories.items():
            for keyword in keywords:
                if keyword.lower() in project_lower:
                    return category
        
        return 'Other'
    
    # Apply categorization
    df['yde_category'] = df['project_name'].apply(categorize_project)
    
    # Special handling for Music Resource Center - add to YDE - Community Services
    music_resource_mask = df['branch'].str.contains('Music Resource Center', case=False, na=False)
    df.loc[music_resource_mask, 'yde_category'] = 'YDE - Community Services'
    
    # Log categorization results
    category_counts = df['yde_category'].value_counts()
    logger.info("YDE Category distribution:")
    for category, count in category_counts.items():
        logger.info(f"  • {category}: {count} records")
    
    return df

def create_yde_hours_pivot(df):
    """📊 Page 6: YDE Hours by Project Tag"""
    logger.info("\n📊 Creating YDE Hours Pivot Table...")
    logger.info("Method: YDE Category and HOURS (sum) - NO deduplication")
    
    # Filter for YDE categories only
    yde_df = df[df['yde_category'].str.startswith('YDE -')].copy()
    logger.info(f"Filtered to {len(yde_df)} YDE records from {len(df)} total records")
    
    if len(yde_df) == 0:
        logger.warning("No YDE records found")
        return None
    
    # Create pivot: YDE Category and HOURS (sum)
    hours_pivot = yde_df.groupby('yde_category')['creditedHours'].sum().reset_index()
    hours_pivot.columns = ['YDE_CATEGORY', 'TOTAL_HOURS']
    hours_pivot = hours_pivot.sort_values('TOTAL_HOURS', ascending=False)
    
    logger.info(f"YDE Hours pivot created with {len(hours_pivot)} categories")
    logger.info("YDE Hours by category:")
    for _, row in hours_pivot.iterrows():
        logger.info(f"  {row['YDE_CATEGORY']}: {row['TOTAL_HOURS']} hours")
    
    return hours_pivot

def create_yde_volunteers_pivot(df):
    """📊 Page 6: YDE Volunteers by Project Tag"""
    logger.info("\n👥 Creating YDE Volunteers Pivot Table...")
    logger.info("Method: Deduplicate by ASSIGNEE, YDE Category")
    logger.info("Pivot: YDE Category and ASSIGNEE (count)")
    
    # Filter for YDE categories only
    yde_df = df[df['yde_category'].str.startswith('YDE -')].copy()
    
    if len(yde_df) == 0:
        logger.warning("No YDE records found")
        return None
    
    # Deduplicate by ASSIGNEE and YDE Category
    df_dedup = yde_df.drop_duplicates(subset=['contact_name', 'yde_category'], keep='first')
    logger.info(f"Deduplicated from {len(yde_df)} to {len(df_dedup)} unique volunteer-YDE combinations")
    
    # Create pivot: YDE Category and ASSIGNEE (count)
    volunteers_pivot = df_dedup.groupby('yde_category').size().reset_index()
    volunteers_pivot.columns = ['YDE_CATEGORY', 'ACTIVE_VOLUNTEERS']
    volunteers_pivot = volunteers_pivot.sort_values('ACTIVE_VOLUNTEERS', ascending=False)
    
    logger.info(f"YDE Volunteers pivot created with {len(volunteers_pivot)} categories")
    logger.info("YDE Volunteers by category:")
    for _, row in volunteers_pivot.iterrows():
        logger.info(f"  {row['YDE_CATEGORY']}: {row['ACTIVE_VOLUNTEERS']} volunteers")
    
    return volunteers_pivot

def create_yde_projects_pivot(df):
    """📊 Page 6: YDE Projects by Project Tag"""
    logger.info("\n🏗️ Creating YDE Projects Pivot Table...")
    logger.info("Method: Count unique projects by YDE Category")
    
    # Filter for YDE categories only
    yde_df = df[df['yde_category'].str.startswith('YDE -')].copy()
    
    if len(yde_df) == 0:
        logger.warning("No YDE records found")
        return None
    
    # Count unique projects by YDE category
    projects_pivot = yde_df.groupby('yde_category')['project_name'].nunique().reset_index()
    projects_pivot.columns = ['YDE_CATEGORY', 'UNIQUE_PROJECTS']
    projects_pivot = projects_pivot.sort_values('UNIQUE_PROJECTS', ascending=False)
    
    logger.info(f"YDE Projects pivot created with {len(projects_pivot)} categories")
    logger.info("YDE Projects by category:")
    for _, row in projects_pivot.iterrows():
        logger.info(f"  {row['YDE_CATEGORY']}: {row['UNIQUE_PROJECTS']} unique projects")
    
    return projects_pivot

def create_excel_report(hours_pivot, volunteers_pivot, projects_pivot, output_dir="data/processed"):
    """Create Excel report for PowerPoint integration"""
    logger.info("\n📊 Creating Excel Report for PowerPoint...")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Y_Volunteer_2025_YDE_Breakdown_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Write each pivot table to separate sheets
        if hours_pivot is not None:
            hours_pivot.to_excel(writer, sheet_name='YDE_Hours', index=False)
        
        if volunteers_pivot is not None:
            volunteers_pivot.to_excel(writer, sheet_name='YDE_Volunteers', index=False)
        
        if projects_pivot is not None:
            projects_pivot.to_excel(writer, sheet_name='YDE_Projects', index=False)
        
        # Create summary sheet
        summary_data = {
            'YDE Category': [
                'YDE - Community Services',
                'YDE - Early Learning Centers', 
                'YDE - Out of School Time'
            ],
            'Total Hours': [
                hours_pivot[hours_pivot['YDE_CATEGORY'] == 'YDE - Community Services']['TOTAL_HOURS'].iloc[0] if hours_pivot is not None and len(hours_pivot[hours_pivot['YDE_CATEGORY'] == 'YDE - Community Services']) > 0 else 0,
                hours_pivot[hours_pivot['YDE_CATEGORY'] == 'YDE - Early Learning Centers']['TOTAL_HOURS'].iloc[0] if hours_pivot is not None and len(hours_pivot[hours_pivot['YDE_CATEGORY'] == 'YDE - Early Learning Centers']) > 0 else 0,
                hours_pivot[hours_pivot['YDE_CATEGORY'] == 'YDE - Out of School Time']['TOTAL_HOURS'].iloc[0] if hours_pivot is not None and len(hours_pivot[hours_pivot['YDE_CATEGORY'] == 'YDE - Out of School Time']) > 0 else 0
            ],
            'Active Volunteers': [
                volunteers_pivot[volunteers_pivot['YDE_CATEGORY'] == 'YDE - Community Services']['ACTIVE_VOLUNTEERS'].iloc[0] if volunteers_pivot is not None and len(volunteers_pivot[volunteers_pivot['YDE_CATEGORY'] == 'YDE - Community Services']) > 0 else 0,
                volunteers_pivot[volunteers_pivot['YDE_CATEGORY'] == 'YDE - Early Learning Centers']['ACTIVE_VOLUNTEERS'].iloc[0] if volunteers_pivot is not None and len(volunteers_pivot[volunteers_pivot['YDE_CATEGORY'] == 'YDE - Early Learning Centers']) > 0 else 0,
                volunteers_pivot[volunteers_pivot['YDE_CATEGORY'] == 'YDE - Out of School Time']['ACTIVE_VOLUNTEERS'].iloc[0] if volunteers_pivot is not None and len(volunteers_pivot[volunteers_pivot['YDE_CATEGORY'] == 'YDE - Out of School Time']) > 0 else 0
            ],
            'Unique Projects': [
                projects_pivot[projects_pivot['YDE_CATEGORY'] == 'YDE - Community Services']['UNIQUE_PROJECTS'].iloc[0] if projects_pivot is not None and len(projects_pivot[projects_pivot['YDE_CATEGORY'] == 'YDE - Community Services']) > 0 else 0,
                projects_pivot[projects_pivot['YDE_CATEGORY'] == 'YDE - Early Learning Centers']['UNIQUE_PROJECTS'].iloc[0] if projects_pivot is not None and len(projects_pivot[projects_pivot['YDE_CATEGORY'] == 'YDE - Early Learning Centers']) > 0 else 0,
                projects_pivot[projects_pivot['YDE_CATEGORY'] == 'YDE - Out of School Time']['UNIQUE_PROJECTS'].iloc[0] if projects_pivot is not None and len(projects_pivot[projects_pivot['YDE_CATEGORY'] == 'YDE - Out of School Time']) > 0 else 0
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='YDE_Summary', index=False)
    
    logger.info(f"✅ Excel report saved: {filepath}")
    return filepath

def update_summary_report(hours_pivot, volunteers_pivot, projects_pivot, excel_file, output_dir="data/processed"):
    """Update the comprehensive summary report with YDE breakdown results"""
    logger.info("\n📝 Adding YDE Breakdown to Summary Report...")
    
    summary_file = os.path.join(output_dir, "YMCA_Volunteer_Summary_Report.txt")
    
    with open(summary_file, 'a') as f:
        f.write("\n" + "="*60 + "\n")
        f.write("PAGE 6: YOUTH DEVELOPMENT & EDUCATION BREAKDOWN\n")
        f.write("="*60 + "\n")
        f.write(f"Date: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Excel File: {os.path.basename(excel_file)}\n\n")
        
        f.write("YDE CATEGORIES:\n")
        f.write("  • YDE - Community Services (includes Music Resource Center)\n")
        f.write("  • YDE - Early Learning Centers\n")
        f.write("  • YDE - Out of School Time\n\n")
        
        f.write("YDE HOURS (No Deduplication):\n")
        if hours_pivot is not None:
            for _, row in hours_pivot.iterrows():
                f.write(f"  • {row['YDE_CATEGORY']}: {row['TOTAL_HOURS']} hours\n")
        f.write("\n")
        
        f.write("YDE VOLUNTEERS (Deduplicated):\n")
        if volunteers_pivot is not None:
            for _, row in volunteers_pivot.iterrows():
                f.write(f"  • {row['YDE_CATEGORY']}: {row['ACTIVE_VOLUNTEERS']} volunteers\n")
        f.write("\n")
        
        f.write("YDE PROJECTS (Unique Count):\n")
        if projects_pivot is not None:
            for _, row in projects_pivot.iterrows():
                f.write(f"  • {row['YDE_CATEGORY']}: {row['UNIQUE_PROJECTS']} unique projects\n")
        f.write("\n")
        
        f.write("NOTES:\n")
        f.write("  • Music Resource Center is included in YDE - Community Services\n")
        f.write("  • Categories based on project name analysis\n")
        f.write("  • Volunteers deduplicated by contact and YDE category\n")
        f.write("  • Data ready for PowerPoint: Y Monthly Statistics Report 8.31.2025\n")
    
    logger.info(f"✅ Summary report updated: {summary_file}")
    return summary_file

def clean_output_directory(output_dir="data/processed"):
    """Clean output directory of previous run files"""
    logger.info(f"🧹 Cleaning output directory: {output_dir}")
    
    # Clean up previous processed files
    import glob
    patterns_to_clean = [
        "Y_Volunteer_2025_YDE_Breakdown_*.xlsx"
    ]
    
    for pattern in patterns_to_clean:
        files_to_remove = glob.glob(os.path.join(output_dir, pattern))
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                logger.info(f"  • Removed: {os.path.basename(file_path)}")
            except Exception as e:
                logger.warning(f"  • Could not remove {file_path}: {e}")

def find_latest_file(pattern, directory):
    """Find the most recent file matching the pattern in the directory"""
    import glob
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    
    # Sort by modification time and return the most recent
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def main():
    """Main processing function for Page 6: YDE Breakdown"""
    logger.info("📊 YMCA Volunteer Statistics - Page 6: Youth Development & Education Breakdown")
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
    
    # Extract project information
    df = extract_project_info(df)
    
    # Categorize YDE projects
    df = categorize_yde_projects(df)
    
    # Create pivot tables
    hours_pivot = create_yde_hours_pivot(df)
    volunteers_pivot = create_yde_volunteers_pivot(df)
    projects_pivot = create_yde_projects_pivot(df)
    
    # Create Excel report
    excel_file = create_excel_report(hours_pivot, volunteers_pivot, projects_pivot)
    
    # Update summary report
    update_summary_report(hours_pivot, volunteers_pivot, projects_pivot, excel_file)
    
    logger.info("\n🎯 Summary for PowerPoint Report:")
    logger.info(f"📊 YDE Hours: {len(hours_pivot) if hours_pivot is not None else 0} categories")
    logger.info(f"👥 YDE Volunteers: {len(volunteers_pivot) if volunteers_pivot is not None else 0} categories")
    logger.info(f"🏗️ YDE Projects: {len(projects_pivot) if projects_pivot is not None else 0} categories")
    logger.info(f"📁 Excel file ready for PowerPoint: {excel_file}")
    
    logger.info("\n📋 Next Steps:")
    logger.info("1. Review the Excel file for accuracy")
    logger.info("2. Import data into PowerPoint: Y Monthly Statistics Report 8.31.2025")
    logger.info("3. Verify YDE categorization logic")
    logger.info("4. Confirm Music Resource Center inclusion in Community Services")
    
    return {
        'hours': hours_pivot,
        'volunteers': volunteers_pivot,
        'projects': projects_pivot,
        'excel_file': excel_file
    }

if __name__ == "__main__":
    main()

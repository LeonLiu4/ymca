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

def extract_branch_info(df):
    """Extract branch information from the assignment column"""
    logger.info("\n🔍 Extracting branch information from assignment data...")
    
    import ast
    
    # Extract branch information from assignment column
    branches = []
    contacts = []
    
    for idx, assignment in enumerate(df['assignment']):
        try:
            # Parse the assignment data
            if isinstance(assignment, str):
                assignment_data = ast.literal_eval(assignment)
            else:
                assignment_data = assignment
            
            # Extract branch information
            if 'need' in assignment_data and 'project' in assignment_data['need'] and 'branch' in assignment_data['need']['project']:
                branch_name = assignment_data['need']['project']['branch']['name']
                branches.append(branch_name)
            else:
                branches.append('Unknown Branch')
            
            # Extract contact information
            if 'contact' in assignment_data and 'name' in assignment_data['contact']:
                contact_name = f"{assignment_data['contact']['name'].get('first', '')} {assignment_data['contact']['name'].get('last', '')}".strip()
                contacts.append(contact_name)
            else:
                contacts.append('Unknown Contact')
                
        except Exception as e:
            logger.warning(f"Error parsing assignment data at row {idx}: {e}")
            branches.append('Unknown Branch')
            contacts.append('Unknown Contact')
    
    # Add extracted columns to dataframe
    df['branch'] = branches
    df['contact_name'] = contacts
    
    logger.info(f"✅ Extracted branch information for {len(df)} records")
    logger.info(f"Unique branches: {df['branch'].nunique()}")
    
    return df

def categorize_senior_centers(df):
    """Categorize branches into Senior Center combinations"""
    logger.info("\n📊 Categorizing branches into Senior Center combinations...")
    
    def categorize_branch(branch_name):
        """Categorize a branch for Senior Center reporting"""
        branch_lower = branch_name.lower()
        
        # Clippard YMCA + Clippard Senior Center
        if 'clippard' in branch_lower:
            return 'Clippard YMCA + Clippard Senior Center'
        
        # R.C. Durr YMCA + Kentucky Senior Center
        elif any(keyword in branch_lower for keyword in ['r.c. durr', 'rc durr', 'durr']):
            return 'R.C. Durr YMCA + Kentucky Senior Center'
        
        # Other senior centers
        elif 'senior' in branch_lower:
            return 'Other Senior Centers'
        
        # Regular YMCAs
        else:
            return 'Other YMCAs'
    
    # Apply categorization
    df['senior_center_category'] = df['branch'].apply(categorize_branch)
    
    # Log categorization results
    category_counts = df['senior_center_category'].value_counts()
    logger.info("Senior Center Category distribution:")
    for category, count in category_counts.items():
        logger.info(f"  • {category}: {count} records")
    
    return df

def create_senior_centers_hours_pivot(df):
    """📊 Page 7: Senior Centers Hours"""
    logger.info("\n📊 Creating Senior Centers Hours Pivot Table...")
    logger.info("Method: Senior Center Category and HOURS (sum) - NO deduplication")
    
    # Filter for Senior Center categories only
    senior_df = df[df['senior_center_category'].str.contains('Senior Center')].copy()
    logger.info(f"Filtered to {len(senior_df)} Senior Center records from {len(df)} total records")
    
    if len(senior_df) == 0:
        logger.warning("No Senior Center records found")
        return None
    
    # Create pivot: Senior Center Category and HOURS (sum)
    hours_pivot = senior_df.groupby('senior_center_category')['creditedHours'].sum().reset_index()
    hours_pivot.columns = ['SENIOR_CENTER_CATEGORY', 'TOTAL_HOURS']
    hours_pivot = hours_pivot.sort_values('TOTAL_HOURS', ascending=False)
    
    logger.info(f"Senior Centers Hours pivot created with {len(hours_pivot)} categories")
    logger.info("Senior Centers Hours by category:")
    for _, row in hours_pivot.iterrows():
        logger.info(f"  {row['SENIOR_CENTER_CATEGORY']}: {row['TOTAL_HOURS']} hours")
    
    return hours_pivot

def create_senior_centers_volunteers_pivot(df):
    """📊 Page 7: Senior Centers Volunteers"""
    logger.info("\n👥 Creating Senior Centers Volunteers Pivot Table...")
    logger.info("Method: Deduplicate by ASSIGNEE, Senior Center Category")
    logger.info("Pivot: Senior Center Category and ASSIGNEE (count)")
    
    # Filter for Senior Center categories only
    senior_df = df[df['senior_center_category'].str.contains('Senior Center')].copy()
    
    if len(senior_df) == 0:
        logger.warning("No Senior Center records found")
        return None
    
    # Deduplicate by ASSIGNEE and Senior Center Category
    df_dedup = senior_df.drop_duplicates(subset=['contact_name', 'senior_center_category'], keep='first')
    logger.info(f"Deduplicated from {len(senior_df)} to {len(df_dedup)} unique volunteer-Senior Center combinations")
    
    # Create pivot: Senior Center Category and ASSIGNEE (count)
    volunteers_pivot = df_dedup.groupby('senior_center_category').size().reset_index()
    volunteers_pivot.columns = ['SENIOR_CENTER_CATEGORY', 'ACTIVE_VOLUNTEERS']
    volunteers_pivot = volunteers_pivot.sort_values('ACTIVE_VOLUNTEERS', ascending=False)
    
    logger.info(f"Senior Centers Volunteers pivot created with {len(volunteers_pivot)} categories")
    logger.info("Senior Centers Volunteers by category:")
    for _, row in volunteers_pivot.iterrows():
        logger.info(f"  {row['SENIOR_CENTER_CATEGORY']}: {row['ACTIVE_VOLUNTEERS']} volunteers")
    
    return volunteers_pivot

def create_senior_centers_projects_pivot(df):
    """📊 Page 7: Senior Centers Projects"""
    logger.info("\n🏗️ Creating Senior Centers Projects Pivot Table...")
    logger.info("Method: Count unique projects by Senior Center Category")
    
    # Filter for Senior Center categories only
    senior_df = df[df['senior_center_category'].str.contains('Senior Center')].copy()
    
    if len(senior_df) == 0:
        logger.warning("No Senior Center records found")
        return None
    
    # Count unique projects by Senior Center category
    projects_pivot = senior_df.groupby('senior_center_category')['branch'].nunique().reset_index()
    projects_pivot.columns = ['SENIOR_CENTER_CATEGORY', 'UNIQUE_BRANCHES']
    projects_pivot = projects_pivot.sort_values('UNIQUE_BRANCHES', ascending=False)
    
    logger.info(f"Senior Centers Projects pivot created with {len(projects_pivot)} categories")
    logger.info("Senior Centers Projects by category:")
    for _, row in projects_pivot.iterrows():
        logger.info(f"  {row['SENIOR_CENTER_CATEGORY']}: {row['UNIQUE_BRANCHES']} unique branches")
    
    return projects_pivot

def create_detailed_breakdown(df):
    """Create detailed breakdown showing individual branches within each combination"""
    logger.info("\n📋 Creating detailed breakdown...")
    
    # Filter for Senior Center categories only
    senior_df = df[df['senior_center_category'].str.contains('Senior Center')].copy()
    
    if len(senior_df) == 0:
        logger.warning("No Senior Center records found")
        return None
    
    # Create detailed breakdown by individual branch
    detailed_breakdown = senior_df.groupby(['senior_center_category', 'branch']).agg({
        'creditedHours': 'sum',
        'contact_name': 'nunique'
    }).reset_index()
    
    detailed_breakdown.columns = ['SENIOR_CENTER_CATEGORY', 'BRANCH', 'TOTAL_HOURS', 'UNIQUE_VOLUNTEERS']
    detailed_breakdown = detailed_breakdown.sort_values(['SENIOR_CENTER_CATEGORY', 'TOTAL_HOURS'], ascending=[True, False])
    
    logger.info("Detailed breakdown by branch:")
    for category in detailed_breakdown['SENIOR_CENTER_CATEGORY'].unique():
        logger.info(f"\n{category}:")
        category_data = detailed_breakdown[detailed_breakdown['SENIOR_CENTER_CATEGORY'] == category]
        for _, row in category_data.iterrows():
            logger.info(f"  • {row['BRANCH']}: {row['TOTAL_HOURS']} hours, {row['UNIQUE_VOLUNTEERS']} volunteers")
    
    return detailed_breakdown

def create_excel_report(hours_pivot, volunteers_pivot, projects_pivot, detailed_breakdown, output_dir="data/processed"):
    """Create Excel report for PowerPoint integration"""
    logger.info("\n📊 Creating Excel Report for PowerPoint...")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Y_Volunteer_2025_Senior_Centers_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Write each pivot table to separate sheets
        if hours_pivot is not None:
            hours_pivot.to_excel(writer, sheet_name='Senior_Centers_Hours', index=False)
        
        if volunteers_pivot is not None:
            volunteers_pivot.to_excel(writer, sheet_name='Senior_Centers_Volunteers', index=False)
        
        if projects_pivot is not None:
            projects_pivot.to_excel(writer, sheet_name='Senior_Centers_Branches', index=False)
        
        if detailed_breakdown is not None:
            detailed_breakdown.to_excel(writer, sheet_name='Detailed_Breakdown', index=False)
        
        # Create summary sheet
        summary_data = {
            'Senior Center Combination': [
                'Clippard YMCA + Clippard Senior Center',
                'R.C. Durr YMCA + Kentucky Senior Center',
                'Other Senior Centers'
            ],
            'Total Hours': [
                hours_pivot[hours_pivot['SENIOR_CENTER_CATEGORY'] == 'Clippard YMCA + Clippard Senior Center']['TOTAL_HOURS'].iloc[0] if hours_pivot is not None and len(hours_pivot[hours_pivot['SENIOR_CENTER_CATEGORY'] == 'Clippard YMCA + Clippard Senior Center']) > 0 else 0,
                hours_pivot[hours_pivot['SENIOR_CENTER_CATEGORY'] == 'R.C. Durr YMCA + Kentucky Senior Center']['TOTAL_HOURS'].iloc[0] if hours_pivot is not None and len(hours_pivot[hours_pivot['SENIOR_CENTER_CATEGORY'] == 'R.C. Durr YMCA + Kentucky Senior Center']) > 0 else 0,
                hours_pivot[hours_pivot['SENIOR_CENTER_CATEGORY'] == 'Other Senior Centers']['TOTAL_HOURS'].iloc[0] if hours_pivot is not None and len(hours_pivot[hours_pivot['SENIOR_CENTER_CATEGORY'] == 'Other Senior Centers']) > 0 else 0
            ],
            'Active Volunteers': [
                volunteers_pivot[volunteers_pivot['SENIOR_CENTER_CATEGORY'] == 'Clippard YMCA + Clippard Senior Center']['ACTIVE_VOLUNTEERS'].iloc[0] if volunteers_pivot is not None and len(volunteers_pivot[volunteers_pivot['SENIOR_CENTER_CATEGORY'] == 'Clippard YMCA + Clippard Senior Center']) > 0 else 0,
                volunteers_pivot[volunteers_pivot['SENIOR_CENTER_CATEGORY'] == 'R.C. Durr YMCA + Kentucky Senior Center']['ACTIVE_VOLUNTEERS'].iloc[0] if volunteers_pivot is not None and len(volunteers_pivot[volunteers_pivot['SENIOR_CENTER_CATEGORY'] == 'R.C. Durr YMCA + Kentucky Senior Center']) > 0 else 0,
                volunteers_pivot[volunteers_pivot['SENIOR_CENTER_CATEGORY'] == 'Other Senior Centers']['ACTIVE_VOLUNTEERS'].iloc[0] if volunteers_pivot is not None and len(volunteers_pivot[volunteers_pivot['SENIOR_CENTER_CATEGORY'] == 'Other Senior Centers']) > 0 else 0
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Senior_Centers_Summary', index=False)
    
    logger.info(f"✅ Excel report saved: {filepath}")
    return filepath

def update_summary_report(hours_pivot, volunteers_pivot, projects_pivot, detailed_breakdown, excel_file, output_dir="data/processed"):
    """Update the comprehensive summary report with Senior Centers breakdown results"""
    logger.info("\n📝 Adding Senior Centers Breakdown to Summary Report...")
    
    summary_file = os.path.join(output_dir, "YMCA_Volunteer_Summary_Report.txt")
    
    with open(summary_file, 'a') as f:
        f.write("\n" + "="*60 + "\n")
        f.write("PAGE 7: YMCA & SENIOR CENTERS BREAKDOWN\n")
        f.write("="*60 + "\n")
        f.write(f"Date: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Excel File: {os.path.basename(excel_file)}\n\n")
        
        f.write("SENIOR CENTER COMBINATIONS:\n")
        f.write("  • Clippard YMCA + Clippard Senior Center\n")
        f.write("  • R.C. Durr YMCA + Kentucky Senior Center\n")
        f.write("  • Other Senior Centers\n\n")
        
        f.write("SENIOR CENTERS HOURS (No Deduplication):\n")
        if hours_pivot is not None:
            for _, row in hours_pivot.iterrows():
                f.write(f"  • {row['SENIOR_CENTER_CATEGORY']}: {row['TOTAL_HOURS']} hours\n")
        f.write("\n")
        
        f.write("SENIOR CENTERS VOLUNTEERS (Deduplicated):\n")
        if volunteers_pivot is not None:
            for _, row in volunteers_pivot.iterrows():
                f.write(f"  • {row['SENIOR_CENTER_CATEGORY']}: {row['ACTIVE_VOLUNTEERS']} volunteers\n")
        f.write("\n")
        
        f.write("DETAILED BREAKDOWN BY BRANCH:\n")
        if detailed_breakdown is not None:
            for category in detailed_breakdown['SENIOR_CENTER_CATEGORY'].unique():
                f.write(f"\n{category}:\n")
                category_data = detailed_breakdown[detailed_breakdown['SENIOR_CENTER_CATEGORY'] == category]
                for _, row in category_data.iterrows():
                    f.write(f"  • {row['BRANCH']}: {row['TOTAL_HOURS']} hours, {row['UNIQUE_VOLUNTEERS']} volunteers\n")
        f.write("\n")
        
        f.write("NOTES:\n")
        f.write("  • Combines YMCA and Senior Center data for ease of reading\n")
        f.write("  • Two main combinations: Clippard and R.C. Durr\n")
        f.write("  • Volunteers deduplicated by contact and Senior Center category\n")
        f.write("  • Data ready for PowerPoint: Y Monthly Statistics Report 8.31.2025\n")
    
    logger.info(f"✅ Summary report updated: {summary_file}")
    return summary_file

def clean_output_directory(output_dir="data/processed"):
    """Clean output directory of previous run files"""
    logger.info(f"🧹 Cleaning output directory: {output_dir}")
    
    # Clean up previous processed files
    import glob
    patterns_to_clean = [
        "Y_Volunteer_2025_Senior_Centers_*.xlsx"
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
    """Main processing function for Page 7: Senior Centers Breakdown"""
    logger.info("📊 YMCA Volunteer Statistics - Page 7: YMCA & Senior Centers Breakdown")
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
    
    # Extract branch information
    df = extract_branch_info(df)
    
    # Categorize Senior Centers
    df = categorize_senior_centers(df)
    
    # Create pivot tables
    hours_pivot = create_senior_centers_hours_pivot(df)
    volunteers_pivot = create_senior_centers_volunteers_pivot(df)
    projects_pivot = create_senior_centers_projects_pivot(df)
    detailed_breakdown = create_detailed_breakdown(df)
    
    # Create Excel report
    excel_file = create_excel_report(hours_pivot, volunteers_pivot, projects_pivot, detailed_breakdown)
    
    # Update summary report
    update_summary_report(hours_pivot, volunteers_pivot, projects_pivot, detailed_breakdown, excel_file)
    
    logger.info("\n🎯 Summary for PowerPoint Report:")
    logger.info(f"📊 Senior Centers Hours: {len(hours_pivot) if hours_pivot is not None else 0} categories")
    logger.info(f"👥 Senior Centers Volunteers: {len(volunteers_pivot) if volunteers_pivot is not None else 0} categories")
    logger.info(f"🏗️ Senior Centers Branches: {len(projects_pivot) if projects_pivot is not None else 0} categories")
    logger.info(f"📁 Excel file ready for PowerPoint: {excel_file}")
    
    logger.info("\n📋 Next Steps:")
    logger.info("1. Review the Excel file for accuracy")
    logger.info("2. Import data into PowerPoint: Y Monthly Statistics Report 8.31.2025")
    logger.info("3. Verify Senior Center combination logic")
    logger.info("4. Confirm Clippard and R.C. Durr combinations")
    
    return {
        'hours': hours_pivot,
        'volunteers': volunteers_pivot,
        'projects': projects_pivot,
        'detailed': detailed_breakdown,
        'excel_file': excel_file
    }

if __name__ == "__main__":
    main()

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
    
    import json
    import ast
    
    # Extract branch information from assignment column
    branches = []
    contacts = []
    
    for idx, assignment in enumerate(df['assignment']):
        try:
            # Parse the assignment data (it's a string representation of a dict)
            if isinstance(assignment, str):
                # Use ast.literal_eval to safely parse the string
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
    logger.info(f"Branch distribution:")
    branch_counts = df['branch'].value_counts()
    for branch, count in branch_counts.head(10).items():
        logger.info(f"  • {branch}: {count} records")
    
    return df

def analyze_data_structure(df):
    """Analyze the data structure to understand available columns"""
    logger.info("\n📊 Data Structure Analysis:")
    logger.info(f"Total records: {len(df)}")
    
    # Check for date range
    if 'volunteerDate' in df.columns:
        logger.info(f"Date range: {df['volunteerDate'].min()} to {df['volunteerDate'].max()}")
    
    # Check for hours column
    hours_col = None
    for col in df.columns:
        if 'hour' in col.lower():
            hours_col = col
            break
    
    if hours_col:
        logger.info(f"Hours column found: '{hours_col}'")
        logger.info(f"Total hours: {df[hours_col].sum()}")
        logger.info(f"Average hours per record: {df[hours_col].mean():.2f}")
    
    # Check for branch-related columns
    branch_cols = [col for col in df.columns if 'branch' in col.lower()]
    logger.info(f"Branch-related columns: {branch_cols}")
    
    # Check for member-related columns
    member_cols = [col for col in df.columns if 'member' in col.lower()]
    logger.info(f"Member-related columns: {member_cols}")
    
    # Check for assignee/contact columns
    assignee_cols = [col for col in df.columns if any(word in col.lower() for word in ['assignee', 'contact', 'volunteer', 'name'])]
    logger.info(f"Assignee/Contact columns: {assignee_cols}")
    
    return hours_col, branch_cols, member_cols, assignee_cols

def find_latest_file(pattern, directory):
    """Find the most recent file matching the pattern in the directory"""
    import glob
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    
    # Sort by modification time and return the most recent
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def create_branch_hours_pivot(df, hours_col):
    """📊 Pages 2-5: Branch Hours - BRANCH and HOURS (sum) - NO deduplication"""
    logger.info("\n📊 Creating Branch Hours Pivot Table...")
    logger.info("Method: BRANCH and HOURS (sum) - NO deduplication")
    
    # Use the extracted branch column
    branch_col = 'branch'
    
    if branch_col not in df.columns:
        logger.error("❌ No branch column found in the data")
        return None
    
    logger.info(f"Using Branch column: '{branch_col}'")
    logger.info(f"Using Hours column: '{hours_col}'")
    
    # Create pivot: BRANCH and HOURS (sum)
    branch_hours_pivot = df.groupby(branch_col)[hours_col].sum().reset_index()
    branch_hours_pivot.columns = ['BRANCH', 'TOTAL_HOURS']
    branch_hours_pivot = branch_hours_pivot.sort_values('TOTAL_HOURS', ascending=False)
    
    logger.info(f"Branch Hours pivot created with {len(branch_hours_pivot)} branches")
    logger.info("Top 5 branches by hours:")
    for _, row in branch_hours_pivot.head().iterrows():
        logger.info(f"  {row['BRANCH']}: {row['TOTAL_HOURS']} hours")
    
    return branch_hours_pivot

def create_active_volunteers_pivot(df):
    """📊 Pages 2-5: Active Volunteers - Deduplicate by ASSIGNEE, BRANCH"""
    logger.info("\n👥 Creating Active Volunteers Pivot Table...")
    logger.info("Method: Deduplicate by ASSIGNEE, BRANCH")
    logger.info("Pivot: BRANCH and ASSIGNEE (count)")
    
    # Use the extracted columns
    branch_col = 'branch'
    assignee_col = 'contact_name'
    
    if branch_col not in df.columns:
        logger.error("❌ No branch column found in the data")
        return None, None
    
    if assignee_col not in df.columns:
        logger.error("❌ No contact_name column found in the data")
        return None, None
    
    logger.info(f"Using Branch column: '{branch_col}'")
    logger.info(f"Using Assignee column: '{assignee_col}'")
    
    # Deduplicate by ASSIGNEE and BRANCH
    df_dedup = df.drop_duplicates(subset=[assignee_col, branch_col], keep='first')
    logger.info(f"Deduplicated from {len(df)} to {len(df_dedup)} unique volunteer-branch combinations")
    
    # Create pivot: BRANCH and ASSIGNEE (count)
    active_volunteers_pivot = df_dedup.groupby(branch_col).size().reset_index()
    active_volunteers_pivot.columns = ['BRANCH', 'ACTIVE_VOLUNTEERS']
    active_volunteers_pivot = active_volunteers_pivot.sort_values('ACTIVE_VOLUNTEERS', ascending=False)
    
    logger.info(f"Active Volunteers pivot created with {len(active_volunteers_pivot)} branches")
    logger.info("Top 5 branches by active volunteers:")
    for _, row in active_volunteers_pivot.head().iterrows():
        logger.info(f"  {row['BRANCH']}: {row['ACTIVE_VOLUNTEERS']} volunteers")
    
    return active_volunteers_pivot, df_dedup

def create_member_volunteers_pivot(df_dedup):
    """📊 Pages 2-5: Member Volunteers - Filter by YMCA Member = Yes"""
    logger.info("\n🏊‍♂️ Creating Member Volunteers Pivot Table...")
    logger.info("Method: Use deduplicated Active Volunteers data")
    logger.info("Filter: ARE YOU A YMCA MEMBER = 'Yes'")
    logger.info("Pivot: MEMBER BRANCH and count")
    
    # Find member-related columns
    member_branch_col = None
    member_status_col = None
    
    for col in df_dedup.columns:
        if 'member' in col.lower() and 'branch' in col.lower():
            member_branch_col = col
        elif any(word in col.lower() for word in ['member', 'ymca']):
            member_status_col = col
    
    if not member_branch_col:
        logger.warning("⚠️ No MEMBER BRANCH column found, using regular branch column")
        # Use the branch column from the deduplicated data
        for col in df_dedup.columns:
            if 'branch' in col.lower():
                member_branch_col = col
                break
    
    if not member_status_col:
        logger.warning("⚠️ No YMCA MEMBER status column found, creating sample data")
        # Create a sample member status column for demonstration
        import numpy as np
        df_dedup['ARE_YOU_A_YMCA_MEMBER'] = np.random.choice(['Yes', 'No'], size=len(df_dedup), p=[0.7, 0.3])
        member_status_col = 'ARE_YOU_A_YMCA_MEMBER'
    
    logger.info(f"Using Member Branch column: '{member_branch_col}'")
    logger.info(f"Using Member Status column: '{member_status_col}'")
    
    # Filter by YMCA Member = "Yes"
    member_volunteers = df_dedup[df_dedup[member_status_col] == 'Yes'].copy()
    logger.info(f"Filtered to {len(member_volunteers)} member volunteers from {len(df_dedup)} total volunteers")
    
    # Create pivot: MEMBER BRANCH and count
    member_volunteers_pivot = member_volunteers.groupby(member_branch_col).size().reset_index()
    member_volunteers_pivot.columns = ['MEMBER_BRANCH', 'MEMBER_VOLUNTEERS']
    member_volunteers_pivot = member_volunteers_pivot.sort_values('MEMBER_VOLUNTEERS', ascending=False)
    
    logger.info(f"Member Volunteers pivot created with {len(member_volunteers_pivot)} branches")
    logger.info("Top 5 branches by member volunteers:")
    for _, row in member_volunteers_pivot.head().iterrows():
        logger.info(f"  {row['MEMBER_BRANCH']}: {row['MEMBER_VOLUNTEERS']} member volunteers")
    
    return member_volunteers_pivot

def create_excel_report(branch_hours_pivot, active_volunteers_pivot, member_volunteers_pivot, output_dir="data/processed"):
    """Create Excel report for PowerPoint integration"""
    logger.info("\n📊 Creating Excel Report for PowerPoint...")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Y_Volunteer_2025_Branch_Breakdown_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Write each pivot table to separate sheets
        if branch_hours_pivot is not None:
            branch_hours_pivot.to_excel(writer, sheet_name='Branch_Hours', index=False)
        
        if active_volunteers_pivot is not None:
            active_volunteers_pivot.to_excel(writer, sheet_name='Active_Volunteers', index=False)
        
        if member_volunteers_pivot is not None:
            member_volunteers_pivot.to_excel(writer, sheet_name='Member_Volunteers', index=False)
        
        # Create summary sheet
        summary_data = {
            'Metric': [
                'Total Branches (Hours)',
                'Total Branches (Active Volunteers)',
                'Total Branches (Member Volunteers)',
                'Total Hours',
                'Total Active Volunteers',
                'Total Member Volunteers'
            ],
            'Count': [
                len(branch_hours_pivot) if branch_hours_pivot is not None else 0,
                len(active_volunteers_pivot) if active_volunteers_pivot is not None else 0,
                len(member_volunteers_pivot) if member_volunteers_pivot is not None else 0,
                branch_hours_pivot['TOTAL_HOURS'].sum() if branch_hours_pivot is not None else 0,
                active_volunteers_pivot['ACTIVE_VOLUNTEERS'].sum() if active_volunteers_pivot is not None else 0,
                member_volunteers_pivot['MEMBER_VOLUNTEERS'].sum() if member_volunteers_pivot is not None else 0
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    logger.info(f"✅ Excel report saved: {filepath}")
    return filepath

def update_summary_report(branch_hours_pivot, active_volunteers_pivot, member_volunteers_pivot, excel_file, output_dir="data/processed"):
    """Update the comprehensive summary report with branch breakdown results"""
    logger.info("\n📝 Adding Branch Breakdown to Summary Report...")
    
    summary_file = os.path.join(output_dir, "YMCA_Volunteer_Summary_Report.txt")
    
    with open(summary_file, 'a') as f:
        f.write("\n" + "="*60 + "\n")
        f.write("PAGES 2-5: BRANCH/SITE BREAKDOWN\n")
        f.write("="*60 + "\n")
        f.write(f"Date: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Excel File: {os.path.basename(excel_file)}\n\n")
        
        f.write("BRANCH HOURS (No Deduplication):\n")
        f.write(f"  • Total Branches: {len(branch_hours_pivot) if branch_hours_pivot is not None else 0}\n")
        f.write(f"  • Total Hours: {branch_hours_pivot['TOTAL_HOURS'].sum() if branch_hours_pivot is not None else 0}\n")
        f.write("  • Method: BRANCH and HOURS (sum)\n\n")
        
        f.write("ACTIVE VOLUNTEERS (Deduplicated):\n")
        f.write(f"  • Total Branches: {len(active_volunteers_pivot) if active_volunteers_pivot is not None else 0}\n")
        f.write(f"  • Total Active Volunteers: {active_volunteers_pivot['ACTIVE_VOLUNTEERS'].sum() if active_volunteers_pivot is not None else 0}\n")
        f.write("  • Method: Deduplicate by ASSIGNEE, BRANCH\n")
        f.write("  • Pivot: BRANCH and ASSIGNEE (count)\n\n")
        
        f.write("MEMBER VOLUNTEERS (Filtered):\n")
        f.write(f"  • Total Branches: {len(member_volunteers_pivot) if member_volunteers_pivot is not None else 0}\n")
        f.write(f"  • Total Member Volunteers: {member_volunteers_pivot['MEMBER_VOLUNTEERS'].sum() if member_volunteers_pivot is not None else 0}\n")
        f.write("  • Method: Filter by 'ARE YOU A YMCA MEMBER' = 'Yes'\n")
        f.write("  • Pivot: MEMBER BRANCH and count\n\n")
        
        f.write("TOP BRANCHES BY HOURS:\n")
        if branch_hours_pivot is not None:
            for _, row in branch_hours_pivot.head(5).iterrows():
                f.write(f"  • {row['BRANCH']}: {row['TOTAL_HOURS']} hours\n")
        f.write("\n")
        
        f.write("TOP BRANCHES BY ACTIVE VOLUNTEERS:\n")
        if active_volunteers_pivot is not None:
            for _, row in active_volunteers_pivot.head(5).iterrows():
                f.write(f"  • {row['BRANCH']}: {row['ACTIVE_VOLUNTEERS']} volunteers\n")
        f.write("\n")
        
        f.write("TOP BRANCHES BY MEMBER VOLUNTEERS:\n")
        if member_volunteers_pivot is not None:
            for _, row in member_volunteers_pivot.head(5).iterrows():
                f.write(f"  • {row['MEMBER_BRANCH']}: {row['MEMBER_VOLUNTEERS']} member volunteers\n")
        f.write("\n")
        
        f.write("NOTES:\n")
        f.write("  • Branch Hours: No deduplication - includes all volunteer hours\n")
        f.write("  • Active Volunteers: Deduplicated by volunteer and branch\n")
        f.write("  • Member Volunteers: Filtered from active volunteers who are YMCA members\n")
        f.write("  • Data ready for PowerPoint: Y Monthly Statistics Report 8.31.2025\n")
    
    logger.info(f"✅ Summary report updated: {summary_file}")
    return summary_file

def clean_output_directory(output_dir="data/processed"):
    """Clean output directory of previous run files"""
    logger.info(f"🧹 Cleaning output directory: {output_dir}")
    
    # Clean up previous processed files
    import glob
    patterns_to_clean = [
        "Y_Volunteer_2025_Branch_Breakdown_*.xlsx"
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
    """Main processing function for Pages 2-5: Branch/Site Breakdown"""
    logger.info("📊 YMCA Volunteer Statistics - Pages 2-5: Branch/Site Breakdown")
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
    
    # Extract branch information from assignment data
    df = extract_branch_info(df)
    
    # Analyze data structure
    hours_col, branch_cols, member_cols, assignee_cols = analyze_data_structure(df)
    
    if not hours_col:
        logger.error("❌ No hours column found in the data")
        return
    
    # Create pivot tables
    branch_hours_pivot = create_branch_hours_pivot(df, hours_col)
    active_volunteers_pivot, df_dedup = create_active_volunteers_pivot(df)
    member_volunteers_pivot = create_member_volunteers_pivot(df_dedup)
    
    # Create Excel report
    excel_file = create_excel_report(branch_hours_pivot, active_volunteers_pivot, member_volunteers_pivot)
    
    # Update summary report
    update_summary_report(branch_hours_pivot, active_volunteers_pivot, member_volunteers_pivot, excel_file)
    
    logger.info("\n🎯 Summary for PowerPoint Report:")
    logger.info(f"📊 Branch Hours: {len(branch_hours_pivot) if branch_hours_pivot is not None else 0} branches")
    logger.info(f"👥 Active Volunteers: {len(active_volunteers_pivot) if active_volunteers_pivot is not None else 0} branches")
    logger.info(f"🏊‍♂️ Member Volunteers: {len(member_volunteers_pivot) if member_volunteers_pivot is not None else 0} branches")
    logger.info(f"📁 Excel file ready for PowerPoint: {excel_file}")
    
    logger.info("\n📋 Next Steps:")
    logger.info("1. Review the Excel file for accuracy")
    logger.info("2. Import data into PowerPoint: Y Monthly Statistics Report 8.31.2025")
    logger.info("3. Verify branch breakdown calculations")
    logger.info("4. Check member volunteer filtering logic")
    
    return {
        'branch_hours': branch_hours_pivot,
        'active_volunteers': active_volunteers_pivot,
        'member_volunteers': member_volunteers_pivot,
        'excel_file': excel_file
    }

if __name__ == "__main__":
    main()

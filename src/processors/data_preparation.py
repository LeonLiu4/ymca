import pandas as pd
import datetime as dt
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, save_excel_data, find_latest_file
from src.utils.email_notifier import notify_processing_complete, notify_processing_error

logger = setup_logger(__name__, 'data_preparation.log')

def load_volunteer_data(file_path):
    """Load volunteer data from Excel file"""
    return load_excel_data(file_path)

def clean_volunteer_data(df):
    """🧹 Step 2: Prepare the Data - Remove 0 hours and clean data"""
    logger.info("\n🧹 Step 2: Preparing the Data...")
    
    # Show initial stats
    initial_count = len(df)
    logger.info(f"Initial rows: {initial_count}")
    
    # Find the hours column (case insensitive)
    hours_col = None
    for col in df.columns:
        if 'hour' in col.lower():
            hours_col = col
            break
    
    if hours_col is None:
        logger.error("❌ No 'Hours' column found. Available columns:")
        logger.error(df.columns.tolist())
        return df
    
    logger.info(f"Using Hours column: '{hours_col}'")
    
    # Show hours distribution
    logger.info(f"\nHours distribution:")
    hours_dist = df[hours_col].value_counts().sort_index()
    for hours, count in hours_dist.items():
        logger.info(f"  {hours} hours: {count} records")
    
    # Remove rows where Hours = 0
    df_cleaned = df[df[hours_col] != 0].copy()
    removed_count = initial_count - len(df_cleaned)
    
    logger.info(f"\n📊 Data Cleaning Results:")
    logger.info(f"  • Removed {removed_count} rows with 0 hours")
    logger.info(f"  • Remaining rows: {len(df_cleaned)}")
    logger.info(f"  • Volunteers with 0 hours only registered but did not complete the activity")
    
    return df_cleaned

def save_raw_data(df, output_dir="data/processed"):
    """Save cleaned data as 'Raw Data' file for multiple deduplication/pivot steps"""
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Raw_Data_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Save to Excel
    df.to_excel(filepath, index=False)
    logger.info(f"✅ Saved Raw Data: {filepath}")
    
    return filepath

def deduplicate_data(df, method="activity"):
    """Deduplicate data based on different methods"""
    logger.info(f"\n🔄 Deduplication by {method}...")
    
    initial_count = len(df)
    
    if method == "activity":
        # Remove duplicate activities (same person, same activity, same date)
        # This counts each unique activity completion
        df_dedup = df.drop_duplicates(subset=['volunteerDate', 'assignment'], keep='first')
        logger.info("  • Counting by activity: Each unique activity completion")
        
    elif method == "person":
        # Remove duplicate people (keep first occurrence)
        # This counts unique volunteers
        df_dedup = df.drop_duplicates(subset=['volunteerDate'], keep='first')
        logger.info("  • Counting by person: Each unique volunteer")
        
    elif method == "location":
        # Remove duplicate locations (same person, same location, same date)
        # This counts by branch/location
        location_col = None
        for col in df.columns:
            if 'location' in col.lower() or 'branch' in col.lower():
                location_col = col
                break
        
        if location_col:
            df_dedup = df.drop_duplicates(subset=['volunteerDate', location_col], keep='first')
            logger.info(f"  • Counting by location: Using column '{location_col}'")
        else:
            logger.warning("  • No location/branch column found, using activity method")
            df_dedup = df.drop_duplicates(subset=['volunteerDate', 'assignment'], keep='first')
            
    else:
        logger.error("❌ Invalid deduplication method. Use: 'activity', 'person', or 'location'")
        return df
    
    removed_count = initial_count - len(df_dedup)
    logger.info(f"  • Removed {removed_count} duplicate rows")
    logger.info(f"  • Remaining rows: {len(df_dedup)}")
    
    return df_dedup

def create_summary_report(df, output_dir="data/processed", step="Step 2: Data Preparation"):
    """Create or append to comprehensive summary report"""
    logger.info(f"\n📝 Adding {step} to Summary Report...")
    
    # Generate summary statistics
    summary = {
        'Total Records': len(df),
        'Date Range': f"{df['volunteerDate'].min()} to {df['volunteerDate'].max()}" if 'volunteerDate' in df.columns else "N/A"
    }
    
    # Add hours summary if available
    hours_col = None
    for col in df.columns:
        if 'hour' in col.lower():
            hours_col = col
            break
    
    if hours_col:
        summary['Total Hours'] = df[hours_col].sum()
        summary['Average Hours per Record'] = round(df[hours_col].mean(), 2)
        summary['Min Hours'] = df[hours_col].min()
        summary['Max Hours'] = df[hours_col].max()
    
    # Count unique assignments if available
    if 'assignment' in df.columns:
        summary['Unique Activities'] = df['assignment'].nunique()
        summary['Most Common Activity'] = df['assignment'].value_counts().index[0] if len(df) > 0 else "N/A"
    
    # Use consistent summary file name
    summary_file = os.path.join(output_dir, "YMCA_Volunteer_Summary_Report.txt")
    
    # Check if file exists to determine if we're appending
    file_exists = os.path.exists(summary_file)
    
    with open(summary_file, 'a' if file_exists else 'w') as f:
        if not file_exists:
            f.write("🏊‍♂️ YMCA Volunteer Data Processing - Complete Summary Report\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"\n{step}\n")
        f.write("-" * 50 + "\n")
        f.write(f"Completed: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")
        
        if step == "Step 2: Data Preparation":
            f.write("\n📋 Data Cleaning Notes:\n")
            f.write("• Removed volunteers with 0 hours (registered but didn't complete activity)\n")
            f.write("• Data ready for multiple deduplication/pivot steps\n")
            f.write("• Each data set requires its own deduplication logic\n")
            f.write("• Numbers vary depending on counting method (activity, person, location)\n")
    
    logger.info(f"✅ Summary report updated: {summary_file}")
    return summary_file

def clean_output_directory(output_dir="data/processed"):
    """Clean output directory of previous run files"""
    logger.info(f"🧹 Cleaning output directory: {output_dir}")
    
    # Clean up previous processed files
    import glob
    patterns_to_clean = [
        "Raw_Data_*.xlsx",
        "Summary_Report_*.txt", 
        "Y_Volunteer_2025_Statistics_*.xlsx",
        "YMCA_Volunteer_Summary_Report.txt"  # Clean the comprehensive summary report
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
    """Main processing function"""
    logger.info("🏊‍♂️ YMCA Volunteer Data Preparation - Step 2")
    logger.info("=" * 60)
    
    input_files = []
    output_files = []
    processing_type = "Data Preparation"
    
    try:
        # Clean output directory first
        clean_output_directory()
        
        # Find the most recent volunteer history file
        latest_file = find_latest_file("VolunteerHistory_*.xlsx", "data/raw")
        if not latest_file:
            error_msg = "No VolunteerHistory_*.xlsx files found in data/raw"
            logger.error(f"❌ {error_msg}")
            notify_processing_error(processing_type, error_msg, input_files)
            return
        
        logger.info(f"📁 Using file: {latest_file}")
        input_files.append(latest_file)
        
        # Load data
        df = load_volunteer_data(latest_file)
        if df is None:
            error_msg = f"Failed to load data from {latest_file}"
            notify_processing_error(processing_type, error_msg, input_files)
            return
        
        # Step 2: Clean data (remove 0 hours)
        df_cleaned = clean_volunteer_data(df)
        
        # Save raw data
        raw_data_file = save_raw_data(df_cleaned)
        output_files.append(raw_data_file)
        
        # Create summary report
        summary_file = create_summary_report(df_cleaned)
        output_files.append(summary_file)
        
        # Show deduplication options
        logger.info("\n🎯 Deduplication Options Available:")
        logger.info("1. By Activity: df.drop_duplicates(subset=['volunteerDate', 'assignment'])")
        logger.info("2. By Person: df.drop_duplicates(subset=['volunteerDate'])")
        logger.info("3. By Location: df.drop_duplicates(subset=['volunteerDate', 'branch'])")
        
        logger.info("\n📋 Next Steps:")
        logger.info("1. Review the Raw Data file for accuracy")
        logger.info("2. Apply specific deduplication logic as needed")
        logger.info("3. Check monthly for reporting errors")
        logger.info("4. Apply manual adjustments for special programs")
        
        # Send completion notification
        summary = f"Processed {len(df_cleaned)} records after removing {len(df) - len(df_cleaned) if df is not None else 0} records with 0 hours. Data is ready for deduplication and analysis."
        notify_processing_complete(
            processing_type=processing_type,
            files_processed=input_files,
            output_files=output_files,
            total_records=len(df_cleaned),
            summary=summary
        )
        
        return df_cleaned
        
    except Exception as e:
        error_msg = f"Unexpected error in data preparation: {str(e)}"
        logger.error(f"❌ {error_msg}")
        notify_processing_error(processing_type, error_msg, input_files)
        raise

if __name__ == "__main__":
    df = main()

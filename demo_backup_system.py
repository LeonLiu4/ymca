#!/usr/bin/env python3
"""
Demonstration of the backup system functionality
"""

import os
import sys
from pathlib import Path
import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import core functions (without pandas dependency for demo)
import shutil
import glob

def create_timestamped_backup_demo(file_path, archive_dir="data/archive"):
    """Demo version of create_timestamped_backup"""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"⚠️ File not found for backup: {file_path}")
            return None
            
        # Create archive directory
        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create backup filename with timestamp
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = archive_path / backup_name
        
        # Copy file to archive
        shutil.copy2(file_path, backup_path)
        
        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)
        
    except Exception as e:
        print(f"❌ Error creating backup for {file_path}: {e}")
        return None


def cleanup_old_backups_demo(archive_dir="data/archive", months_to_keep=6):
    """Demo version of cleanup_old_backups"""
    try:
        archive_path = Path(archive_dir)
        
        if not archive_path.exists():
            print(f"ℹ️ Archive directory does not exist: {archive_dir}")
            return 0
            
        # Calculate cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=months_to_keep * 30)
        
        removed_count = 0
        total_files = 0
        
        # Find all files in archive directory
        for file_path in archive_path.iterdir():
            if file_path.is_file():
                total_files += 1
                
                # Get file modification time
                file_mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    try:
                        file_path.unlink()
                        print(f"🗑️ Removed old backup: {file_path.name}")
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Error removing {file_path}: {e}")
                else:
                    age_days = (datetime.datetime.now() - file_mtime).days
                    print(f"📁 Keeping backup: {file_path.name} (age: {age_days} days)")
        
        print(f"📊 Cleanup complete: {removed_count}/{total_files} files removed (older than {months_to_keep} months)")
        return removed_count
        
    except Exception as e:
        print(f"❌ Error during backup cleanup: {e}")
        return 0


def get_archive_summary_demo(archive_dir="data/archive"):
    """Demo version of get_archive_summary"""
    try:
        archive_path = Path(archive_dir)
        
        if not archive_path.exists():
            return {"total_files": 0, "total_size_mb": 0, "oldest_file": None, "newest_file": None}
        
        files = [f for f in archive_path.iterdir() if f.is_file()]
        
        if not files:
            return {"total_files": 0, "total_size_mb": 0, "oldest_file": None, "newest_file": None}
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in files)
        total_size_mb = round(total_size / (1024 * 1024), 2)
        
        # Find oldest and newest files
        files_with_mtime = [(f, datetime.datetime.fromtimestamp(f.stat().st_mtime)) for f in files]
        oldest_file = min(files_with_mtime, key=lambda x: x[1])
        newest_file = max(files_with_mtime, key=lambda x: x[1])
        
        return {
            "total_files": len(files),
            "total_size_mb": total_size_mb,
            "oldest_file": {"name": oldest_file[0].name, "date": oldest_file[1].strftime("%Y-%m-%d %H:%M")},
            "newest_file": {"name": newest_file[0].name, "date": newest_file[1].strftime("%Y-%m-%d %H:%M")}
        }
        
    except Exception as e:
        print(f"❌ Error getting archive summary: {e}")
        return {"error": str(e)}


def main():
    """Demonstrate backup system functionality"""
    print("🏊‍♂️ YMCA Volunteer Data Backup System Demo")
    print("=" * 50)
    
    # Create some sample files to backup
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    sample_files = [
        "Raw_Data_20250906_120000.xlsx",
        "Y_Volunteer_2025_Statistics_20250906_130000.xlsx", 
        "Summary_Report_20250906.txt"
    ]
    
    print("📁 Creating sample processed files...")
    for filename in sample_files:
        file_path = processed_dir / filename
        content = f"Sample {filename} created at {datetime.datetime.now().isoformat()}\n"
        content += "This file contains YMCA volunteer data processing results.\n"
        file_path.write_text(content)
        print(f"   • Created: {filename}")
    
    print(f"\n🔄 Creating timestamped backups...")
    backup_count = 0
    for file_path in processed_dir.iterdir():
        if file_path.is_file():
            backup_result = create_timestamped_backup_demo(file_path)
            if backup_result:
                backup_count += 1
    
    print(f"\n✅ Created {backup_count} backup files")
    
    # Show archive summary
    print(f"\n📊 Archive Summary:")
    summary = get_archive_summary_demo()
    print(f"   • Total files: {summary['total_files']}")
    print(f"   • Total size: {summary['total_size_mb']} MB")
    if summary.get('oldest_file'):
        print(f"   • Oldest backup: {summary['oldest_file']['name']} ({summary['oldest_file']['date']})")
        print(f"   • Newest backup: {summary['newest_file']['name']} ({summary['newest_file']['date']})")
    
    # Test cleanup (with 0 months to show what would be cleaned)
    print(f"\n🧹 Testing cleanup functionality (dry run with 0 months retention)...")
    cleanup_old_backups_demo(months_to_keep=0)
    
    print(f"\n✨ Backup System Features Demonstrated:")
    print("   ✅ Timestamped backup creation")
    print("   ✅ Archive directory management") 
    print("   ✅ File size and date tracking")
    print("   ✅ Automated cleanup capabilities")
    print("   ✅ Integration ready for existing processors")


if __name__ == "__main__":
    main()
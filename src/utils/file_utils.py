"""
Shared file utilities for YMCA volunteer data processing
"""
import os
import pandas as pd
from pathlib import Path
from typing import Optional, Union
import logging
import shutil
import datetime
import glob

logger = logging.getLogger(__name__)


def load_excel_data(file_path: str) -> Optional[pd.DataFrame]:
    """Load data from Excel file with error handling"""
    try:
        df = pd.read_excel(file_path)
        logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"❌ Error loading file: {e}")
        return None


def save_excel_data(df: pd.DataFrame, filename: str, output_dir: str = "data/processed") -> str:
    """Save DataFrame to Excel with consistent naming and directory structure"""
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate full file path
    filepath = os.path.join(output_dir, filename)
    
    # Save to Excel
    df.to_excel(filepath, index=False)
    logger.info(f"✅ Saved: {filepath} | rows: {len(df)}")
    
    return filepath


def find_latest_file(pattern: str, directory: str = ".") -> Optional[Path]:
    """Find the most recent file matching a pattern"""
    files = list(Path(directory).glob(pattern))
    if not files:
        return None
    
    return max(files, key=os.path.getctime)


def create_timestamped_backup(file_path: Union[str, Path], archive_dir: str = "data/archive") -> Optional[str]:
    """
    Create a timestamped backup copy of a file in the archive directory
    
    Args:
        file_path: Path to the file to backup
        archive_dir: Directory to store backups (default: data/archive)
        
    Returns:
        Path to the backup file if successful, None if failed
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"File not found for backup: {file_path}")
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
        
        logger.info(f"✅ Backup created: {backup_path}")
        return str(backup_path)
        
    except Exception as e:
        logger.error(f"❌ Error creating backup for {file_path}: {e}")
        return None


def cleanup_old_backups(archive_dir: str = "data/archive", months_to_keep: int = 6) -> int:
    """
    Remove backup files older than specified number of months
    
    Args:
        archive_dir: Directory containing backup files
        months_to_keep: Number of months to keep (default: 6)
        
    Returns:
        Number of files removed
    """
    try:
        archive_path = Path(archive_dir)
        
        if not archive_path.exists():
            logger.info(f"Archive directory does not exist: {archive_dir}")
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
                        logger.info(f"🗑️ Removed old backup: {file_path.name}")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"❌ Error removing {file_path}: {e}")
        
        logger.info(f"📊 Cleanup complete: {removed_count}/{total_files} files removed (older than {months_to_keep} months)")
        return removed_count
        
    except Exception as e:
        logger.error(f"❌ Error during backup cleanup: {e}")
        return 0


def backup_and_save_excel_data(df: pd.DataFrame, filename: str, output_dir: str = "data/processed", 
                              create_backup: bool = True, archive_dir: str = "data/archive") -> str:
    """
    Save DataFrame to Excel with optional backup of existing file
    
    Args:
        df: DataFrame to save
        filename: Name of the output file
        output_dir: Directory to save the file (default: data/processed)
        create_backup: Whether to create backup of existing file (default: True)
        archive_dir: Directory to store backups (default: data/archive)
        
    Returns:
        Path to the saved file
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate full file path
    filepath = os.path.join(output_dir, filename)
    
    # Create backup of existing file before overwriting
    if create_backup and os.path.exists(filepath):
        create_timestamped_backup(filepath, archive_dir)
    
    # Save to Excel
    df.to_excel(filepath, index=False)
    logger.info(f"✅ Saved: {filepath} | rows: {len(df)}")
    
    return filepath


def get_archive_summary(archive_dir: str = "data/archive") -> dict:
    """
    Get summary information about backup files in archive directory
    
    Args:
        archive_dir: Directory containing backup files
        
    Returns:
        Dictionary with archive statistics
    """
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
        logger.error(f"❌ Error getting archive summary: {e}")
        return {"error": str(e)}
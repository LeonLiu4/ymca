#!/usr/bin/env python3
"""
YMCA Volunteer Data Backup Manager

This utility manages automatic backups and cleanup of processed files.
It provides commands to:
- Create timestamped backups of all processed files
- Clean up old backup files (older than X months)
- Show backup archive statistics
- Restore files from backups
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import setup_logger
from utils.file_utils import (
    create_timestamped_backup, 
    cleanup_old_backups, 
    get_archive_summary
)

logger = setup_logger(__name__, 'backup_manager.log')


def backup_all_processed_files(processed_dir: str = "data/processed", archive_dir: str = "data/archive"):
    """Create timestamped backups of all files in processed directory"""
    logger.info("🔄 Starting backup of all processed files...")
    
    processed_path = Path(processed_dir)
    if not processed_path.exists():
        logger.warning(f"Processed directory does not exist: {processed_dir}")
        return 0
    
    backup_count = 0
    
    # Backup all files in processed directory
    for file_path in processed_path.rglob("*"):
        if file_path.is_file():
            backup_result = create_timestamped_backup(file_path, archive_dir)
            if backup_result:
                backup_count += 1
    
    logger.info(f"✅ Backup complete: {backup_count} files backed up to {archive_dir}")
    return backup_count


def restore_file_from_backup(backup_file: str, restore_to: str = None):
    """Restore a file from backup to its original location or specified path"""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        logger.error(f"❌ Backup file not found: {backup_file}")
        return False
    
    if restore_to is None:
        # Try to determine original location from backup filename
        # Remove timestamp pattern from filename
        import re
        original_name = re.sub(r'_\d{8}_\d{6}', '', backup_path.name)
        restore_to = f"data/processed/{original_name}"
    
    restore_path = Path(restore_to)
    restore_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        import shutil
        shutil.copy2(backup_path, restore_path)
        logger.info(f"✅ File restored: {backup_file} -> {restore_to}")
        return True
    except Exception as e:
        logger.error(f"❌ Error restoring file: {e}")
        return False


def show_backup_status(archive_dir: str = "data/archive"):
    """Display current backup archive status"""
    logger.info("📊 Backup Archive Status")
    logger.info("=" * 50)
    
    summary = get_archive_summary(archive_dir)
    
    if "error" in summary:
        logger.error(f"❌ Error getting archive summary: {summary['error']}")
        return
    
    logger.info(f"Archive Directory: {archive_dir}")
    logger.info(f"Total Files: {summary['total_files']}")
    logger.info(f"Total Size: {summary['total_size_mb']} MB")
    
    if summary['oldest_file']:
        logger.info(f"Oldest Backup: {summary['oldest_file']['name']} ({summary['oldest_file']['date']})")
        logger.info(f"Newest Backup: {summary['newest_file']['name']} ({summary['newest_file']['date']})")
    
    # List recent backups
    archive_path = Path(archive_dir)
    if archive_path.exists():
        recent_files = sorted(
            [f for f in archive_path.iterdir() if f.is_file()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]  # Show last 10 files
        
        if recent_files:
            logger.info("\n📝 Recent Backups (last 10):")
            for file_path in recent_files:
                import datetime
                mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                size_kb = round(file_path.stat().st_size / 1024, 1)
                logger.info(f"  • {file_path.name} ({size_kb} KB, {mtime.strftime('%Y-%m-%d %H:%M')})")


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="YMCA Volunteer Data Backup Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backup_manager.py --backup-all          # Backup all processed files
  python backup_manager.py --cleanup 3           # Remove backups older than 3 months
  python backup_manager.py --status              # Show backup archive status
  python backup_manager.py --restore backup.xlsx # Restore specific backup file
        """
    )
    
    parser.add_argument('--backup-all', action='store_true',
                        help='Create timestamped backups of all processed files')
    
    parser.add_argument('--cleanup', type=int, metavar='MONTHS',
                        help='Remove backup files older than specified months (default: 6)')
    
    parser.add_argument('--status', action='store_true',
                        help='Show backup archive status and recent files')
    
    parser.add_argument('--restore', metavar='BACKUP_FILE',
                        help='Restore a specific backup file')
    
    parser.add_argument('--restore-to', metavar='PATH',
                        help='Specify restore destination (used with --restore)')
    
    parser.add_argument('--archive-dir', default='data/archive',
                        help='Archive directory path (default: data/archive)')
    
    parser.add_argument('--processed-dir', default='data/processed',
                        help='Processed files directory path (default: data/processed)')
    
    args = parser.parse_args()
    
    if not any([args.backup_all, args.cleanup is not None, args.status, args.restore]):
        parser.print_help()
        return
    
    logger.info("🏊‍♂️ YMCA Volunteer Data Backup Manager")
    logger.info("=" * 60)
    
    if args.backup_all:
        backup_all_processed_files(args.processed_dir, args.archive_dir)
    
    if args.cleanup is not None:
        months = args.cleanup if args.cleanup > 0 else 6
        removed = cleanup_old_backups(args.archive_dir, months)
        logger.info(f"🧹 Cleanup completed: {removed} files removed")
    
    if args.status:
        show_backup_status(args.archive_dir)
    
    if args.restore:
        restore_file_from_backup(args.restore, args.restore_to)


if __name__ == "__main__":
    main()
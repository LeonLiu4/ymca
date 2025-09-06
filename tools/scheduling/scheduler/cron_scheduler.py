#!/usr/bin/env python3
"""
Cron Scheduler Integration
=========================

This module handles integration with Unix/Linux cron jobs for automated
pipeline scheduling.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
import logging

from .scheduler_config import SchedulerConfigManager, ScheduleConfig


class CronScheduler:
    """Manages cron job integration for pipeline scheduling"""
    
    def __init__(self, config_manager: SchedulerConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.pipeline_script = self._get_pipeline_script_path()
    
    def _get_pipeline_script_path(self) -> str:
        """Get the path to the pipeline runner script"""
        # Get absolute path to the pipeline runner
        current_dir = Path(__file__).parent.parent.parent
        return str(current_dir / "run_scheduled_pipeline.py")
    
    def _get_current_crontab(self) -> List[str]:
        """Get current crontab entries"""
        try:
            result = subprocess.run(['crontab', '-l'], 
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip().split('\n') if result.stdout.strip() else []
            else:
                # No crontab exists yet
                return []
        except FileNotFoundError:
            raise RuntimeError("cron is not available on this system")
    
    def _write_crontab(self, lines: List[str]):
        """Write crontab entries"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cron') as f:
            f.write('\n'.join(lines))
            if lines:
                f.write('\n')  # Ensure file ends with newline
            temp_file = f.name
        
        try:
            result = subprocess.run(['crontab', temp_file], 
                                  capture_output=True, text=True, check=True)
            self.logger.info("Crontab updated successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to update crontab: {e}")
            raise
        finally:
            os.unlink(temp_file)
    
    def _generate_cron_comment(self, schedule_name: str) -> str:
        """Generate comment line for cron entry"""
        return f"# YMCA Pipeline: {schedule_name}"
    
    def _generate_cron_entry(self, schedule: ScheduleConfig) -> List[str]:
        """Generate cron entry for a schedule"""
        comment = self._generate_cron_comment(schedule.name)
        cron_expr = self.config_manager.get_cron_expression(schedule)
        
        # Build command with proper shell handling
        cmd_parts = [
            'cd', str(Path(self.pipeline_script).parent), '&&',
            'python3', self.pipeline_script,
            '--schedule', schedule.name,
            '2>>', '/tmp/ymca_pipeline_error.log',
            '1>>', '/tmp/ymca_pipeline.log'
        ]
        
        command = ' '.join(cmd_parts)
        cron_line = f"{cron_expr} {command}"
        
        return [comment, cron_line]
    
    def install_schedule(self, schedule_name: str) -> bool:
        """Install a schedule as a cron job"""
        schedule = self.config_manager.get_schedule(schedule_name)
        if not schedule:
            self.logger.error(f"Schedule '{schedule_name}' not found")
            return False
        
        if not schedule.enabled:
            self.logger.info(f"Schedule '{schedule_name}' is disabled, skipping")
            return True
        
        try:
            # Get current crontab
            current_lines = self._get_current_crontab()
            
            # Remove existing entries for this schedule
            self.remove_schedule(schedule_name, save_crontab=False)
            current_lines = self._get_current_crontab()
            
            # Add new entries
            new_entries = self._generate_cron_entry(schedule)
            updated_lines = current_lines + new_entries
            
            # Write updated crontab
            self._write_crontab(updated_lines)
            
            self.logger.info(f"Installed cron job for schedule: {schedule_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install schedule {schedule_name}: {e}")
            return False
    
    def remove_schedule(self, schedule_name: str, save_crontab: bool = True) -> bool:
        """Remove a schedule from cron"""
        try:
            current_lines = self._get_current_crontab()
            comment_marker = self._generate_cron_comment(schedule_name)
            
            # Find and remove lines related to this schedule
            filtered_lines = []
            skip_next = False
            
            for line in current_lines:
                if skip_next:
                    skip_next = False
                    continue
                
                if line == comment_marker:
                    skip_next = True  # Skip the cron entry that follows
                    continue
                
                filtered_lines.append(line)
            
            if save_crontab:
                self._write_crontab(filtered_lines)
                self.logger.info(f"Removed cron job for schedule: {schedule_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove schedule {schedule_name}: {e}")
            return False
    
    def install_all_schedules(self) -> Dict[str, bool]:
        """Install all enabled schedules as cron jobs"""
        results = {}
        schedules = self.config_manager.list_schedules()
        
        self.logger.info(f"Installing {len(schedules)} schedules to cron")
        
        for name, schedule in schedules.items():
            if schedule.enabled:
                results[name] = self.install_schedule(name)
            else:
                self.logger.info(f"Skipping disabled schedule: {name}")
                results[name] = True
        
        return results
    
    def remove_all_schedules(self) -> bool:
        """Remove all pipeline schedules from cron"""
        try:
            current_lines = self._get_current_crontab()
            
            # Filter out all YMCA Pipeline entries
            filtered_lines = []
            skip_next = False
            
            for line in current_lines:
                if skip_next:
                    skip_next = False
                    continue
                
                if line.startswith("# YMCA Pipeline:"):
                    skip_next = True  # Skip the cron entry that follows
                    continue
                
                filtered_lines.append(line)
            
            self._write_crontab(filtered_lines)
            self.logger.info("Removed all YMCA Pipeline cron jobs")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove all schedules: {e}")
            return False
    
    def list_installed_schedules(self) -> List[str]:
        """List schedules currently installed in cron"""
        try:
            current_lines = self._get_current_crontab()
            installed = []
            
            for line in current_lines:
                if line.startswith("# YMCA Pipeline:"):
                    schedule_name = line.replace("# YMCA Pipeline:", "").strip()
                    installed.append(schedule_name)
            
            return installed
            
        except Exception as e:
            self.logger.error(f"Failed to list installed schedules: {e}")
            return []
    
    def is_cron_available(self) -> bool:
        """Check if cron is available on the system"""
        try:
            result = subprocess.run(['which', 'crontab'], 
                                  capture_output=True, check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_cron_status(self) -> Dict[str, any]:
        """Get status information about cron integration"""
        return {
            'cron_available': self.is_cron_available(),
            'installed_schedules': self.list_installed_schedules(),
            'pipeline_script': self.pipeline_script,
            'log_files': {
                'output': '/tmp/ymca_pipeline.log',
                'errors': '/tmp/ymca_pipeline_error.log'
            }
        }
#!/usr/bin/env python3
"""
Windows Task Scheduler Integration
=================================

This module handles integration with Windows Task Scheduler for automated
pipeline scheduling.
"""

import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

from .scheduler_config import SchedulerConfigManager, ScheduleConfig, ScheduleFrequency


class WindowsScheduler:
    """Manages Windows Task Scheduler integration for pipeline scheduling"""
    
    def __init__(self, config_manager: SchedulerConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.pipeline_script = self._get_pipeline_script_path()
        self.task_prefix = "YMCA_Pipeline"
    
    def _get_pipeline_script_path(self) -> str:
        """Get the path to the pipeline runner script"""
        current_dir = Path(__file__).parent.parent.parent
        return str(current_dir / "run_scheduled_pipeline.py")
    
    def _run_schtasks_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run schtasks command with error handling"""
        try:
            result = subprocess.run(['schtasks'] + args, 
                                  capture_output=True, text=True, 
                                  check=False, encoding='utf-8')
            return result
        except FileNotFoundError:
            raise RuntimeError("schtasks is not available on this system")
    
    def _get_task_name(self, schedule_name: str) -> str:
        """Generate task name for Windows Task Scheduler"""
        return f"{self.task_prefix}_{schedule_name}"
    
    def _get_schedule_trigger(self, schedule: ScheduleConfig) -> str:
        """Convert schedule to Windows Task Scheduler trigger"""
        if schedule.frequency == ScheduleFrequency.DAILY:
            return "DAILY"
        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            return "WEEKLY"
        elif schedule.frequency == ScheduleFrequency.MONTHLY:
            return "MONTHLY"
        else:
            raise ValueError(f"Unsupported frequency: {schedule.frequency}")
    
    def _generate_task_xml(self, schedule: ScheduleConfig) -> str:
        """Generate XML for Windows Task Scheduler task"""
        # Create root element
        task = ET.Element("Task", version="1.3", 
                         xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task")
        
        # Registration info
        registration = ET.SubElement(task, "RegistrationInfo")
        ET.SubElement(registration, "Description").text = f"YMCA Pipeline: {schedule.name}"
        ET.SubElement(registration, "Author").text = "YMCA Data Processing System"
        
        # Triggers
        triggers = ET.SubElement(task, "Triggers")
        
        if schedule.frequency == ScheduleFrequency.DAILY:
            trigger = ET.SubElement(triggers, "CalendarTrigger")
            ET.SubElement(trigger, "StartBoundary").text = f"2025-01-01T{schedule.time}:00"
            schedule_by_day = ET.SubElement(trigger, "ScheduleByDay")
            ET.SubElement(schedule_by_day, "DaysInterval").text = "1"
            
        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            trigger = ET.SubElement(triggers, "CalendarTrigger")
            ET.SubElement(trigger, "StartBoundary").text = f"2025-01-05T{schedule.time}:00"  # Sunday
            schedule_by_week = ET.SubElement(trigger, "ScheduleByWeek")
            ET.SubElement(schedule_by_week, "WeeksInterval").text = "1"
            days_of_week = ET.SubElement(schedule_by_week, "DaysOfWeek")
            ET.SubElement(days_of_week, "Sunday")
            
        elif schedule.frequency == ScheduleFrequency.MONTHLY:
            trigger = ET.SubElement(triggers, "CalendarTrigger")
            ET.SubElement(trigger, "StartBoundary").text = f"2025-01-01T{schedule.time}:00"
            schedule_by_month = ET.SubElement(trigger, "ScheduleByMonth")
            days_of_month = ET.SubElement(schedule_by_month, "DaysOfMonth")
            ET.SubElement(days_of_month, "Day").text = "1"
            months = ET.SubElement(schedule_by_month, "Months")
            for month in ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"]:
                ET.SubElement(months, month)
        
        # Principal (run settings)
        principals = ET.SubElement(task, "Principals")
        principal = ET.SubElement(principals, "Principal", id="Author")
        ET.SubElement(principal, "LogonType").text = "InteractiveToken"
        ET.SubElement(principal, "RunLevel").text = "LeastPrivilege"
        
        # Settings
        settings = ET.SubElement(task, "Settings")
        ET.SubElement(settings, "MultipleInstancesPolicy").text = "IgnoreNew"
        ET.SubElement(settings, "DisallowStartIfOnBatteries").text = "false"
        ET.SubElement(settings, "StopIfGoingOnBatteries").text = "false"
        ET.SubElement(settings, "AllowHardTerminate").text = "true"
        ET.SubElement(settings, "StartWhenAvailable").text = "false"
        ET.SubElement(settings, "RunOnlyIfNetworkAvailable").text = "false"
        ET.SubElement(settings, "IdleSettings")
        ET.SubElement(settings, "AllowStartOnDemand").text = "true"
        ET.SubElement(settings, "Enabled").text = "true"
        ET.SubElement(settings, "Hidden").text = "false"
        ET.SubElement(settings, "RunOnlyIfIdle").text = "false"
        ET.SubElement(settings, "DisallowStartOnRemoteAppSession").text = "false"
        ET.SubElement(settings, "UseUnifiedSchedulingEngine").text = "true"
        ET.SubElement(settings, "WakeToRun").text = "false"
        ET.SubElement(settings, "ExecutionTimeLimit").text = f"PT{schedule.timeout_minutes}M"
        ET.SubElement(settings, "Priority").text = "7"
        
        # Actions
        actions = ET.SubElement(task, "Actions", Context="Author")
        exec_action = ET.SubElement(actions, "Exec")
        ET.SubElement(exec_action, "Command").text = "python"
        ET.SubElement(exec_action, "Arguments").text = f'"{self.pipeline_script}" --schedule "{schedule.name}"'
        ET.SubElement(exec_action, "WorkingDirectory").text = str(Path(self.pipeline_script).parent)
        
        # Convert to string
        ET.indent(task, space="  ", level=0)
        return ET.tostring(task, encoding='unicode')
    
    def install_schedule(self, schedule_name: str) -> bool:
        """Install a schedule as a Windows Task"""
        schedule = self.config_manager.get_schedule(schedule_name)
        if not schedule:
            self.logger.error(f"Schedule '{schedule_name}' not found")
            return False
        
        if not schedule.enabled:
            self.logger.info(f"Schedule '{schedule_name}' is disabled, skipping")
            return True
        
        try:
            task_name = self._get_task_name(schedule_name)
            
            # Remove existing task if it exists
            self.remove_schedule(schedule_name)
            
            # Generate task XML
            xml_content = self._generate_task_xml(schedule)
            
            # Write XML to temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                           suffix='.xml', encoding='utf-8') as f:
                f.write(xml_content)
                xml_file = f.name
            
            try:
                # Create task using schtasks
                result = self._run_schtasks_command([
                    '/Create', '/TN', task_name, '/XML', xml_file, '/F'
                ])
                
                if result.returncode == 0:
                    self.logger.info(f"Installed Windows Task for schedule: {schedule_name}")
                    return True
                else:
                    self.logger.error(f"Failed to create task: {result.stderr}")
                    return False
                    
            finally:
                os.unlink(xml_file)
            
        except Exception as e:
            self.logger.error(f"Failed to install schedule {schedule_name}: {e}")
            return False
    
    def remove_schedule(self, schedule_name: str) -> bool:
        """Remove a schedule from Windows Task Scheduler"""
        try:
            task_name = self._get_task_name(schedule_name)
            
            # Check if task exists first
            result = self._run_schtasks_command(['/Query', '/TN', task_name])
            
            if result.returncode == 0:
                # Task exists, delete it
                result = self._run_schtasks_command(['/Delete', '/TN', task_name, '/F'])
                
                if result.returncode == 0:
                    self.logger.info(f"Removed Windows Task for schedule: {schedule_name}")
                    return True
                else:
                    self.logger.error(f"Failed to delete task: {result.stderr}")
                    return False
            else:
                # Task doesn't exist, consider it success
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove schedule {schedule_name}: {e}")
            return False
    
    def install_all_schedules(self) -> Dict[str, bool]:
        """Install all enabled schedules as Windows Tasks"""
        results = {}
        schedules = self.config_manager.list_schedules()
        
        self.logger.info(f"Installing {len(schedules)} schedules to Windows Task Scheduler")
        
        for name, schedule in schedules.items():
            if schedule.enabled:
                results[name] = self.install_schedule(name)
            else:
                self.logger.info(f"Skipping disabled schedule: {name}")
                results[name] = True
        
        return results
    
    def remove_all_schedules(self) -> bool:
        """Remove all pipeline schedules from Windows Task Scheduler"""
        try:
            # Get all tasks with our prefix
            result = self._run_schtasks_command(['/Query', '/FO', 'CSV'])
            
            if result.returncode != 0:
                return True  # No tasks to remove
            
            # Parse CSV output to find our tasks
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:  # No data rows
                return True
            
            # Find tasks with our prefix
            our_tasks = []
            for line in lines[1:]:  # Skip header
                if f'"{self.task_prefix}_' in line:
                    # Extract task name (first column in CSV)
                    task_name = line.split(',')[0].strip('"')
                    our_tasks.append(task_name)
            
            # Remove each task
            success = True
            for task_name in our_tasks:
                result = self._run_schtasks_command(['/Delete', '/TN', task_name, '/F'])
                if result.returncode != 0:
                    self.logger.error(f"Failed to delete task {task_name}: {result.stderr}")
                    success = False
            
            if success:
                self.logger.info("Removed all YMCA Pipeline Windows Tasks")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to remove all schedules: {e}")
            return False
    
    def list_installed_schedules(self) -> List[str]:
        """List schedules currently installed in Windows Task Scheduler"""
        try:
            result = self._run_schtasks_command(['/Query', '/FO', 'CSV'])
            
            if result.returncode != 0:
                return []
            
            # Parse CSV output
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:  # No data rows
                return []
            
            installed = []
            for line in lines[1:]:  # Skip header
                if f'"{self.task_prefix}_' in line:
                    # Extract task name and convert back to schedule name
                    task_name = line.split(',')[0].strip('"')
                    schedule_name = task_name.replace(f"{self.task_prefix}_", "")
                    installed.append(schedule_name)
            
            return installed
            
        except Exception as e:
            self.logger.error(f"Failed to list installed schedules: {e}")
            return []
    
    def is_task_scheduler_available(self) -> bool:
        """Check if Windows Task Scheduler is available"""
        try:
            result = subprocess.run(['where', 'schtasks'], 
                                  capture_output=True, check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_task_status(self, schedule_name: str) -> Optional[Dict[str, any]]:
        """Get status of a specific task"""
        try:
            task_name = self._get_task_name(schedule_name)
            result = self._run_schtasks_command(['/Query', '/TN', task_name, '/V', '/FO', 'CSV'])
            
            if result.returncode != 0:
                return None
            
            # Parse the CSV output (simplified)
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return None
            
            # This is a simplified parser - in practice you might want more robust CSV parsing
            data = lines[1].split(',')
            
            return {
                'task_name': task_name,
                'status': 'Installed',
                'next_run_time': data[4] if len(data) > 4 else 'Unknown',
                'last_run_time': data[5] if len(data) > 5 else 'Unknown',
                'last_result': data[6] if len(data) > 6 else 'Unknown'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get task status for {schedule_name}: {e}")
            return None
    
    def get_scheduler_status(self) -> Dict[str, any]:
        """Get status information about Windows Task Scheduler integration"""
        return {
            'task_scheduler_available': self.is_task_scheduler_available(),
            'installed_schedules': self.list_installed_schedules(),
            'pipeline_script': self.pipeline_script,
            'task_prefix': self.task_prefix
        }
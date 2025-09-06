#!/usr/bin/env python3
"""
Schedule Manager
===============

Command-line interface for managing automated pipeline scheduling.

Usage:
    python schedule_manager.py --help
"""

import sys
import os
import argparse
import platform
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scheduler import (
    SchedulerConfigManager, 
    CronScheduler, 
    WindowsScheduler,
    ScheduleConfig,
    ScheduleFrequency,
    ProcessingStep
)
from utils.logging_config import setup_logger


class ScheduleManager:
    """Main schedule management interface"""
    
    def __init__(self, config_file: str = 'scheduler_config.json'):
        self.logger = setup_logger(__name__)
        self.config_manager = SchedulerConfigManager(config_file)
        
        # Initialize appropriate scheduler based on platform
        if platform.system() == 'Windows':
            self.system_scheduler = WindowsScheduler(self.config_manager)
            self.platform = 'Windows'
        else:
            self.system_scheduler = CronScheduler(self.config_manager)
            self.platform = 'Unix/Linux'
        
        self.logger.info(f"Schedule Manager initialized for {self.platform}")
    
    def create_schedule(self, args) -> bool:
        """Create a new schedule"""
        try:
            # Parse processing steps
            steps = []
            if args.steps:
                for step_name in args.steps:
                    try:
                        steps.append(ProcessingStep(step_name.lower()))
                    except ValueError:
                        self.logger.error(f"Invalid processing step: {step_name}")
                        return False
            else:
                # Default steps
                steps = [ProcessingStep.EXTRACT, ProcessingStep.PREPARE, 
                        ProcessingStep.STATISTICS, ProcessingStep.PIE_CHARTS]
            
            # Create schedule configuration
            schedule = ScheduleConfig(
                name=args.name,
                frequency=ScheduleFrequency(args.frequency),
                time=args.time,
                enabled=not args.disabled,
                processing_steps=steps,
                input_directory=args.input_dir or "data/raw",
                output_directory=args.output_dir or "data/processed",
                email_notifications=args.email_notifications,
                notification_email=args.notification_email,
                max_retries=args.max_retries,
                timeout_minutes=args.timeout
            )
            
            # Validate schedule
            errors = self.config_manager.validate_schedule(schedule)
            if errors:
                self.logger.error("Schedule validation failed:")
                for error in errors:
                    self.logger.error(f"  - {error}")
                return False
            
            # Add to configuration
            self.config_manager.add_schedule(schedule)
            self.logger.info(f"Created schedule: {args.name}")
            
            # Install to system scheduler if enabled
            if schedule.enabled and args.install:
                if self.system_scheduler.install_schedule(args.name):
                    self.logger.info(f"Installed schedule to {self.platform} scheduler")
                else:
                    self.logger.warning("Failed to install to system scheduler")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create schedule: {e}")
            return False
    
    def list_schedules(self, args) -> bool:
        """List all schedules"""
        try:
            schedules = self.config_manager.list_schedules()
            
            if not schedules:
                print("No schedules configured")
                return True
            
            # Get installed schedules from system
            installed_schedules = set(self.system_scheduler.list_installed_schedules())
            
            print(f"\nConfigured Schedules ({len(schedules)}):")
            print("=" * 80)
            
            for name, schedule in schedules.items():
                status = "✓ Enabled" if schedule.enabled else "✗ Disabled"
                installed = "🔗 Installed" if name in installed_schedules else "⚪ Not Installed"
                
                print(f"\n📋 {name}")
                print(f"   Status: {status}")
                print(f"   System: {installed}")
                print(f"   Frequency: {schedule.frequency.value}")
                print(f"   Time: {schedule.time}")
                print(f"   Steps: {', '.join(step.value for step in schedule.processing_steps)}")
                print(f"   Input: {schedule.input_directory}")
                print(f"   Output: {schedule.output_directory}")
                
                if schedule.email_notifications:
                    print(f"   Email: {schedule.notification_email}")
            
            print(f"\n📊 System Scheduler Status ({self.platform}):")
            if hasattr(self.system_scheduler, 'is_cron_available'):
                available = self.system_scheduler.is_cron_available()
            else:
                available = self.system_scheduler.is_task_scheduler_available()
            
            print(f"   Available: {'✓ Yes' if available else '✗ No'}")
            print(f"   Installed: {len(installed_schedules)} schedule(s)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to list schedules: {e}")
            return False
    
    def install_schedules(self, args) -> bool:
        """Install schedules to system scheduler"""
        try:
            if args.name:
                # Install specific schedule
                success = self.system_scheduler.install_schedule(args.name)
                if success:
                    self.logger.info(f"Installed schedule '{args.name}' to {self.platform} scheduler")
                else:
                    self.logger.error(f"Failed to install schedule '{args.name}'")
                return success
            else:
                # Install all schedules
                results = self.system_scheduler.install_all_schedules()
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                self.logger.info(f"Installed {success_count}/{total_count} schedules to {self.platform} scheduler")
                
                # Show failures
                for name, success in results.items():
                    if not success:
                        self.logger.error(f"Failed to install: {name}")
                
                return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"Failed to install schedules: {e}")
            return False
    
    def remove_schedules(self, args) -> bool:
        """Remove schedules from system scheduler"""
        try:
            if args.name:
                # Remove specific schedule
                success = self.system_scheduler.remove_schedule(args.name)
                if success:
                    self.logger.info(f"Removed schedule '{args.name}' from {self.platform} scheduler")
                else:
                    self.logger.error(f"Failed to remove schedule '{args.name}'")
                
                # Also remove from config if requested
                if args.delete_config:
                    if self.config_manager.remove_schedule(args.name):
                        self.logger.info(f"Deleted schedule configuration: {args.name}")
                    else:
                        self.logger.error(f"Failed to delete schedule configuration: {args.name}")
                
                return success
            else:
                # Remove all schedules
                success = self.system_scheduler.remove_all_schedules()
                if success:
                    self.logger.info(f"Removed all YMCA Pipeline schedules from {self.platform} scheduler")
                else:
                    self.logger.error("Failed to remove all schedules")
                return success
            
        except Exception as e:
            self.logger.error(f"Failed to remove schedules: {e}")
            return False
    
    def enable_disable_schedule(self, args) -> bool:
        """Enable or disable a schedule"""
        try:
            success = self.config_manager.enable_schedule(args.name, args.enable)
            if success:
                action = "enabled" if args.enable else "disabled"
                self.logger.info(f"Schedule '{args.name}' {action}")
                
                # Update system scheduler
                if args.enable:
                    self.system_scheduler.install_schedule(args.name)
                else:
                    self.system_scheduler.remove_schedule(args.name)
                
                return True
            else:
                self.logger.error(f"Schedule '{args.name}' not found")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to modify schedule: {e}")
            return False
    
    def show_status(self, args) -> bool:
        """Show system scheduler status"""
        try:
            if hasattr(self.system_scheduler, 'get_cron_status'):
                status = self.system_scheduler.get_cron_status()
            else:
                status = self.system_scheduler.get_scheduler_status()
            
            print(f"\n{self.platform} Scheduler Status:")
            print("=" * 50)
            
            if self.platform == 'Unix/Linux':
                print(f"Cron Available: {'✓ Yes' if status['cron_available'] else '✗ No'}")
                print(f"Pipeline Script: {status['pipeline_script']}")
                print(f"Output Log: {status['log_files']['output']}")
                print(f"Error Log: {status['log_files']['errors']}")
            else:
                print(f"Task Scheduler Available: {'✓ Yes' if status['task_scheduler_available'] else '✗ No'}")
                print(f"Pipeline Script: {status['pipeline_script']}")
                print(f"Task Prefix: {status['task_prefix']}")
            
            print(f"\nInstalled Schedules ({len(status['installed_schedules'])}):")
            for schedule_name in status['installed_schedules']:
                print(f"  • {schedule_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Manage automated pipeline scheduling')
    parser.add_argument('--config', default='scheduler_config.json',
                       help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create schedule command
    create_parser = subparsers.add_parser('create', help='Create a new schedule')
    create_parser.add_argument('name', help='Schedule name')
    create_parser.add_argument('--frequency', required=True, 
                              choices=['daily', 'weekly', 'monthly'],
                              help='Schedule frequency')
    create_parser.add_argument('--time', required=True,
                              help='Time to run (HH:MM format)')
    create_parser.add_argument('--steps', nargs='+',
                              choices=['extract', 'prepare', 'statistics', 'pie_charts',
                                     'bar_charts', 'line_graphs', 'scatter_plots', 'histograms'],
                              help='Processing steps to include')
    create_parser.add_argument('--input-dir', help='Input directory path')
    create_parser.add_argument('--output-dir', help='Output directory path')
    create_parser.add_argument('--email-notifications', action='store_true',
                              help='Enable email notifications')
    create_parser.add_argument('--notification-email', help='Notification email address')
    create_parser.add_argument('--max-retries', type=int, default=3,
                              help='Maximum retry attempts')
    create_parser.add_argument('--timeout', type=int, default=60,
                              help='Timeout in minutes')
    create_parser.add_argument('--disabled', action='store_true',
                              help='Create schedule as disabled')
    create_parser.add_argument('--install', action='store_true',
                              help='Install to system scheduler after creation')
    
    # List schedules command
    list_parser = subparsers.add_parser('list', help='List all schedules')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install schedules to system')
    install_parser.add_argument('name', nargs='?', help='Specific schedule to install')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove schedules from system')
    remove_parser.add_argument('name', nargs='?', help='Specific schedule to remove')
    remove_parser.add_argument('--delete-config', action='store_true',
                              help='Also delete from configuration')
    
    # Enable/disable commands
    enable_parser = subparsers.add_parser('enable', help='Enable a schedule')
    enable_parser.add_argument('name', help='Schedule name to enable')
    
    disable_parser = subparsers.add_parser('disable', help='Disable a schedule')
    disable_parser.add_argument('name', help='Schedule name to disable')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show scheduler status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize schedule manager
    try:
        manager = ScheduleManager(args.config)
    except Exception as e:
        print(f"Failed to initialize schedule manager: {e}")
        return 1
    
    # Execute command
    success = False
    if args.command == 'create':
        success = manager.create_schedule(args)
    elif args.command == 'list':
        success = manager.list_schedules(args)
    elif args.command == 'install':
        success = manager.install_schedules(args)
    elif args.command == 'remove':
        success = manager.remove_schedules(args)
    elif args.command == 'enable':
        args.enable = True
        success = manager.enable_disable_schedule(args)
    elif args.command == 'disable':
        args.enable = False
        success = manager.enable_disable_schedule(args)
    elif args.command == 'status':
        success = manager.show_status(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
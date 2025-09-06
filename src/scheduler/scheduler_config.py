#!/usr/bin/env python3
"""
Scheduler Configuration System
=============================

This module handles configuration for automated pipeline scheduling.
Supports daily, weekly, and monthly schedules with customizable processing options.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class ScheduleFrequency(Enum):
    """Supported scheduling frequencies"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ProcessingStep(Enum):
    """Available processing steps in the pipeline"""
    EXTRACT = "extract"
    PREPARE = "prepare"
    STATISTICS = "statistics"
    PIE_CHARTS = "pie_charts"
    BAR_CHARTS = "bar_charts"
    LINE_GRAPHS = "line_graphs"
    SCATTER_PLOTS = "scatter_plots"
    HISTOGRAMS = "histograms"


@dataclass
class ScheduleConfig:
    """Configuration for a scheduled task"""
    name: str
    frequency: ScheduleFrequency
    time: str  # Format: "HH:MM" (24-hour)
    enabled: bool = True
    processing_steps: List[ProcessingStep] = None
    input_directory: str = "data/raw"
    output_directory: str = "data/processed"
    email_notifications: bool = False
    notification_email: Optional[str] = None
    max_retries: int = 3
    timeout_minutes: int = 60
    
    def __post_init__(self):
        if self.processing_steps is None:
            # Default to full pipeline
            self.processing_steps = [
                ProcessingStep.EXTRACT,
                ProcessingStep.PREPARE,
                ProcessingStep.STATISTICS,
                ProcessingStep.PIE_CHARTS
            ]


class SchedulerConfigManager:
    """Manages scheduler configuration file"""
    
    def __init__(self, config_path: str = "scheduler_config.json"):
        self.config_path = Path(config_path)
        self.schedules: Dict[str, ScheduleConfig] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    
                for name, config_data in data.get('schedules', {}).items():
                    # Convert string enums back to enum objects
                    config_data['frequency'] = ScheduleFrequency(config_data['frequency'])
                    config_data['processing_steps'] = [
                        ProcessingStep(step) for step in config_data.get('processing_steps', [])
                    ]
                    self.schedules[name] = ScheduleConfig(**config_data)
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error loading scheduler config: {e}")
                self.schedules = {}
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        # Daily processing at 6:00 AM
        daily_config = ScheduleConfig(
            name="daily_processing",
            frequency=ScheduleFrequency.DAILY,
            time="06:00",
            processing_steps=[
                ProcessingStep.EXTRACT,
                ProcessingStep.PREPARE,
                ProcessingStep.STATISTICS
            ]
        )
        
        # Weekly full processing on Sundays at 3:00 AM
        weekly_config = ScheduleConfig(
            name="weekly_full_processing",
            frequency=ScheduleFrequency.WEEKLY,
            time="03:00",
            processing_steps=[step for step in ProcessingStep]
        )
        
        # Monthly comprehensive report on 1st at 2:00 AM
        monthly_config = ScheduleConfig(
            name="monthly_report",
            frequency=ScheduleFrequency.MONTHLY,
            time="02:00",
            processing_steps=[step for step in ProcessingStep],
            email_notifications=True
        )
        
        self.schedules = {
            "daily_processing": daily_config,
            "weekly_full_processing": weekly_config,
            "monthly_report": monthly_config
        }
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        config_data = {
            'schedules': {
                name: {
                    **asdict(schedule),
                    'frequency': schedule.frequency.value,
                    'processing_steps': [step.value for step in schedule.processing_steps]
                }
                for name, schedule in self.schedules.items()
            },
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def add_schedule(self, schedule: ScheduleConfig):
        """Add a new schedule"""
        self.schedules[schedule.name] = schedule
        self.save_config()
    
    def remove_schedule(self, name: str):
        """Remove a schedule"""
        if name in self.schedules:
            del self.schedules[name]
            self.save_config()
            return True
        return False
    
    def get_schedule(self, name: str) -> Optional[ScheduleConfig]:
        """Get a specific schedule"""
        return self.schedules.get(name)
    
    def list_schedules(self) -> Dict[str, ScheduleConfig]:
        """List all schedules"""
        return self.schedules.copy()
    
    def enable_schedule(self, name: str, enabled: bool = True):
        """Enable or disable a schedule"""
        if name in self.schedules:
            self.schedules[name].enabled = enabled
            self.save_config()
            return True
        return False
    
    def get_cron_expression(self, schedule: ScheduleConfig) -> str:
        """Convert schedule to cron expression"""
        hour, minute = schedule.time.split(':')
        
        if schedule.frequency == ScheduleFrequency.DAILY:
            return f"{minute} {hour} * * *"
        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            # Sunday = 0 in cron
            return f"{minute} {hour} * * 0"
        elif schedule.frequency == ScheduleFrequency.MONTHLY:
            # First day of month
            return f"{minute} {hour} 1 * *"
        else:
            raise ValueError(f"Unsupported frequency: {schedule.frequency}")
    
    def validate_schedule(self, schedule: ScheduleConfig) -> List[str]:
        """Validate schedule configuration"""
        errors = []
        
        # Validate time format
        try:
            time_parts = schedule.time.split(':')
            if len(time_parts) != 2:
                errors.append("Time must be in HH:MM format")
            else:
                hour, minute = int(time_parts[0]), int(time_parts[1])
                if not (0 <= hour <= 23):
                    errors.append("Hour must be between 0 and 23")
                if not (0 <= minute <= 59):
                    errors.append("Minute must be between 0 and 59")
        except ValueError:
            errors.append("Invalid time format")
        
        # Validate directories
        if not Path(schedule.input_directory).exists():
            errors.append(f"Input directory does not exist: {schedule.input_directory}")
        
        # Validate email if notifications enabled
        if schedule.email_notifications and not schedule.notification_email:
            errors.append("Email address required when notifications are enabled")
        
        # Validate processing steps
        if not schedule.processing_steps:
            errors.append("At least one processing step must be specified")
        
        return errors
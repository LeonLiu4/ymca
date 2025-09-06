#!/usr/bin/env python3
"""
Pipeline Runner
==============

This module runs the actual data processing pipeline based on scheduled
configuration.
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from .scheduler_config import SchedulerConfigManager, ScheduleConfig, ProcessingStep
from utils.logging_config import setup_logger


class PipelineRunner:
    """Executes the data processing pipeline based on schedule configuration"""
    
    def __init__(self, config_manager: SchedulerConfigManager):
        self.config_manager = config_manager
        self.logger = setup_logger(__name__)
        self.project_root = Path(__file__).parent.parent.parent
    
    def _run_processing_step(self, step: ProcessingStep, schedule: ScheduleConfig) -> bool:
        """Run a single processing step"""
        self.logger.info(f"Running processing step: {step.value}")
        
        try:
            if step == ProcessingStep.EXTRACT:
                return self._run_extractor(schedule)
            elif step == ProcessingStep.PREPARE:
                return self._run_data_preparation(schedule)
            elif step == ProcessingStep.STATISTICS:
                return self._run_statistics(schedule)
            elif step == ProcessingStep.PIE_CHARTS:
                return self._run_pie_charts(schedule)
            elif step == ProcessingStep.BAR_CHARTS:
                return self._run_bar_charts(schedule)
            elif step == ProcessingStep.LINE_GRAPHS:
                return self._run_line_graphs(schedule)
            elif step == ProcessingStep.SCATTER_PLOTS:
                return self._run_scatter_plots(schedule)
            elif step == ProcessingStep.HISTOGRAMS:
                return self._run_histograms(schedule)
            else:
                self.logger.error(f"Unknown processing step: {step}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in processing step {step.value}: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _run_extractor(self, schedule: ScheduleConfig) -> bool:
        """Run volunteer history extractor"""
        try:
            from extractors.volunteer_history_extractor import main as extract_main
            
            # Change to project root directory
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                extract_main()
                self.logger.info("Data extraction completed successfully")
                return True
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run data extraction: {e}")
            return False
    
    def _run_data_preparation(self, schedule: ScheduleConfig) -> bool:
        """Run data preparation"""
        try:
            from processors.data_preparation import main as prepare_main
            
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                prepare_main()
                self.logger.info("Data preparation completed successfully")
                return True
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run data preparation: {e}")
            return False
    
    def _run_statistics(self, schedule: ScheduleConfig) -> bool:
        """Run project statistics"""
        try:
            from processors.project_statistics import main as stats_main
            
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                stats_main()
                self.logger.info("Statistics generation completed successfully")
                return True
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run statistics: {e}")
            return False
    
    def _run_pie_charts(self, schedule: ScheduleConfig) -> bool:
        """Run pie chart generation"""
        try:
            # Check if we have XLSX files to process
            input_path = Path(schedule.input_directory)
            xlsx_files = list(input_path.glob("*.xlsx"))
            
            if not xlsx_files:
                # Try processed directory
                processed_path = Path(schedule.output_directory)
                xlsx_files = list(processed_path.glob("*.xlsx"))
            
            if not xlsx_files:
                self.logger.warning("No XLSX files found for pie chart generation")
                return True  # Not a failure, just nothing to process
            
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                # Import and run pie chart generation
                import subprocess
                result = subprocess.run([
                    sys.executable, 'create_pie_charts.py'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    self.logger.info("Pie chart generation completed successfully")
                    return True
                else:
                    self.logger.error(f"Pie chart generation failed: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run pie chart generation: {e}")
            return False
    
    def _run_bar_charts(self, schedule: ScheduleConfig) -> bool:
        """Run bar chart generation"""
        try:
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, 'generate_bar_charts.py'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    self.logger.info("Bar chart generation completed successfully")
                    return True
                else:
                    self.logger.error(f"Bar chart generation failed: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run bar chart generation: {e}")
            return False
    
    def _run_line_graphs(self, schedule: ScheduleConfig) -> bool:
        """Run line graph generation"""
        try:
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, 'generate_line_graphs.py'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    self.logger.info("Line graph generation completed successfully")
                    return True
                else:
                    self.logger.error(f"Line graph generation failed: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run line graph generation: {e}")
            return False
    
    def _run_scatter_plots(self, schedule: ScheduleConfig) -> bool:
        """Run scatter plot generation"""
        try:
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, 'create_scatter_plots.py'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    self.logger.info("Scatter plot generation completed successfully")
                    return True
                else:
                    self.logger.error(f"Scatter plot generation failed: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run scatter plot generation: {e}")
            return False
    
    def _run_histograms(self, schedule: ScheduleConfig) -> bool:
        """Run histogram generation"""
        try:
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, 'generate_histograms.py'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    self.logger.info("Histogram generation completed successfully")
                    return True
                else:
                    self.logger.error(f"Histogram generation failed: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Failed to run histogram generation: {e}")
            return False
    
    def run_schedule(self, schedule_name: str) -> Dict[str, Any]:
        """Run a complete schedule"""
        self.logger.info(f"Starting scheduled pipeline run: {schedule_name}")
        start_time = datetime.now()
        
        # Get schedule configuration
        schedule = self.config_manager.get_schedule(schedule_name)
        if not schedule:
            error_msg = f"Schedule '{schedule_name}' not found"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': 0,
                'steps_completed': 0,
                'steps_total': 0
            }
        
        if not schedule.enabled:
            self.logger.info(f"Schedule '{schedule_name}' is disabled, skipping")
            return {
                'success': True,
                'message': 'Schedule disabled',
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': 0,
                'steps_completed': 0,
                'steps_total': 0
            }
        
        # Validate schedule
        errors = self.config_manager.validate_schedule(schedule)
        if errors:
            error_msg = f"Schedule validation failed: {'; '.join(errors)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': 0,
                'steps_completed': 0,
                'steps_total': len(schedule.processing_steps)
            }
        
        # Create output directory if it doesn't exist
        os.makedirs(schedule.output_directory, exist_ok=True)
        
        # Run processing steps
        steps_completed = 0
        steps_total = len(schedule.processing_steps)
        
        for step in schedule.processing_steps:
            retry_count = 0
            success = False
            
            while retry_count <= schedule.max_retries and not success:
                if retry_count > 0:
                    self.logger.info(f"Retrying step {step.value} (attempt {retry_count + 1})")
                
                success = self._run_processing_step(step, schedule)
                
                if not success:
                    retry_count += 1
                    if retry_count <= schedule.max_retries:
                        self.logger.warning(f"Step {step.value} failed, retrying...")
            
            if success:
                steps_completed += 1
            else:
                error_msg = f"Step {step.value} failed after {schedule.max_retries + 1} attempts"
                self.logger.error(error_msg)
                end_time = datetime.now()
                return {
                    'success': False,
                    'error': error_msg,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': (end_time - start_time).total_seconds(),
                    'steps_completed': steps_completed,
                    'steps_total': steps_total,
                    'failed_step': step.value
                }
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.logger.info(f"Pipeline run completed successfully in {duration.total_seconds():.1f} seconds")
        
        return {
            'success': True,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'steps_completed': steps_completed,
            'steps_total': steps_total
        }
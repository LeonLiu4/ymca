#!/usr/bin/env python3
"""
Scheduled Pipeline Runner
========================

This script is called by the system scheduler (cron or Windows Task Scheduler)
to run the data processing pipeline.

Usage:
    python run_scheduled_pipeline.py --schedule <schedule_name>
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scheduler import SchedulerConfigManager, PipelineRunner
from utils.logging_config import setup_logger


def main():
    """Main entry point for scheduled pipeline execution"""
    parser = argparse.ArgumentParser(description='Run scheduled data processing pipeline')
    parser.add_argument('--schedule', required=True, 
                       help='Name of the schedule to run')
    parser.add_argument('--config', default='scheduler_config.json',
                       help='Path to scheduler configuration file')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(__name__, level=getattr(logging, args.log_level))
    
    try:
        # Initialize configuration manager and pipeline runner
        config_manager = SchedulerConfigManager(args.config)
        runner = PipelineRunner(config_manager)
        
        # Run the specified schedule
        result = runner.run_schedule(args.schedule)
        
        if result['success']:
            logger.info(f"Pipeline completed successfully: {result}")
            sys.exit(0)
        else:
            logger.error(f"Pipeline failed: {result}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
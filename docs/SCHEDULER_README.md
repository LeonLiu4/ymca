# Automated Pipeline Scheduler

This scheduler system allows you to run the YMCA volunteer data processing pipeline automatically at specified times using system cron jobs (Unix/Linux) or Windows Task Scheduler.

## Features

- **Cross-platform**: Works on Unix/Linux (cron) and Windows (Task Scheduler)
- **Flexible scheduling**: Daily, weekly, or monthly execution
- **Configurable processing**: Choose which pipeline steps to run
- **Retry logic**: Automatically retry failed steps
- **Logging**: Comprehensive logging of all operations
- **Email notifications**: Optional email alerts (configuration required)

## Quick Start

### 1. Install Dependencies

Ensure you have the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Create Your First Schedule

Create a daily processing schedule that runs at 6:00 AM:
```bash
python schedule_manager.py create daily_processing --frequency daily --time 06:00 --install
```

### 3. List All Schedules

View all configured schedules:
```bash
python schedule_manager.py list
```

### 4. Install Schedules to System

Install all enabled schedules to your system scheduler:
```bash
python schedule_manager.py install
```

## Schedule Management Commands

### Create a Schedule

```bash
python schedule_manager.py create <name> --frequency <daily|weekly|monthly> --time <HH:MM> [options]
```

Options:
- `--steps`: Processing steps to include (extract, prepare, statistics, pie_charts, bar_charts, line_graphs, scatter_plots, histograms)
- `--input-dir`: Input directory path (default: data/raw)
- `--output-dir`: Output directory path (default: data/processed)
- `--email-notifications`: Enable email notifications
- `--notification-email`: Email address for notifications
- `--max-retries`: Maximum retry attempts (default: 3)
- `--timeout`: Timeout in minutes (default: 60)
- `--disabled`: Create schedule as disabled
- `--install`: Install to system scheduler immediately

Example:
```bash
python schedule_manager.py create weekly_full --frequency weekly --time 03:00 \
    --steps extract prepare statistics pie_charts bar_charts \
    --email-notifications --notification-email admin@example.com \
    --install
```

### List Schedules

```bash
python schedule_manager.py list
```

### Enable/Disable Schedules

```bash
python schedule_manager.py enable <schedule_name>
python schedule_manager.py disable <schedule_name>
```

### Install Schedules

Install specific schedule:
```bash
python schedule_manager.py install <schedule_name>
```

Install all enabled schedules:
```bash
python schedule_manager.py install
```

### Remove Schedules

Remove from system scheduler:
```bash
python schedule_manager.py remove <schedule_name>
```

Remove all schedules:
```bash
python schedule_manager.py remove
```

Remove from system and delete configuration:
```bash
python schedule_manager.py remove <schedule_name> --delete-config
```

### Check Status

```bash
python schedule_manager.py status
```

## Default Schedules

The system creates three default schedules:

1. **daily_processing** - Runs daily at 6:00 AM
   - Steps: extract, prepare, statistics
   
2. **weekly_full_processing** - Runs weekly on Sundays at 3:00 AM
   - Steps: All available processing steps
   
3. **monthly_report** - Runs monthly on the 1st at 2:00 AM
   - Steps: All available processing steps
   - Email notifications enabled (requires email configuration)

## Processing Steps

Available processing steps:

- **extract**: Extract volunteer data from source
- **prepare**: Prepare and clean data
- **statistics**: Generate project statistics
- **pie_charts**: Create pie charts from XLSX files
- **bar_charts**: Generate bar charts
- **line_graphs**: Create line graphs
- **scatter_plots**: Generate scatter plots
- **histograms**: Create histograms

## Platform-Specific Information

### Unix/Linux (Cron)

- Uses standard cron jobs via `crontab`
- Logs output to `/tmp/ymca_pipeline.log`
- Logs errors to `/tmp/ymca_pipeline_error.log`
- Requires `crontab` command to be available

### Windows (Task Scheduler)

- Uses Windows Task Scheduler via `schtasks`
- Creates tasks with prefix "YMCA_Pipeline_"
- Requires `schtasks` command to be available
- Tasks run with current user privileges

## Configuration File

The scheduler uses `scheduler_config.json` to store configurations. This file is automatically created with default schedules if it doesn't exist.

Example configuration:
```json
{
  "schedules": {
    "daily_processing": {
      "name": "daily_processing",
      "frequency": "daily",
      "time": "06:00",
      "enabled": true,
      "processing_steps": ["extract", "prepare", "statistics"],
      "input_directory": "data/raw",
      "output_directory": "data/processed",
      "email_notifications": false,
      "notification_email": null,
      "max_retries": 3,
      "timeout_minutes": 60
    }
  },
  "last_updated": "2025-01-01T12:00:00"
}
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure scripts are executable
   ```bash
   chmod +x schedule_manager.py run_scheduled_pipeline.py
   ```

2. **Cron not available**: Install cron package on your system
   ```bash
   # Ubuntu/Debian
   sudo apt-get install cron
   
   # CentOS/RHEL
   sudo yum install cronie
   ```

3. **Windows Task Scheduler access denied**: Run command prompt as Administrator

4. **Python path issues**: Ensure Python is in your system PATH

### Checking Logs

**Unix/Linux:**
```bash
# View pipeline output
tail -f /tmp/ymca_pipeline.log

# View errors
tail -f /tmp/ymca_pipeline_error.log
```

**Windows:**
Check Windows Event Viewer or Task Scheduler history for task execution details.

### Manual Testing

Test a schedule manually:
```bash
python run_scheduled_pipeline.py --schedule daily_processing
```

## Integration with Existing Pipeline

The scheduler integrates with existing pipeline components:

- `src/extractors/volunteer_history_extractor.py`
- `src/processors/data_preparation.py`
- `src/processors/project_statistics.py`
- Chart generation scripts: `create_pie_charts.py`, `generate_bar_charts.py`, etc.

## Email Notifications

To enable email notifications, you'll need to configure SMTP settings in your environment or modify the pipeline runner to include email functionality.

## Security Considerations

- Schedule tasks run with the privileges of the user who created them
- Ensure proper file permissions on data directories
- Consider using dedicated service accounts for production deployments
- Regularly review and audit scheduled tasks

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify system scheduler availability (`cron` or `schtasks`)
3. Test schedules manually using `run_scheduled_pipeline.py`
4. Ensure all dependencies are installed
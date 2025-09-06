# Scheduling Tools

Automated scheduling and pipeline management tools for the YMCA Volunteer Data Processing System.

## ⏰ **Available Tools:**

### **Schedule Manager**
- **File**: `schedule_manager.py`
- **Purpose**: Manage automated report generation and scheduling
- **Usage**: `python schedule_manager.py`

### **Pipeline Runner**
- **File**: `run_scheduled_pipeline.py`
- **Purpose**: Execute the full data processing pipeline on schedule
- **Usage**: `python run_scheduled_pipeline.py`

### **Scheduler Module**
- **Directory**: `scheduler/`
- **Purpose**: Core scheduling functionality

#### **Cron Scheduler**
- **File**: `scheduler/cron_scheduler.py`
- **Purpose**: Linux/Mac scheduling support using cron
- **Usage**: Configure cron jobs for automated execution

#### **Windows Scheduler**
- **File**: `scheduler/windows_scheduler.py`
- **Purpose**: Windows task scheduling support
- **Usage**: Configure Windows Task Scheduler

#### **Pipeline Runner**
- **File**: `scheduler/pipeline_runner.py`
- **Purpose**: Execute the complete data processing pipeline
- **Usage**: Called by scheduling systems

#### **Scheduler Configuration**
- **File**: `scheduler/scheduler_config.py`
- **Purpose**: Configuration management for scheduling
- **Usage**: Configure scheduling parameters

## 🚀 **Quick Start:**

### **Set Up Automated Scheduling:**
```bash
python schedule_manager.py
```

### **Run Scheduled Pipeline:**
```bash
python run_scheduled_pipeline.py
```

### **Configure Cron Job (Linux/Mac):**
```bash
# Add to crontab for daily execution at 6 AM
0 6 * * * /path/to/run_scheduled_pipeline.py
```

### **Configure Windows Task Scheduler:**
```bash
# Use Windows Task Scheduler to run run_scheduled_pipeline.py
```

## 📋 **Features:**

- **Cross-Platform Support**: Works on Linux, Mac, and Windows
- **Flexible Scheduling**: Daily, weekly, monthly, or custom schedules
- **Pipeline Automation**: Complete data processing pipeline execution
- **Configuration Management**: Centralized scheduling configuration
- **Error Handling**: Robust error handling and logging
- **Status Monitoring**: Track execution status and results

## 📚 **Documentation:**

- `docs/SCHEDULER_README.md` - Comprehensive scheduling documentation

## 🔧 **Configuration:**

The scheduler can be configured to run:
- **Daily**: Every day at a specified time
- **Weekly**: On specific days of the week
- **Monthly**: On specific dates each month
- **Custom**: Any custom schedule pattern

## 📊 **Pipeline Execution:**

The scheduled pipeline includes:
1. Data extraction from VolunteerMatters API
2. Data preparation and cleaning
3. Statistical analysis and reporting
4. Report generation and export
5. Summary report creation

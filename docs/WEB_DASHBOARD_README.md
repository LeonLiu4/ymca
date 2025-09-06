# YMCA Data Processing Web Dashboard

A Flask-based web interface for triggering data processing, monitoring job status, and downloading generated reports.

## Features

- **Dashboard**: Start different types of data processing jobs
- **Status Monitor**: Real-time job status tracking with progress bars
- **Report Downloads**: Browse and download all generated reports and charts
- **Responsive UI**: Modern web interface that works on desktop and mobile

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the web application:
```bash
python app.py
```

3. Open your browser and go to: http://localhost:5000

## Available Processing Types

- **Full Processing Pipeline**: Runs the complete data processing workflow
- **Generate Pie Charts**: Creates pie chart visualizations
- **Generate Line Graphs**: Creates line graph visualizations  
- **Generate Bar Charts**: Creates bar chart visualizations
- **Generate Scatter Plots**: Creates scatter plot visualizations

## Web Interface Pages

### Dashboard (/)
- Start new processing jobs
- View current job status
- Browse processed files
- Quick access to recent reports

### Status Monitor (/status)
- Real-time job monitoring
- Progress tracking with visual progress bars
- Job statistics and completion status
- Auto-refresh for running jobs

### Reports (/reports)
- Browse all generated reports
- Download charts (JSON, PNG, SVG)
- Download data files (XLSX, CSV, TXT)
- Organized by report type

## File Structure

```
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── base.html         # Base template with styling
│   ├── dashboard.html    # Main dashboard
│   ├── status.html       # Job status monitor
│   └── reports.html      # Reports browser
├── data/
│   ├── raw/              # Raw data files
│   ├── processed/        # Processed data outputs
│   └── processed/reports/ # Generated reports
├── charts/               # Chart outputs
└── final_charts/         # Final chart outputs
```

## API Endpoints

- `GET /`: Main dashboard
- `POST /process`: Start data processing job
- `GET /status/<job_id>`: Get job status (JSON API)
- `GET /status`: Status monitoring page
- `GET /reports`: Reports browser page
- `GET /download/<filename>`: Download file

## Development

The application runs in debug mode by default. For production deployment:

1. Set `debug=False` in app.py
2. Use a proper WSGI server (gunicorn, uWSGI, etc.)
3. Configure proper secret key
4. Set up proper logging

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: pandas, openpyxl, matplotlib, seaborn
- **File Handling**: Werkzeug for secure file operations
#!/usr/bin/env python3
"""
Flask Web Dashboard for Data Processing and Report Generation

A web interface that allows users to:
- Trigger data processing jobs
- View processing status
- Download generated reports
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logging_config import setup_logger

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

logger = setup_logger(__name__)

job_status = {}
job_counter = 0

@app.route('/')
def dashboard():
    """Main dashboard page"""
    processed_files = get_processed_files()
    reports = get_available_reports()
    return render_template('dashboard.html', 
                         processed_files=processed_files,
                         reports=reports,
                         jobs=job_status)

@app.route('/process', methods=['POST'])
def process_data():
    """Trigger data processing"""
    global job_counter
    job_counter += 1
    job_id = f"job_{job_counter}"
    
    processing_type = request.form.get('processing_type', 'full')
    
    job_status[job_id] = {
        'id': job_id,
        'status': 'queued',
        'type': processing_type,
        'started_at': datetime.now().isoformat(),
        'progress': 0,
        'message': 'Job queued for processing'
    }
    
    thread = threading.Thread(target=run_processing_job, args=(job_id, processing_type))
    thread.daemon = True
    thread.start()
    
    flash(f'Processing job {job_id} started', 'success')
    return redirect(url_for('dashboard'))

@app.route('/status/<job_id>')
def job_status_api(job_id):
    """Get job status via API"""
    if job_id in job_status:
        return jsonify(job_status[job_id])
    return jsonify({'error': 'Job not found'}), 404

@app.route('/status')
def status_page():
    """Status monitoring page"""
    return render_template('status.html', jobs=job_status)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated reports"""
    safe_filename = secure_filename(filename)
    
    possible_paths = [
        Path('data/processed') / safe_filename,
        Path('data/processed/reports') / safe_filename,
        Path('charts') / safe_filename,
        Path('final_charts') / safe_filename
    ]
    
    for file_path in possible_paths:
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
    
    flash(f'File {filename} not found', 'error')
    return redirect(url_for('dashboard'))

@app.route('/reports')
def reports_page():
    """Reports listing page"""
    reports = get_available_reports()
    return render_template('reports.html', reports=reports)

def run_processing_job(job_id, processing_type):
    """Run data processing job in background thread"""
    try:
        job_status[job_id]['status'] = 'running'
        job_status[job_id]['progress'] = 10
        job_status[job_id]['message'] = 'Starting data processing...'
        
        if processing_type == 'pie_charts':
            job_status[job_id]['progress'] = 30
            job_status[job_id]['message'] = 'Generating pie charts...'
            os.system('python create_pie_charts.py')
            
        elif processing_type == 'line_graphs':
            job_status[job_id]['progress'] = 30
            job_status[job_id]['message'] = 'Generating line graphs...'
            os.system('python generate_line_graphs.py')
            
        elif processing_type == 'bar_charts':
            job_status[job_id]['progress'] = 30
            job_status[job_id]['message'] = 'Generating bar charts...'
            os.system('python generate_bar_charts.py')
            
        elif processing_type == 'scatter_plots':
            job_status[job_id]['progress'] = 30
            job_status[job_id]['message'] = 'Generating scatter plots...'
            os.system('python create_scatter_plots.py')
            
        else:
            job_status[job_id]['progress'] = 30
            job_status[job_id]['message'] = 'Running full processing pipeline...'
            os.system('python main.py')
        
        job_status[job_id]['progress'] = 80
        job_status[job_id]['message'] = 'Finalizing reports...'
        time.sleep(2)
        
        job_status[job_id]['status'] = 'completed'
        job_status[job_id]['progress'] = 100
        job_status[job_id]['message'] = 'Processing completed successfully'
        job_status[job_id]['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        job_status[job_id]['status'] = 'failed'
        job_status[job_id]['message'] = f'Processing failed: {str(e)}'
        job_status[job_id]['completed_at'] = datetime.now().isoformat()

def get_processed_files():
    """Get list of processed files"""
    files = []
    processed_dir = Path('data/processed')
    if processed_dir.exists():
        for file_path in processed_dir.rglob('*'):
            if file_path.is_file():
                files.append({
                    'name': file_path.name,
                    'path': str(file_path.relative_to('data/processed')),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
    return files

def get_available_reports():
    """Get list of available reports"""
    reports = []
    
    report_dirs = ['charts', 'final_charts', 'data/processed/reports']
    
    for report_dir in report_dirs:
        dir_path = Path(report_dir)
        if dir_path.exists():
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    reports.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'type': file_path.suffix.lower(),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
    
    return sorted(reports, key=lambda x: x['modified'], reverse=True)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    logger.info("🌐 Starting Flask Web Dashboard")
    logger.info("Dashboard will be available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
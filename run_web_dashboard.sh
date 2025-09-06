#!/bin/bash

# YMCA Data Processing Web Dashboard Launcher
echo "🏊‍♂️ YMCA Data Processing Web Dashboard"
echo "======================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null
then
    echo "❌ Python is not installed. Please install Python 3.6+ to run the web dashboard."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "📦 Installing/updating dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "🚀 Starting web dashboard..."
echo "📍 Dashboard will be available at: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
$PYTHON_CMD app.py
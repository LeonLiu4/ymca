#!/bin/bash

echo "🏊‍♂️ XLSX Line Graph Generator Setup & Usage"
echo "=============================================="

# Check if pip/pip3 is available
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    echo "💡 You may need to run: sudo $PIP_CMD install -r requirements.txt"
    echo "💡 Or use a virtual environment:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "🚀 Running line graph generator..."

# Run the main script
python3 generate_line_graphs.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Line graph generation complete!"
    echo "📁 Check the data/visualizations/ directory for your graphs"
else
    echo "❌ Line graph generation failed"
    echo "💡 Try running the simple version:"
    echo "   python3 src/visualizers/simple_line_graph_generator.py"
fi
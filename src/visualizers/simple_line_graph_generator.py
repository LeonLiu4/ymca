#!/usr/bin/env python3
"""
Simple Line Graph Generator from XLSX files
Works with basic Python libraries and attempts to import visualization libraries
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import pandas as pd
    except ImportError:
        missing_deps.append('pandas')
        
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        missing_deps.append('matplotlib')
        
    try:
        import seaborn as sns
    except ImportError:
        missing_deps.append('seaborn')
    
    return missing_deps

def create_requirements_file():
    """Create a requirements.txt for the missing dependencies"""
    requirements_content = """pandas>=1.5.0
matplotlib>=3.6.0
seaborn>=0.12.0
openpyxl>=3.0.0
"""
    
    with open('line_graph_requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    return 'line_graph_requirements.txt'

def generate_sample_data():
    """Generate sample data for demonstration"""
    import random
    from datetime import date, timedelta
    
    # Generate sample volunteer data over 12 months
    start_date = date(2025, 1, 1)
    data = []
    
    for i in range(12):
        month_date = start_date + timedelta(days=i*30)
        volunteer_hours = random.randint(50, 200)
        num_volunteers = random.randint(10, 50)
        num_activities = random.randint(5, 15)
        
        data.append({
            'Date': month_date.strftime('%Y-%m-%d'),
            'Volunteer_Hours': volunteer_hours,
            'Number_of_Volunteers': num_volunteers,
            'Number_of_Activities': num_activities
        })
    
    return data

def save_sample_excel():
    """Save sample data as Excel file"""
    try:
        import pandas as pd
        from openpyxl import Workbook
        
        data = generate_sample_data()
        df = pd.DataFrame(data)
        
        # Create output directory
        os.makedirs('data/sample', exist_ok=True)
        
        # Save as Excel
        filename = 'data/sample/sample_volunteer_data.xlsx'
        df.to_excel(filename, index=False)
        
        print(f"✅ Created sample XLSX file: {filename}")
        return filename
        
    except ImportError as e:
        print(f"❌ Cannot create Excel file without pandas and openpyxl: {e}")
        return None

def create_line_graphs_with_matplotlib(excel_file):
    """Create line graphs using matplotlib"""
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        
        # Load data
        df = pd.read_excel(excel_file)
        print(f"📊 Loaded data with {len(df)} rows and columns: {list(df.columns)}")
        
        # Convert date column
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                df[col] = pd.to_datetime(df[col])
                date_col = col
                break
        
        if date_col is None:
            print("❌ No date column found")
            return []
        
        # Find numeric columns
        numeric_cols = []
        for col in df.columns:
            if col != date_col and df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                numeric_cols.append(col)
        
        if not numeric_cols:
            print("❌ No numeric columns found for plotting")
            return []
        
        print(f"📈 Creating line graphs for: {numeric_cols}")
        
        # Create output directory
        os.makedirs('data/visualizations', exist_ok=True)
        
        saved_files = []
        
        # Create individual graphs
        for col in numeric_cols:
            plt.figure(figsize=(12, 6))
            plt.plot(df[date_col], df[col], marker='o', linewidth=2)
            plt.title(f'{col.replace("_", " ").title()} Over Time')
            plt.xlabel('Date')
            plt.ylabel(col.replace("_", " ").title())
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filename = f'data/visualizations/{col.lower()}_line_graph.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            saved_files.append(filename)
            print(f"✅ Saved: {filename}")
        
        # Create combined graph
        if len(numeric_cols) > 1:
            plt.figure(figsize=(14, 8))
            for col in numeric_cols:
                plt.plot(df[date_col], df[col], marker='o', linewidth=2, label=col.replace('_', ' ').title())
            
            plt.title('All Metrics Over Time')
            plt.xlabel('Date') 
            plt.ylabel('Value')
            plt.legend()
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filename = 'data/visualizations/all_metrics_line_graph.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            saved_files.append(filename)
            print(f"✅ Saved: {filename}")
        
        return saved_files
        
    except Exception as e:
        print(f"❌ Error creating line graphs: {e}")
        return []

def main():
    """Main function"""
    print("🏊‍♂️ XLSX Line Graph Generator")
    print("=" * 40)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        print("⚠️ Missing dependencies:", ", ".join(missing_deps))
        requirements_file = create_requirements_file()
        print(f"📋 Created requirements file: {requirements_file}")
        print("💡 To install dependencies, run:")
        print(f"   python3 -m pip install -r {requirements_file}")
        print()
    
    # Look for existing XLSX files
    xlsx_files = []
    for directory in ['data/processed', 'data/raw']:
        if os.path.exists(directory):
            for file in Path(directory).glob('*.xlsx'):
                xlsx_files.append(str(file))
    
    if not xlsx_files:
        print("📁 No XLSX files found in data/processed or data/raw")
        if not missing_deps:
            print("🔧 Creating sample data for demonstration...")
            sample_file = save_sample_excel()
            if sample_file:
                xlsx_files = [sample_file]
    
    if not xlsx_files:
        print("❌ No XLSX files available for processing")
        return
    
    # Process files
    all_saved_files = []
    
    if not missing_deps:
        for xlsx_file in xlsx_files:
            print(f"\n📊 Processing: {xlsx_file}")
            saved_files = create_line_graphs_with_matplotlib(xlsx_file)
            all_saved_files.extend(saved_files)
    else:
        print("❌ Cannot process files without required dependencies")
        return
    
    # Summary
    if all_saved_files:
        print(f"\n🎉 Successfully generated {len(all_saved_files)} line graphs!")
        print("📁 Files saved to: data/visualizations/")
        print("\nGenerated files:")
        for file in all_saved_files:
            print(f"  • {os.path.basename(file)}")
    else:
        print("❌ No line graphs were generated")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Example Usage of Bar Chart Generator
===================================

This script demonstrates how to use the bar chart generator with sample data.
Run this after installing dependencies to see how the charts are generated.

Usage:
    python example_usage.py
"""

import sys
import os

def create_sample_data():
    """Create sample data to demonstrate chart generation"""
    try:
        import pandas as pd
        import numpy as np
        
        # Create sample volunteer data similar to the XLSX files
        np.random.seed(42)
        
        branches = ['Downtown YMCA', 'West Side YMCA', 'East Branch', 'North Center', 'South Branch']
        activities = ['Youth Programs', 'Senior Activities', 'Fitness Classes', 'Community Events', 'Sports Programs']
        
        # Generate sample data
        data = []
        for i in range(200):
            data.append({
                'volunteerDate': f"2025-0{np.random.randint(1, 9)}-{np.random.randint(10, 28):02d}",
                'branch': np.random.choice(branches),
                'assignment': np.random.choice(activities),
                'hoursContributed': np.random.randint(1, 8),
                'volunteerName': f"Volunteer_{i+1:03d}"
            })
        
        df = pd.DataFrame(data)
        
        # Save sample data
        os.makedirs('data/processed', exist_ok=True)
        sample_file = 'data/processed/Sample_Volunteer_Data.xlsx'
        df.to_excel(sample_file, index=False)
        print(f"✅ Created sample data: {sample_file}")
        print(f"📊 Sample contains {len(df)} volunteer records")
        print(f"🏢 Branches: {', '.join(branches)}")
        print(f"🎯 Activities: {', '.join(activities)}")
        
        return sample_file
        
    except ImportError as e:
        print(f"❌ Cannot create sample data: {e}")
        print("Please install pandas and openpyxl first")
        return None

def run_example():
    """Run the example chart generation"""
    print("🏊‍♂️ Bar Chart Generator Example")
    print("=" * 50)
    
    # Check if dependencies are available
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        # Create sample data
        sample_file = create_sample_data()
        if not sample_file:
            return False
        
        # Import and run chart generator
        from src.visualizations.bar_chart_generator import generate_bar_charts_from_xlsx
        
        print("\n📊 Generating bar charts from sample data...")
        charts = generate_bar_charts_from_xlsx(sample_file, output_dir="data/visualizations")
        
        if charts:
            print(f"\n✅ Generated {len(charts)} charts:")
            for chart in charts:
                print(f"  • {os.path.basename(chart)}")
            print(f"\n📁 Charts saved in: data/visualizations/")
            return True
        else:
            print("⚠️ No charts were generated")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install: pip install pandas matplotlib seaborn numpy openpyxl")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_example()
    if success:
        print("\n🎉 Example completed successfully!")
        print("You can now use generate_bar_charts.py with your own XLSX files")
    else:
        print("\n❌ Example failed. Please check dependencies and try again.")
    
    sys.exit(0 if success else 1)
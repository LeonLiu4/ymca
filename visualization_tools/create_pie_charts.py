#!/usr/bin/env python3
"""
Script to create pie charts from XLSX files.
This script reads data from Excel files and generates pie charts for visualization.
"""

import os
import sys
from pathlib import Path
import argparse

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install required packages: pip install pandas matplotlib openpyxl")
    sys.exit(1)


class PieChartGenerator:
    """Class to handle pie chart generation from XLSX files."""
    
    def __init__(self, output_dir="charts"):
        """Initialize the pie chart generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def read_xlsx_file(self, file_path):
        """Read an XLSX file and return a pandas DataFrame."""
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def identify_chart_columns(self, df):
        """Identify potential columns for pie chart creation."""
        suitable_columns = []
        
        for col in df.columns:
            # Check for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                # Skip if all values are the same or mostly null
                non_null_values = df[col].dropna()
                if len(non_null_values) > 1 and non_null_values.nunique() > 1:
                    suitable_columns.append(col)
            
            # Check for categorical columns with reasonable number of categories
            elif df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
                unique_count = df[col].nunique()
                if 2 <= unique_count <= 20:  # Reasonable range for pie chart
                    suitable_columns.append(col)
        
        return suitable_columns
    
    def create_pie_chart_from_categorical(self, df, column, title_prefix=""):
        """Create a pie chart from a categorical column."""
        value_counts = df[column].value_counts()
        
        # Filter out very small segments (less than 1% of total)
        total = value_counts.sum()
        threshold = total * 0.01
        filtered_counts = value_counts[value_counts >= threshold]
        
        if len(filtered_counts) < 2:
            return None
            
        plt.figure(figsize=(10, 8))
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(
            filtered_counts.values,
            labels=filtered_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 9}
        )
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title(f"{title_prefix}{column} Distribution", fontsize=14, fontweight='bold')
        plt.axis('equal')
        
        return plt.gcf()
    
    def create_pie_chart_from_numeric(self, df, column, group_by_column=None, title_prefix=""):
        """Create a pie chart from numeric data, optionally grouped by another column."""
        if group_by_column and group_by_column in df.columns:
            # Group by the specified column and sum the numeric values
            grouped_data = df.groupby(group_by_column)[column].sum()
            
            # Filter out very small values
            total = grouped_data.sum()
            if total <= 0:
                return None
                
            threshold = total * 0.01
            filtered_data = grouped_data[grouped_data >= threshold]
            
            if len(filtered_data) < 2:
                return None
            
            plt.figure(figsize=(10, 8))
            
            wedges, texts, autotexts = plt.pie(
                filtered_data.values,
                labels=filtered_data.index,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 9}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title(f"{title_prefix}{column} by {group_by_column}", fontsize=14, fontweight='bold')
            plt.axis('equal')
            
            return plt.gcf()
        
        return None
    
    def process_xlsx_file(self, file_path):
        """Process a single XLSX file and generate pie charts."""
        print(f"Processing: {file_path}")
        
        df = self.read_xlsx_file(file_path)
        if df is None or df.empty:
            print(f"Skipping {file_path}: No data found")
            return
        
        file_name = Path(file_path).stem
        print(f"Data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Identify suitable columns for charts
        suitable_columns = self.identify_chart_columns(df)
        print(f"Suitable columns for charts: {suitable_columns}")
        
        if not suitable_columns:
            print(f"No suitable columns found for pie charts in {file_path}")
            return
        
        charts_created = 0
        
        # Try to create charts for categorical columns
        for col in suitable_columns:
            if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
                fig = self.create_pie_chart_from_categorical(df, col, f"{file_name} - ")
                if fig:
                    output_path = self.output_dir / f"{file_name}_{col}_pie_chart.png"
                    fig.savefig(output_path, dpi=300, bbox_inches='tight')
                    plt.close(fig)
                    print(f"Created chart: {output_path}")
                    charts_created += 1
        
        # Try to create charts for numeric columns grouped by categorical columns
        numeric_cols = [col for col in suitable_columns if pd.api.types.is_numeric_dtype(df[col])]
        categorical_cols = [col for col in suitable_columns if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col])]
        
        for num_col in numeric_cols:
            for cat_col in categorical_cols:
                fig = self.create_pie_chart_from_numeric(df, num_col, cat_col, f"{file_name} - ")
                if fig:
                    output_path = self.output_dir / f"{file_name}_{num_col}_by_{cat_col}_pie_chart.png"
                    fig.savefig(output_path, dpi=300, bbox_inches='tight')
                    plt.close(fig)
                    print(f"Created chart: {output_path}")
                    charts_created += 1
        
        print(f"Created {charts_created} charts for {file_path}")
        print("-" * 50)
    
    def process_all_xlsx_files(self, directory):
        """Process all XLSX files in a directory."""
        xlsx_files = list(Path(directory).glob("**/*.xlsx"))
        
        if not xlsx_files:
            print(f"No XLSX files found in {directory}")
            return
        
        print(f"Found {len(xlsx_files)} XLSX files")
        
        for xlsx_file in xlsx_files:
            self.process_xlsx_file(xlsx_file)


def main():
    """Main function to run the pie chart generator."""
    parser = argparse.ArgumentParser(description="Generate pie charts from XLSX files")
    parser.add_argument(
        "--input-dir", 
        default="data", 
        help="Directory containing XLSX files (default: data)"
    )
    parser.add_argument(
        "--output-dir", 
        default="charts", 
        help="Output directory for generated charts (default: charts)"
    )
    parser.add_argument(
        "--file", 
        help="Process a specific XLSX file instead of a directory"
    )
    
    args = parser.parse_args()
    
    generator = PieChartGenerator(args.output_dir)
    
    if args.file:
        if os.path.exists(args.file):
            generator.process_xlsx_file(args.file)
        else:
            print(f"File not found: {args.file}")
    else:
        if os.path.exists(args.input_dir):
            generator.process_all_xlsx_files(args.input_dir)
        else:
            print(f"Directory not found: {args.input_dir}")


if __name__ == "__main__":
    main()
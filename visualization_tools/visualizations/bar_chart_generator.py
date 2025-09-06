import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from pathlib import Path
import numpy as np
import datetime as dt

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, find_latest_file

logger = setup_logger(__name__, 'bar_chart_generator.log')

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_xlsx_file(file_path):
    """Load data from XLSX file"""
    logger.info(f"📊 Loading data from: {file_path}")
    return load_excel_data(file_path)

def detect_numeric_columns(df):
    """Detect columns that can be used for bar chart values"""
    numeric_cols = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64'] or df[col].dtype == 'object':
            try:
                # Try to convert to numeric
                pd.to_numeric(df[col], errors='raise')
                numeric_cols.append(col)
            except (ValueError, TypeError):
                # Check if it's a column with numeric-like values
                if 'hour' in col.lower() or 'count' in col.lower() or 'total' in col.lower():
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        if not df[col].isna().all():
                            numeric_cols.append(col)
                    except:
                        continue
    
    logger.info(f"📈 Found numeric columns: {numeric_cols}")
    return numeric_cols

def detect_categorical_columns(df):
    """Detect columns that can be used for bar chart categories"""
    categorical_cols = []
    for col in df.columns:
        unique_count = df[col].nunique()
        total_count = len(df)
        
        # Consider as categorical if:
        # - Less than 20 unique values OR
        # - Less than 10% of total records are unique OR
        # - Column name suggests it's categorical
        if (unique_count < 20 or 
            unique_count / total_count < 0.1 or
            any(keyword in col.lower() for keyword in ['branch', 'location', 'assignment', 'category', 'type', 'group', 'department'])):
            categorical_cols.append(col)
    
    logger.info(f"🏷️ Found categorical columns: {categorical_cols}")
    return categorical_cols

def create_bar_chart(df, x_column, y_column, title=None, output_dir="data/visualizations"):
    """Create a bar chart from the data"""
    logger.info(f"📊 Creating bar chart: {x_column} vs {y_column}")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Aggregate data by x_column
    if df[y_column].dtype in ['int64', 'float64']:
        chart_data = df.groupby(x_column)[y_column].sum().sort_values(ascending=False)
    else:
        chart_data = df[x_column].value_counts().sort_values(ascending=False)
    
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    
    # Create bar chart
    bars = plt.bar(range(len(chart_data)), chart_data.values)
    
    # Customize the chart
    plt.xlabel(x_column.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    plt.ylabel(y_column.replace('_', ' ').title() if df[y_column].dtype in ['int64', 'float64'] else 'Count', 
               fontsize=12, fontweight='bold')
    
    if title is None:
        title = f"{y_column.replace('_', ' ').title()} by {x_column.replace('_', ' ').title()}"
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Set x-axis labels
    plt.xticks(range(len(chart_data)), chart_data.index, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, chart_data.values)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(chart_data.values)*0.01,
                f'{value:,.0f}' if value >= 1 else f'{value:.2f}', 
                ha='center', va='bottom', fontweight='bold')
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the chart
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in title).replace(' ', '_')
    filename = f"bar_chart_{safe_title}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info(f"✅ Bar chart saved: {filepath}")
    return filepath

def create_horizontal_bar_chart(df, x_column, y_column, title=None, output_dir="data/visualizations"):
    """Create a horizontal bar chart from the data"""
    logger.info(f"📊 Creating horizontal bar chart: {x_column} vs {y_column}")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Aggregate data by x_column
    if df[y_column].dtype in ['int64', 'float64']:
        chart_data = df.groupby(x_column)[y_column].sum().sort_values(ascending=True)
    else:
        chart_data = df[x_column].value_counts().sort_values(ascending=True)
    
    # Create figure and axis
    plt.figure(figsize=(12, max(8, len(chart_data) * 0.5)))
    
    # Create horizontal bar chart
    bars = plt.barh(range(len(chart_data)), chart_data.values)
    
    # Customize the chart
    plt.ylabel(x_column.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    plt.xlabel(y_column.replace('_', ' ').title() if df[y_column].dtype in ['int64', 'float64'] else 'Count', 
               fontsize=12, fontweight='bold')
    
    if title is None:
        title = f"{y_column.replace('_', ' ').title()} by {x_column.replace('_', ' ').title()} (Horizontal)"
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Set y-axis labels
    plt.yticks(range(len(chart_data)), chart_data.index)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, chart_data.values)):
        plt.text(bar.get_width() + max(chart_data.values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{value:,.0f}' if value >= 1 else f'{value:.2f}', 
                ha='left', va='center', fontweight='bold')
    
    # Add grid for better readability
    plt.grid(axis='x', alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in title).replace(' ', '_')
    filename = f"horizontal_bar_chart_{safe_title}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info(f"✅ Horizontal bar chart saved: {filepath}")
    return filepath

def create_grouped_bar_chart(df, x_column, y_column, group_column, title=None, output_dir="data/visualizations"):
    """Create a grouped bar chart from the data"""
    logger.info(f"📊 Creating grouped bar chart: {x_column} vs {y_column} grouped by {group_column}")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Prepare data for grouped bar chart
    if df[y_column].dtype in ['int64', 'float64']:
        pivot_data = df.pivot_table(values=y_column, index=x_column, columns=group_column, aggfunc='sum', fill_value=0)
    else:
        # Count occurrences
        pivot_data = df.groupby([x_column, group_column]).size().unstack(fill_value=0)
    
    # Create figure and axis
    plt.figure(figsize=(14, 8))
    
    # Create grouped bar chart
    pivot_data.plot(kind='bar', ax=plt.gca())
    
    # Customize the chart
    plt.xlabel(x_column.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    plt.ylabel(y_column.replace('_', ' ').title() if df[y_column].dtype in ['int64', 'float64'] else 'Count', 
               fontsize=12, fontweight='bold')
    
    if title is None:
        title = f"{y_column.replace('_', ' ').title()} by {x_column.replace('_', ' ').title()} (Grouped by {group_column.replace('_', ' ').title()})"
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Customize legend
    plt.legend(title=group_column.replace('_', ' ').title(), bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in title).replace(' ', '_')
    filename = f"grouped_bar_chart_{safe_title}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info(f"✅ Grouped bar chart saved: {filepath}")
    return filepath

def generate_bar_charts_from_xlsx(file_path, output_dir="data/visualizations", auto_detect=True):
    """Generate multiple bar charts from an XLSX file"""
    logger.info(f"🎯 Generating bar charts from: {file_path}")
    
    # Load data
    df = load_xlsx_file(file_path)
    if df is None:
        logger.error(f"❌ Could not load data from {file_path}")
        return []
    
    generated_charts = []
    
    if auto_detect:
        # Auto-detect columns for charts
        numeric_cols = detect_numeric_columns(df)
        categorical_cols = detect_categorical_columns(df)
        
        logger.info(f"🔍 Auto-detected columns - Numeric: {numeric_cols}, Categorical: {categorical_cols}")
        
        # Generate basic bar charts
        for cat_col in categorical_cols[:3]:  # Limit to first 3 categorical columns
            for num_col in numeric_cols[:2]:  # Limit to first 2 numeric columns
                try:
                    chart_path = create_bar_chart(df, cat_col, num_col, output_dir=output_dir)
                    generated_charts.append(chart_path)
                    
                    # Also create horizontal version if there are many categories
                    if df[cat_col].nunique() > 5:
                        h_chart_path = create_horizontal_bar_chart(df, cat_col, num_col, output_dir=output_dir)
                        generated_charts.append(h_chart_path)
                except Exception as e:
                    logger.warning(f"⚠️ Could not create chart for {cat_col} vs {num_col}: {e}")
        
        # Generate grouped bar charts if we have enough categorical columns
        if len(categorical_cols) >= 2:
            for i, cat_col1 in enumerate(categorical_cols[:2]):
                for j, cat_col2 in enumerate(categorical_cols[i+1:3], i+1):
                    for num_col in numeric_cols[:1]:  # Just first numeric column
                        try:
                            grouped_chart_path = create_grouped_bar_chart(df, cat_col1, num_col, cat_col2, output_dir=output_dir)
                            generated_charts.append(grouped_chart_path)
                        except Exception as e:
                            logger.warning(f"⚠️ Could not create grouped chart for {cat_col1} vs {num_col} grouped by {cat_col2}: {e}")
    
    logger.info(f"✅ Generated {len(generated_charts)} bar charts")
    return generated_charts

def process_all_xlsx_files(input_dir="data/processed", output_dir="data/visualizations"):
    """Process all XLSX files in the input directory and generate bar charts"""
    logger.info(f"🔄 Processing all XLSX files in: {input_dir}")
    
    # Find all XLSX files
    xlsx_files = []
    if os.path.exists(input_dir):
        for file in os.listdir(input_dir):
            if file.endswith('.xlsx') and not file.startswith('~'):
                xlsx_files.append(os.path.join(input_dir, file))
    
    if not xlsx_files:
        logger.warning(f"⚠️ No XLSX files found in {input_dir}")
        return []
    
    all_generated_charts = []
    for xlsx_file in xlsx_files:
        logger.info(f"\n📂 Processing: {os.path.basename(xlsx_file)}")
        charts = generate_bar_charts_from_xlsx(xlsx_file, output_dir)
        all_generated_charts.extend(charts)
    
    logger.info(f"\n🎉 Total charts generated: {len(all_generated_charts)}")
    return all_generated_charts

def main():
    """Main function to generate bar charts from XLSX files"""
    logger.info("📊 YMCA Data Visualization - Bar Chart Generator")
    logger.info("=" * 60)
    
    # Process all XLSX files in the processed data directory
    charts = process_all_xlsx_files()
    
    if charts:
        logger.info(f"\n✅ Successfully generated {len(charts)} bar charts:")
        for chart in charts:
            logger.info(f"  • {os.path.basename(chart)}")
        logger.info(f"\n📁 Charts saved in: data/visualizations/")
    else:
        logger.warning("⚠️ No charts were generated. Please check if XLSX files exist in data/processed/")

if __name__ == "__main__":
    main()
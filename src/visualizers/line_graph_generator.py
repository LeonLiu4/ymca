import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from datetime import datetime
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data

logger = setup_logger(__name__, 'line_graph_generator.log')

class LineGraphGenerator:
    """Generate line graphs from XLSX files"""
    
    def __init__(self, output_dir="data/visualizations"):
        self.output_dir = output_dir
        self.setup_output_directory()
        self.setup_plotting_style()
    
    def setup_output_directory(self):
        """Create output directory for visualizations"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory set to: {self.output_dir}")
    
    def setup_plotting_style(self):
        """Set up matplotlib and seaborn styling"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def detect_date_column(self, df):
        """Detect date column in DataFrame"""
        date_keywords = ['date', 'time', 'created', 'updated', 'volunteer']
        
        for col in df.columns:
            col_lower = col.lower()
            # Check if column name contains date keywords
            if any(keyword in col_lower for keyword in date_keywords):
                # Try to convert to datetime
                try:
                    pd.to_datetime(df[col])
                    logger.info(f"Found date column: {col}")
                    return col
                except:
                    continue
        
        # If no obvious date column, look for datetime types
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'datetime' in str(df[col].dtype):
                logger.info(f"Found datetime column: {col}")
                return col
        
        logger.warning("No date column detected")
        return None
    
    def detect_numeric_columns(self, df, exclude_cols=None):
        """Detect numeric columns suitable for line graphs"""
        if exclude_cols is None:
            exclude_cols = []
        
        numeric_cols = []
        for col in df.columns:
            if col in exclude_cols:
                continue
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                numeric_cols.append(col)
        
        logger.info(f"Found numeric columns: {numeric_cols}")
        return numeric_cols
    
    def aggregate_by_period(self, df, date_col, value_cols, period='M'):
        """Aggregate data by time period"""
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        
        # Group by period and sum numeric values
        df_agg = df_copy.groupby(pd.Grouper(key=date_col, freq=period))[value_cols].sum().reset_index()
        
        # Remove rows with all zeros
        df_agg = df_agg[df_agg[value_cols].sum(axis=1) > 0]
        
        logger.info(f"Aggregated data by {period} - {len(df_agg)} periods")
        return df_agg
    
    def create_line_graph(self, df, x_col, y_cols, title, filename, show_trend=True):
        """Create a line graph with multiple y-axis variables"""
        plt.figure(figsize=(14, 8))
        
        # Create main plot
        ax = plt.gca()
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(y_cols)))
        
        for i, col in enumerate(y_cols):
            plt.plot(df[x_col], df[col], marker='o', linewidth=2, 
                    label=col.replace('_', ' ').title(), color=colors[i])
            
            # Add trend line if requested
            if show_trend and len(df) > 2:
                x_numeric = range(len(df))
                coeffs = np.polyfit(x_numeric, df[col], 1)
                trend_line = np.poly1d(coeffs)
                plt.plot(df[x_col], trend_line(x_numeric), 
                        '--', alpha=0.7, color=colors[i])
        
        # Formatting
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(x_col.replace('_', ' ').title(), fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels if they're dates
        if 'date' in x_col.lower() or df[x_col].dtype == 'datetime64[ns]':
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save the plot
        filepath = os.path.join(self.output_dir, f"{filename}.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        logger.info(f"Line graph saved: {filepath}")
        
        plt.close()
        return filepath
    
    def create_multiple_line_graphs(self, df, date_col, numeric_cols, base_filename, period='M'):
        """Create multiple line graphs from a single dataset"""
        saved_files = []
        
        # Aggregate data by period
        df_agg = self.aggregate_by_period(df, date_col, numeric_cols, period)
        
        if len(df_agg) == 0:
            logger.warning("No data available after aggregation")
            return saved_files
        
        # Create comprehensive graph with all metrics
        if len(numeric_cols) > 1:
            title = f"All Metrics Over Time ({period} aggregation)"
            filename = f"{base_filename}_all_metrics"
            filepath = self.create_line_graph(df_agg, date_col, numeric_cols, 
                                            title, filename, show_trend=True)
            saved_files.append(filepath)
        
        # Create individual graphs for each metric
        for col in numeric_cols:
            title = f"{col.replace('_', ' ').title()} Over Time"
            filename = f"{base_filename}_{col.lower().replace(' ', '_')}"
            filepath = self.create_line_graph(df_agg, date_col, [col], 
                                            title, filename, show_trend=True)
            saved_files.append(filepath)
        
        return saved_files
    
    def process_xlsx_file(self, filepath, period='M'):
        """Process a single XLSX file and generate line graphs"""
        logger.info(f"Processing XLSX file: {filepath}")
        
        # Load data
        df = load_excel_data(filepath)
        if df is None or df.empty:
            logger.error(f"Could not load data from {filepath}")
            return []
        
        logger.info(f"Loaded data with shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Detect date column
        date_col = self.detect_date_column(df)
        if date_col is None:
            logger.error("No date column found - cannot create time series line graphs")
            return []
        
        # Detect numeric columns (excluding date column)
        numeric_cols = self.detect_numeric_columns(df, exclude_cols=[date_col])
        if not numeric_cols:
            logger.error("No numeric columns found for plotting")
            return []
        
        # Generate base filename from input file
        base_filename = Path(filepath).stem + "_line_graphs"
        
        # Create line graphs
        saved_files = self.create_multiple_line_graphs(df, date_col, numeric_cols, 
                                                      base_filename, period)
        
        logger.info(f"Generated {len(saved_files)} line graphs")
        return saved_files
    
    def process_directory(self, directory, pattern="*.xlsx", period='M'):
        """Process all XLSX files in a directory"""
        directory_path = Path(directory)
        xlsx_files = list(directory_path.glob(pattern))
        
        if not xlsx_files:
            logger.warning(f"No XLSX files found in {directory} with pattern {pattern}")
            return []
        
        logger.info(f"Found {len(xlsx_files)} XLSX files to process")
        
        all_saved_files = []
        for xlsx_file in xlsx_files:
            try:
                saved_files = self.process_xlsx_file(str(xlsx_file), period)
                all_saved_files.extend(saved_files)
            except Exception as e:
                logger.error(f"Error processing {xlsx_file}: {e}")
                continue
        
        return all_saved_files


def main():
    """Main execution function"""
    logger.info("Starting Line Graph Generator")
    logger.info("=" * 50)
    
    # Initialize generator
    generator = LineGraphGenerator()
    
    # Process files in data/processed directory
    processed_dir = "data/processed"
    if os.path.exists(processed_dir):
        logger.info(f"Processing files in {processed_dir}")
        saved_files = generator.process_directory(processed_dir, "*.xlsx", period='M')
    else:
        logger.warning(f"Directory {processed_dir} not found")
        saved_files = []
    
    # Also process files in data/raw directory
    raw_dir = "data/raw"
    if os.path.exists(raw_dir):
        logger.info(f"Processing files in {raw_dir}")
        raw_saved_files = generator.process_directory(raw_dir, "*.xlsx", period='M')
        saved_files.extend(raw_saved_files)
    else:
        logger.warning(f"Directory {raw_dir} not found")
    
    # Summary
    if saved_files:
        logger.info(f"\n✅ Successfully generated {len(saved_files)} line graphs:")
        for file in saved_files:
            logger.info(f"  • {file}")
        
        print(f"\n🎉 Generated {len(saved_files)} line graphs!")
        print(f"📁 Output directory: {generator.output_dir}")
        print("\nGenerated files:")
        for file in saved_files:
            print(f"  • {os.path.basename(file)}")
    else:
        logger.warning("No line graphs were generated")
        print("❌ No line graphs were generated. Check logs for details.")


if __name__ == "__main__":
    main()
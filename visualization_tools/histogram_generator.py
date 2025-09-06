#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, find_latest_file

logger = setup_logger(__name__, 'histogram_generator.log')

class HistogramGenerator:
    """Generate histograms from XLSX files"""
    
    def __init__(self, output_dir='data/processed/histograms'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
    def load_xlsx_file(self, file_path):
        """Load XLSX file and return DataFrame"""
        logger.info(f"Loading XLSX file: {file_path}")
        return load_excel_data(file_path)
    
    def identify_numeric_columns(self, df):
        """Identify numeric columns suitable for histograms"""
        numeric_columns = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        
        # Filter out ID columns or other non-meaningful numeric columns
        filtered_columns = []
        for col in numeric_columns:
            col_lower = col.lower()
            if not any(skip_word in col_lower for skip_word in ['id', 'index', 'key']):
                filtered_columns.append(col)
        
        logger.info(f"Found numeric columns suitable for histograms: {filtered_columns}")
        return filtered_columns
    
    def generate_histogram(self, df, column, file_name, bins=30):
        """Generate a histogram for a specific column"""
        plt.figure(figsize=(10, 6))
        
        # Remove any null values
        data = df[column].dropna()
        
        if len(data) == 0:
            logger.warning(f"No data found for column '{column}' in {file_name}")
            return None
            
        # Create histogram
        plt.hist(data, bins=bins, alpha=0.7, edgecolor='black', linewidth=0.5)
        plt.title(f'Histogram of {column}\n({file_name})', fontsize=14, fontweight='bold')
        plt.xlabel(column, fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add statistics text
        stats_text = f'Count: {len(data)}\nMean: {data.mean():.2f}\nStd: {data.std():.2f}'
        plt.text(0.7, 0.95, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # Save histogram
        safe_filename = f"{file_name.replace('.xlsx', '')}_{column.replace(' ', '_').replace('/', '_')}_histogram.png"
        output_path = self.output_dir / safe_filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Histogram saved: {output_path}")
        return output_path
    
    def generate_multi_column_histogram(self, df, columns, file_name):
        """Generate a multi-subplot histogram for multiple columns"""
        if len(columns) == 0:
            return None
            
        # Calculate subplot layout
        n_cols = min(3, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        elif n_rows == 1 or n_cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        for i, column in enumerate(columns):
            ax = axes[i] if len(columns) > 1 else axes[0]
            data = df[column].dropna()
            
            if len(data) > 0:
                ax.hist(data, bins=20, alpha=0.7, edgecolor='black', linewidth=0.5)
                ax.set_title(f'{column}', fontsize=12, fontweight='bold')
                ax.set_xlabel(column, fontsize=10)
                ax.set_ylabel('Frequency', fontsize=10)
                ax.grid(True, alpha=0.3)
                
                # Add basic stats
                stats_text = f'μ={data.mean():.1f}\nσ={data.std():.1f}'
                ax.text(0.7, 0.95, stats_text, transform=ax.transAxes, 
                       verticalalignment='top', fontsize=8,
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
        
        # Hide unused subplots
        for i in range(len(columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle(f'Histograms Overview - {file_name}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save multi-histogram
        safe_filename = f"{file_name.replace('.xlsx', '')}_multi_histogram.png"
        output_path = self.output_dir / safe_filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Multi-histogram saved: {output_path}")
        return output_path
    
    def process_xlsx_file(self, file_path):
        """Process a single XLSX file and generate histograms"""
        file_name = Path(file_path).name
        logger.info(f"\n📊 Processing {file_name}...")
        
        try:
            # Load the file
            df = self.load_xlsx_file(file_path)
            
            if df is None or df.empty:
                logger.warning(f"No data found in {file_name}")
                return []
            
            # Identify numeric columns
            numeric_columns = self.identify_numeric_columns(df)
            
            if not numeric_columns:
                logger.warning(f"No numeric columns found in {file_name}")
                return []
            
            generated_files = []
            
            # Generate individual histograms for each numeric column
            for column in numeric_columns:
                histogram_path = self.generate_histogram(df, column, file_name)
                if histogram_path:
                    generated_files.append(histogram_path)
            
            # Generate multi-column overview histogram
            if len(numeric_columns) > 1:
                multi_path = self.generate_multi_column_histogram(df, numeric_columns, file_name)
                if multi_path:
                    generated_files.append(multi_path)
            
            logger.info(f"✅ Generated {len(generated_files)} histogram(s) for {file_name}")
            return generated_files
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_name}: {str(e)}")
            return []
    
    def process_directory(self, directory_path):
        """Process all XLSX files in a directory"""
        directory = Path(directory_path)
        xlsx_files = list(directory.glob('**/*.xlsx'))
        
        if not xlsx_files:
            logger.warning(f"No XLSX files found in {directory_path}")
            return []
        
        logger.info(f"Found {len(xlsx_files)} XLSX files to process")
        
        all_generated_files = []
        for xlsx_file in xlsx_files:
            generated_files = self.process_xlsx_file(xlsx_file)
            all_generated_files.extend(generated_files)
        
        return all_generated_files


def main():
    """Main function to generate histograms from XLSX files"""
    logger.info("📊 YMCA Volunteer Data Histogram Generator")
    logger.info("=" * 50)
    
    generator = HistogramGenerator()
    
    # Process both raw and processed data directories
    data_dirs = ['data/raw', 'data/processed']
    all_generated = []
    
    for data_dir in data_dirs:
        if Path(data_dir).exists():
            logger.info(f"\n🔍 Processing directory: {data_dir}")
            generated_files = generator.process_directory(data_dir)
            all_generated.extend(generated_files)
        else:
            logger.info(f"Directory not found: {data_dir}")
    
    logger.info(f"\n✅ Histogram generation complete!")
    logger.info(f"Generated {len(all_generated)} histogram files")
    logger.info(f"Output directory: {generator.output_dir}")
    
    if all_generated:
        logger.info("\nGenerated files:")
        for file_path in all_generated:
            logger.info(f"  📈 {file_path}")


if __name__ == "__main__":
    main()
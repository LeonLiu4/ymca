#!/usr/bin/env python3
"""
Scatter Plot Generator for XLSX Files

This utility creates scatter plots from XLSX files with automatic column detection
and multiple visualization options.

Usage Examples:
    # Process all XLSX files in data directory
    python create_scatter_plots.py
    
    # Process a specific file
    python create_scatter_plots.py data/raw/myfile.xlsx
    
    # Create specific scatter plot
    python create_scatter_plots.py data/raw/myfile.xlsx column1 column2
    
    # List available columns in a file
    python create_scatter_plots.py data/raw/myfile.xlsx --list-columns
    
    # Programmatic usage
    from src.utils.scatter_plot_generator import ScatterPlotGenerator
    generator = ScatterPlotGenerator()
    generator.process_xlsx_file('myfile.xlsx')
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import logging
import numpy as np
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScatterPlotGenerator:
    """Generate scatter plots from XLSX data with various customization options"""
    
    def __init__(self, output_dir: str = "data/plots"):
        """Initialize the scatter plot generator
        
        Args:
            output_dir: Directory to save generated plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def load_excel_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load Excel file and return DataFrame
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            DataFrame if successful, None if error
        """
        try:
            df = pd.read_excel(file_path)
            logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
            logger.info(f"📊 Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"❌ Error loading file {file_path}: {e}")
            return None
    
    def detect_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """Detect columns that can be used for plotting
        
        Args:
            df: Input DataFrame
            
        Returns:
            List of numeric column names
        """
        numeric_cols = []
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                numeric_cols.append(col)
            elif df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    pd.to_numeric(df[col], errors='coerce')
                    # If more than 50% are numeric, consider it plottable
                    if df[col].notna().sum() / len(df) > 0.5:
                        numeric_cols.append(col)
                except:
                    continue
        
        logger.info(f"🔢 Found {len(numeric_cols)} numeric columns: {numeric_cols}")
        return numeric_cols
    
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, 
                          title: str = None, color_col: str = None,
                          size_col: str = None, alpha: float = 0.7) -> plt.Figure:
        """Create a scatter plot from DataFrame columns
        
        Args:
            df: Input DataFrame
            x_col: Column name for x-axis
            y_col: Column name for y-axis  
            title: Plot title (auto-generated if None)
            color_col: Column name for color coding points
            size_col: Column name for sizing points
            alpha: Transparency of points
            
        Returns:
            matplotlib Figure object
        """
        # Clean data
        plot_df = df[[x_col, y_col]].copy()
        if color_col and color_col in df.columns:
            plot_df[color_col] = df[color_col]
        if size_col and size_col in df.columns:
            plot_df[size_col] = df[size_col]
        
        # Remove rows with missing values
        plot_df = plot_df.dropna()
        
        if len(plot_df) == 0:
            logger.warning(f"⚠️ No valid data points for {x_col} vs {y_col}")
            return None
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Prepare scatter plot parameters
        scatter_kwargs = {
            'x': plot_df[x_col],
            'y': plot_df[y_col],
            'alpha': alpha
        }
        
        # Add color coding if specified
        if color_col and color_col in plot_df.columns:
            scatter_kwargs['c'] = plot_df[color_col]
            scatter_kwargs['cmap'] = 'viridis'
        
        # Add size variation if specified
        if size_col and size_col in plot_df.columns:
            # Normalize sizes to reasonable range
            sizes = plot_df[size_col]
            sizes = (sizes - sizes.min()) / (sizes.max() - sizes.min()) * 100 + 20
            scatter_kwargs['s'] = sizes
        else:
            scatter_kwargs['s'] = 50
        
        # Create scatter plot
        scatter = ax.scatter(**scatter_kwargs)
        
        # Add colorbar if using color coding
        if color_col and color_col in plot_df.columns:
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label(color_col)
        
        # Customize plot
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        
        if title is None:
            title = f'{y_col} vs {x_col}'
        ax.set_title(title)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add statistics as text
        correlation = plot_df[x_col].corr(plot_df[y_col])
        stats_text = f'n = {len(plot_df)}\nr = {correlation:.3f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        logger.info(f"✅ Created scatter plot: {title} (n={len(plot_df)}, r={correlation:.3f})")
        return fig
    
    def create_multiple_scatter_plots(self, df: pd.DataFrame, max_plots: int = 10) -> List[plt.Figure]:
        """Create multiple scatter plots from all numeric column combinations
        
        Args:
            df: Input DataFrame
            max_plots: Maximum number of plots to generate
            
        Returns:
            List of matplotlib Figure objects
        """
        numeric_cols = self.detect_numeric_columns(df)
        
        if len(numeric_cols) < 2:
            logger.warning("⚠️ Need at least 2 numeric columns for scatter plots")
            return []
        
        figures = []
        plot_count = 0
        
        # Generate all possible combinations
        for i, x_col in enumerate(numeric_cols):
            for j, y_col in enumerate(numeric_cols):
                if i >= j or plot_count >= max_plots:  # Avoid duplicates and limit plots
                    continue
                
                fig = self.create_scatter_plot(df, x_col, y_col)
                if fig:
                    figures.append(fig)
                    plot_count += 1
        
        logger.info(f"✅ Generated {len(figures)} scatter plots")
        return figures
    
    def save_plots(self, figures: List[plt.Figure], base_filename: str = "scatter_plot") -> List[str]:
        """Save matplotlib figures to files
        
        Args:
            figures: List of matplotlib Figure objects
            base_filename: Base name for saved files
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, fig in enumerate(figures):
            if len(figures) == 1:
                filename = f"{base_filename}_{timestamp}.png"
            else:
                filename = f"{base_filename}_{i+1}_{timestamp}.png"
            
            filepath = self.output_dir / filename
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            saved_files.append(str(filepath))
            logger.info(f"💾 Saved: {filepath}")
        
        return saved_files
    
    def process_xlsx_file(self, file_path: str, auto_detect: bool = True, 
                         x_col: str = None, y_col: str = None) -> List[str]:
        """Process an XLSX file and generate scatter plots
        
        Args:
            file_path: Path to XLSX file
            auto_detect: If True, create plots from all numeric column combinations
            x_col: Specific x-axis column (required if auto_detect=False)
            y_col: Specific y-axis column (required if auto_detect=False)
            
        Returns:
            List of saved plot file paths
        """
        logger.info(f"🔄 Processing XLSX file: {file_path}")
        
        # Load data
        df = self.load_excel_file(file_path)
        if df is None:
            return []
        
        # Generate base filename from input file
        base_name = Path(file_path).stem
        
        if auto_detect:
            # Generate multiple plots automatically
            figures = self.create_multiple_scatter_plots(df)
            if figures:
                return self.save_plots(figures, f"{base_name}_auto_scatter")
            else:
                return []
        else:
            # Create specific plot
            if not x_col or not y_col:
                logger.error("❌ x_col and y_col must be specified when auto_detect=False")
                return []
            
            fig = self.create_scatter_plot(df, x_col, y_col)
            if fig:
                return self.save_plots([fig], f"{base_name}_scatter_{x_col}_vs_{y_col}")
            else:
                return []


def main():
    """Main function to demonstrate scatter plot generation"""
    generator = ScatterPlotGenerator()
    
    # Find all XLSX files in data directory
    data_dir = Path("data")
    xlsx_files = []
    
    for pattern in ["**/*.xlsx", "**/*.xls"]:
        xlsx_files.extend(data_dir.glob(pattern))
    
    if not xlsx_files:
        logger.warning("⚠️ No XLSX files found in data directory")
        return
    
    logger.info(f"📁 Found {len(xlsx_files)} Excel files:")
    for file in xlsx_files:
        logger.info(f"  • {file}")
    
    # Process each file
    all_saved_plots = []
    for xlsx_file in xlsx_files:
        logger.info(f"\n{'='*60}")
        saved_plots = generator.process_xlsx_file(str(xlsx_file))
        all_saved_plots.extend(saved_plots)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 SUMMARY: Generated {len(all_saved_plots)} scatter plots")
    if all_saved_plots:
        logger.info("📊 Saved plots:")
        for plot_file in all_saved_plots:
            logger.info(f"  • {plot_file}")


if __name__ == "__main__":
    main()
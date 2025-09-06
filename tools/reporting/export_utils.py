#!/usr/bin/env python3
"""
Export Utilities for YMCA Volunteer Data Reports

This module provides utilities for exporting data in both Excel and CSV formats,
supporting the --format csv command-line flag across all report generators.
"""

import pandas as pd
import os
from pathlib import Path
import datetime as dt
from typing import Dict, List, Union, Any

from .logging_config import setup_logger

logger = setup_logger(__name__)


def export_data_sheets(data_sheets: Dict[str, pd.DataFrame], 
                      output_path: str, 
                      format_type: str = "excel") -> Union[str, List[str]]:
    """
    Export data sheets to either Excel (single file) or CSV (multiple files).
    
    Args:
        data_sheets: Dictionary mapping sheet names to DataFrames
        output_path: Base output path (without extension)
        format_type: "excel" or "csv"
    
    Returns:
        String (Excel) or List of strings (CSV) with created file paths
    """
    if format_type.lower() == "csv":
        return export_csv_sheets(data_sheets, output_path)
    else:
        return export_excel_sheets(data_sheets, output_path)


def export_excel_sheets(data_sheets: Dict[str, pd.DataFrame], output_path: str) -> str:
    """Export data sheets to Excel file with multiple sheets."""
    excel_path = f"{output_path}.xlsx"
    
    # Ensure output directory exists
    Path(excel_path).parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet_name, df in data_sheets.items():
            # Clean sheet name for Excel compatibility
            clean_sheet_name = clean_excel_sheet_name(sheet_name)
            df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
    
    logger.info(f"✅ Excel report saved: {excel_path}")
    return excel_path


def export_csv_sheets(data_sheets: Dict[str, pd.DataFrame], output_path: str) -> List[str]:
    """Export data sheets to separate CSV files."""
    created_files = []
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(output_path).stem
    
    for sheet_name, df in data_sheets.items():
        # Create CSV filename
        clean_name = clean_filename(sheet_name)
        csv_filename = f"{base_name}_{clean_name}.csv"
        csv_path = output_dir / csv_filename
        
        # Save CSV
        df.to_csv(csv_path, index=False)
        created_files.append(str(csv_path))
        logger.info(f"✅ CSV file saved: {csv_path}")
    
    logger.info(f"✅ CSV export complete: {len(created_files)} files created")
    return created_files


def clean_excel_sheet_name(sheet_name: str) -> str:
    """Clean sheet name to be compatible with Excel requirements."""
    # Excel sheet names cannot exceed 31 characters and cannot contain certain characters
    invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
    clean_name = str(sheet_name)
    
    for char in invalid_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Truncate to 31 characters if needed
    if len(clean_name) > 31:
        clean_name = clean_name[:31]
    
    return clean_name


def clean_filename(name: str) -> str:
    """Clean name to be safe for use in filenames."""
    invalid_chars = ['\\', '/', '?', '*', '<', '>', '|', ':', '"', ' ']
    clean_name = str(name)
    
    for char in invalid_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Remove multiple underscores
    while '__' in clean_name:
        clean_name = clean_name.replace('__', '_')
    
    return clean_name.strip('_')


def add_format_argument(parser):
    """Add --format argument to argparse parser."""
    parser.add_argument(
        '--format',
        choices=['excel', 'csv'],
        default='excel',
        help='Output format: excel (default) or csv for easier data sharing and backup'
    )
    return parser


def get_output_format_description(format_type: str) -> Dict[str, Any]:
    """Get description and file extensions for output format."""
    if format_type.lower() == "csv":
        return {
            'name': 'CSV',
            'description': 'Comma-separated values for data sharing and backup',
            'extension': '.csv',
            'multiple_files': True
        }
    else:
        return {
            'name': 'Excel',
            'description': 'Excel workbook with multiple sheets',
            'extension': '.xlsx',
            'multiple_files': False
        }


def create_summary_sheet(data: Dict[str, Any], sheet_name: str = "Summary") -> pd.DataFrame:
    """Create a standard summary sheet from key-value data."""
    if not data:
        return pd.DataFrame()
    
    # Convert data to DataFrame format
    metrics = []
    values = []
    
    for key, value in data.items():
        metrics.append(str(key).replace('_', ' ').title())
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        else:
            values.append(str(value))
    
    # Add generation timestamp
    metrics.append('Report Generated')
    values.append(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return pd.DataFrame({
        'Metric': metrics,
        'Value': values
    })


def export_report_with_format(report_data: Dict[str, pd.DataFrame],
                             base_filename: str,
                             output_dir: str = "data/processed",
                             format_type: str = "excel",
                             timestamp: bool = True) -> Union[str, List[str]]:
    """
    Unified function to export report data in the specified format.
    
    Args:
        report_data: Dictionary of sheet_name -> DataFrame
        base_filename: Base filename without extension
        output_dir: Output directory
        format_type: "excel" or "csv"
        timestamp: Whether to add timestamp to filename
    
    Returns:
        File path (Excel) or list of file paths (CSV)
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Add timestamp if requested
    if timestamp:
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{ts}"
    else:
        filename = base_filename
    
    output_path = os.path.join(output_dir, filename)
    
    # Export in requested format
    return export_data_sheets(report_data, output_path, format_type)


# Convenience functions for common use cases
def export_volunteer_statistics(hours_data: pd.DataFrame,
                               volunteers_data: pd.DataFrame,
                               projects_data: pd.DataFrame,
                               summary_data: Dict[str, Any],
                               output_dir: str = "data/processed",
                               format_type: str = "excel") -> Union[str, List[str]]:
    """Export volunteer statistics in the specified format."""
    
    report_data = {
        'Hours_Statistics': hours_data,
        'Volunteers_Statistics': volunteers_data,
        'Projects_Statistics': projects_data,
        'Summary': create_summary_sheet(summary_data)
    }
    
    return export_report_with_format(
        report_data,
        "Y_Volunteer_2025_Statistics",
        output_dir,
        format_type
    )
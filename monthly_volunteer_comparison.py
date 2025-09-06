#!/usr/bin/env python3
"""
Monthly Volunteer Data Comparison Script
Compares current month's volunteer data with previous month's data 
and highlights significant changes in volunteer hours and participation numbers.
"""

import os
import sys
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter
import re
from datetime import datetime


class VolunteerDataComparison:
    """Compares monthly volunteer data and highlights significant changes."""
    
    def __init__(self, output_dir="comparison_results"):
        """Initialize the comparison tool."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_data = None
        self.previous_data = None
        self.current_month = None
        self.previous_month = None
    
    def read_xlsx_basic(self, file_path):
        """Read XLSX file using zipfile and xml parsing."""
        try:
            with zipfile.ZipFile(file_path, 'r') as xlsx_file:
                # Read shared strings
                shared_strings = []
                try:
                    with xlsx_file.open('xl/sharedStrings.xml') as strings_file:
                        strings_xml = ET.parse(strings_file)
                        for si in strings_xml.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                            t_elem = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                            if t_elem is not None:
                                shared_strings.append(t_elem.text or '')
                            else:
                                shared_strings.append('')
                except KeyError:
                    pass
                
                # Read worksheet data
                try:
                    with xlsx_file.open('xl/worksheets/sheet1.xml') as sheet_file:
                        sheet_xml = ET.parse(sheet_file)
                        return self.parse_worksheet(sheet_xml, shared_strings)
                except KeyError:
                    print(f"Could not find sheet1.xml in {file_path}")
                    return None
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def parse_worksheet(self, sheet_xml, shared_strings):
        """Parse worksheet XML and extract data."""
        rows = {}
        
        for cell in sheet_xml.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            cell_ref = cell.get('r')
            cell_type = cell.get('t', '')
            
            if not cell_ref:
                continue
            
            match = re.match(r'([A-Z]+)(\d+)', cell_ref)
            if not match:
                continue
                
            col_letters, row_num = match.groups()
            row_num = int(row_num)
            col_num = self.column_letters_to_number(col_letters)
            
            value_elem = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            if value_elem is None:
                continue
                
            value = value_elem.text
            if not value:
                continue
            
            if cell_type == 's':  # Shared string
                try:
                    value = shared_strings[int(value)]
                except (IndexError, ValueError):
                    pass
            elif cell_type == 'n':  # Number
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
            
            if row_num not in rows:
                rows[row_num] = {}
            rows[row_num][col_num] = value
        
        if not rows:
            return None
            
        max_row = max(rows.keys())
        max_col = max(max(row.keys()) if row else [0] for row in rows.values())
        
        data = []
        for row_num in range(1, max_row + 1):
            row_data = []
            for col_num in range(1, max_col + 1):
                value = rows.get(row_num, {}).get(col_num, '')
                row_data.append(value)
            data.append(row_data)
        
        return data
    
    def column_letters_to_number(self, letters):
        """Convert column letters to number."""
        result = 0
        for char in letters:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result
    
    def extract_volunteer_metrics(self, data, month_name):
        """Extract key volunteer metrics from the data."""
        if not data or len(data) < 2:
            return None
            
        # Skip header row
        data_rows = data[1:]
        
        metrics = {
            'month': month_name,
            'total_records': len(data_rows),
            'total_hours': 0.0,
            'active_volunteers': 0,
            'participation_rate': 0.0,
            'hours_distribution': defaultdict(int),
            'volunteer_count_by_category': defaultdict(int)
        }
        
        for row in data_rows:
            if len(row) >= 4:
                # Column 3 (index 2) appears to be hours
                hours_val = row[2] if len(row) > 2 else 0
                try:
                    hours = float(hours_val) if hours_val else 0.0
                except (ValueError, TypeError):
                    hours = 0.0
                
                metrics['total_hours'] += hours
                
                # Column 4 (index 3) appears to be participation status (1/0)
                participation = row[3] if len(row) > 3 else 0
                try:
                    if str(participation) == '1':
                        metrics['active_volunteers'] += 1
                except (ValueError, TypeError):
                    pass
                
                # Categorize hours for distribution
                if hours == 0:
                    metrics['hours_distribution']['0_hours'] += 1
                elif hours < 5:
                    metrics['hours_distribution']['1-4_hours'] += 1
                elif hours < 15:
                    metrics['hours_distribution']['5-14_hours'] += 1
                elif hours < 30:
                    metrics['hours_distribution']['15-29_hours'] += 1
                else:
                    metrics['hours_distribution']['30+_hours'] += 1
        
        if metrics['total_records'] > 0:
            metrics['participation_rate'] = (metrics['active_volunteers'] / metrics['total_records']) * 100
        
        return metrics
    
    def calculate_percentage_change(self, current_val, previous_val):
        """Calculate percentage change between two values."""
        if previous_val == 0:
            return float('inf') if current_val > 0 else 0
        return ((current_val - previous_val) / previous_val) * 100
    
    def identify_significant_changes(self, current_metrics, previous_metrics, threshold=10.0):
        """Identify significant changes between months."""
        changes = {
            'significant_changes': [],
            'summary': {},
            'threshold_percentage': threshold
        }
        
        # Compare key metrics
        comparisons = [
            ('total_hours', 'Total Volunteer Hours'),
            ('active_volunteers', 'Active Volunteers'),
            ('participation_rate', 'Participation Rate'),
            ('total_records', 'Total Records')
        ]
        
        for metric_key, metric_name in comparisons:
            current_val = current_metrics.get(metric_key, 0)
            previous_val = previous_metrics.get(metric_key, 0)
            
            change_pct = self.calculate_percentage_change(current_val, previous_val)
            change_abs = current_val - previous_val
            
            changes['summary'][metric_key] = {
                'current': current_val,
                'previous': previous_val,
                'change_absolute': change_abs,
                'change_percentage': change_pct
            }
            
            # Flag significant changes
            if abs(change_pct) >= threshold and change_pct != float('inf'):
                direction = "increased" if change_pct > 0 else "decreased"
                changes['significant_changes'].append({
                    'metric': metric_name,
                    'current_value': current_val,
                    'previous_value': previous_val,
                    'change_percentage': change_pct,
                    'change_absolute': change_abs,
                    'direction': direction,
                    'significance': 'HIGH' if abs(change_pct) >= 25 else 'MEDIUM'
                })
        
        return changes
    
    def generate_comparison_report(self, current_metrics, previous_metrics, changes):
        """Generate a detailed comparison report."""
        report_lines = []
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_lines.append("="*80)
        report_lines.append("MONTHLY VOLUNTEER DATA COMPARISON REPORT")
        report_lines.append("="*80)
        report_lines.append(f"Generated: {timestamp}")
        report_lines.append(f"Current Month: {current_metrics['month']}")
        report_lines.append(f"Previous Month: {previous_metrics['month']}")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("📊 EXECUTIVE SUMMARY")
        report_lines.append("-"*50)
        
        significant_count = len(changes['significant_changes'])
        if significant_count == 0:
            report_lines.append("✅ No significant changes detected (changes < 10%)")
        else:
            report_lines.append(f"⚠️  {significant_count} significant change(s) detected")
        
        report_lines.append("")
        
        # Key Metrics Overview
        report_lines.append("📈 KEY METRICS COMPARISON")
        report_lines.append("-"*50)
        
        for metric_key, data in changes['summary'].items():
            current = data['current']
            previous = data['previous']
            change_pct = data['change_percentage']
            change_abs = data['change_absolute']
            
            metric_names = {
                'total_hours': 'Total Hours',
                'active_volunteers': 'Active Volunteers', 
                'participation_rate': 'Participation Rate (%)',
                'total_records': 'Total Records'
            }
            
            name = metric_names.get(metric_key, metric_key)
            
            if change_pct == float('inf'):
                change_str = "N/A (previous was 0)"
            else:
                sign = "+" if change_pct > 0 else ""
                change_str = f"{sign}{change_pct:.1f}%"
            
            if metric_key == 'participation_rate':
                report_lines.append(f"{name:20}: {current:.1f}% → {previous:.1f}% ({change_str})")
            elif metric_key == 'total_hours':
                report_lines.append(f"{name:20}: {current:.1f} → {previous:.1f} ({change_str})")
            else:
                report_lines.append(f"{name:20}: {current} → {previous} ({change_str})")
        
        report_lines.append("")
        
        # Significant Changes Detail
        if changes['significant_changes']:
            report_lines.append("🚨 SIGNIFICANT CHANGES (>10% threshold)")
            report_lines.append("-"*50)
            
            for change in changes['significant_changes']:
                significance_icon = "🔴" if change['significance'] == 'HIGH' else "🟡"
                direction_icon = "📈" if change['direction'] == 'increased' else "📉"
                
                report_lines.append(f"{significance_icon} {change['metric']}")
                report_lines.append(f"   {direction_icon} {change['direction'].title()} by {abs(change['change_percentage']):.1f}%")
                report_lines.append(f"   Previous: {change['previous_value']}")
                report_lines.append(f"   Current:  {change['current_value']}")
                report_lines.append("")
        
        # Hours Distribution Comparison
        report_lines.append("⏱️  VOLUNTEER HOURS DISTRIBUTION")
        report_lines.append("-"*50)
        
        hour_categories = ['0_hours', '1-4_hours', '5-14_hours', '15-29_hours', '30+_hours']
        
        for category in hour_categories:
            current_count = current_metrics['hours_distribution'].get(category, 0)
            previous_count = previous_metrics['hours_distribution'].get(category, 0)
            change_abs = current_count - previous_count
            
            category_name = category.replace('_', ' ').title()
            sign = "+" if change_abs > 0 else ""
            
            report_lines.append(f"{category_name:15}: {current_count:3} → {previous_count:3} ({sign}{change_abs})")
        
        report_lines.append("")
        report_lines.append("="*80)
        
        return "\n".join(report_lines)
    
    def load_and_compare_months(self, current_file, previous_file):
        """Load data from two files and perform comparison."""
        print(f"Loading current month data from: {current_file}")
        current_data = self.read_xlsx_basic(current_file)
        
        print(f"Loading previous month data from: {previous_file}")
        previous_data = self.read_xlsx_basic(previous_file)
        
        if not current_data or not previous_data:
            print("Error: Could not load one or both data files")
            return None
        
        # Extract month names from filenames
        current_month = Path(current_file).stem
        previous_month = Path(previous_file).stem
        
        print(f"Extracting metrics for current month: {current_month}")
        current_metrics = self.extract_volunteer_metrics(current_data, current_month)
        
        print(f"Extracting metrics for previous month: {previous_month}")
        previous_metrics = self.extract_volunteer_metrics(previous_data, previous_month)
        
        if not current_metrics or not previous_metrics:
            print("Error: Could not extract metrics from one or both files")
            return None
        
        print("Identifying significant changes...")
        changes = self.identify_significant_changes(current_metrics, previous_metrics)
        
        print("Generating comparison report...")
        report = self.generate_comparison_report(current_metrics, previous_metrics, changes)
        
        # Save report
        report_filename = f"volunteer_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = self.output_dir / report_filename
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"Report saved to: {report_path}")
        print("\n" + "="*80)
        print("COMPARISON REPORT PREVIEW")
        print("="*80)
        print(report[:1000] + "..." if len(report) > 1000 else report)
        
        return {
            'current_metrics': current_metrics,
            'previous_metrics': previous_metrics,
            'changes': changes,
            'report_path': report_path
        }


def main():
    """Main execution function."""
    if len(sys.argv) < 3:
        print("Usage: python monthly_volunteer_comparison.py <current_month_file.xlsx> <previous_month_file.xlsx>")
        print("Example: python monthly_volunteer_comparison.py data/August_2025.xlsx data/July_2025.xlsx")
        sys.exit(1)
    
    current_file = sys.argv[1]
    previous_file = sys.argv[2]
    
    # Check if files exist
    if not os.path.exists(current_file):
        print(f"Error: Current month file not found: {current_file}")
        sys.exit(1)
    
    if not os.path.exists(previous_file):
        print(f"Error: Previous month file not found: {previous_file}")
        sys.exit(1)
    
    # Create comparison tool and run analysis
    comparator = VolunteerDataComparison()
    result = comparator.load_and_compare_months(current_file, previous_file)
    
    if result:
        significant_changes = len(result['changes']['significant_changes'])
        print(f"\n✅ Analysis complete! Found {significant_changes} significant changes.")
        print(f"📄 Full report saved to: {result['report_path']}")
    else:
        print("❌ Analysis failed. Please check your input files.")
        sys.exit(1)


if __name__ == "__main__":
    main()
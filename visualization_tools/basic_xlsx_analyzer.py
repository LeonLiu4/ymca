#!/usr/bin/env python3
"""
Basic XLSX file analyzer and pie chart data generator.
Uses standard library only to read XLSX files and prepare data for visualization.
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import json
import re
from collections import Counter, defaultdict


class BasicXLSXAnalyzer:
    """Basic XLSX analyzer using only standard library."""
    
    def __init__(self, output_dir="charts"):
        """Initialize the analyzer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
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
                    # No shared strings file
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
        
        # Find all cells
        for cell in sheet_xml.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            cell_ref = cell.get('r')  # e.g., 'A1'
            cell_type = cell.get('t', '')
            
            if not cell_ref:
                continue
            
            # Extract row and column from reference
            match = re.match(r'([A-Z]+)(\d+)', cell_ref)
            if not match:
                continue
                
            col_letters, row_num = match.groups()
            row_num = int(row_num)
            col_num = self.column_letters_to_number(col_letters)
            
            # Get cell value
            value_elem = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            if value_elem is None:
                continue
                
            value = value_elem.text
            if not value:
                continue
            
            # Handle different cell types
            if cell_type == 's':  # Shared string
                try:
                    value = shared_strings[int(value)]
                except (IndexError, ValueError):
                    pass
            elif cell_type == 'n':  # Number
                try:
                    # Try to convert to int first, then float
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
            
            # Store in rows dict
            if row_num not in rows:
                rows[row_num] = {}
            rows[row_num][col_num] = value
        
        # Convert to list of lists format
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
        """Convert column letters (A, B, AA, etc.) to number."""
        result = 0
        for char in letters:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result
    
    def analyze_data(self, data):
        """Analyze the data to identify patterns suitable for pie charts."""
        if not data:
            return None
            
        # Assume first row is headers
        headers = data[0] if data else []
        data_rows = data[1:] if len(data) > 1 else []
        
        if not data_rows:
            return None
        
        # Clean headers
        headers = [str(h) if h else f"Column_{i+1}" for i, h in enumerate(headers)]
        
        analysis = {
            'headers': headers,
            'row_count': len(data_rows),
            'column_count': len(headers),
            'pie_chart_opportunities': [],
            'debug_info': []
        }
        
        print(f"  Analyzing {len(headers)} columns with {len(data_rows)} data rows")
        print(f"  Headers: {headers[:5]}..." if len(headers) > 5 else f"  Headers: {headers}")
        
        # Analyze each column
        for col_idx, header in enumerate(headers):
            column_values = []
            numeric_count = 0
            
            for row in data_rows:
                if col_idx < len(row):
                    value = row[col_idx]
                    if value is not None and str(value).strip():
                        column_values.append(value)
                        
                        # Check if numeric
                        try:
                            if isinstance(value, (int, float)):
                                numeric_count += 1
                            else:
                                float(str(value).replace(',', '').replace('$', '').strip())
                                numeric_count += 1
                        except:
                            pass
            
            if not column_values:
                continue
            
            # Determine column type and suitability
            is_numeric = numeric_count / len(column_values) > 0.9  # More strict numeric threshold
            unique_count = len(set(str(v) for v in column_values))
            sample_values = list(set(str(v) for v in column_values))[:5]
            
            # Special handling for potentially categorical numeric columns
            is_categorical_numeric = False
            if is_numeric and unique_count <= 50:
                # If numeric but few unique values, might be categorical (like status codes)
                avg_value_length = sum(len(str(v)) for v in sample_values) / len(sample_values)
                if avg_value_length <= 3 and unique_count <= 20:  # Short values, few categories
                    is_categorical_numeric = True
                    is_numeric = False  # Treat as categorical for pie chart purposes
            
            column_info = {
                'name': header,
                'index': col_idx,
                'total_values': len(column_values),
                'unique_values': unique_count,
                'is_numeric': is_numeric,
                'is_categorical_numeric': is_categorical_numeric,
                'sample_values': sample_values,
                'suitable_for_pie': False
            }
            
            debug_msg = f"    Col {col_idx} '{header}': {len(column_values)} values, {unique_count} unique, numeric: {is_numeric}, cat_num: {is_categorical_numeric}"
            analysis['debug_info'].append(debug_msg)
            print(debug_msg)
            print(f"      Sample values: {sample_values}")
            
            # More lenient check for pie chart suitability
            if (not is_numeric or is_categorical_numeric) and 2 <= unique_count <= 50:  # Include categorical numeric
                # Categorical column suitable for pie chart
                value_counts = Counter(str(v) for v in column_values)
                column_info['suitable_for_pie'] = True
                column_info['value_distribution'] = dict(value_counts.most_common(10))
                analysis['pie_chart_opportunities'].append(column_info)
                print(f"      -> Suitable for pie chart! Sample distribution: {dict(list(value_counts.most_common(3)))}")
            elif is_numeric:
                print(f"      -> Numeric column (samples: {sample_values[:3]})")
            else:
                print(f"      -> Too many unique values ({unique_count}) for pie chart")
            
            analysis[f'column_{col_idx}'] = column_info
        
        return analysis
    
    def generate_pie_chart_data(self, analysis, data):
        """Generate pie chart data from analysis."""
        if not analysis or not data:
            return []
        
        headers = analysis['headers']
        data_rows = data[1:] if len(data) > 1 else []
        pie_charts = []
        
        for opportunity in analysis['pie_chart_opportunities']:
            col_idx = opportunity['index']
            col_name = opportunity['name']
            
            # Extract column values
            values = []
            for row in data_rows:
                if col_idx < len(row) and row[col_idx]:
                    values.append(str(row[col_idx]))
            
            if not values:
                continue
            
            # Count values
            counter = Counter(values)
            
            # Filter small segments (less than 1% of total)
            total = sum(counter.values())
            min_count = max(1, total * 0.01)
            filtered_counter = {k: v for k, v in counter.items() if v >= min_count}
            
            if len(filtered_counter) >= 2:
                pie_chart_data = {
                    'title': f"{col_name} Distribution",
                    'data': dict(filtered_counter),
                    'total_count': total,
                    'percentages': {k: (v/total)*100 for k, v in filtered_counter.items()}
                }
                pie_charts.append(pie_chart_data)
        
        return pie_charts
    
    def create_text_visualization(self, pie_chart_data, file_stem):
        """Create text-based visualization of pie chart data."""
        output_lines = []
        
        for chart in pie_chart_data:
            output_lines.append(f"\n{chart['title']}")
            output_lines.append("=" * len(chart['title']))
            
            # Sort by count descending
            sorted_items = sorted(chart['data'].items(), key=lambda x: x[1], reverse=True)
            
            for label, count in sorted_items:
                percentage = chart['percentages'][label]
                bar_length = int(percentage / 2)  # Scale bar to max 50 chars
                bar = "█" * bar_length
                output_lines.append(f"{label:20} |{bar:<25} {count:4} ({percentage:5.1f}%)")
            
            output_lines.append("")
        
        # Save to file
        output_file = self.output_dir / f"{file_stem}_pie_chart_data.txt"
        with open(output_file, 'w') as f:
            f.write("\n".join(output_lines))
        
        return output_file
    
    def process_xlsx_file(self, file_path):
        """Process a single XLSX file."""
        print(f"Processing: {file_path}")
        
        data = self.read_xlsx_basic(file_path)
        if not data:
            print(f"Could not read data from {file_path}")
            return
        
        file_stem = Path(file_path).stem
        print(f"Successfully read {len(data)} rows")
        
        # Analyze the data
        analysis = self.analyze_data(data)
        if not analysis:
            print("Could not analyze data")
            return
        
        print(f"Found {len(analysis['pie_chart_opportunities'])} columns suitable for pie charts")
        
        # Generate pie chart data
        pie_charts = self.generate_pie_chart_data(analysis, data)
        
        if not pie_charts:
            print("No pie chart data generated")
            return
        
        # Create text visualization
        output_file = self.create_text_visualization(pie_charts, file_stem)
        print(f"Created text visualization: {output_file}")
        
        # Save analysis as JSON
        analysis_file = self.output_dir / f"{file_stem}_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Save pie chart data as JSON
        charts_file = self.output_dir / f"{file_stem}_pie_charts.json"
        with open(charts_file, 'w') as f:
            json.dump(pie_charts, f, indent=2)
        
        print(f"Analysis saved: {analysis_file}")
        print(f"Pie chart data saved: {charts_file}")
        print(f"Generated {len(pie_charts)} pie chart datasets")
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
    """Main function."""
    parser = argparse.ArgumentParser(description="Analyze XLSX files and generate pie chart data")
    parser.add_argument(
        "--input-dir", 
        default="data", 
        help="Directory containing XLSX files (default: data)"
    )
    parser.add_argument(
        "--output-dir", 
        default="charts", 
        help="Output directory for generated data (default: charts)"
    )
    parser.add_argument(
        "--file", 
        help="Process a specific XLSX file instead of a directory"
    )
    
    args = parser.parse_args()
    
    analyzer = BasicXLSXAnalyzer(args.output_dir)
    
    if args.file:
        if os.path.exists(args.file):
            analyzer.process_xlsx_file(args.file)
        else:
            print(f"File not found: {args.file}")
    else:
        if os.path.exists(args.input_dir):
            analyzer.process_all_xlsx_files(args.input_dir)
        else:
            print(f"Directory not found: {args.input_dir}")


if __name__ == "__main__":
    main()
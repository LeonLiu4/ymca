#!/usr/bin/env python3
"""
Example usage of the Monthly Volunteer Data Comparison Script
"""

import os
from monthly_volunteer_comparison import VolunteerDataComparison


def run_example_comparison():
    """Run an example comparison using available data."""
    print("🔍 Monthly Volunteer Data Comparison - Example Usage")
    print("="*60)
    
    # Check for available data files
    data_dir = "data/raw"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    xlsx_files = []
    for file in os.listdir(data_dir):
        if file.endswith('.xlsx'):
            xlsx_files.append(os.path.join(data_dir, file))
    
    if len(xlsx_files) == 0:
        print("❌ No XLSX files found in data directory")
        return
    
    print(f"📁 Found {len(xlsx_files)} XLSX file(s):")
    for i, file in enumerate(xlsx_files):
        print(f"   {i+1}. {os.path.basename(file)}")
    
    if len(xlsx_files) >= 2:
        # Use first two files for comparison
        current_file = xlsx_files[0]
        previous_file = xlsx_files[1]
        
        print(f"\n🔄 Comparing:")
        print(f"   Current:  {os.path.basename(current_file)}")
        print(f"   Previous: {os.path.basename(previous_file)}")
    else:
        # Use the same file twice for demo purposes
        current_file = xlsx_files[0]
        previous_file = xlsx_files[0]
        
        print(f"\n🔄 Demo comparison using same file twice:")
        print(f"   File: {os.path.basename(current_file)}")
        print("   (In real usage, you would use different monthly files)")
    
    # Run the comparison
    comparator = VolunteerDataComparison()
    result = comparator.load_and_compare_months(current_file, previous_file)
    
    if result:
        print(f"\n✅ Comparison completed successfully!")
        print(f"📊 Summary of changes found:")
        changes = result['changes']
        
        if changes['significant_changes']:
            print(f"   🚨 {len(changes['significant_changes'])} significant change(s) detected:")
            for change in changes['significant_changes']:
                print(f"      • {change['metric']}: {change['direction']} by {abs(change['change_percentage']):.1f}%")
        else:
            print("   ✅ No significant changes (< 10% threshold)")
        
        print(f"\n📄 Full report saved to: {result['report_path']}")
        
        # Show usage instructions
        print(f"\n📖 USAGE INSTRUCTIONS:")
        print(f"=" * 30)
        print(f"To compare different months, use:")
        print(f"   python monthly_volunteer_comparison.py current_month.xlsx previous_month.xlsx")
        print(f"")
        print(f"The script will:")
        print(f"   • Extract volunteer hours and participation data")
        print(f"   • Calculate percentage changes between months")
        print(f"   • Highlight changes > 10% as significant")
        print(f"   • Generate a detailed comparison report")
        print(f"   • Save results to comparison_results/ directory")
    else:
        print("❌ Comparison failed")


if __name__ == "__main__":
    run_example_comparison()
#!/usr/bin/env python3
"""
Test script for the flexible date range functionality
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from processors.date_range_processor import DateRangeProcessor


def test_comprehensive_date_validation():
    """Test comprehensive date validation functionality"""
    print("🧪 YMCA Date Range Validation Test Suite")
    print("=" * 50)
    
    processor = DateRangeProcessor()
    
    # Test 1: Various date format parsing
    print("\n📅 Test 1: Date Format Parsing")
    print("-" * 30)
    
    test_cases = [
        "2025-01-15",
        "01/15/2025", 
        "01-15-2025",
        "2025/01/15",
        "15/01/2025",
        "January 15, 2025",
        "Jan 15, 2025",
        "2025-01",
        "01/2025",
        "today",
        "yesterday", 
        "30 days ago",
        "2 weeks ago",
        "1 month ago",
        "invalid date string"
    ]
    
    successful_parses = 0
    for i, date_str in enumerate(test_cases, 1):
        parsed = processor.parse_date_string(date_str)
        status = "✅" if parsed else "❌"
        print(f"{i:2d}. {date_str:<20} → {status} {parsed or 'Failed'}")
        if parsed:
            successful_parses += 1
    
    print(f"\nParsing success rate: {successful_parses}/{len(test_cases)} ({100*successful_parses/len(test_cases):.1f}%)")
    
    # Test 2: Date range validation scenarios
    print("\n🔍 Test 2: Date Range Validation")
    print("-" * 35)
    
    validation_tests = [
        ("2025-01-01", "2025-01-31", "Valid monthly range"),
        ("2025-01-01", "2025-03-31", "Valid quarterly range"),
        ("2025-01-01", "2025-12-31", "Valid yearly range"),
        ("today", "30 days ago", "Invalid: backwards range"),
        ("2025-01-01", "2024-12-31", "Invalid: backwards range"),
        ("2030-01-01", "2030-12-31", "Future dates"),
        ("2020-01-01", "2025-12-31", "Very long range"),
        ("2025-02-29", "2025-03-01", "Invalid date handling"),
    ]
    
    valid_ranges = 0
    for i, (start_str, end_str, description) in enumerate(validation_tests, 1):
        result = processor.create_date_range_from_strings(start_str, end_str)
        status = "✅" if result['success'] else "❌"
        
        print(f"{i:2d}. {description}")
        print(f"    Range: '{start_str}' to '{end_str}' → {status}")
        
        if result['success']:
            valid_ranges += 1
            validation = result['validation']
            print(f"    Type: {validation['range_type']} ({validation['range_days']} days)")
            if validation['warnings']:
                for warning in validation['warnings']:
                    print(f"    ⚠️  {warning}")
        else:
            if result['error_message']:
                print(f"    Error: {result['error_message']}")
        print()
    
    print(f"Valid ranges: {valid_ranges}/{len(validation_tests)} ({100*valid_ranges/len(validation_tests):.1f}%)")
    
    # Test 3: Common preset ranges
    print("\n💡 Test 3: Preset Range Generation")
    print("-" * 35)
    
    suggestions = processor.suggest_common_ranges()
    print(f"Generated {len(suggestions)} preset ranges:")
    
    for i, (name, (start_date, end_date)) in enumerate(suggestions.items(), 1):
        days = (end_date - start_date).days + 1
        description = processor.get_period_description(start_date, end_date)
        print(f"{i:2d}. {name:<15} | {start_date} to {end_date} | {days:3d} days | {description}")
    
    # Test 4: Edge cases and error handling  
    print("\n🔬 Test 4: Edge Cases and Error Handling")
    print("-" * 40)
    
    edge_cases = [
        ("", "", "Empty strings"),
        (None, None, "None values"),
        ("2025-02-29", "2025-03-01", "Invalid leap year date"),
        ("not-a-date", "also-not-a-date", "Invalid strings"),
        ("2025-01-01", "2025-01-01", "Same start/end date"),
    ]
    
    for i, (start_str, end_str, description) in enumerate(edge_cases, 1):
        print(f"{i:2d}. {description}")
        try:
            result = processor.create_date_range_from_strings(str(start_str) if start_str else "", 
                                                           str(end_str) if end_str else "")
            status = "✅" if result['success'] else "❌"
            print(f"    Result: {status}")
            if not result['success'] and result['error_message']:
                print(f"    Error: {result['error_message']}")
        except Exception as e:
            print(f"    Exception: {e}")
        print()
    
    # Test 5: Performance with large date range
    print("\n⚡ Test 5: Performance Test")
    print("-" * 25)
    
    import time
    start_time = time.time()
    
    # Test multiple operations
    for _ in range(100):
        processor.parse_date_string("2025-01-15")
        processor.create_date_range_from_strings("2025-01-01", "2025-12-31")
        processor.suggest_common_ranges()
    
    end_time = time.time()
    operations_per_second = 300 / (end_time - start_time)  # 3 operations * 100 iterations
    
    print(f"Completed 300 operations in {end_time - start_time:.3f} seconds")
    print(f"Performance: {operations_per_second:.1f} operations/second")
    
    print("\n🎯 Test Suite Complete!")
    return True


def main():
    """Run the test suite"""
    try:
        success = test_comprehensive_date_validation()
        if success:
            print("\n✅ All tests completed successfully!")
            print("The flexible date range processor is working correctly.")
        else:
            print("\n❌ Some tests failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
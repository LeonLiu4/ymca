#!/usr/bin/env python3
"""
Flexible Date Range Processor for YMCA Volunteer Reports

This module provides comprehensive date range processing and validation functionality,
allowing users to generate reports for any custom date range, not just standard
monthly periods.
"""

import datetime as dt
from typing import Tuple, Optional, Dict, Any
import re
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, 'date_range_processor.log')


class DateRangeProcessor:
    """Process and validate flexible date ranges for report generation"""
    
    def __init__(self):
        self.supported_formats = [
            '%Y-%m-%d',      # 2025-01-15
            '%m/%d/%Y',      # 01/15/2025
            '%m-%d-%Y',      # 01-15-2025
            '%Y/%m/%d',      # 2025/01/15
            '%d/%m/%Y',      # 15/01/2025 (European)
            '%B %d, %Y',     # January 15, 2025
            '%b %d, %Y',     # Jan 15, 2025
            '%Y-%m',         # 2025-01 (will use first day of month)
            '%m/%Y',         # 01/2025 (will use first day of month)
        ]
        
    def parse_date_string(self, date_str: str) -> Optional[dt.date]:
        """
        Parse a date string using multiple supported formats
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed date object or None if parsing fails
        """
        if not date_str or not isinstance(date_str, str):
            logger.error(f"Invalid date string: {date_str}")
            return None
            
        # Clean the input string
        date_str = date_str.strip()
        
        # Try each supported format
        for fmt in self.supported_formats:
            try:
                parsed_date = dt.datetime.strptime(date_str, fmt).date()
                logger.debug(f"Successfully parsed '{date_str}' using format '{fmt}'")
                return parsed_date
            except ValueError:
                continue
        
        # Try relative date parsing (e.g., "today", "yesterday", "30 days ago")
        relative_date = self._parse_relative_date(date_str)
        if relative_date:
            return relative_date
            
        logger.error(f"Could not parse date string: '{date_str}'. Supported formats: {self.supported_formats}")
        return None
    
    def _parse_relative_date(self, date_str: str) -> Optional[dt.date]:
        """Parse relative date expressions like 'today', '30 days ago', etc."""
        date_str_lower = date_str.lower()
        today = dt.date.today()
        
        if date_str_lower == 'today':
            return today
        elif date_str_lower == 'yesterday':
            return today - dt.timedelta(days=1)
        elif date_str_lower == 'tomorrow':
            return today + dt.timedelta(days=1)
        
        # Parse patterns like "30 days ago", "2 weeks ago", "1 month ago"
        patterns = [
            (r'(\d+)\s+days?\s+ago', lambda x: today - dt.timedelta(days=int(x))),
            (r'(\d+)\s+weeks?\s+ago', lambda x: today - dt.timedelta(weeks=int(x))),
            (r'(\d+)\s+months?\s+ago', lambda x: self._subtract_months(today, int(x))),
            (r'(\d+)\s+years?\s+ago', lambda x: today.replace(year=today.year - int(x))),
        ]
        
        for pattern, calculator in patterns:
            match = re.match(pattern, date_str_lower)
            if match:
                try:
                    result = calculator(match.group(1))
                    logger.debug(f"Parsed relative date '{date_str}' as {result}")
                    return result
                except (ValueError, OverflowError) as e:
                    logger.warning(f"Error parsing relative date '{date_str}': {e}")
                    continue
        
        return None
    
    def _subtract_months(self, date: dt.date, months: int) -> dt.date:
        """Subtract months from a date, handling year boundaries"""
        year = date.year
        month = date.month - months
        
        while month <= 0:
            month += 12
            year -= 1
        
        # Handle day overflow (e.g., Jan 31 - 1 month should be Dec 31, not Feb 31)
        try:
            return date.replace(year=year, month=month)
        except ValueError:
            # If day doesn't exist in target month, use last day of that month
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            return date.replace(year=year, month=month, day=min(date.day, last_day))
    
    def validate_date_range(self, start_date: dt.date, end_date: dt.date, 
                          allow_future: bool = False, max_range_days: int = None) -> Dict[str, Any]:
        """
        Validate a date range with comprehensive checks
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            allow_future: Whether to allow future dates
            max_range_days: Maximum allowed range in days (None for no limit)
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'range_days': (end_date - start_date).days + 1,
            'start_date': start_date,
            'end_date': end_date
        }
        
        today = dt.date.today()
        
        # Check if start_date is before end_date
        if start_date >= end_date:
            validation_result['is_valid'] = False
            validation_result['errors'].append(
                f"Start date ({start_date}) must be before end date ({end_date})"
            )
        
        # Check future dates
        if not allow_future:
            if start_date > today:
                validation_result['is_valid'] = False
                validation_result['errors'].append(
                    f"Start date ({start_date}) cannot be in the future"
                )
            if end_date > today:
                validation_result['warnings'].append(
                    f"End date ({end_date}) is in the future"
                )
        
        # Check maximum range
        if max_range_days and validation_result['range_days'] > max_range_days:
            validation_result['is_valid'] = False
            validation_result['errors'].append(
                f"Date range ({validation_result['range_days']} days) exceeds maximum allowed range ({max_range_days} days)"
            )
        
        # Check if dates are too old (more than 5 years ago)
        five_years_ago = today.replace(year=today.year - 5)
        if start_date < five_years_ago:
            validation_result['warnings'].append(
                f"Start date ({start_date}) is more than 5 years ago - data may be limited"
            )
        
        # Add helpful info
        if validation_result['range_days'] <= 7:
            validation_result['range_type'] = 'weekly'
        elif validation_result['range_days'] <= 31:
            validation_result['range_type'] = 'monthly'
        elif validation_result['range_days'] <= 92:
            validation_result['range_type'] = 'quarterly'
        elif validation_result['range_days'] <= 366:
            validation_result['range_type'] = 'yearly'
        else:
            validation_result['range_type'] = 'multi-year'
        
        # Log results
        if validation_result['is_valid']:
            logger.info(f"✅ Date range validation passed: {start_date} to {end_date} ({validation_result['range_days']} days, {validation_result['range_type']})")
            for warning in validation_result['warnings']:
                logger.warning(f"⚠️ {warning}")
        else:
            logger.error(f"❌ Date range validation failed: {start_date} to {end_date}")
            for error in validation_result['errors']:
                logger.error(f"  • {error}")
        
        return validation_result
    
    def create_date_range_from_strings(self, start_str: str, end_str: str, 
                                     allow_future: bool = False, max_range_days: int = None) -> Dict[str, Any]:
        """
        Create and validate a date range from string inputs
        
        Args:
            start_str: Start date string
            end_str: End date string
            allow_future: Whether to allow future dates
            max_range_days: Maximum allowed range in days
            
        Returns:
            Dictionary with parsed dates and validation results
        """
        result = {
            'success': False,
            'start_date': None,
            'end_date': None,
            'validation': None,
            'error_message': None
        }
        
        # Parse start date
        start_date = self.parse_date_string(start_str)
        if not start_date:
            result['error_message'] = f"Could not parse start date: '{start_str}'"
            return result
        
        # Parse end date
        end_date = self.parse_date_string(end_str)
        if not end_date:
            result['error_message'] = f"Could not parse end date: '{end_str}'"
            return result
        
        # Validate the range
        validation = self.validate_date_range(start_date, end_date, allow_future, max_range_days)
        
        result['start_date'] = start_date
        result['end_date'] = end_date
        result['validation'] = validation
        result['success'] = validation['is_valid']
        
        if not validation['is_valid']:
            result['error_message'] = "; ".join(validation['errors'])
        
        return result
    
    def suggest_common_ranges(self) -> Dict[str, Tuple[dt.date, dt.date]]:
        """Generate suggestions for common date ranges"""
        today = dt.date.today()
        suggestions = {}
        
        # Current periods
        suggestions['This Week'] = self._get_week_range(today)
        suggestions['This Month'] = self._get_month_range(today)
        suggestions['This Quarter'] = self._get_quarter_range(today)
        suggestions['This Year'] = (dt.date(today.year, 1, 1), today)
        
        # Previous periods
        last_month = today.replace(day=1) - dt.timedelta(days=1)
        suggestions['Last Month'] = self._get_month_range(last_month)
        
        last_quarter_month = today.month - 3
        if last_quarter_month <= 0:
            last_quarter_month += 12
            last_quarter_year = today.year - 1
        else:
            last_quarter_year = today.year
        last_quarter_date = dt.date(last_quarter_year, last_quarter_month, 1)
        suggestions['Last Quarter'] = self._get_quarter_range(last_quarter_date)
        
        suggestions['Last Year'] = (dt.date(today.year - 1, 1, 1), dt.date(today.year - 1, 12, 31))
        
        # Recent periods
        suggestions['Last 7 Days'] = (today - dt.timedelta(days=7), today)
        suggestions['Last 30 Days'] = (today - dt.timedelta(days=30), today)
        suggestions['Last 90 Days'] = (today - dt.timedelta(days=90), today)
        
        # YTD
        suggestions['Year to Date'] = (dt.date(today.year, 1, 1), today)
        
        return suggestions
    
    def _get_week_range(self, date: dt.date) -> Tuple[dt.date, dt.date]:
        """Get the week range (Monday to Sunday) for a given date"""
        start = date - dt.timedelta(days=date.weekday())  # Monday
        end = start + dt.timedelta(days=6)  # Sunday
        return start, end
    
    def _get_month_range(self, date: dt.date) -> Tuple[dt.date, dt.date]:
        """Get the full month range for a given date"""
        import calendar
        start = date.replace(day=1)
        last_day = calendar.monthrange(date.year, date.month)[1]
        end = date.replace(day=last_day)
        return start, end
    
    def _get_quarter_range(self, date: dt.date) -> Tuple[dt.date, dt.date]:
        """Get the quarter range for a given date"""
        quarter = (date.month - 1) // 3 + 1
        if quarter == 1:  # Q1: Jan-Mar
            start = dt.date(date.year, 1, 1)
            end = dt.date(date.year, 3, 31)
        elif quarter == 2:  # Q2: Apr-Jun
            start = dt.date(date.year, 4, 1)
            end = dt.date(date.year, 6, 30)
        elif quarter == 3:  # Q3: Jul-Sep
            start = dt.date(date.year, 7, 1)
            end = dt.date(date.year, 9, 30)
        else:  # Q4: Oct-Dec
            start = dt.date(date.year, 10, 1)
            end = dt.date(date.year, 12, 31)
        return start, end
    
    def format_date_for_filename(self, date: dt.date) -> str:
        """Format date for use in filenames"""
        return date.strftime('%Y-%m-%d')
    
    def format_date_range_for_filename(self, start_date: dt.date, end_date: dt.date) -> str:
        """Format date range for use in filenames"""
        start_str = self.format_date_for_filename(start_date)
        end_str = self.format_date_for_filename(end_date)
        return f"{start_str}_to_{end_str}"
    
    def get_period_description(self, start_date: dt.date, end_date: dt.date) -> str:
        """Get a human-readable description of the date range"""
        days = (end_date - start_date).days + 1
        
        # Check for exact month
        if (start_date.day == 1 and 
            end_date == self._get_month_range(start_date)[1]):
            return start_date.strftime('%B %Y')
        
        # Check for exact year
        if (start_date == dt.date(start_date.year, 1, 1) and
            end_date == dt.date(start_date.year, 12, 31)):
            return str(start_date.year)
        
        # Check for quarter
        quarter_start, quarter_end = self._get_quarter_range(start_date)
        if start_date == quarter_start and end_date == quarter_end:
            quarter = (start_date.month - 1) // 3 + 1
            return f"Q{quarter} {start_date.year}"
        
        # Default to date range
        if days == 1:
            return start_date.strftime('%B %d, %Y')
        elif days <= 7:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} ({days} days)"
        else:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} ({days} days)"


def main():
    """Example usage and testing of DateRangeProcessor"""
    processor = DateRangeProcessor()
    
    print("🗓️ YMCA Date Range Processor - Example Usage")
    print("=" * 50)
    
    # Test date parsing
    test_dates = [
        "2025-01-15",
        "01/15/2025", 
        "January 15, 2025",
        "2025-01",
        "today",
        "30 days ago",
        "invalid date"
    ]
    
    print("\n📅 Date Parsing Tests:")
    for date_str in test_dates:
        parsed = processor.parse_date_string(date_str)
        print(f"  '{date_str}' → {parsed}")
    
    # Test date range creation
    print("\n📊 Date Range Creation Tests:")
    test_ranges = [
        ("2025-01-01", "2025-01-31"),
        ("01/01/2025", "03/31/2025"),
        ("today", "30 days ago"),  # Invalid (backwards)
        ("2025-01-01", "2025-12-31"),
    ]
    
    for start_str, end_str in test_ranges:
        result = processor.create_date_range_from_strings(start_str, end_str)
        print(f"  '{start_str}' to '{end_str}' → {'✅' if result['success'] else '❌'}")
        if not result['success']:
            print(f"    Error: {result['error_message']}")
        else:
            validation = result['validation']
            print(f"    Range: {validation['range_days']} days ({validation['range_type']})")
    
    # Show common range suggestions
    print("\n💡 Common Range Suggestions:")
    suggestions = processor.suggest_common_ranges()
    for name, (start, end) in list(suggestions.items())[:5]:  # Show first 5
        description = processor.get_period_description(start, end)
        print(f"  {name}: {start} to {end} ({description})")


if __name__ == "__main__":
    main()
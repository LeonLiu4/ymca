import pandas as pd
import numpy as np
import datetime as dt
from typing import Dict, List, Any, Optional, Tuple
import re
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import load_excel_data, save_excel_data

logger = setup_logger(__name__, 'data_quality_validation.log')


class DataQualityValidator:
    """Comprehensive data quality validation framework"""
    
    def __init__(self, required_fields: Optional[List[str]] = None):
        self.required_fields = required_fields or []
        self.validation_results = {}
        self.quality_issues = []
        
    def validate_data(self, df: pd.DataFrame, filename: str = "unknown") -> Dict[str, Any]:
        """Run comprehensive data quality validation"""
        logger.info(f"\n🔍 Starting Data Quality Validation for {filename}")
        logger.info("=" * 60)
        
        self.validation_results = {
            'filename': filename,
            'total_records': len(df),
            'validation_timestamp': dt.datetime.now().isoformat(),
            'issues': []
        }
        self.quality_issues = []
        
        # Run all validation checks
        self._check_duplicate_records(df)
        self._check_missing_required_fields(df)
        self._check_invalid_dates(df)
        self._check_data_consistency(df)
        self._check_data_completeness(df)
        self._check_numeric_ranges(df)
        self._check_text_quality(df)
        
        self.validation_results['total_issues'] = len(self.quality_issues)
        self.validation_results['issues'] = self.quality_issues
        
        # Calculate quality score
        self._calculate_quality_score(df)
        
        return self.validation_results
    
    def _check_duplicate_records(self, df: pd.DataFrame):
        """Check for duplicate records using multiple strategies"""
        logger.info("🔄 Checking for duplicate records...")
        
        # Complete duplicate rows
        complete_duplicates = df.duplicated(keep=False)
        complete_dup_count = complete_duplicates.sum()
        
        if complete_dup_count > 0:
            issue = {
                'type': 'duplicate_records',
                'severity': 'high',
                'count': complete_dup_count,
                'description': f"Found {complete_dup_count} complete duplicate rows",
                'affected_rows': df[complete_duplicates].index.tolist()
            }
            self.quality_issues.append(issue)
            logger.warning(f"  ⚠️ {complete_dup_count} complete duplicate rows found")
        
        # Check for potential duplicates based on key fields
        key_fields = self._identify_key_fields(df)
        if key_fields:
            key_duplicates = df.duplicated(subset=key_fields, keep=False)
            key_dup_count = key_duplicates.sum()
            
            if key_dup_count > 0:
                issue = {
                    'type': 'key_field_duplicates',
                    'severity': 'medium',
                    'count': key_dup_count,
                    'description': f"Found {key_dup_count} records with duplicate key fields: {key_fields}",
                    'affected_rows': df[key_duplicates].index.tolist(),
                    'key_fields': key_fields
                }
                self.quality_issues.append(issue)
                logger.warning(f"  ⚠️ {key_dup_count} key field duplicates found in fields: {key_fields}")
        
        if complete_dup_count == 0 and (not key_fields or key_dup_count == 0):
            logger.info("  ✅ No duplicate records found")
    
    def _check_missing_required_fields(self, df: pd.DataFrame):
        """Check for missing values in required fields"""
        logger.info("📋 Checking missing required fields...")
        
        # Auto-detect important fields if none specified
        fields_to_check = self.required_fields or self._identify_important_fields(df)
        
        for field in fields_to_check:
            if field in df.columns:
                missing_count = df[field].isna().sum()
                empty_strings = (df[field].astype(str).str.strip() == '').sum()
                total_missing = missing_count + empty_strings
                
                if total_missing > 0:
                    missing_percentage = (total_missing / len(df)) * 100
                    severity = 'high' if missing_percentage > 10 else 'medium' if missing_percentage > 5 else 'low'
                    
                    issue = {
                        'type': 'missing_required_field',
                        'severity': severity,
                        'field': field,
                        'count': total_missing,
                        'percentage': round(missing_percentage, 2),
                        'description': f"Field '{field}' has {total_missing} missing values ({missing_percentage:.1f}%)",
                        'affected_rows': df[df[field].isna() | (df[field].astype(str).str.strip() == '')].index.tolist()
                    }
                    self.quality_issues.append(issue)
                    logger.warning(f"  ⚠️ {field}: {total_missing} missing values ({missing_percentage:.1f}%)")
                else:
                    logger.info(f"  ✅ {field}: No missing values")
            else:
                issue = {
                    'type': 'missing_column',
                    'severity': 'high',
                    'field': field,
                    'description': f"Required field '{field}' not found in dataset",
                }
                self.quality_issues.append(issue)
                logger.error(f"  ❌ Required field '{field}' not found in dataset")
    
    def _check_invalid_dates(self, df: pd.DataFrame):
        """Check for invalid or suspicious dates"""
        logger.info("📅 Checking date field validity...")
        
        date_fields = self._identify_date_fields(df)
        
        for field in date_fields:
            if field in df.columns:
                # Convert to datetime and check for errors
                try:
                    date_series = pd.to_datetime(df[field], errors='coerce')
                    invalid_dates = date_series.isna() & df[field].notna()
                    invalid_count = invalid_dates.sum()
                    
                    if invalid_count > 0:
                        issue = {
                            'type': 'invalid_date_format',
                            'severity': 'medium',
                            'field': field,
                            'count': invalid_count,
                            'description': f"Field '{field}' has {invalid_count} invalid date formats",
                            'affected_rows': df[invalid_dates].index.tolist()
                        }
                        self.quality_issues.append(issue)
                        logger.warning(f"  ⚠️ {field}: {invalid_count} invalid date formats")
                    
                    # Check for future dates (if suspicious)
                    valid_dates = date_series[~date_series.isna()]
                    if len(valid_dates) > 0:
                        future_dates = valid_dates > dt.datetime.now()
                        future_count = future_dates.sum()
                        
                        if future_count > 0:
                            issue = {
                                'type': 'future_dates',
                                'severity': 'low',
                                'field': field,
                                'count': future_count,
                                'description': f"Field '{field}' has {future_count} future dates",
                                'affected_rows': df[future_dates].index.tolist()
                            }
                            self.quality_issues.append(issue)
                            logger.info(f"  ℹ️ {field}: {future_count} future dates found")
                        
                        # Check for very old dates (potential data entry errors)
                        old_threshold = dt.datetime.now() - dt.timedelta(days=365 * 10)  # 10 years ago
                        old_dates = valid_dates < old_threshold
                        old_count = old_dates.sum()
                        
                        if old_count > 0:
                            issue = {
                                'type': 'very_old_dates',
                                'severity': 'low',
                                'field': field,
                                'count': old_count,
                                'description': f"Field '{field}' has {old_count} dates older than 10 years",
                                'affected_rows': df[old_dates].index.tolist()
                            }
                            self.quality_issues.append(issue)
                            logger.info(f"  ℹ️ {field}: {old_count} very old dates (>10 years)")
                    
                    if invalid_count == 0 and future_count == 0 and old_count == 0:
                        logger.info(f"  ✅ {field}: All dates are valid")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error processing date field '{field}': {e}")
    
    def _check_data_consistency(self, df: pd.DataFrame):
        """Check for data consistency issues"""
        logger.info("🔧 Checking data consistency...")
        
        # Check for inconsistent text formatting
        text_fields = df.select_dtypes(include=['object']).columns
        
        for field in text_fields:
            if field in df.columns:
                # Check for mixed case issues
                non_null_values = df[field].dropna().astype(str)
                if len(non_null_values) > 0:
                    unique_values = non_null_values.unique()
                    normalized_values = [str(v).strip().lower() for v in unique_values]
                    
                    # Find values that might be the same but have different formatting
                    case_issues = 0
                    for norm_val in set(normalized_values):
                        matching_original = [v for v, n in zip(unique_values, normalized_values) if n == norm_val]
                        if len(matching_original) > 1:
                            case_issues += len(matching_original) - 1
                    
                    if case_issues > 0:
                        issue = {
                            'type': 'inconsistent_formatting',
                            'severity': 'low',
                            'field': field,
                            'count': case_issues,
                            'description': f"Field '{field}' has {case_issues} values with inconsistent formatting",
                            'examples': unique_values[:5].tolist()
                        }
                        self.quality_issues.append(issue)
                        logger.info(f"  ℹ️ {field}: {case_issues} formatting inconsistencies")
    
    def _check_data_completeness(self, df: pd.DataFrame):
        """Check overall data completeness"""
        logger.info("📊 Checking data completeness...")
        
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isna().sum().sum()
        completeness_rate = ((total_cells - missing_cells) / total_cells) * 100
        
        if completeness_rate < 95:
            severity = 'high' if completeness_rate < 80 else 'medium'
            issue = {
                'type': 'low_completeness',
                'severity': severity,
                'completeness_rate': round(completeness_rate, 2),
                'missing_cells': missing_cells,
                'total_cells': total_cells,
                'description': f"Dataset completeness is {completeness_rate:.1f}% ({missing_cells}/{total_cells} missing values)"
            }
            self.quality_issues.append(issue)
            logger.warning(f"  ⚠️ Dataset completeness: {completeness_rate:.1f}%")
        else:
            logger.info(f"  ✅ Dataset completeness: {completeness_rate:.1f}%")
    
    def _check_numeric_ranges(self, df: pd.DataFrame):
        """Check for suspicious numeric values"""
        logger.info("🔢 Checking numeric data ranges...")
        
        numeric_fields = df.select_dtypes(include=[np.number]).columns
        
        for field in numeric_fields:
            if field in df.columns:
                values = df[field].dropna()
                if len(values) > 0:
                    # Check for negative values where they shouldn't be
                    if 'hour' in field.lower() or 'age' in field.lower() or 'count' in field.lower():
                        negative_count = (values < 0).sum()
                        if negative_count > 0:
                            issue = {
                                'type': 'negative_values',
                                'severity': 'medium',
                                'field': field,
                                'count': negative_count,
                                'description': f"Field '{field}' has {negative_count} negative values",
                                'affected_rows': df[df[field] < 0].index.tolist()
                            }
                            self.quality_issues.append(issue)
                            logger.warning(f"  ⚠️ {field}: {negative_count} negative values")
                    
                    # Check for outliers using IQR method
                    Q1 = values.quantile(0.25)
                    Q3 = values.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = values[(values < lower_bound) | (values > upper_bound)]
                    outlier_count = len(outliers)
                    
                    if outlier_count > 0 and outlier_count < len(values) * 0.1:  # Only report if < 10% outliers
                        issue = {
                            'type': 'outliers',
                            'severity': 'low',
                            'field': field,
                            'count': outlier_count,
                            'description': f"Field '{field}' has {outlier_count} statistical outliers",
                            'range': [lower_bound, upper_bound],
                            'affected_rows': df[(df[field] < lower_bound) | (df[field] > upper_bound)].index.tolist()
                        }
                        self.quality_issues.append(issue)
                        logger.info(f"  ℹ️ {field}: {outlier_count} outliers detected")
    
    def _check_text_quality(self, df: pd.DataFrame):
        """Check text field quality"""
        logger.info("📝 Checking text data quality...")
        
        text_fields = df.select_dtypes(include=['object']).columns
        
        for field in text_fields:
            if field in df.columns:
                text_values = df[field].dropna().astype(str)
                if len(text_values) > 0:
                    # Check for very short values that might be data entry errors
                    very_short = text_values[text_values.str.len() < 2]
                    short_count = len(very_short)
                    
                    if short_count > 0:
                        issue = {
                            'type': 'very_short_text',
                            'severity': 'low',
                            'field': field,
                            'count': short_count,
                            'description': f"Field '{field}' has {short_count} very short text values (< 2 characters)",
                            'examples': very_short.head(5).tolist()
                        }
                        self.quality_issues.append(issue)
                        logger.info(f"  ℹ️ {field}: {short_count} very short text values")
                    
                    # Check for unusual characters or encoding issues
                    unusual_chars = text_values[text_values.str.contains(r'[^\x20-\x7E]', regex=True, na=False)]
                    unusual_count = len(unusual_chars)
                    
                    if unusual_count > 0:
                        issue = {
                            'type': 'unusual_characters',
                            'severity': 'low',
                            'field': field,
                            'count': unusual_count,
                            'description': f"Field '{field}' has {unusual_count} values with unusual characters",
                            'examples': unusual_chars.head(3).tolist()
                        }
                        self.quality_issues.append(issue)
                        logger.info(f"  ℹ️ {field}: {unusual_count} values with unusual characters")
    
    def _calculate_quality_score(self, df: pd.DataFrame):
        """Calculate an overall data quality score"""
        base_score = 100
        
        for issue in self.quality_issues:
            severity = issue.get('severity', 'low')
            if severity == 'high':
                base_score -= 10
            elif severity == 'medium':
                base_score -= 5
            else:  # low
                base_score -= 2
        
        # Ensure score doesn't go below 0
        quality_score = max(0, base_score)
        
        self.validation_results['quality_score'] = quality_score
        
        # Quality rating
        if quality_score >= 90:
            rating = "Excellent"
        elif quality_score >= 80:
            rating = "Good"
        elif quality_score >= 70:
            rating = "Fair"
        elif quality_score >= 50:
            rating = "Poor"
        else:
            rating = "Very Poor"
        
        self.validation_results['quality_rating'] = rating
        logger.info(f"📊 Data Quality Score: {quality_score}/100 ({rating})")
    
    def _identify_key_fields(self, df: pd.DataFrame) -> List[str]:
        """Identify potential key fields for duplicate detection"""
        key_fields = []
        
        # Common key field patterns
        potential_keys = ['id', 'email', 'phone', 'volunteerdate', 'assignment', 'name']
        
        for col in df.columns:
            col_lower = col.lower()
            for key_pattern in potential_keys:
                if key_pattern in col_lower:
                    key_fields.append(col)
                    break
        
        return key_fields[:3]  # Limit to top 3 key fields
    
    def _identify_important_fields(self, df: pd.DataFrame) -> List[str]:
        """Identify important fields that shouldn't be missing"""
        important_fields = []
        
        # Common important field patterns
        important_patterns = ['id', 'name', 'email', 'date', 'hour', 'assignment', 'location']
        
        for col in df.columns:
            col_lower = col.lower()
            for pattern in important_patterns:
                if pattern in col_lower:
                    important_fields.append(col)
                    break
        
        return important_fields
    
    def _identify_date_fields(self, df: pd.DataFrame) -> List[str]:
        """Identify date fields in the dataset"""
        date_fields = []
        
        # Date field patterns
        date_patterns = ['date', 'time', 'created', 'updated', 'modified']
        
        for col in df.columns:
            col_lower = col.lower()
            for pattern in date_patterns:
                if pattern in col_lower:
                    date_fields.append(col)
                    break
        
        return date_fields
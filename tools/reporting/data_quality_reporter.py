import pandas as pd
import json
import datetime as dt
from typing import Dict, List, Any
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger
from src.utils.file_utils import save_excel_data

logger = setup_logger(__name__, 'data_quality_reporter.log')


class DataQualityReporter:
    """Comprehensive data quality reporting system"""
    
    def __init__(self):
        self.report_data = {}
    
    def generate_comprehensive_report(self, validation_results: Dict[str, Any], 
                                    output_dir: str = "data/processed/reports") -> str:
        """Generate comprehensive data quality report"""
        logger.info("\n📋 Generating Comprehensive Data Quality Report...")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_quality_report_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            self._write_report_header(f, validation_results)
            self._write_executive_summary(f, validation_results)
            self._write_detailed_findings(f, validation_results)
            self._write_recommendations(f, validation_results)
            self._write_technical_details(f, validation_results)
        
        logger.info(f"✅ Comprehensive report saved: {filepath}")
        return filepath
    
    def generate_excel_report(self, validation_results: Dict[str, Any], df: pd.DataFrame,
                            output_dir: str = "data/processed/reports") -> str:
        """Generate Excel-based data quality report with multiple sheets"""
        logger.info("\n📊 Generating Excel Data Quality Report...")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_quality_analysis_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = self._create_summary_sheet(validation_results, df)
            summary_df.to_excel(writer, sheet_name='Quality Summary', index=False)
            
            # Issues sheet
            issues_df = self._create_issues_sheet(validation_results)
            issues_df.to_excel(writer, sheet_name='Quality Issues', index=False)
            
            # Data profile sheet
            profile_df = self._create_data_profile_sheet(df)
            profile_df.to_excel(writer, sheet_name='Data Profile', index=False)
            
            # Field analysis sheet
            field_analysis_df = self._create_field_analysis_sheet(df, validation_results)
            field_analysis_df.to_excel(writer, sheet_name='Field Analysis', index=False)
            
            # Recommendations sheet
            recommendations_df = self._create_recommendations_sheet(validation_results)
            recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        logger.info(f"✅ Excel report saved: {filepath}")
        return filepath
    
    def generate_json_report(self, validation_results: Dict[str, Any],
                           output_dir: str = "data/processed/reports") -> str:
        """Generate JSON format report for programmatic access"""
        logger.info("\n🔧 Generating JSON Data Quality Report...")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_quality_report_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Create JSON-serializable report
        json_report = {
            'metadata': {
                'report_generated': dt.datetime.now().isoformat(),
                'validator_version': '1.0.0',
                'filename': validation_results.get('filename', 'unknown')
            },
            'summary': {
                'total_records': validation_results.get('total_records', 0),
                'total_issues': validation_results.get('total_issues', 0),
                'quality_score': validation_results.get('quality_score', 0),
                'quality_rating': validation_results.get('quality_rating', 'Unknown')
            },
            'issues': validation_results.get('issues', []),
            'recommendations': self._generate_recommendations_list(validation_results)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON report saved: {filepath}")
        return filepath
    
    def _write_report_header(self, f, validation_results: Dict[str, Any]):
        """Write report header section"""
        f.write("🏊‍♂️ DATA QUALITY VALIDATION REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset: {validation_results.get('filename', 'Unknown')}\n")
        f.write(f"Total Records: {validation_results.get('total_records', 0):,}\n")
        f.write(f"Validation Timestamp: {validation_results.get('validation_timestamp', 'Unknown')}\n")
        f.write("\n")
    
    def _write_executive_summary(self, f, validation_results: Dict[str, Any]):
        """Write executive summary section"""
        f.write("📊 EXECUTIVE SUMMARY\n")
        f.write("-" * 40 + "\n")
        
        quality_score = validation_results.get('quality_score', 0)
        quality_rating = validation_results.get('quality_rating', 'Unknown')
        total_issues = validation_results.get('total_issues', 0)
        
        f.write(f"Overall Data Quality Score: {quality_score}/100 ({quality_rating})\n")
        f.write(f"Total Quality Issues Found: {total_issues}\n")
        
        # Categorize issues by severity
        issues = validation_results.get('issues', [])
        high_severity = len([i for i in issues if i.get('severity') == 'high'])
        medium_severity = len([i for i in issues if i.get('severity') == 'medium'])
        low_severity = len([i for i in issues if i.get('severity') == 'low'])
        
        f.write(f"\nIssue Breakdown by Severity:\n")
        f.write(f"  🔴 High Priority: {high_severity} issues\n")
        f.write(f"  🟡 Medium Priority: {medium_severity} issues\n")
        f.write(f"  🟢 Low Priority: {low_severity} issues\n")
        
        # Overall assessment
        f.write(f"\nOverall Assessment:\n")
        if quality_score >= 90:
            f.write("✅ Your data quality is excellent! Minor issues may exist but overall integrity is high.\n")
        elif quality_score >= 80:
            f.write("✅ Your data quality is good. Address medium/high priority issues for improvement.\n")
        elif quality_score >= 70:
            f.write("⚠️ Your data quality is fair. Several issues need attention to improve reliability.\n")
        elif quality_score >= 50:
            f.write("⚠️ Your data quality is poor. Significant issues may impact analysis accuracy.\n")
        else:
            f.write("❌ Your data quality is very poor. Immediate attention required before analysis.\n")
        
        f.write("\n")
    
    def _write_detailed_findings(self, f, validation_results: Dict[str, Any]):
        """Write detailed findings section"""
        f.write("🔍 DETAILED FINDINGS\n")
        f.write("-" * 40 + "\n")
        
        issues = validation_results.get('issues', [])
        
        if not issues:
            f.write("✅ No data quality issues detected!\n\n")
            return
        
        # Group issues by type
        issues_by_type = {}
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        for issue_type, type_issues in issues_by_type.items():
            f.write(f"\n{issue_type.replace('_', ' ').title()}:\n")
            
            for issue in type_issues:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get('severity', 'low'), "🟢")
                f.write(f"  {severity_icon} {issue.get('description', 'No description')}\n")
                
                if 'field' in issue:
                    f.write(f"     Field: {issue['field']}\n")
                if 'count' in issue:
                    f.write(f"     Affected Records: {issue['count']}\n")
                if 'percentage' in issue:
                    f.write(f"     Percentage: {issue['percentage']}%\n")
                if 'examples' in issue:
                    f.write(f"     Examples: {', '.join(map(str, issue['examples'][:3]))}\n")
                f.write("\n")
    
    def _write_recommendations(self, f, validation_results: Dict[str, Any]):
        """Write recommendations section"""
        f.write("💡 RECOMMENDATIONS\n")
        f.write("-" * 40 + "\n")
        
        recommendations = self._generate_recommendations_list(validation_results)
        
        if not recommendations:
            f.write("✅ No specific recommendations at this time.\n\n")
            return
        
        for i, rec in enumerate(recommendations, 1):
            f.write(f"{i}. {rec}\n")
        
        f.write("\nGeneral Best Practices:\n")
        f.write("• Implement data validation at the point of entry\n")
        f.write("• Establish regular data quality monitoring\n")
        f.write("• Create data governance policies and procedures\n")
        f.write("• Train staff on proper data entry techniques\n")
        f.write("• Implement automated data quality checks\n")
        f.write("\n")
    
    def _write_technical_details(self, f, validation_results: Dict[str, Any]):
        """Write technical details section"""
        f.write("🔧 TECHNICAL DETAILS\n")
        f.write("-" * 40 + "\n")
        f.write("Validation Checks Performed:\n")
        f.write("• Duplicate record detection (complete and key-field duplicates)\n")
        f.write("• Missing required field validation\n")
        f.write("• Date format and range validation\n")
        f.write("• Data consistency checks\n")
        f.write("• Data completeness analysis\n")
        f.write("• Numeric range and outlier detection\n")
        f.write("• Text quality assessment\n")
        f.write("\nReport generated by Data Quality Validation Tool v1.0.0\n")
    
    def _create_summary_sheet(self, validation_results: Dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
        """Create summary sheet for Excel report"""
        summary_data = [
            ['Dataset Name', validation_results.get('filename', 'Unknown')],
            ['Total Records', validation_results.get('total_records', 0)],
            ['Total Columns', len(df.columns)],
            ['Quality Score', f"{validation_results.get('quality_score', 0)}/100"],
            ['Quality Rating', validation_results.get('quality_rating', 'Unknown')],
            ['Total Issues Found', validation_results.get('total_issues', 0)],
            ['Report Generated', dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        return pd.DataFrame(summary_data, columns=['Metric', 'Value'])
    
    def _create_issues_sheet(self, validation_results: Dict[str, Any]) -> pd.DataFrame:
        """Create issues sheet for Excel report"""
        issues = validation_results.get('issues', [])
        
        if not issues:
            return pd.DataFrame({'Message': ['No data quality issues detected!']})
        
        issues_data = []
        for issue in issues:
            issues_data.append({
                'Type': issue.get('type', 'Unknown').replace('_', ' ').title(),
                'Severity': issue.get('severity', 'Unknown').title(),
                'Field': issue.get('field', 'N/A'),
                'Count': issue.get('count', 'N/A'),
                'Percentage': f"{issue.get('percentage', 'N/A')}%" if 'percentage' in issue else 'N/A',
                'Description': issue.get('description', 'No description')
            })
        
        return pd.DataFrame(issues_data)
    
    def _create_data_profile_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create data profile sheet for Excel report"""
        profile_data = []
        
        for col in df.columns:
            profile_data.append({
                'Column Name': col,
                'Data Type': str(df[col].dtype),
                'Non-Null Count': df[col].count(),
                'Null Count': df[col].isnull().sum(),
                'Unique Values': df[col].nunique(),
                'Most Frequent Value': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'N/A'
            })
        
        return pd.DataFrame(profile_data)
    
    def _create_field_analysis_sheet(self, df: pd.DataFrame, validation_results: Dict[str, Any]) -> pd.DataFrame:
        """Create detailed field analysis sheet"""
        field_data = []
        issues = validation_results.get('issues', [])
        
        for col in df.columns:
            # Get issues for this field
            field_issues = [i for i in issues if i.get('field') == col]
            issue_types = ', '.join([i.get('type', 'Unknown') for i in field_issues]) if field_issues else 'None'
            
            # Calculate completeness
            completeness = ((df[col].count() / len(df)) * 100) if len(df) > 0 else 0
            
            field_data.append({
                'Field Name': col,
                'Data Type': str(df[col].dtype),
                'Completeness %': round(completeness, 2),
                'Unique Values': df[col].nunique(),
                'Issues Found': len(field_issues),
                'Issue Types': issue_types,
                'Quality Status': 'Good' if len(field_issues) == 0 else 'Needs Attention'
            })
        
        return pd.DataFrame(field_data)
    
    def _create_recommendations_sheet(self, validation_results: Dict[str, Any]) -> pd.DataFrame:
        """Create recommendations sheet"""
        recommendations = self._generate_recommendations_list(validation_results)
        
        if not recommendations:
            return pd.DataFrame({'Recommendation': ['No specific recommendations at this time.']})
        
        rec_data = []
        for i, rec in enumerate(recommendations, 1):
            rec_data.append({
                'Priority': i,
                'Recommendation': rec,
                'Impact': 'High' if i <= 3 else 'Medium' if i <= 6 else 'Low'
            })
        
        return pd.DataFrame(rec_data)
    
    def _generate_recommendations_list(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on issues found"""
        recommendations = []
        issues = validation_results.get('issues', [])
        
        # High priority recommendations
        high_issues = [i for i in issues if i.get('severity') == 'high']
        if high_issues:
            recommendations.append("Address all high-priority data quality issues immediately")
        
        # Specific recommendations based on issue types
        issue_types = set([i.get('type', 'unknown') for i in issues])
        
        if 'duplicate_records' in issue_types:
            recommendations.append("Implement data deduplication processes before analysis")
        
        if 'missing_required_field' in issue_types:
            recommendations.append("Establish data entry validation to prevent missing required fields")
        
        if 'invalid_date_format' in issue_types:
            recommendations.append("Standardize date formats and implement date validation")
        
        if 'inconsistent_formatting' in issue_types:
            recommendations.append("Create data formatting standards and validation rules")
        
        if 'low_completeness' in issue_types:
            recommendations.append("Improve data collection processes to increase completeness")
        
        if 'negative_values' in issue_types:
            recommendations.append("Add validation checks to prevent negative values in inappropriate fields")
        
        if 'outliers' in issue_types:
            recommendations.append("Review statistical outliers to identify potential data entry errors")
        
        # General recommendations based on quality score
        quality_score = validation_results.get('quality_score', 100)
        if quality_score < 80:
            recommendations.append("Implement comprehensive data quality monitoring")
            recommendations.append("Train data entry personnel on quality best practices")
        
        return recommendations
#!/usr/bin/env python3

import os
import sys
import json
import sqlite3
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def analyze_l_line_mapping_issues():
    """Analyze the current L Line mapping issues"""
    
    print("=== ANALYZING L LINE MAPPING ISSUES ===")
    
    # Check current database state
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        
        # Get all supervisor forms
        c.execute("SELECT id, employee_name, pass_number, title, job_number, overtime_hours, raw_extracted_data FROM exception_forms WHERE form_type='supervisor' ORDER BY id DESC")
        forms = c.fetchall()
        
        print(f"Total supervisor forms in database: {len(forms)}")
        
        # Analyze the mapping issues
        for form in forms:
            form_id, employee_name, pass_number, title, job_number, overtime_hours, raw_data = form
            
            print(f"\n--- Form ID {form_id} ---")
            print(f"  Employee: {employee_name}")
            print(f"  Pass: {pass_number}")
            print(f"  Title: {title}")
            print(f"  Job: {job_number}")
            print(f"  Overtime: {overtime_hours}")
            
            # Parse raw data to see what Gemini actually returned
            try:
                raw_json = json.loads(raw_data)
                print(f"  Raw Gemini fields:")
                for key, value in raw_json.items():
                    if key in ['employee_name', 'name', 'pass_number', 'assignment', 'reg', 'job_number', 'job', 'title', 'overtime_hours', 'overtime', 'rc_number', 'rc']:
                        print(f"    {key}: {value}")
            except:
                print(f"  Raw data parsing failed")
    
    print(f"\n=== MAPPING ISSUE ANALYSIS ===")
    print("1. The system is only capturing David Foster's forms")
    print("2. Multiple forms exist for the same employee (different job numbers)")
    print("3. Field mapping is inconsistent between different Gemini responses")
    print("4. The L Line PDF likely contains forms for multiple employees")

def fix_mapping_for_l_line():
    """Fix the mapping issues for L Line forms"""
    
    print("\n=== FIXING L LINE MAPPING ===")
    
    # The issue is in the field mapping logic in app.py
    # Let me create an enhanced mapping function
    
    enhanced_mapping = {
        # Employee identification - multiple variations
        'employee_name': ['employee_name', 'name', 'employee', 'employee name', 'EMPLOYEE NAME'],
        'pass_number': ['pass_number', 'pass', 'PASS', 'assignment', 'reg', 'pass no', 'passnumber', 'pass number'],
        'title': ['title', 'TITLE', 'position', 'job_title', 'role', 'job title', 'employee_title'],
        
        # Job and location fields
        'job_number': ['job_number', 'job', 'JOB #', 'job no', 'job_no', 'job#', 'job number', 'ta_job_no', 'ta job no'],
        'rc_number': ['rc_number', 'rc', 'RC#', 'rc#', 'rc no', 'rc_no', 'rc number'],
        'report_loc': ['report_loc', 'report location', 'REPORT LOC.', 'location', 'reportloc', 'report', 'loc'],
        'overtime_location': ['overtime_location', 'overtime location', 'OVERTIME LOCATION', 'ot_location', 'otloc', 'ot location'],
        
        # Time fields
        'report_time': ['report_time', 'report time', 'REPORT TIME', 'report-time', 'report.time', 'reporttime'],
        'relief_time': ['relief_time', 'relief time', 'RELIEF TIME', 'relief-time', 'relief.time', 'relieftime'],
        'overtime_hours': ['overtime_hours', 'overtime hours', 'OVERTIME HOURS', 'overtime', 'hours', 'ot_hours', 'ot', 'total_overtime'],
        
        # Date fields
        'date_of_overtime': ['date_of_overtime', 'date of overtime', 'date', 'DATE', 's_m', 'W/T', 'w_t'],
        'rdos': ['rdos', 'rdo', 'S/M', 'rdo\'s', 'rduos', 'sm'],
        
        # Account fields
        'acct_number': ['acct_number', 'acct', 'ACCT #', 'acct#', 'acct no', 'acct_no', 'acct number', 'account_number', 'account number'],
        'amount': ['amount'],
        
        # Reason fields
        'reason_rdo': ['reason_rdo', 'rdo', 'RDO'],
        'reason_absentee_coverage': ['reason_absentee_coverage', 'absentee_coverage', 'absenteeCoverage', 'absentee coverage', 'Absentee Coverage'],
        'reason_no_lunch': ['reason_no_lunch', 'no_lunch', 'noLunch', 'no lunch', 'NO LUNCH'],
        'reason_early_report': ['reason_early_report', 'early_report', 'earlyReport', 'early report'],
        'reason_late_clear': ['reason_late_clear', 'late_clear', 'lateClear', 'late clear'],
        'reason_save_as_oto': ['reason_save_as_oto', 'save_as_oto', 'saveAsOto', 'save as oto'],
        'reason_capital_support_go': ['reason_capital_support_go', 'capital_support_go', 'capitalSupportGo', 'capital support go'],
        'reason_other': ['reason_other', 'other', 'OTHER', 'other_reason']
    }
    
    print("Enhanced mapping created with comprehensive field variations")
    print("This will handle the inconsistent Gemini field naming")
    
    return enhanced_mapping

def create_enhanced_extraction_prompt():
    """Create an enhanced prompt for L Line extraction"""
    
    enhanced_prompt = """You are an expert at extracting supervisor overtime authorization information from NYC Transit L Line forms.

CRITICAL: This L Line PDF contains MULTIPLE overtime slips for MULTIPLE employees. Extract EVERY single overtime slip you can identify.

EXTRACTION REQUIREMENTS:
1. Look for MULTIPLE employees - not just David Foster
2. Each employee may have multiple overtime entries
3. Extract ALL visible forms, even partial ones
4. Look for patterns of repeated employee information

EMPLOYEE IDENTIFICATION:
- Look for different pass numbers, names, titles
- Check for multiple RC numbers
- Identify different job assignments

OVERTIME DETAILS:
- Extract ALL overtime hours, locations, times
- Look for multiple dates and reasons
- Capture all account numbers and amounts

STRUCTURE OUTPUT:
- Use 'entries' array for multiple forms
- Each entry should be a complete overtime slip
- Include ALL fields that are visible

BE EXTREMELY THOROUGH - the L Line PDF contains dozens of overtime slips for multiple employees."""

    print("\n=== ENHANCED EXTRACTION PROMPT ===")
    print(enhanced_prompt)
    
    return enhanced_prompt

def test_enhanced_mapping():
    """Test the enhanced mapping with sample data"""
    
    print("\n=== TESTING ENHANCED MAPPING ===")
    
    # Sample Gemini output that might be causing issues
    sample_gemini_output = {
        "reg": "L-456",
        "assignment": "123456",
        "employee_name": "Jane Smith", 
        "title": "TSS",
        "rc": "7890",
        "job": "L-789",
        "overtime_location": "8 AV / 14 ST",
        "report_time": "06:00",
        "relief_time": "14:00",
        "overtime_hours": "02:00",
        "reason_for_overtime": ["NO LUNCH"],
        "acct": "12345"
    }
    
    enhanced_mapping = fix_mapping_for_l_line()
    
    # Test the mapping
    mapped_data = {}
    for target_field, source_variants in enhanced_mapping.items():
        for variant in source_variants:
            if variant in sample_gemini_output:
                mapped_data[target_field] = sample_gemini_output[variant]
                break
    
    print("Sample mapping test:")
    print(f"  Original: {sample_gemini_output}")
    print(f"  Mapped: {mapped_data}")
    
    return mapped_data

def main():
    """Main function to fix L Line mapping issues"""
    
    print("=== L LINE MAPPING FIX ===")
    
    # Analyze current issues
    analyze_l_line_mapping_issues()
    
    # Create enhanced mapping
    enhanced_mapping = fix_mapping_for_l_line()
    
    # Create enhanced prompt
    enhanced_prompt = create_enhanced_extraction_prompt()
    
    # Test enhanced mapping
    test_enhanced_mapping()
    
    print("\n=== RECOMMENDATIONS ===")
    print("1. Update the field mapping in app.py to use the enhanced mapping")
    print("2. Use the enhanced extraction prompt for L Line PDFs")
    print("3. Ensure the system processes ALL segments, not just the first few")
    print("4. Add better error handling for network issues")
    print("5. Implement retry logic for failed Gemini API calls")

if __name__ == "__main__":
    main()

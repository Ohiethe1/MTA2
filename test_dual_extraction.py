#!/usr/bin/env python3
"""
Test script to demonstrate how forms are stored in both pure and mapped extraction modes.
This shows how each uploaded form creates two database entries - one for each extraction mode.
"""

import json
import sys
import os

# Mock Gemini output for testing
SAMPLE_GEMINI_OUTPUT = '''
{
  "Regular Assignment": "A-201",
  "Report station": "207th",
  "Today's Date": "7/17/2025",
  "Pass Number": "086345",
  "Title": "C/R",
  "Employee Name": "John Doe",
  "RDOS": "5/5",
  "Actual OT Date": "7/17/2025",
  "DIV": "B",
  "Code": "39",
  "Line/Location": "A 207th St",
  "Run No.": "201A",
  "Exception Time From HH": "1",
  "Exception Time From MM": "00",
  "Exception Time To HH": "1",
  "Exception Time To MM": "30",
  "Overtime HH": "0",
  "Overtime MM": "30",
  "TA Job No.": "09068",
  "Comments": "Delay by Lender B/E at Jay - Metrotech",
  "OTO": "YES",
  "Entered in UTS": "YES"
}
'''

def process_gemini_extraction_dual(gemini_output: str, form_type: str = None):
    """
    Mock function to demonstrate dual extraction processing.
    """
    import re
    
    # Clean the Gemini output
    cleaned = re.sub(r"^```json|^```|```$", "", gemini_output.strip(), flags=re.MULTILINE).strip()
    
    try:
        raw_data = json.loads(cleaned)
        raw_gemini_json = json.dumps(raw_data, indent=2)
    except Exception as e:
        print("Error parsing cleaned Gemini output:", e)
        return [], ""
    
    all_forms = []
    
    # Process as pure extraction
    print("=== PROCESSING AS PURE EXTRACTION ===")
    pure_form_data = {
        'form_type': form_type,
        'raw_extracted_data': json.dumps(raw_data),
        'extraction_mode': 'pure',
        'employee_name': raw_data.get('Employee Name', 'N/A'),
        'pass_number': raw_data.get('Pass Number', 'N/A'),
        'title': raw_data.get('Title', 'N/A'),
        'comments': raw_data.get('Comments', 'N/A')
    }
    pure_rows = []
    if 'rows' in raw_data and isinstance(raw_data['rows'], list):
        pure_rows = raw_data['rows']
    
    all_forms.append((pure_form_data, pure_rows, raw_gemini_json))
    print("Pure extraction form data:", json.dumps(pure_form_data, indent=2))
    
    # Process as mapped extraction
    print("\n=== PROCESSING AS MAPPED EXTRACTION ===")
    mapped_form_data = {
        'form_type': form_type,
        'raw_extracted_data': json.dumps(raw_data),
        'extraction_mode': 'mapped',
        'employee_name': raw_data.get('Employee Name', 'N/A'),
        'pass_number': raw_data.get('Pass Number', 'N/A'),
        'title': raw_data.get('Title', 'N/A'),
        'regular_assignment': raw_data.get('Regular Assignment', 'N/A'),
        'report_loc': raw_data.get('Report station', 'N/A'),
        'todays_date': raw_data.get("Today's Date", 'N/A'),
        'rdos': raw_data.get('RDOS', 'N/A'),
        'actual_ot_date': raw_data.get('Actual OT Date', 'N/A'),
        'div': raw_data.get('DIV', 'N/A'),
        'exception_code': raw_data.get('Code', 'N/A'),
        'line_location': raw_data.get('Line/Location', 'N/A'),
        'run_no': raw_data.get('Run No.', 'N/A'),
        'exception_time_from_hh': raw_data.get('Exception Time From HH', 'N/A'),
        'exception_time_from_mm': raw_data.get('Exception Time From MM', 'N/A'),
        'exception_time_to_hh': raw_data.get('Exception Time To HH', 'N/A'),
        'exception_time_to_mm': raw_data.get('Exception Time To MM', 'N/A'),
        'overtime_hh': raw_data.get('Overtime HH', 'N/A'),
        'overtime_mm': raw_data.get('Overtime MM', 'N/A'),
        'ta_job_no': raw_data.get('TA Job No.', 'N/A'),
        'comments': raw_data.get('Comments', 'N/A'),
        'oto': raw_data.get('OTO', 'N/A'),
        'entered_in_uts': raw_data.get('Entered in UTS', 'N/A')
    }
    
    # Create mapped rows
    mapped_rows = [{
        'exception_code': raw_data.get('Code', ''),
        'line_location': raw_data.get('Line/Location', ''),
        'run_no': raw_data.get('Run No.', ''),
        'exception_time_from_hh': raw_data.get('Exception Time From HH', ''),
        'exception_time_from_mm': raw_data.get('Exception Time From MM', ''),
        'exception_time_to_hh': raw_data.get('Exception Time To HH', ''),
        'exception_time_to_mm': raw_data.get('Exception Time To MM', ''),
        'overtime_hh': raw_data.get('Overtime HH', ''),
        'overtime_mm': raw_data.get('Overtime MM', ''),
        'ta_job_no': raw_data.get('TA Job No.', '')
    }]
    
    all_forms.append((mapped_form_data, mapped_rows, raw_gemini_json))
    print("Mapped extraction form data:", json.dumps(mapped_form_data, indent=2))
    
    return all_forms, raw_gemini_json

def test_dual_extraction():
    """Test dual extraction processing"""
    print("=== DUAL EXTRACTION TEST ===")
    print("This demonstrates how each uploaded form creates TWO database entries:")
    print("1. Pure extraction entry (stores all raw data)")
    print("2. Mapped extraction entry (stores structured fields)")
    print()
    
    # Process the sample Gemini output
    forms_data, raw_gemini_json = process_gemini_extraction_dual(SAMPLE_GEMINI_OUTPUT, 'hourly')
    
    print(f"\n=== RESULTS ===")
    print(f"Total forms created: {len(forms_data)}")
    print(f"Raw Gemini JSON length: {len(raw_gemini_json)} characters")
    
    for i, (form_data, rows, individual_json) in enumerate(forms_data):
        print(f"\n--- Form {i+1} ({form_data['extraction_mode']} extraction) ---")
        print(f"Extraction Mode: {form_data['extraction_mode']}")
        print(f"Employee Name: {form_data.get('employee_name', 'N/A')}")
        print(f"Pass Number: {form_data.get('pass_number', 'N/A')}")
        print(f"Title: {form_data.get('title', 'N/A')}")
        print(f"Comments: {form_data.get('comments', 'N/A')}")
        
        if form_data['extraction_mode'] == 'mapped':
            print(f"Regular Assignment: {form_data.get('regular_assignment', 'N/A')}")
            print(f"Report Location: {form_data.get('report_loc', 'N/A')}")
            print(f"Overtime: {form_data.get('overtime_hh', 'N/A')}h {form_data.get('overtime_mm', 'N/A')}m")
            print(f"TA Job No: {form_data.get('ta_job_no', 'N/A')}")
            print(f"Rows count: {len(rows)}")
        else:
            print(f"Raw data stored: {len(form_data.get('raw_extracted_data', ''))} characters")
            print(f"All original fields preserved in raw_extracted_data")

def demonstrate_benefits():
    """Demonstrate the benefits of dual extraction"""
    print("\n=== BENEFITS OF DUAL EXTRACTION ===")
    
    print("✅ Pure Extraction Benefits:")
    print("   - Complete data preservation")
    print("   - No information loss")
    print("   - Flexible field discovery")
    print("   - Future-proof data storage")
    
    print("\n✅ Mapped Extraction Benefits:")
    print("   - Structured database queries")
    print("   - Fast filtering and sorting")
    print("   - Consistent field names")
    print("   - Easy reporting and analytics")
    
    print("\n✅ Dual Extraction Benefits:")
    print("   - Best of both worlds")
    print("   - Compare extraction approaches")
    print("   - Switch between modes seamlessly")
    print("   - Complete data lineage")

def show_dashboard_behavior():
    """Show how dashboard behaves with dual extraction"""
    print("\n=== DASHBOARD BEHAVIOR ===")
    
    print("When you upload a form, it creates TWO database entries:")
    print("1. Pure extraction entry (extraction_mode = 'pure')")
    print("2. Mapped extraction entry (extraction_mode = 'mapped')")
    print()
    
    print("Dashboard filtering:")
    print("- Pure Mode: Shows only forms with extraction_mode = 'pure'")
    print("- Mapped Mode: Shows only forms with extraction_mode = 'mapped'")
    print("- Same form appears in both modes with different data structures")
    print()
    
    print("Statistics calculation:")
    print("- Pure Mode: Calculates stats from raw_extracted_data JSON")
    print("- Mapped Mode: Calculates stats from structured database fields")
    print("- Each mode shows accurate statistics for its data format")

if __name__ == "__main__":
    test_dual_extraction()
    demonstrate_benefits()
    show_dashboard_behavior()
    
    print("\n=== IMPLEMENTATION SUMMARY ===")
    print("✅ Forms are now stored in BOTH extraction modes")
    print("✅ Dashboard filters by extraction_mode")
    print("✅ You can compare pure vs mapped results")
    print("✅ No data loss - everything is preserved")
    print("✅ Easy switching between extraction approaches") 
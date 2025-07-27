#!/usr/bin/env python3
"""
Test script to demonstrate the difference between pure and mapped extraction modes.
This script shows how the same Gemini output would be processed differently.
"""

import json
import sys
import os

# Add the current directory to Python path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Gemini output for testing
SAMPLE_GEMINI_OUTPUT = '''
{
  "employee_name": "John Doe",
  "pass_number": "12345678",
  "title": "Operator",
  "regular_assignment": "Line 1",
  "report": "Station A",
  "relief": "Station B",
  "todays_date": "2024-01-15",
  "rdos": "Sat/Sun",
  "actual_ot_date": "2024-01-14",
  "div": "A",
  "comments": "Worked extra hours due to emergency",
  "unexpected_field": "This field is not in our schema",
  "another_unknown_field": "Another field we didn't expect",
  "rows": [
    {
      "line_location": "Line 1",
      "run_no": "101",
      "exception_time_from_hh": "14",
      "exception_time_from_mm": "30",
      "exception_time_to_hh": "18",
      "exception_time_to_mm": "45",
      "overtime_hh": "4",
      "overtime_mm": "15",
      "bonus_hh": "0",
      "bonus_mm": "0",
      "nite_diff_hh": "0",
      "nite_diff_mm": "0",
      "ta_job_no": "TA123"
    }
  ]
}
'''

def test_pure_extraction():
    """Test pure extraction mode"""
    print("=== PURE EXTRACTION MODE ===")
    
    # Simulate pure extraction
    data = json.loads(SAMPLE_GEMINI_OUTPUT)
    
    form_data = {
        'form_type': 'hourly',
        'raw_extracted_data': json.dumps(data),
        'extraction_mode': 'pure'
    }
    
    # Only extract obvious fields for basic functionality
    if 'employee_name' in data:
        form_data['employee_name'] = data['employee_name']
    if 'pass_number' in data:
        form_data['pass_number'] = data['pass_number']
    if 'title' in data:
        form_data['title'] = data['title']
    if 'comments' in data:
        form_data['comments'] = data['comments']
    
    print("Form Data (Pure Mode):")
    print(json.dumps(form_data, indent=2))
    print(f"\nTotal fields extracted: {len(form_data)}")
    print(f"Raw data preserved: {len(data)} fields")
    print(f"Unexpected fields captured: {len([k for k in data.keys() if k not in ['employee_name', 'pass_number', 'title', 'comments', 'rows']])}")

def test_mapped_extraction():
    """Test mapped extraction mode"""
    print("\n=== MAPPED EXTRACTION MODE ===")
    
    # Simulate mapped extraction (simplified version)
    data = json.loads(SAMPLE_GEMINI_OUTPUT)
    
    # Define all expected fields
    all_fields = [
        "regular_assignment", "report", "relief", "todays_date", "title", 
        "employee_name", "rdos", "actual_ot_date", "div", "pass_number",
        "exception_code", "line_location", "run_no", "exception_time_from_hh", 
        "exception_time_from_mm", "exception_time_to_hh", "exception_time_to_mm",
        "overtime_hh", "overtime_mm", "ta_job_no", "comments", "oto", 
        "oto_amount_saved_hh", "oto_amount_saved_mm", "entered_in_uts_yes", 
        "entered_in_uts_no", "supervisor_name", "supervisor_pass_no"
    ]
    
    form_data = {field: '' for field in all_fields}
    form_data['form_type'] = 'hourly'
    form_data['extraction_mode'] = 'mapped'
    
    # Map fields (simplified mapping)
    key_map = {
        'employee_name': 'employee_name',
        'pass_number': 'pass_number',
        'title': 'title',
        'regular_assignment': 'regular_assignment',
        'report': 'report',
        'relief': 'relief',
        'todays_date': 'todays_date',
        'rdos': 'rdos',
        'actual_ot_date': 'actual_ot_date',
        'div': 'div',
        'comments': 'comments'
    }
    
    # Apply mapping
    for gemini_key, db_key in key_map.items():
        if gemini_key in data:
            form_data[db_key] = data[gemini_key]
    
    print("Form Data (Mapped Mode):")
    print(json.dumps(form_data, indent=2))
    print(f"\nTotal fields in schema: {len(all_fields)}")
    print(f"Fields successfully mapped: {len([v for v in form_data.values() if v != ''])}")
    print(f"Unexpected fields lost: {len([k for k in data.keys() if k not in key_map and k != 'rows'])}")

def compare_approaches():
    """Compare both approaches"""
    print("\n=== COMPARISON ===")
    print("Pure Extraction:")
    print("✅ Captures all fields from Gemini")
    print("✅ No mapping maintenance needed")
    print("✅ Future-proof for new fields")
    print("❌ Harder to query specific fields")
    print("❌ Unstructured data storage")
    print("❌ More complex UI handling")
    
    print("\nMapped Extraction:")
    print("✅ Structured, predictable schema")
    print("✅ Easy to query and filter")
    print("✅ Better performance")
    print("✅ Type safety and validation")
    print("❌ Complex mapping logic")
    print("❌ Brittle to Gemini output changes")
    print("❌ May miss unexpected fields")

if __name__ == "__main__":
    test_pure_extraction()
    test_mapped_extraction()
    compare_approaches()
    
    print("\n=== RECOMMENDATION ===")
    print("Use the hybrid approach implemented in the app:")
    print("1. Set PURE_GEMINI_EXTRACTION = False for production (mapped mode)")
    print("2. Set PURE_GEMINI_EXTRACTION = True for exploration (pure mode)")
    print("3. Both modes store raw Gemini JSON for future reference")
    print("4. Toggle between modes using the UI button") 
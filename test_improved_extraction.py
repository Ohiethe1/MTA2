#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_improved_extraction():
    """Test the improved field mapping for John Maida's forms"""
    
    # Import the functions from app.py
    from app import gemini_extract_file_details, process_gemini_extraction_dual
    
    # Test with the full page 2 which should have John Maida's data
    test_file = "debug_segment_page2_full_page.png"
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    print("=== Testing Improved Extraction for John Maida ===")
    print(f"Test file: {test_file}")
    
    try:
        # Test Gemini extraction
        gemini_output = gemini_extract_file_details(test_file, form_type='supervisor')
        
        if gemini_output:
            print(f"Gemini output length: {len(gemini_output)} characters")
            
            # Test processing
            forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type='supervisor')
            print(f"Forms extracted: {len(forms_data)}")
            
            for k, (form_data, rows, individual_json) in enumerate(forms_data):
                print(f"\nForm {k+1}:")
                print(f"  Pass Number: {form_data.get('pass_number', 'NOT_FOUND')}")
                print(f"  Employee Name: {form_data.get('employee_name', 'NOT_FOUND')}")
                print(f"  Title: {form_data.get('title', 'NOT_FOUND')}")
                print(f"  Job Number: {form_data.get('job_number', 'NOT_FOUND')}")
                print(f"  RC Number: {form_data.get('rc_number', 'NOT_FOUND')}")
                print(f"  Overtime Hours: {form_data.get('overtime_hours', 'NOT_FOUND')}")
                print(f"  Date of Overtime: {form_data.get('date_of_overtime', 'NOT_FOUND')}")
                print(f"  Report Location: {form_data.get('report_loc', 'NOT_FOUND')}")
                print(f"  Overtime Location: {form_data.get('overtime_location', 'NOT_FOUND')}")
                
                # Check if this form would pass duplicate detection
                if form_data.get('pass_number') and form_data.get('overtime_hours') and form_data.get('date_of_overtime'):
                    print(f"  ✅ WOULD BE STORED (all required fields present)")
                else:
                    print(f"  ❌ WOULD NOT BE STORED (missing required fields)")
                    missing = []
                    if not form_data.get('pass_number'): missing.append('pass_number')
                    if not form_data.get('overtime_hours'): missing.append('overtime_hours')
                    if not form_data.get('date_of_overtime'): missing.append('date_of_overtime')
                    print(f"     Missing: {', '.join(missing)}")
        else:
            print("No Gemini output")
            
    except Exception as e:
        print(f"Error processing {test_file}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_extraction() 
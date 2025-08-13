#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import the functions from app.py
from app import gemini_extract_file_details, process_gemini_extraction_dual

def test_supervisor_extraction():
    """Test the supervisor form extraction process step by step"""
    
    # Test with a different image - use the exact filename from ls output
    test_file = "uploads/supervisor/Screenshot 2025-07-24 at 5.41.18 PM.png"
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        # Try to find the file with a different approach
        import glob
        files = glob.glob("uploads/supervisor/*5.41.18*")
        if files:
            test_file = files[0]
            print(f"Found file: {test_file}")
        else:
            print("No matching files found")
            return
    
    print("=== Testing Supervisor Form Extraction ===")
    print(f"Test file: {test_file}")
    print(f"File size: {os.path.getsize(test_file)} bytes")
    print()
    
    # Step 1: Test Gemini extraction
    print("Step 1: Testing Gemini extraction...")
    try:
        gemini_output = gemini_extract_file_details(test_file, form_type='supervisor')
        print(f"Gemini output received: {len(gemini_output) if gemini_output else 0} characters")
        if gemini_output:
            print("First 500 characters of Gemini output:")
            print(gemini_output[:500])
            print("...")
        else:
            print("ERROR: No Gemini output received")
            return
    except Exception as e:
        print(f"ERROR in Gemini extraction: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # Step 2: Test processing the Gemini output
    print("Step 2: Testing Gemini output processing...")
    try:
        forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type='supervisor')
        print(f"Forms data: {len(forms_data)} forms extracted")
        print(f"Raw JSON length: {len(raw_gemini_json)} characters")
        
        for i, (form_data, rows, individual_json) in enumerate(forms_data):
            print(f"\nForm {i+1}:")
            print(f"  Form data keys: {list(form_data.keys())}")
            print(f"  Rows: {len(rows)}")
            print(f"  Rows: {len(rows)}")
            print(f"  Individual JSON length: {len(individual_json)}")
            
            # Show some key fields
            key_fields = ['pass_number', 'employee_name', 'title', 'overtime_hours', 'job_number']
            for field in key_fields:
                value = form_data.get(field, 'NOT_FOUND')
                print(f"  {field}: {value}")
                
    except Exception as e:
        print(f"ERROR in processing Gemini output: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_supervisor_extraction() 
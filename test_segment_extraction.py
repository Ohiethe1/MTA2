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

def test_segment_extraction():
    """Test extraction from individual segments to see what we can extract"""
    
    # Test with different segments
    test_segments = [
        "test_segment_page1_half_1.png",
        "test_segment_page1_half_2.png", 
        "test_segment_page1_quarter_1.png",
        "test_segment_page1_quarter_2.png",
        "test_segment_page1_quarter_3.png"
    ]
    
    for segment_file in test_segments:
        if not os.path.exists(segment_file):
            print(f"Segment file not found: {segment_file}")
            continue
        
        print(f"\n=== Testing Segment: {segment_file} ===")
        print(f"File size: {os.path.getsize(segment_file)} bytes")
        
        # Test Gemini extraction
        try:
            gemini_output = gemini_extract_file_details(segment_file, form_type='supervisor')
            if gemini_output:
                print(f"Gemini output: {len(gemini_output)} characters")
                print("First 300 characters:")
                print(gemini_output[:300])
                
                # Test processing
                forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type='supervisor')
                print(f"Forms extracted: {len(forms_data)}")
                
                for i, (form_data, rows, individual_json) in enumerate(forms_data):
                    print(f"  Form {i+1}:")
                    key_fields = ['pass_number', 'employee_name', 'title', 'job_number', 'overtime_hours']
                    for field in key_fields:
                        value = form_data.get(field, 'NOT_FOUND')
                        if value:
                            print(f"    {field}: {value}")
            else:
                print("No Gemini output")
                
        except Exception as e:
            print(f"Error processing segment: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_segment_extraction() 
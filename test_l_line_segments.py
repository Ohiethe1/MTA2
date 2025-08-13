#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_l_line_segments():
    """Test processing of L Line segments to see what's happening"""
    
    print("=== TESTING L LINE SEGMENT PROCESSING ===")
    
    # Test a few segments manually
    test_segments = [
        "L Line OT Slips PPE 7.26.25_page1_segment1.png",
        "L Line OT Slips PPE 7.26.25_page1_segment2.png", 
        "L Line OT Slips PPE 7.26.25_page1_segment3.png",
        "L Line OT Slips PPE 7.26.25_page2_segment1.png",
        "L Line OT Slips PPE 7.26.25_page2_segment2.png"
    ]
    
    segments_dir = "uploads/supervisor"
    
    for segment_name in test_segments:
        segment_path = os.path.join(segments_dir, segment_name)
        if not os.path.exists(segment_path):
            print(f"Segment not found: {segment_path}")
            continue
            
        print(f"\n--- Testing {segment_name} ---")
        
        try:
            # Import the extraction function
            from app import gemini_extract_file_details, process_gemini_extraction_dual
            
            # Extract from this segment
            print(f"Extracting from {segment_name}...")
            gemini_output = gemini_extract_file_details(segment_path, form_type='supervisor')
            
            if gemini_output:
                print(f"✅ Gemini extraction successful")
                print(f"Output length: {len(gemini_output)} characters")
                print(f"First 200 chars: {gemini_output[:200]}...")
                
                # Process the extraction
                print(f"Processing extraction...")
                forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type='supervisor')
                
                print(f"✅ Processing successful")
                print(f"Forms extracted: {len(forms_data)}")
                
                for i, (form_data, rows, individual_json) in enumerate(forms_data):
                    print(f"  Form {i+1}:")
                    print(f"    Employee: {form_data.get('employee_name', 'N/A')}")
                    print(f"    Pass: {form_data.get('pass_number', 'N/A')}")
                    print(f"    Title: {form_data.get('title', 'N/A')}")
                    print(f"    Job: {form_data.get('job_number', 'N/A')}")
                    print(f"    Overtime: {form_data.get('overtime_hours', 'N/A')}")
                    print(f"    Extraction mode: {form_data.get('extraction_mode', 'N/A')}")
                    
            else:
                print(f"❌ Gemini extraction failed - no output")
                
        except Exception as e:
            print(f"❌ Error processing {segment_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== SUMMARY ===")
    print(f"Tested {len(test_segments)} segments")

if __name__ == "__main__":
    test_l_line_segments()

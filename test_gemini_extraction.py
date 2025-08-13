#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_gemini_extraction():
    """Test Gemini extraction on a few L Line segments"""
    
    print("=== GEMINI EXTRACTION TEST ===")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        print("Please set it with: export GEMINI_API_KEY='your_key_here'")
        return
    else:
        print(f"✅ GEMINI_API_KEY found: {api_key[:20]}...")
    
    # Test with a few segments
    segments_dir = "uploads/supervisor"
    test_segments = [
        "L Line OT Slips PPE 7.26.25_page1_segment1.png",
        "L Line OT Slips PPE 7.26.25_page2_segment1.png",
        "L Line OT Slips PPE 7.26.25_page3_segment1.png"
    ]
    
    print(f"\nTesting Gemini extraction on {len(test_segments)} segments:")
    
    for segment in test_segments:
        segment_path = os.path.join(segments_dir, segment)
        if not os.path.exists(segment_path):
            print(f"❌ Segment not found: {segment}")
            continue
            
        print(f"\n--- Testing {segment} ---")
        
        try:
            # Import and test Gemini extraction
            from app import gemini_extract_file_details, process_gemini_extraction_dual
            
            print(f"  Calling Gemini extraction...")
            gemini_output = gemini_extract_file_details(segment_path, form_type='supervisor')
            
            if gemini_output:
                print(f"  ✅ Gemini returned output ({len(gemini_output)} characters)")
                print(f"  Output preview: {gemini_output[:200]}...")
                
                # Test processing the output
                print(f"  Processing Gemini output...")
                forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type='supervisor')
                
                if forms_data:
                    print(f"  ✅ Extracted {len(forms_data)} forms")
                    for i, (form_data, rows, individual_json) in enumerate(forms_data):
                        employee_name = form_data.get('employee_name', 'Unknown')
                        pass_number = form_data.get('pass_number', 'Unknown')
                        print(f"    Form {i+1}: {employee_name} ({pass_number})")
                else:
                    print(f"  ❌ No forms extracted from Gemini output")
                    
            else:
                print(f"  ❌ Gemini returned no output")
                
        except Exception as e:
            print(f"  ❌ Error during extraction: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_gemini_extraction()

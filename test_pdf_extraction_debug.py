#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_pdf_extraction_debug():
    """Debug why only David Foster's forms are being extracted"""
    
    pdf_path = "uploads/supervisor/L Line OT Slips PPE 7.26.25.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("=== PDF Extraction Debug ===")
    print(f"File: {pdf_path}")
    print(f"Size: {os.path.getsize(pdf_path)} bytes")
    
    try:
        import pdfplumber
        from PIL import Image
        import io
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                print(f"\n--- Page {i+1} ---")
                
                img = page.to_image(resolution=300).original
                width, height = img.size
                print(f"Image dimensions: {width}x{height}")
                
                # Test the exact segmentation logic from app.py
                segments = []
                
                # Method 1: Halves
                segments.append(("Half 1", img.crop((0, 0, width, height // 2))))
                segments.append(("Half 2", img.crop((0, height // 2, width, height))))
                
                # Method 2: Quarters
                if height > 1000:
                    quarter_height = height // 4
                    for q in range(4):
                        y_start = q * quarter_height
                        y_end = (q + 1) * quarter_height if q < 3 else height
                        segments.append((f"Quarter {q+1}", img.crop((0, y_start, width, y_end))))
                
                # Method 3: Eighths
                if height > 1500:
                    eighth_height = height // 8
                    for e in range(8):
                        y_start = e * eighth_height
                        y_end = (e + 1) * eighth_height if e < 7 else height
                        segments.append((f"Eighth {e+1}", img.crop((0, y_start, width, y_end))))
                
                # Method 4: Tenths
                if height > 2000:
                    tenth_height = height // 10
                    for t in range(10):
                        y_start = t * tenth_height
                        y_end = (t + 1) * tenth_height if t < 9 else height
                        segments.append((f"Tenth {t+1}", img.crop((0, y_start, width, y_end))))
                
                # Method 5: Full page
                segments.append(("Full Page", img))
                
                print(f"Generated {len(segments)} potential segments")
                
                # Save segments for visual inspection
                for j, (name, segment) in enumerate(segments):
                    segment_path = f"debug_segment_page{i+1}_{name.lower().replace(' ', '_')}.png"
                    segment.save(segment_path)
                    print(f"  Saved {segment_path}: {segment.size}")
                
                # Only process first 2 pages for debugging
                if i >= 1:
                    break
                    
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

def test_gemini_extraction_on_segments():
    """Test Gemini extraction on the saved segments"""
    
    print("\n=== Testing Gemini Extraction on Segments ===")
    
    # Import the functions from app.py
    from app import gemini_extract_file_details, process_gemini_extraction_dual
    
    # Find all debug segments
    import glob
    segment_files = glob.glob("debug_segment_*.png")
    
    if not segment_files:
        print("No debug segments found. Run the first test first.")
        return
    
    print(f"Found {len(segment_files)} debug segments")
    
    for segment_file in segment_files[:5]:  # Test first 5 segments
        print(f"\n--- Testing {segment_file} ---")
        
        try:
            # Test Gemini extraction
            gemini_output = gemini_extract_file_details(segment_file, form_type='supervisor')
            
            if gemini_output:
                print(f"Gemini output length: {len(gemini_output)} characters")
                print("First 300 characters:")
                print(gemini_output[:300])
                
                # Test processing
                forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type='supervisor')
                print(f"Forms extracted: {len(forms_data)}")
                
                for k, (form_data, rows, individual_json) in enumerate(forms_data):
                    print(f"  Form {k+1}:")
                    print(f"    Pass Number: {form_data.get('pass_number', 'NOT_FOUND')}")
                    print(f"    Employee Name: {form_data.get('employee_name', 'NOT_FOUND')}")
                    print(f"    Title: {form_data.get('title', 'NOT_FOUND')}")
                    print(f"    Job Number: {form_data.get('job_number', 'NOT_FOUND')}")
                    print(f"    Overtime Hours: {form_data.get('overtime_hours', 'NOT_FOUND')}")
                    print(f"    Date: {form_data.get('date_of_overtime', 'NOT_FOUND')}")
                    print(f"    RC Number: {form_data.get('rc_number', 'NOT_FOUND')}")
            else:
                print("No Gemini output")
                
        except Exception as e:
            print(f"Error processing {segment_file}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_pdf_extraction_debug()
    test_gemini_extraction_on_segments() 
#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def analyze_pdf_structure():
    """Analyze the PDF structure to understand what forms might be present"""
    
    pdf_path = "uploads/supervisor/L Line OT Slips PPE 7.26.25.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("=== PDF Structure Analysis ===")
    print(f"File: {pdf_path}")
    print(f"Size: {os.path.getsize(pdf_path)} bytes")
    
    try:
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                print(f"\n--- Page {i+1} ---")
                
                # Get page dimensions
                width = page.width
                height = page.height
                print(f"Dimensions: {width} x {height}")
                
                # Extract text to see what's on each page
                text = page.extract_text()
                if text:
                    print(f"Text length: {len(text)} characters")
                    print("First 200 characters:")
                    print(text[:200])
                    
                    # Look for potential form indicators
                    lines = text.split('\n')
                    print(f"Number of text lines: {len(lines)}")
                    
                    # Look for employee names, job numbers, etc.
                    employee_indicators = ['pass', 'employee', 'name', 'title', 'rdos']
                    job_indicators = ['job', 'l-', 'l_', 'line']
                    time_indicators = ['overtime', 'hours', 'time', 'report', 'relief']
                    
                    for line in lines[:20]:  # Check first 20 lines
                        line_lower = line.lower()
                        if any(indicator in line_lower for indicator in employee_indicators):
                            print(f"  Employee indicator found: {line.strip()}")
                        if any(indicator in line_lower for indicator in job_indicators):
                            print(f"  Job indicator found: {line.strip()}")
                        if any(indicator in line_lower for indicator in time_indicators):
                            print(f"  Time indicator found: {line.strip()}")
                else:
                    print("No text extracted from this page")
                
                # Check if page has images
                if page.images:
                    print(f"Page has {len(page.images)} images")
                
                # Check for tables
                tables = page.extract_tables()
                if tables:
                    print(f"Page has {len(tables)} tables")
                    for j, table in enumerate(tables):
                        print(f"  Table {j+1}: {len(table)} rows")
                
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

def test_enhanced_segmentation():
    """Test the enhanced segmentation approach"""
    
    pdf_path = "uploads/supervisor/L Line OT Slips PPE 7.26.25.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("\n=== Enhanced Segmentation Test ===")
    
    try:
        import pdfplumber
        from PIL import Image
        import io
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"\n--- Page {i+1} Segmentation ---")
                
                img = page.to_image(resolution=300).original
                width, height = img.size
                print(f"Image dimensions: {width}x{height}")
                
                # Test different segmentation approaches
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
                
                # Method 5: Overlapping segments for better coverage
                overlap_height = height // 12
                for o in range(0, height - overlap_height, overlap_height // 2):
                    segments.append((f"Overlap {o//(overlap_height//2)+1}", img.crop((0, o, width, o + overlap_height))))
                
                print(f"Generated {len(segments)} potential segments")
                
                # Save a few sample segments for visual inspection
                for j, (name, segment) in enumerate(segments[:5]):  # Save first 5 segments
                    segment_path = f"test_segment_page{i+1}_{name.lower().replace(' ', '_')}.png"
                    segment.save(segment_path)
                    print(f"  Saved {segment_path}: {segment.size}")
                
                break  # Only process first page for testing
                
    except Exception as e:
        print(f"Error testing segmentation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_pdf_structure()
    test_enhanced_segmentation() 
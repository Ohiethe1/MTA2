#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def debug_l_line_extraction():
    """Debug why only David Foster forms are being extracted from L Line PDF"""
    
    print("=== L LINE PDF EXTRACTION DEBUG ===")
    
    # Check if we have the segments
    segments_dir = "uploads/supervisor"
    if not os.path.exists(segments_dir):
        print(f"Segments directory not found: {segments_dir}")
        return
    
    # Find L Line segments
    l_line_segments = [f for f in os.listdir(segments_dir) if "L Line OT Slips PPE 7.26.25" in f and f.endswith('.png')]
    print(f"Found {len(l_line_segments)} L Line segments")
    
    if not l_line_segments:
        print("No L Line segments found!")
        return
    
    # Test a few segments to see what's happening
    test_segments = l_line_segments[:5]  # Test first 5 segments
    
    print(f"\nTesting first 5 segments:")
    for segment in test_segments:
        segment_path = os.path.join(segments_dir, segment)
        print(f"\n--- Testing {segment} ---")
        
        # Check file size and dimensions
        try:
            from PIL import Image
            img = Image.open(segment_path)
            width, height = img.size
            file_size = os.path.getsize(segment_path)
            print(f"  Dimensions: {width}x{height}")
            print(f"  File size: {file_size} bytes")
            
            # Check if it's blank
            gray_img = img.convert('L')
            nonwhite = sum(1 for p in gray_img.getdata() if p < 240)
            print(f"  Non-white pixels: {nonwhite}")
            
            # Test blank detection
            from app import is_blank_or_crossed_out
            is_blank = is_blank_or_crossed_out(segment_path)
            print(f"  Is blank: {is_blank}")
            
            if not is_blank:
                print(f"  ✅ Segment would be processed")
            else:
                print(f"  ❌ Segment would be skipped")
                
        except Exception as e:
            print(f"  Error analyzing segment: {e}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total L Line segments: {len(l_line_segments)}")
    print(f"Tested segments: {len(test_segments)}")
    
    # Check database for L Line forms
    try:
        import sqlite3
        with sqlite3.connect('forms.db', timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT employee_name, pass_number, title, file_name FROM exception_forms WHERE file_name LIKE '%L Line%' ORDER BY upload_date DESC")
            l_line_forms = c.fetchall()
            
            print(f"\nL Line forms in database: {len(l_line_forms)}")
            for form in l_line_forms:
                print(f"  - {form[0]} ({form[1]}) - {form[2]} - {form[3]}")
                
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    debug_l_line_extraction()

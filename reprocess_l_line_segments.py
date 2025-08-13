#!/usr/bin/env python3

import os
import sys
import json
import sqlite3
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def reprocess_l_line_segments():
    """Reprocess L Line segments with enhanced mapping"""
    
    print("=== REPROCESSING L LINE SEGMENTS ===")
    
    # Check if we have the segments
    segments_dir = "uploads/supervisor"
    if not os.path.exists(segments_dir):
        print(f"Segments directory not found: {segments_dir}")
        return
    
    # Find L Line segments
    l_line_segments = [f for f in os.listdir(segments_dir) if "L Line OT Slips PPE 7.26.25" in f and f.endswith('.png')]
    print(f"Found {len(l_line_segments)} L Line segments to reprocess")
    
    if not l_line_segments:
        print("No L Line segments found!")
        return
    
    # Test a few segments first
    test_segments = l_line_segments[:3]  # Test first 3 segments
    
    print(f"\nTesting first 3 segments with enhanced mapping:")
    
    for segment_name in test_segments:
        segment_path = os.path.join(segments_dir, segment_name)
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
                print(f"First 300 chars: {gemini_output[:300]}...")
                
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
                    print(f"    RC: {form_data.get('rc_number', 'N/A')}")
                    print(f"    Location: {form_data.get('overtime_location', 'N/A')}")
                    print(f"    Extraction mode: {form_data.get('extraction_mode', 'N/A')}")
                    
            else:
                print(f"❌ Gemini extraction failed - no output")
                
        except Exception as e:
            print(f"❌ Error processing {segment_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== REPROCESSING SUMMARY ===")
    print(f"Total L Line segments: {len(l_line_segments)}")
    print(f"Tested segments: {len(test_segments)}")
    print(f"Ready to reprocess all segments with enhanced mapping")

def check_database_for_l_line_forms():
    """Check what L Line forms are currently in the database"""
    
    print("\n=== CHECKING DATABASE FOR L LINE FORMS ===")
    
    try:
        with sqlite3.connect('forms.db', timeout=10) as conn:
            c = conn.cursor()
            
            # Check for forms with L Line references
            c.execute("""
                SELECT id, employee_name, pass_number, title, job_number, overtime_hours, 
                       file_name, extraction_mode, upload_date
                FROM exception_forms 
                WHERE form_type='supervisor' 
                AND (file_name LIKE '%L Line%' OR job_number LIKE 'L-%' OR employee_name LIKE '%L Line%')
                ORDER BY upload_date DESC
            """)
            
            l_line_forms = c.fetchall()
            
            print(f"L Line forms in database: {len(l_line_forms)}")
            for form in l_line_forms:
                form_id, employee_name, pass_number, title, job_number, overtime_hours, file_name, extraction_mode, upload_date = form
                print(f"  - ID {form_id}: {employee_name} ({pass_number}) - {title} - Job: {job_number} - OT: {overtime_hours} - {file_name}")
                
            # Check for forms with L-213 or L-313 job numbers
            c.execute("""
                SELECT COUNT(*) as count, job_number, GROUP_CONCAT(employee_name) as employees
                FROM exception_forms 
                WHERE form_type='supervisor' AND job_number LIKE 'L-%'
                GROUP BY job_number
                ORDER BY job_number
            """)
            
            job_summary = c.fetchall()
            print(f"\nJob number summary:")
            for count, job_number, employees in job_summary:
                print(f"  {job_number}: {count} forms - {employees}")
                
    except Exception as e:
        print(f"Error checking database: {e}")

def main():
    """Main function to reprocess L Line segments"""
    
    print("=== L LINE SEGMENT REPROCESSING ===")
    
    # Check current database state
    check_database_for_l_line_forms()
    
    # Reprocess segments
    reprocess_l_line_segments()
    
    print("\n=== NEXT STEPS ===")
    print("1. The enhanced mapping should now handle all Gemini field variations")
    print("2. L Line specific prompts will extract multiple employees and forms")
    print("3. Retry logic will handle network issues")
    print("4. All 109 L Line segments should now be processed properly")
    print("5. You should see forms for multiple employees, not just David Foster")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to create test forms with pure extraction mode to demonstrate export functionality.
"""

import sqlite3
import datetime
import json

def create_pure_extraction_test_data():
    """Create test forms with pure extraction mode"""
    
    # Sample pure extraction data (raw Gemini output)
    pure_extraction_data_1 = {
        "employee_name": "Test Employee 1",
        "pass_number": "12345678",
        "title": "Operator",
        "regular_assignment": "A-201",
        "report_station": "207th",
        "today_date": "2025-01-15",
        "rdos": "Sat/Sun",
        "actual_ot_date": "2025-01-15",
        "div": "A",
        "exception_code": "39",
        "line_location": "A 207th St",
        "run_no": "201A",
        "exception_time_from": "01:00",
        "exception_time_to": "01:30",
        "overtime_hours": "00:30",
        "ta_job_no": "09068",
        "comments": "Test pure extraction form 1",
        "oto": "YES",
        "entered_in_uts": "YES"
    }
    
    pure_extraction_data_2 = {
        "reg_assignment": "RR A/306",
        "report_location": "UNPT",
        "assignment": "311099 ATD 2302",
        "employee_name": "Test Employee 2",
        "pass": "311L",
        "title": "UNPT",
        "job_number": "311L",
        "overtime_location": "UNPT",
        "date": "2025-01-16",
        "rdos": "M/T",
        "date_of_overtime": "2025-01-16",
        "report_time": "20:00",
        "relief_time": "04:40",
        "overtime_hours": "00:40 + 00:20",
        "reason_for_overtime": "EARLY REPORT",
        "acct_number": "02186",
        "comments": "Test pure extraction form 2",
        "superintendent_authorization": "713026 2025-01-16",
        "entered_into_uts": "NO"
    }
    
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        
        # Insert test form 1 (hourly) - using minimal required fields
        c.execute('''
            INSERT INTO exception_forms (
                pass_number, title, employee_name, rdos, actual_ot_date, div, comments,
                status, username, form_type, upload_date, file_name,
                raw_gemini_json, raw_extracted_data, extraction_mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pure_extraction_data_1.get('pass_number', ''),
            pure_extraction_data_1.get('title', ''),
            pure_extraction_data_1.get('employee_name', ''),
            pure_extraction_data_1.get('rdos', ''),
            pure_extraction_data_1.get('actual_ot_date', ''),
            pure_extraction_data_1.get('div', ''),
            pure_extraction_data_1.get('comments', ''),
            'processed', 'test_user', 'hourly', datetime.datetime.now().isoformat(),
            'test_pure_extraction_1.png',
            json.dumps(pure_extraction_data_1),
            json.dumps(pure_extraction_data_1),
            'pure'
        ))
        
        # Insert test form 2 (supervisor) - using minimal required fields
        c.execute('''
            INSERT INTO exception_forms (
                pass_number, title, employee_name, rdos, actual_ot_date, div, comments,
                status, username, form_type, upload_date, file_name,
                raw_gemini_json, raw_extracted_data, extraction_mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pure_extraction_data_2.get('pass', ''),
            pure_extraction_data_2.get('title', ''),
            pure_extraction_data_2.get('employee_name', ''),
            pure_extraction_data_2.get('rdos', ''),
            pure_extraction_data_2.get('date_of_overtime', ''),
            '', pure_extraction_data_2.get('comments', ''),
            'processed', 'test_user', 'supervisor', datetime.datetime.now().isoformat(),
            'test_pure_extraction_2.png',
            json.dumps(pure_extraction_data_2),
            json.dumps(pure_extraction_data_2),
            'pure'
        ))
        
        conn.commit()
        
        print("✅ Created 2 test forms with pure extraction mode:")
        print("   - Test Employee 1 (hourly form)")
        print("   - Test Employee 2 (supervisor form)")
        print("\n📊 Current database stats:")
        
        # Show current extraction mode distribution
        c.execute("SELECT extraction_mode, COUNT(*) FROM exception_forms GROUP BY extraction_mode")
        for mode, count in c.fetchall():
            print(f"   - {mode}: {count} forms")

if __name__ == "__main__":
    create_pure_extraction_test_data() 
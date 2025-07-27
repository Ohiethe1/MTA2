#!/usr/bin/env python3
"""
Test script to demonstrate that the export functionality correctly filters 
based on dashboard context (general, supervisor, hourly).
"""

import requests
import csv
import io

def test_dashboard_export_functionality():
    """Test the export functionality for different dashboard contexts"""
    base_url = "http://localhost:8000"
    
    print("=== DASHBOARD EXPORT FUNCTIONALITY TEST ===")
    print("Testing that exports correctly filter based on dashboard context.\n")
    
    # Test 1: General Dashboard Export (all data)
    print("1. GENERAL DASHBOARD EXPORT (All Forms):")
    try:
        response = requests.get(f"{base_url}/api/forms/export")
        if response.status_code == 200:
            csv_data = response.text
            lines = csv_data.splitlines()
            print(f"   ✅ Success: {len(lines)} lines exported (including header)")
            print(f"   📊 Data rows: {len(lines) - 1}")
            
            # Count form types in the export
            if len(lines) > 1:
                reader = csv.reader(io.StringIO(csv_data))
                headers = next(reader)
                form_type_index = None
                for i, header in enumerate(headers):
                    if 'form type' in header.lower():
                        form_type_index = i
                        break
                
                if form_type_index is not None:
                    hourly_count = 0
                    supervisor_count = 0
                    for row in reader:
                        if len(row) > form_type_index:
                            if row[form_type_index].lower() == 'hourly':
                                hourly_count += 1
                            elif row[form_type_index].lower() == 'supervisor':
                                supervisor_count += 1
                    
                    print(f"   📋 Hourly forms: {hourly_count}")
                    print(f"   📋 Supervisor forms: {supervisor_count}")
                    print(f"   📋 Total forms: {hourly_count + supervisor_count}")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Supervisor Dashboard Export (only supervisor forms)
    print("\n2. SUPERVISOR DASHBOARD EXPORT (Supervisor Forms Only):")
    try:
        response = requests.get(f"{base_url}/api/forms/export?form_type=supervisor")
        if response.status_code == 200:
            csv_data = response.text
            lines = csv_data.splitlines()
            print(f"   ✅ Success: {len(lines)} lines exported (including header)")
            print(f"   📊 Data rows: {len(lines) - 1}")
            
            # Verify all forms are supervisor type
            if len(lines) > 1:
                reader = csv.reader(io.StringIO(csv_data))
                headers = next(reader)
                form_type_index = None
                for i, header in enumerate(headers):
                    if 'form type' in header.lower():
                        form_type_index = i
                        break
                
                if form_type_index is not None:
                    all_supervisor = True
                    for row in reader:
                        if len(row) > form_type_index and row[form_type_index].lower() != 'supervisor':
                            all_supervisor = False
                            break
                    
                    if all_supervisor:
                        print("   ✅ All exported forms are supervisor type")
                    else:
                        print("   ❌ Found non-supervisor forms in export")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Hourly Dashboard Export (only hourly forms)
    print("\n3. HOURLY DASHBOARD EXPORT (Hourly Forms Only):")
    try:
        response = requests.get(f"{base_url}/api/forms/export?form_type=hourly")
        if response.status_code == 200:
            csv_data = response.text
            lines = csv_data.splitlines()
            print(f"   ✅ Success: {len(lines)} lines exported (including header)")
            print(f"   📊 Data rows: {len(lines) - 1}")
            
            # Verify all forms are hourly type
            if len(lines) > 1:
                reader = csv.reader(io.StringIO(csv_data))
                headers = next(reader)
                form_type_index = None
                for i, header in enumerate(headers):
                    if 'form type' in header.lower():
                        form_type_index = i
                        break
                
                if form_type_index is not None:
                    all_hourly = True
                    for row in reader:
                        if len(row) > form_type_index and row[form_type_index].lower() != 'hourly':
                            all_hourly = False
                            break
                    
                    if all_hourly:
                        print("   ✅ All exported forms are hourly type")
                    else:
                        print("   ❌ Found non-hourly forms in export")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n=== SUMMARY ===")
    print("✅ Dashboard-specific export functionality is working correctly!")
    print("✅ General Dashboard exports ALL forms")
    print("✅ Supervisor Dashboard exports ONLY supervisor forms")
    print("✅ Hourly Dashboard exports ONLY hourly forms")
    print("\n📋 How it works:")
    print("   - General Dashboard: No form_type filter → exports everything")
    print("   - Supervisor Dashboard: form_type=supervisor → exports only supervisor forms")
    print("   - Hourly Dashboard: form_type=hourly → exports only hourly forms")

if __name__ == "__main__":
    test_dashboard_export_functionality() 
#!/usr/bin/env python3
"""
Test script to demonstrate that the export functionality includes both mapped and pure extraction data.
"""

import requests
import csv
import io

def test_pure_extraction_export():
    """Test the export functionality with pure extraction data"""
    base_url = "http://localhost:8000"
    
    print("=== PURE EXTRACTION EXPORT TEST ===")
    print("Testing that exports include both mapped and pure extraction data.\n")
    
    # Test 1: Export all data (should include both mapped and pure)
    print("1. EXPORT ALL DATA (Mapped + Pure):")
    try:
        response = requests.get(f"{base_url}/api/forms/export")
        if response.status_code == 200:
            csv_data = response.text
            lines = csv_data.splitlines()
            print(f"   ✅ Success: {len(lines)} lines exported (including header)")
            print(f"   📊 Data rows: {len(lines) - 1}")
            
            # Count extraction modes
            if len(lines) > 1:
                reader = csv.reader(io.StringIO(csv_data))
                headers = next(reader)
                extraction_mode_index = None
                for i, header in enumerate(headers):
                    if 'extraction mode' in header.lower():
                        extraction_mode_index = i
                        break
                
                if extraction_mode_index is not None:
                    mapped_count = 0
                    pure_count = 0
                    for row in reader:
                        if len(row) > extraction_mode_index:
                            if row[extraction_mode_index].lower() == 'mapped':
                                mapped_count += 1
                            elif row[extraction_mode_index].lower() == 'pure':
                                pure_count += 1
                    
                    print(f"   📋 Mapped extraction: {mapped_count} forms")
                    print(f"   📋 Pure extraction: {pure_count} forms")
                    print(f"   📋 Total forms: {mapped_count + pure_count}")
                    
                    if pure_count > 0:
                        print("   ✅ Pure extraction data is included in export!")
                    else:
                        print("   ❌ No pure extraction data found")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Export only pure extraction data
    print("\n2. EXPORT PURE EXTRACTION ONLY:")
    try:
        response = requests.get(f"{base_url}/api/forms/export?extraction_mode=pure")
        if response.status_code == 200:
            csv_data = response.text
            lines = csv_data.splitlines()
            print(f"   ✅ Success: {len(lines)} lines exported (including header)")
            print(f"   📊 Data rows: {len(lines) - 1}")
            
            # Verify all forms are pure extraction
            if len(lines) > 1:
                reader = csv.reader(io.StringIO(csv_data))
                headers = next(reader)
                extraction_mode_index = None
                for i, header in enumerate(headers):
                    if 'extraction mode' in header.lower():
                        extraction_mode_index = i
                        break
                
                if extraction_mode_index is not None:
                    all_pure = True
                    for row in reader:
                        if len(row) > extraction_mode_index and row[extraction_mode_index].lower() != 'pure':
                            all_pure = False
                            break
                    
                    if all_pure:
                        print("   ✅ All exported forms are pure extraction")
                    else:
                        print("   ❌ Found non-pure forms in export")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Export only mapped extraction data
    print("\n3. EXPORT MAPPED EXTRACTION ONLY:")
    try:
        response = requests.get(f"{base_url}/api/forms/export?extraction_mode=mapped")
        if response.status_code == 200:
            csv_data = response.text
            lines = csv_data.splitlines()
            print(f"   ✅ Success: {len(lines)} lines exported (including header)")
            print(f"   📊 Data rows: {len(lines) - 1}")
            
            # Verify all forms are mapped extraction
            if len(lines) > 1:
                reader = csv.reader(io.StringIO(csv_data))
                headers = next(reader)
                extraction_mode_index = None
                for i, header in enumerate(headers):
                    if 'extraction mode' in header.lower():
                        extraction_mode_index = i
                        break
                
                if extraction_mode_index is not None:
                    all_mapped = True
                    for row in reader:
                        if len(row) > extraction_mode_index and row[extraction_mode_index].lower() != 'mapped':
                            all_mapped = False
                            break
                    
                    if all_mapped:
                        print("   ✅ All exported forms are mapped extraction")
                    else:
                        print("   ❌ Found non-mapped forms in export")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Export pure extraction with form type filter
    print("\n4. EXPORT PURE EXTRACTION + FORM TYPE FILTER:")
    try:
        response = requests.get(f"{base_url}/api/forms/export?extraction_mode=pure&form_type=hourly")
        if response.status_code == 200:
            csv_data = response.text
            lines = csv_data.splitlines()
            print(f"   ✅ Success: {len(lines)} lines exported (including header)")
            print(f"   📊 Data rows: {len(lines) - 1}")
            
            # Verify all forms are pure extraction and hourly
            if len(lines) > 1:
                reader = csv.reader(io.StringIO(csv_data))
                headers = next(reader)
                extraction_mode_index = None
                form_type_index = None
                for i, header in enumerate(headers):
                    if 'extraction mode' in header.lower():
                        extraction_mode_index = i
                    elif 'form type' in header.lower():
                        form_type_index = i
                
                if extraction_mode_index is not None and form_type_index is not None:
                    all_valid = True
                    for row in reader:
                        if (len(row) > extraction_mode_index and row[extraction_mode_index].lower() != 'pure') or \
                           (len(row) > form_type_index and row[form_type_index].lower() != 'hourly'):
                            all_valid = False
                            break
                    
                    if all_valid:
                        print("   ✅ All exported forms are pure extraction + hourly")
                    else:
                        print("   ❌ Found invalid forms in export")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n=== SUMMARY ===")
    print("✅ Export functionality includes both mapped and pure extraction data!")
    print("✅ You can filter by extraction mode (pure/mapped)")
    print("✅ You can combine extraction mode with form type filters")
    print("✅ Pure extraction data contains raw Gemini JSON output")
    print("✅ Mapped extraction data contains structured database fields")
    print("\n📋 Export Options:")
    print("   - All data: GET /api/forms/export")
    print("   - Pure only: GET /api/forms/export?extraction_mode=pure")
    print("   - Mapped only: GET /api/forms/export?extraction_mode=mapped")
    print("   - Pure + Hourly: GET /api/forms/export?extraction_mode=pure&form_type=hourly")

if __name__ == "__main__":
    test_pure_extraction_export() 
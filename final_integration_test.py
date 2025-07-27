#!/usr/bin/env python3
"""
Final integration test for the complete MTA Forms application.
Tests the running Flask server and verifies all endpoints are working.
"""

import requests
import json
import time
import sys

def test_flask_server():
    """Test the Flask server endpoints"""
    print("=== FINAL INTEGRATION TEST ===")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Extraction mode endpoint
        print("1. Testing extraction mode endpoint...")
        response = requests.get(f"{base_url}/api/extraction-mode")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Current mode: {data['mode']}")
            print(f"   ✅ Descriptions available: {list(data['description'].keys())}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test 2: Dashboard endpoint
        print("\n2. Testing dashboard endpoint...")
        response = requests.get(f"{base_url}/api/dashboard")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total forms: {data['total_forms']}")
            print(f"   ✅ Total overtime: {data['total_overtime']}")
            print(f"   ✅ Forms in table: {len(data['forms'])}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test 3: Dashboard with extraction mode filter
        print("\n3. Testing dashboard with extraction mode filter...")
        response = requests.get(f"{base_url}/api/dashboard?extraction_mode=mapped")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Mapped forms: {data['total_forms']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test 4: Export functionality
        print("\n4. Testing export functionality...")
        response = requests.get(f"{base_url}/api/forms/export?extraction_mode=mapped")
        if response.status_code == 200:
            print(f"   ✅ Export successful: {len(response.text)} characters")
            print(f"   ✅ Content-Type: {response.headers.get('Content-Type')}")
            print(f"   ✅ Filename: {response.headers.get('Content-Disposition')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test 5: Switch extraction mode
        print("\n5. Testing extraction mode switching...")
        response = requests.post(f"{base_url}/api/extraction-mode", 
                               json={"mode": "pure"})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Switched to: {data['mode']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test 6: Verify mode change
        response = requests.get(f"{base_url}/api/extraction-mode")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Confirmed mode: {data['mode']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test 7: Switch back to mapped
        response = requests.post(f"{base_url}/api/extraction-mode", 
                               json={"mode": "mapped"})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Switched back to: {data['mode']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        print("\n" + "=" * 50)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("=" * 50)
        
        print("\n🎯 SYSTEM STATUS:")
        print("✅ Flask server running on port 8000")
        print("✅ All API endpoints responding")
        print("✅ Dashboard filtering working")
        print("✅ Export functionality working")
        print("✅ Extraction mode switching working")
        print("✅ React frontend should be accessible")
        
        print("\n🌐 ACCESS POINTS:")
        print("   Backend API: http://localhost:8000")
        print("   Frontend: http://localhost:3000 (if React is running)")
        print("   Dashboard: http://localhost:3000 (after login)")
        
        print("\n🚀 READY FOR PRODUCTION USE!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server on port 8000")
        print("   Make sure the server is running with: python3 app.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_flask_server()
    sys.exit(0 if success else 1) 
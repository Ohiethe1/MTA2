#!/usr/bin/env python3
"""
Test script for the registration system
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    # Test 1: Valid registration
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=test_user)
    print(f"Registration response: {response.status_code}")
    if response.status_code == 201:
        print("✅ Registration successful")
        return test_user
    else:
        print(f"❌ Registration failed: {response.text}")
        return None

def test_login(username, password):
    """Test user login"""
    print(f"\nTesting login for user: {username}")
    
    response = requests.post(f"{BASE_URL}/api/login", json={
        "username": username,
        "password": password
    })
    
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful")
        return True
    else:
        print(f"❌ Login failed: {response.text}")
        return False

def test_get_users():
    """Test getting all users"""
    print("\nTesting get users...")
    
    response = requests.get(f"{BASE_URL}/api/users")
    print(f"Get users response: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()["users"]
        print(f"✅ Found {len(users)} users")
        for user in users:
            print(f"  - ID: {user['id']}, Username: {user['username']}")
        return users
    else:
        print(f"❌ Get users failed: {response.text}")
        return []

def test_duplicate_registration(username):
    """Test duplicate registration"""
    print(f"\nTesting duplicate registration for: {username}")
    
    response = requests.post(f"{BASE_URL}/api/register", json={
        "username": username,
        "password": "differentpassword"
    })
    
    print(f"Duplicate registration response: {response.status_code}")
    if response.status_code == 409:
        print("✅ Correctly rejected duplicate username")
        return True
    else:
        print(f"❌ Unexpected response: {response.text}")
        return False

def main():
    print("🧪 Testing Registration System")
    print("=" * 40)
    
    # Test registration
    test_user = test_registration()
    if not test_user:
        print("❌ Registration test failed, stopping")
        return
    
    # Test login
    if not test_login(test_user["username"], test_user["password"]):
        print("❌ Login test failed")
        return
    
    # Test get users
    users = test_get_users()
    if not users:
        print("❌ Get users test failed")
        return
    
    # Test duplicate registration
    if not test_duplicate_registration(test_user["username"]):
        print("❌ Duplicate registration test failed")
        return
    
    print("\n🎉 All tests passed! Registration system is working correctly.")

if __name__ == "__main__":
    main() 
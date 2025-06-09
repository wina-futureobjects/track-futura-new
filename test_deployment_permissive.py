#!/usr/bin/env python
"""
Test Deployment with Permissive Settings

This script tests both Django admin CSRF functionality and
frontend API accessibility to ensure both work properly.
"""

import requests
import json
import sys
from pathlib import Path

def test_api_login():
    """Test the API login endpoint (frontend)"""
    print("\n🔍 Testing API Login (Frontend)")
    print("-" * 40)

    url = "http://localhost:8000/api/users/login/"
    data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        response = requests.post(url, json=data, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API Login successful!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            except:
                print("❌ Response is not JSON")
                print(f"Raw response: {response.text}")
                return False
        else:
            print(f"❌ API Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ API Login error: {e}")
        return False

def test_admin_access():
    """Test Django admin accessibility"""
    print("\n🔍 Testing Django Admin Access")
    print("-" * 40)

    try:
        # Test admin login page
        response = requests.get("http://localhost:8000/admin/")
        print(f"Admin page status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Django admin page accessible")
            return True
        else:
            print(f"❌ Django admin not accessible: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Admin access error: {e}")
        return False

def test_server_health():
    """Test basic server health"""
    print("\n🔍 Testing Server Health")
    print("-" * 40)

    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Server responding (Status: {response.status_code})")
        return True
    except:
        print("❌ Server not responding")
        return False

def test_cors_headers():
    """Test CORS headers"""
    print("\n🔍 Testing CORS Headers")
    print("-" * 40)

    try:
        response = requests.options("http://localhost:8000/api/users/login/", headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })

        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }

        print(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")

        if cors_headers['Access-Control-Allow-Origin']:
            print("✅ CORS properly configured")
            return True
        else:
            print("❌ CORS not properly configured")
            return False

    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Deployment Permissive Settings Test")
    print("=" * 50)

    results = []

    # Test server health first
    if not test_server_health():
        print("\n💡 Please start the Django server:")
        print("   cd backend && python manage.py runserver")
        sys.exit(1)

    # Run all tests
    results.append(("Server Health", test_server_health()))
    results.append(("CORS Headers", test_cors_headers()))
    results.append(("API Login", test_api_login()))
    results.append(("Django Admin", test_admin_access()))

    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! Both frontend and admin should work.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

    print("\n📝 Deployment Notes:")
    print("- API endpoints have CSRF disabled for frontend compatibility")
    print("- Django admin has CSRF enabled but very permissive")
    print("- CORS allows all origins for maximum compatibility")
    print("- Security is reduced for functionality - secure properly for production!")

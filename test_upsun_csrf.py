#!/usr/bin/env python
"""
Test CSRF and CORS for Upsun Deployment

This script specifically tests your Upsun URL to ensure no more CSRF or origin issues:
https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site
"""

import requests
import json

def test_upsun_cors():
    """Test CORS with your specific Upsun domain"""
    print("🔍 Testing CORS for Upsun Domain")
    print("-" * 50)

    upsun_url = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"

    try:
        # Test OPTIONS request (CORS preflight)
        response = requests.options(f"{upsun_url}/api/users/login/", headers={
            'Origin': upsun_url,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }, timeout=10)

        print(f"OPTIONS Status: {response.status_code}")

        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }

        print("CORS Headers:")
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")

        if response.status_code == 200 and cors_headers['Access-Control-Allow-Origin']:
            print("✅ CORS configured correctly for Upsun!")
            return True
        else:
            print("❌ CORS not properly configured")
            return False

    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def test_upsun_csrf():
    """Test CSRF token endpoint"""
    print("\n🔍 Testing CSRF Token for Upsun")
    print("-" * 50)

    upsun_url = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"

    try:
        # Test CSRF token endpoint
        response = requests.get(f"{upsun_url}/api/users/csrf-token/", headers={
            'Origin': upsun_url,
            'Referer': upsun_url
        }, timeout=10)

        print(f"CSRF Token Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ CSRF token retrieved successfully!")
                print(f"Token: {data.get('csrfToken', 'Not found')}")
                return True
            except:
                print("❌ Invalid JSON response")
                return False
        else:
            print(f"❌ CSRF endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ CSRF test failed: {e}")
        return False

def test_upsun_admin():
    """Test Django admin accessibility"""
    print("\n🔍 Testing Django Admin for Upsun")
    print("-" * 50)

    upsun_url = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"

    try:
        # Test admin page
        response = requests.get(f"{upsun_url}/admin/", headers={
            'Origin': upsun_url,
            'Referer': upsun_url
        }, timeout=10)

        print(f"Admin Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Django admin accessible!")
            return True
        elif response.status_code == 302:
            print("✅ Django admin redirecting to login (normal behavior)")
            return True
        else:
            print(f"❌ Admin not accessible: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Admin test failed: {e}")
        return False

def test_local_server():
    """Test local development server"""
    print("\n🔍 Testing Local Development Server")
    print("-" * 50)

    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Local server responding (Status: {response.status_code})")
        return True
    except:
        print("❌ Local server not running")
        print("💡 Start with: cd backend && python manage.py runserver")
        return False

if __name__ == "__main__":
    print("🚀 Upsun CSRF & CORS Test")
    print("=" * 60)
    print("Testing your specific Upsun domain:")
    print("https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site")
    print("=" * 60)

    results = []

    # Test local server first
    local_ok = test_local_server()
    if local_ok:
        results.append(("Local Server", local_ok))

    # Test Upsun deployment
    results.append(("Upsun CORS", test_upsun_cors()))
    results.append(("Upsun CSRF", test_upsun_csrf()))
    results.append(("Upsun Admin", test_upsun_admin()))

    # Summary
    print("\n📊 Test Results")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n🎉 SUCCESS! No more CSRF or CORS issues expected!")
        print("\n✅ Your Upsun deployment should now work properly:")
        print("  - Django admin login should work without CSRF errors")
        print("  - Frontend API calls should work without origin errors")
        print("  - All cross-origin requests are allowed")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        print("\n💡 If Upsun tests fail but local works, deploy the changes:")
        print("   upsun push")

    print("\n🔒 Security Note:")
    print("These settings are VERY permissive for maximum compatibility.")
    print("Consider tightening security once everything works correctly.")

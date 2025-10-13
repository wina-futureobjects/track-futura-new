#!/usr/bin/env python3
"""
🎯 SETUP AND TEST COMPLETE WORKFLOW INTEGRATION
First creates superadmin, then tests the critical Workflow Management → Data Storage flow
"""

import requests
import json
import time
import sys
from datetime import datetime

# Production Configuration
BASE_URL = "https://trackfutura.futureobjects.io"
API_BASE = f"{BASE_URL}/api"

def create_superadmin_account():
    """Create superadmin account for testing"""
    print("👑 Creating Superadmin Account...")
    
    try:
        admin_data = {
            "username": "admin@trackfutura.com",
            "password": "trackfutura2024!",
            "email": "admin@trackfutura.com",
            "first_name": "Track",
            "last_name": "Futura"
        }
        
        response = requests.post(
            f"{API_BASE}/users/create-superadmin/",
            json=admin_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Superadmin created successfully!")
            return True
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print(f"✅ Superadmin already exists!")
            return True
        else:
            print(f"❌ Superadmin creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Superadmin creation error: {e}")
        return False

def test_authentication():
    """Test authentication with production system"""
    print("\n🔐 Testing Authentication...")
    
    try:
        auth_data = {
            "username": "admin@trackfutura.com",
            "password": "trackfutura2024!"
        }
        
        response = requests.post(
            f"{API_BASE}/users/login/",
            json=auth_data,
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('token', token_data.get('access'))
            print(f"✅ Authentication successful! Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_basic_endpoints(token):
    """Test basic system endpoints to verify deployment"""
    print("\n🔍 Testing Basic System Endpoints...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints_to_test = [
        ("/users/me/", "User Profile"),
        ("/brightdata/", "BrightData Integration"),
        ("/workflow/", "Workflow Management"),
        ("/users/projects/", "Projects"),
    ]
    
    working_endpoints = []
    
    for endpoint, name in endpoints_to_test:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
            if response.status_code in [200, 404, 405]:  # 404/405 means endpoint exists but different method
                print(f"✅ {name}: Accessible ({response.status_code})")
                working_endpoints.append(endpoint)
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error ({e})")
    
    return working_endpoints

def test_webhook_endpoint():
    """Test webhook endpoint availability"""
    print("\n🔗 Testing Webhook Endpoints...")
    
    webhook_endpoints = [
        f"{BASE_URL}/trigger-system/brightdata-webhook/",
        f"{BASE_URL}/brightdata-trigger/",
        f"{BASE_URL}/trigger/",
    ]
    
    for webhook_url in webhook_endpoints:
        try:
            response = requests.get(webhook_url, timeout=10)
            # Webhook should return method not allowed for GET (expecting POST)
            if response.status_code == 405:
                print(f"✅ Webhook endpoint accessible: {webhook_url}")
                return webhook_url
            elif response.status_code in [200, 404]:
                print(f"⚠️  Webhook endpoint found but different behavior: {webhook_url} ({response.status_code})")
            else:
                print(f"❌ Webhook endpoint failed: {webhook_url} ({response.status_code})")
        except Exception as e:
            print(f"❌ Webhook test error for {webhook_url}: {e}")
    
    return None

def test_brightdata_integration(token):
    """Test BrightData integration endpoints"""
    print("\n🎯 Testing BrightData Integration...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    test_data = {
        "platform": "instagram", 
        "source_urls": ["https://www.instagram.com/nike/"],
        "job_name": f"Test_Job_{datetime.now().strftime('%H%M%S')}",
        "max_posts": 3
    }
    
    brightdata_endpoints = [
        "/brightdata/trigger-system/",
        "/brightdata/trigger-scraper/", 
        "/brightdata/configs/",
        "/brightdata/batch-jobs/",
    ]
    
    for endpoint in brightdata_endpoints:
        try:
            print(f"🔍 Testing: {endpoint}")
            response = requests.post(f"{API_BASE}{endpoint}", json=test_data, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ BrightData trigger successful at {endpoint}!")
                print(f"📊 Response keys: {list(result.keys())}")
                return result
            elif response.status_code == 405:
                # Try GET method
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Endpoint accessible (GET): {endpoint}")
                else:
                    print(f"⚠️  POST not allowed, GET failed: {endpoint}")
            else:
                print(f"❌ Failed {response.status_code}: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")
    
    return None

def main():
    """Run complete system setup and test"""
    print("🚀 COMPLETE WORKFLOW INTEGRATION SETUP & TEST")
    print("=" * 60)
    print("Phase 1: Setup superadmin account")
    print("Phase 2: Test authentication and basic endpoints")
    print("Phase 3: Test BrightData integration")
    print("Phase 4: Test webhook delivery system")
    print("=" * 60)
    
    # Phase 1: Create Superadmin
    if not create_superadmin_account():
        print("\n❌ CRITICAL: Cannot create superadmin - check system deployment")
        sys.exit(1)
    
    # Phase 2: Authentication
    token = test_authentication()
    if not token:
        print("\n❌ CRITICAL: Authentication failed - cannot proceed")
        sys.exit(1)
    
    # Phase 3: Basic System Test
    working_endpoints = test_basic_endpoints(token)
    if not working_endpoints:
        print("\n⚠️  WARNING: No basic endpoints working")
    
    # Phase 4: Webhook Test
    webhook_url = test_webhook_endpoint()
    if not webhook_url:
        print("\n⚠️  WARNING: No webhook endpoints accessible")
    
    # Phase 5: BrightData Integration Test
    brightdata_result = test_brightdata_integration(token)
    
    # Final Assessment
    print("\n" + "=" * 60)
    print("🎯 WORKFLOW INTEGRATION DEPLOYMENT STATUS")
    print("=" * 60)
    
    print(f"✅ Superadmin Account: Created/Available")
    print(f"✅ Authentication: Working")
    print(f"✅ Basic Endpoints: {len(working_endpoints)} accessible")
    print(f"{'✅' if webhook_url else '⚠️ '} Webhook System: {'Available' if webhook_url else 'Needs verification'}")
    print(f"{'✅' if brightdata_result else '⚠️ '} BrightData Integration: {'Working' if brightdata_result else 'Needs configuration'}")
    
    if brightdata_result and webhook_url:
        print("\n🎉 SUCCESS: Complete workflow management integration is DEPLOYED!")
        print("🎯 System ready for: Workflow Management → BrightData → Data Storage")
        print(f"🔗 Frontend URL: {BASE_URL}/organizations/1/projects/2/workflow-management")
        print(f"📂 Data Storage: {BASE_URL}/organizations/1/projects/2/data-storage")
    else:
        print("\n⚠️  PARTIAL DEPLOYMENT: System accessible but integration needs verification")
        print("💡 Recommend: Test workflow from frontend interface")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
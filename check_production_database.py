#!/usr/bin/env python3
"""
Production Database Status Check
Check what projects and users exist in production
"""

import requests
import json

def check_production_database():
    """Check the production database status"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test endpoints to check database state
    endpoints = [
        "/api/users/",  # Check users
        "/api/brightdata/configs/",  # Check if we can access with auth
    ]
    
    print("📊 Production Database Status Check")
    print("=" * 50)
    
    for endpoint_path in endpoints:
        url = base_url + endpoint_path
        print(f"\n🔍 Testing: {endpoint_path}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Count: {len(data)} items")
                        if data:
                            print(f"   Sample: {json.dumps(data[0], indent=6)}")
                    else:
                        print(f"   Data: {json.dumps(data, indent=6)}")
                except:
                    print(f"   Raw: {response.text[:200]}...")
            elif response.status_code == 401:
                print("   ✅ Endpoint exists (requires auth)")
            elif response.status_code == 404:
                print("   ❌ Endpoint not found")
            else:
                print(f"   ⚠️ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_project_creation():
    """Test creating a project via Web Unlocker"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    endpoint = f"{base_url}/api/brightdata/web-unlocker/scrape/"
    
    # Use specific data that should trigger project creation
    test_data = {
        "url": "https://httpbin.org/ip",  # Simple test URL
        "scraper_name": "Project Creation Test"
    }
    
    print("\n🏗️ Testing Automatic Project Creation")
    print("-" * 50)
    print(f"URL: {endpoint}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for project creation
        )
        
        print(f"✅ Status: {response.status_code}")
        
        try:
            data = response.json()
            print(f"📄 Response:")
            print(json.dumps(data, indent=2))
            
            if response.status_code == 200 and data.get('success'):
                print("🎉 SUCCESS: Project creation and Web Unlocker working!")
                return True
            elif 'project_id' in str(data) or 'foreign key' in str(data):
                print("🔧 Foreign key issue - project creation needs verification")
                return False
            else:
                print("⚠️ Other issue detected")
                return False
                
        except:
            print(f"📝 Raw Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_production_database()
    success = test_project_creation()
    
    if success:
        print("\n🎉 Web Unlocker is fully operational!")
    else:
        print("\n🔧 Web Unlocker needs project creation fix")
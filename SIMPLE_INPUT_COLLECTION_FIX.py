#!/usr/bin/env python3
"""
SIMPLE INPUT COLLECTION FIX
Direct approach to create InputCollection via production API
"""

import requests
import json

# Production endpoints
BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
API_BASE = f"{BASE_URL}/api"

def test_workflow_endpoints():
    """Test all workflow endpoints"""
    print("🔍 Testing Workflow API Endpoints...")
    
    endpoints = [
        "/workflow/platforms/",
        "/workflow/platform-services/", 
        "/workflow/input-collections/",
        "/track-accounts/uploads/"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{API_BASE}{endpoint}"
            response = requests.get(url, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    print(f"   Count: {len(data['results'])}")
                    if data['results']:
                        print(f"   Sample: {data['results'][0]}")
                elif isinstance(data, list):
                    print(f"   Count: {len(data)}")
                    if data:
                        print(f"   Sample: {data[0]}")
                else:
                    print(f"   Data: {data}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")
        print()

def create_input_collection():
    """Create InputCollection via POST"""
    print("🚀 Creating InputCollection...")
    
    # First get track uploads
    try:
        uploads_response = requests.get(f"{API_BASE}/track-accounts/uploads/")
        if uploads_response.status_code != 200:
            print(f"❌ Failed to get uploads: {uploads_response.status_code}")
            return
            
        uploads = uploads_response.json()
        if 'results' in uploads:
            uploads = uploads['results']
            
        if not uploads:
            print("❌ No track uploads found")
            return
            
        print(f"✅ Found {len(uploads)} track uploads")
        
        # Find Nike IG upload
        nike_upload = None
        for upload in uploads:
            if 'nike' in str(upload).lower() and 'instagram' in str(upload).lower():
                nike_upload = upload
                break
                
        if not nike_upload:
            nike_upload = uploads[0]  # Use first available
            
        print(f"📝 Using upload: {nike_upload}")
        
        # Create InputCollection
        input_collection_data = {
            "name": f"Nike Instagram Collection",
            "description": "Nike Instagram tracking for workflow",
            "track_account_upload": nike_upload['id'],
            "platform": 1,  # Instagram platform ID
            "is_active": True
        }
        
        response = requests.post(
            f"{API_BASE}/workflow/input-collections/",
            json=input_collection_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print("✅ InputCollection created successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to create InputCollection: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating InputCollection: {str(e)}")

def main():
    print("=" * 60)
    print("🎯 SIMPLE INPUT COLLECTION FIX")
    print("=" * 60)
    
    test_workflow_endpoints()
    create_input_collection()
    
    print("\n" + "=" * 60)
    print("🏁 NEXT STEPS:")
    print("1. Refresh workflow management page")
    print("2. Check if track sources appear")
    print("3. Test scraping functionality")
    print("=" * 60)

if __name__ == "__main__":
    main()
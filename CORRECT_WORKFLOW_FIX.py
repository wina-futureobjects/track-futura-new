#!/usr/bin/env python3
"""
CORRECT WORKFLOW FIX
Using the actual available endpoints
"""

import requests
import json

# Production endpoints
BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
API_BASE = f"{BASE_URL}/api"

def test_available_endpoints():
    """Test all available endpoints from the URL patterns"""
    print("🔍 Testing Available API Endpoints...")
    
    endpoints = [
        "/workflow/platforms/",
        "/workflow/platform-services/", 
        "/workflow/input-collections/",
        "/track-accounts/sources/",    # This exists based on URL patterns
        "/track-accounts/accounts/",   # This exists
        "/track-accounts/",            # Root endpoint
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
                        item = data['results'][0]
                        # Show relevant fields
                        keys = ['id', 'name', 'username', 'platform', 'account_name', 'title']
                        filtered = {k: v for k, v in item.items() if k in keys}
                        print(f"   Sample: {filtered}")
                elif isinstance(data, list):
                    print(f"   Count: {len(data)}")
                    if data:
                        item = data[0]
                        keys = ['id', 'name', 'username', 'platform', 'account_name', 'title']
                        filtered = {k: v for k, v in item.items() if k in keys}
                        print(f"   Sample: {filtered}")
                else:
                    print(f"   Data: {data}")
            else:
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")
        print()

def create_input_collection_from_sources():
    """Create InputCollection from track sources"""
    print("🚀 Creating InputCollection from Track Sources...")
    
    try:
        # Get track sources (these should be the Nike IG accounts)
        sources_response = requests.get(f"{API_BASE}/track-accounts/sources/")
        if sources_response.status_code != 200:
            print(f"❌ Failed to get sources: {sources_response.status_code}")
            print(f"Error: {sources_response.text}")
            return
            
        sources_data = sources_response.json()
        if 'results' in sources_data:
            sources = sources_data['results']
        else:
            sources = sources_data
            
        if not sources:
            print("❌ No track sources found")
            return
            
        print(f"✅ Found {len(sources)} track sources")
        
        # Find Nike IG source
        nike_source = None
        for source in sources:
            source_str = str(source).lower()
            if ('nike' in source_str and 'instagram' in source_str) or \
               ('nike' in source_str and 'ig' in source_str):
                nike_source = source
                break
                
        if not nike_source:
            # Use first available source
            nike_source = sources[0]
            
        print(f"📝 Using source: {nike_source}")
        
        # Now create InputCollection
        input_collection_data = {
            "name": f"Nike Instagram Workflow Collection",
            "description": "Nike Instagram tracking for BrightData workflow",
            "platform": 1,  # Instagram platform ID
            "is_active": True,
            "source_id": nike_source.get('id'),
            "metadata": {
                "track_source": nike_source,
                "created_for": "workflow_integration",
                "brightdata_ready": True
            }
        }
        
        print(f"📤 Creating InputCollection with data: {input_collection_data}")
        
        response = requests.post(
            f"{API_BASE}/workflow/input-collections/",
            json=input_collection_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ InputCollection created successfully!")
            result = response.json()
            print(f"Created: {result}")
            
            # Verify it was created
            verify_response = requests.get(f"{API_BASE}/workflow/input-collections/")
            if verify_response.status_code == 200:
                collections = verify_response.json()
                if 'results' in collections:
                    collections = collections['results']
                print(f"✅ Verification: {len(collections)} input collections now exist")
                
        else:
            print(f"❌ Failed to create InputCollection: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating InputCollection: {str(e)}")

def test_workflow_after_fix():
    """Test workflow endpoints after creating InputCollection"""
    print("🧪 Testing Workflow After Fix...")
    
    try:
        response = requests.get(f"{API_BASE}/workflow/input-collections/")
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                collections = data['results']
            else:
                collections = data
                
            print(f"✅ InputCollections: {len(collections)}")
            for collection in collections:
                print(f"   - {collection.get('name', 'Unnamed')} (ID: {collection.get('id')})")
                
        # Test available platforms
        platforms_response = requests.get(f"{API_BASE}/workflow/platforms/")
        if platforms_response.status_code == 200:
            platforms_data = platforms_response.json()
            if 'results' in platforms_data:
                platforms = platforms_data['results']
            else:
                platforms = platforms_data
            print(f"✅ Platforms: {len(platforms)}")
            
        # Test platform services
        services_response = requests.get(f"{API_BASE}/workflow/platform-services/")
        if services_response.status_code == 200:
            services_data = services_response.json()
            if 'results' in services_data:
                services = services_data['results']
            else:
                services = services_data
            print(f"✅ Platform Services: {len(services)}")
            
    except Exception as e:
        print(f"❌ Error testing workflow: {str(e)}")

def main():
    print("=" * 60)
    print("🎯 CORRECT WORKFLOW FIX")
    print("=" * 60)
    
    test_available_endpoints()
    create_input_collection_from_sources()
    test_workflow_after_fix()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL STEPS:")
    print("1. Go to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
    print("2. Refresh the page")
    print("3. You should now see track sources available")
    print("4. Try creating a scraping run")
    print("=" * 60)

if __name__ == "__main__":
    main()
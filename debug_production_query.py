#!/usr/bin/env python
"""
DEBUG: Test the exact query used by the trigger service
"""

import requests
import json

def debug_production_query():
    """Debug the exact query issue on production"""
    
    print("🔍 DEBUGGING PRODUCTION QUERY")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test 1: Check all sources in folder 1
    print("📊 TEST 1: All sources in folder 1")
    try:
        response = requests.get(f"{base_url}/api/track-accounts/sources/?folder=1", timeout=30)
        if response.ok:
            data = response.json()
            sources = data.get('results', data) if isinstance(data, dict) else data
            print(f"✅ Found {len(sources)} sources in folder 1")
            for source in sources:
                print(f"  📋 ID {source.get('id')}: {source.get('name')} ({source.get('platform')})")
                print(f"     Folder: {source.get('folder')}, Project: {source.get('project')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"💥 Error: {e}")
    
    # Test 2: Check sources with project filter (the query the service uses)
    print("\n📊 TEST 2: Sources with folder=1 AND project=1 filter")
    try:
        response = requests.get(f"{base_url}/api/track-accounts/sources/?folder=1&project=1", timeout=30)
        if response.ok:
            data = response.json()
            sources = data.get('results', data) if isinstance(data, dict) else data
            print(f"✅ Found {len(sources)} sources with both filters")
            for source in sources:
                print(f"  📋 ID {source.get('id')}: {source.get('name')} ({source.get('platform')})")
                print(f"     Folder: {source.get('folder')}, Project: {source.get('project')}")
                print(f"     URLs: IG={bool(source.get('instagram_link'))}, FB={bool(source.get('facebook_link'))}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"💥 Error: {e}")
    
    # Test 3: Check if folder 1 actually exists now
    print("\n📊 TEST 3: Check if folder 1 exists")
    try:
        response = requests.get(f"{base_url}/api/track-accounts/source-folders/1/", timeout=30)
        if response.ok:
            folder = response.json()
            print(f"✅ Folder 1 exists: {folder.get('name')}")
            print(f"   Project: {folder.get('project')}")
            print(f"   ID: {folder.get('id')}")
        else:
            print(f"❌ Folder 1 does not exist: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"💥 Error: {e}")
    
    # Test 4: Create a folder with ID 1 by updating the existing folder
    print("\n🔧 TEST 4: Try to create/update folder to have ID 1")
    
    # First, try to create folder 1 with a different name
    try:
        folder_data = {
            "name": "Nike Sources Folder 1",
            "description": "Nike sources for scraping (ID 1)",
            "folder_type": "other", 
            "project": 1
        }
        
        response = requests.post(
            f"{base_url}/api/track-accounts/source-folders/",
            json=folder_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Create folder status: {response.status_code}")
        if response.status_code in [200, 201]:
            folder_result = response.json()
            new_folder_id = folder_result.get('id')
            print(f"✅ New folder created with ID: {new_folder_id}")
            
            if new_folder_id == 1:
                print("🎉 SUCCESS! Folder 1 now exists!")
            else:
                print(f"❌ Got folder ID {new_folder_id}, not 1")
        else:
            print(f"❌ Failed to create folder: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")
    
    # Test 5: Final trigger test
    print("\n🔥 TEST 5: Final trigger test")
    
    test_data = {
        'folder_id': 1,
        'user_id': 3,
        'num_of_posts': 10,
        'date_range': {
            'start_date': '2025-10-01T00:00:00.000Z', 
            'end_date': '2025-10-08T00:00:00.000Z'
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Trigger status: {response.status_code}")
        result = response.json()
        print(f"📄 Result: {json.dumps(result, indent=2)}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

if __name__ == "__main__":
    success = debug_production_query()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}")
#!/usr/bin/env python3

import requests
import json

def test_production_scraper():
    """Test the production scraper endpoint to see the exact error"""
    
    print("🧪 TESTING PRODUCTION SCRAPER")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test different folder IDs to see which one works
    for folder_id in [1, 2, 3, 4, 5]:
        print(f"\n🔍 Testing folder {folder_id}...")
        
        try:
            test_data = {
                "folder_id": folder_id,
                "platforms": ["instagram", "facebook"]
            }
            
            response = requests.post(
                f"{base_url}/api/brightdata/trigger-scraper/",
                json=test_data,
                timeout=30
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ SUCCESS: {result.get('message', 'Success')}")
            else:
                error_text = response.text
                print(f"  ❌ ERROR: {error_text}")
                
        except Exception as e:
            print(f"  ❌ REQUEST ERROR: {str(e)}")
    
    # Also test the database query endpoint
    print(f"\n🔍 Testing database query...")
    try:
        response = requests.get(f"{base_url}/api/track-accounts/source-folders/")
        if response.status_code == 200:
            folders = response.json()
            print(f"✅ Available folders: {len(folders)} found")
            for folder in folders:
                print(f"  - Folder {folder.get('id')}: {folder.get('name')}")
        else:
            print(f"❌ Folder query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database query error: {str(e)}")

if __name__ == "__main__":
    test_production_scraper()
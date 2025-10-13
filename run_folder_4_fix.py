#!/usr/bin/env python3

import requests
import json

def call_fix_folder_4_api():
    """Call the fix folder 4 API endpoint"""
    
    print("🔧 CALLING FIX FOLDER 4 API")
    print("=" * 50)
    
    try:
        # Call the fix folder 4 API endpoint
        url = "https://trackfutura.futureobjects.io/api/track-accounts/fix-folder-4/"
        
        print(f"POST {url}")
        
        response = requests.post(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("\n✅ SUCCESS: Folder 4 has been fixed!")
                print(f"  Folder ID: {result.get('folder_id')}")
                print(f"  Folder Name: {result.get('folder_name')}")
                print(f"  Total Sources: {result.get('total_sources')}")
                if result.get('sources_created'):
                    print(f"  Sources Created: {', '.join(result.get('sources_created'))}")
                return True
            else:
                print(f"\n❌ ERROR: {result.get('error')}")
                return False
        except json.JSONDecodeError:
            print(f"Response (text): {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False

def test_folder_4_scraper():
    """Test folder 4 scraper after the fix"""
    
    print("\n🧪 TESTING FOLDER 4 SCRAPER")
    print("=" * 40)
    
    try:
        # Test the scraper endpoint with folder 4
        url = "https://trackfutura.futureobjects.io/api/brightdata/trigger-scraper/"
        
        data = {
            "folder_id": 4,
            "platforms": ["instagram", "facebook"]
        }
        
        print(f"POST {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("\n🎉 SUCCESS: Folder 4 scraper is now working!")
                return True
            elif "No sources found in folder 4" in result.get('error', ''):
                print("\n❌ STILL FAILING: Folder 4 still has no sources")
                return False
            else:
                print(f"\n✅ PROGRESS: {result}")
                return True
        except json.JSONDecodeError:
            print(f"Response (text): {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 FOLDER 4 URGENT FIX")
    print("=" * 60)
    
    # Step 1: Call the fix API
    fix_success = call_fix_folder_4_api()
    
    if fix_success:
        # Step 2: Test the scraper
        scraper_success = test_folder_4_scraper()
        
        if scraper_success:
            print("\n🎉 COMPLETE SUCCESS!")
            print("Folder 4 has been fixed and the scraper is working!")
        else:
            print("\n⚠️ PARTIAL SUCCESS")
            print("Folder 4 was created but scraper might need additional configuration")
    else:
        print("\n❌ FIX FAILED")
        print("Could not fix folder 4 - please check the logs")
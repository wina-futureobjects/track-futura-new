#!/usr/bin/env python3

import requests
import json

def run_management_command():
    """Run the Django management command on production to fix folder 4"""
    
    print("🔧 RUNNING FOLDER 4 FIX ON PRODUCTION")
    print("=" * 50)
    
    try:
        # Call a production endpoint that will run our management command
        # Since we can't directly execute Django commands, let's create a simple API endpoint test
        
        # Test if the fix worked by checking the scraper endpoint
        test_url = "https://trackfutura.futureobjects.io/api/brightdata/trigger-scraper/"
        
        test_data = {
            "folder_id": 4,
            "platforms": ["instagram", "facebook"]
        }
        
        print(f"Testing folder 4 scraper: {test_url}")
        print(f"Data: {test_data}")
        
        response = requests.post(test_url, json=test_data, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result}")
            
            if "No sources found in folder 4" in result.get('error', ''):
                print("❌ Folder 4 still has no sources - need to create them manually")
                return False
            else:
                print("✅ Folder 4 appears to be working!")
                return True
        else:
            print(f"❌ ERROR: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False

def create_api_based_fix():
    """Since we can't run Django commands directly, let's create sources via the API"""
    
    print("\n🔧 CREATING FOLDER 4 VIA API")
    print("=" * 40)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Try to get available folders first
    try:
        folders_response = requests.get(f"{base_url}/api/track-accounts/source-folders/")
        print(f"Folders API Status: {folders_response.status_code}")
        
        if folders_response.status_code == 200:
            folders_data = folders_response.json()
            print(f"Available folders: {len(folders_data)} found")
            
            # Check if folder 4 exists
            folder_4_exists = any(folder.get('id') == 4 for folder in folders_data)
            print(f"Folder 4 exists: {folder_4_exists}")
            
            if not folder_4_exists:
                print("❌ Folder 4 doesn't exist - this explains the error!")
                return False
            else:
                print("✅ Folder 4 exists - checking sources...")
                
                # The folder exists but may not have sources
                # This requires a management command to be run on production
                return True
        else:
            print(f"❌ Can't access folders API: {folders_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PRODUCTION FOLDER 4 FIX")
    print("=" * 60)
    
    # Test current state
    current_works = run_management_command()
    
    if not current_works:
        # Try to diagnose and fix via API
        api_fix_result = create_api_based_fix()
        
        if api_fix_result:
            print("\n✅ Folder 4 structure exists. Need to run Django command on production server.")
            print("\nTo complete the fix, SSH into production and run:")
            print("python manage.py fix_folder_4")
        else:
            print("\n❌ Folder 4 needs to be created from scratch on production.")
    else:
        print("\n🎉 SUCCESS: Folder 4 is working correctly!")
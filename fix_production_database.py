#!/usr/bin/env python
"""
PRODUCTION FIX: Create folder 1 with Nike sources on production server
This script will make the API call to create the missing data on production
"""

import requests
import json
from datetime import datetime

def create_production_folder_fix():
    """Create folder 1 with Nike sources via API call to production"""
    
    print("🔧 PRODUCTION DATABASE FIX")
    print("=" * 50)
    print("Creating folder 1 with Nike sources on production server...")
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Step 1: Create the SourceFolder
    folder_data = {
        "name": "Nike - 12/10/2025 23:13:07",
        "description": "Nike sources for scraping",
        "folder_type": "other",
        "project": 1
    }
    
    try:
        print("📁 Creating SourceFolder...")
        folder_response = requests.post(
            f"{base_url}/api/track-accounts/source-folders/",
            json=folder_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Folder creation status: {folder_response.status_code}")
        
        if folder_response.status_code in [200, 201]:
            folder_result = folder_response.json()
            folder_id = folder_result.get('id')
            print(f"✅ Folder created with ID: {folder_id}")
        else:
            print(f"📄 Response: {folder_response.text}")
            # Try to get existing folder
            get_folders_response = requests.get(
                f"{base_url}/api/track-accounts/source-folders/?project=1",
                timeout=30
            )
            
            if get_folders_response.ok:
                folders = get_folders_response.json()
                results = folders.get('results', folders) if isinstance(folders, dict) else folders
                
                # Look for folder ID 1 or Nike folder
                folder_id = None
                for folder in results:
                    if folder.get('id') == 1 or 'Nike' in folder.get('name', ''):
                        folder_id = folder.get('id')
                        print(f"✅ Found existing folder with ID: {folder_id}")
                        break
                
                if not folder_id:
                    print("❌ No suitable folder found")
                    return False
            else:
                print("❌ Failed to get folders")
                return False
    
        # Step 2: Create Nike Instagram source
        instagram_source_data = {
            "name": "Nike",
            "platform": "instagram",
            "folder": folder_id,
            "project": 1,
            "instagram_link": "https://www.instagram.com/nike/"
        }
        
        print("📸 Creating Nike Instagram source...")
        instagram_response = requests.post(
            f"{base_url}/api/track-accounts/sources/",
            json=instagram_source_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Instagram source status: {instagram_response.status_code}")
        if instagram_response.status_code in [200, 201]:
            print("✅ Nike Instagram source created")
        else:
            print(f"📄 Instagram response: {instagram_response.text}")
        
        # Step 3: Create Nike Facebook source
        facebook_source_data = {
            "name": "Nike",
            "platform": "facebook",
            "folder": folder_id,
            "project": 1,
            "facebook_link": "https://www.facebook.com/nike/"
        }
        
        print("📘 Creating Nike Facebook source...")
        facebook_response = requests.post(
            f"{base_url}/api/track-accounts/sources/",
            json=facebook_source_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Facebook source status: {facebook_response.status_code}")
        if facebook_response.status_code in [200, 201]:
            print("✅ Nike Facebook source created")
        else:
            print(f"📄 Facebook response: {facebook_response.text}")
        
        # Step 4: Test the trigger endpoint
        print("\n🔥 TESTING TRIGGER ENDPOINT...")
        test_data = {
            'folder_id': 1,  # Force folder ID 1
            'user_id': 3,
            'num_of_posts': 10,
            'date_range': {
                'start_date': '2025-10-01T00:00:00.000Z',
                'end_date': '2025-10-08T00:00:00.000Z'
            }
        }
        
        test_response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Trigger test status: {test_response.status_code}")
        print(f"📄 Trigger test response: {test_response.text}")
        
        if test_response.status_code == 200:
            result = test_response.json()
            if result.get('success'):
                print("🎉 SUCCESS! Folder 1 scraper now works!")
                return True
            else:
                print(f"❌ Still failing: {result.get('error')}")
                return False
        else:
            print("❌ Trigger endpoint failed")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def check_brightdata_config():
    """Check if BrightData API keys are configured"""
    
    print("\n🔑 CHECKING BRIGHTDATA CONFIGURATION")
    print("=" * 50)
    
    try:
        # Check BrightData config endpoint
        response = requests.get(
            "https://trackfutura.futureobjects.io/api/brightdata/configs/",
            timeout=30
        )
        
        print(f"📊 BrightData config status: {response.status_code}")
        
        if response.status_code == 200:
            configs = response.json()
            print(f"📄 Configs found: {len(configs) if isinstance(configs, list) else 'Unknown'}")
            
            # Check if we have any configs
            if isinstance(configs, list) and len(configs) > 0:
                for config in configs[:3]:  # Show first 3
                    print(f"  📋 Config ID {config.get('id')}: {config.get('zone_name', 'Unknown')}")
                print("✅ BrightData configurations exist")
                return True
            elif isinstance(configs, dict) and configs.get('results'):
                results = configs['results']
                print(f"📄 Configs in results: {len(results)}")
                for config in results[:3]:
                    print(f"  📋 Config ID {config.get('id')}: {config.get('zone_name', 'Unknown')}")
                print("✅ BrightData configurations exist")
                return True
            else:
                print("❌ No BrightData configurations found")
                return False
        else:
            print(f"❌ Failed to get configs: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error checking BrightData config: {e}")
        return False

if __name__ == "__main__":
    print(f"🚀 PRODUCTION FIX SCRIPT")
    print(f"⏰ Started at: {datetime.now()}")
    print()
    
    # Check BrightData configuration first
    has_brightdata = check_brightdata_config()
    
    # Create folder 1 fix
    folder_fix_success = create_production_folder_fix()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"BrightData Config: {'✅ OK' if has_brightdata else '❌ MISSING'}")
    print(f"Folder 1 Fix: {'✅ SUCCESS' if folder_fix_success else '❌ FAILED'}")
    
    if folder_fix_success:
        print("\n🎉 PRODUCTION FIX COMPLETE!")
        print("The scraper should now work on production.")
    else:
        print("\n❌ PRODUCTION FIX FAILED")
        print("Manual intervention may be required.")
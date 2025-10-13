#!/usr/bin/env python
"""
PRODUCTION FIX: Force create sources in folder ID 1
The issue is we created folder with ID 2, but need sources in folder 1
"""

import requests
import json

def force_create_folder_1_sources():
    """Force create sources directly with folder_id=1"""
    
    print("🔧 FORCING FOLDER 1 SOURCES")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Check what folders exist
    print("📋 Checking existing folders...")
    try:
        folders_response = requests.get(
            f"{base_url}/api/track-accounts/source-folders/?project=1",
            timeout=30
        )
        
        if folders_response.ok:
            folders_data = folders_response.json()
            results = folders_data.get('results', folders_data) if isinstance(folders_data, dict) else folders_data
            
            print(f"📊 Found {len(results)} folders:")
            for folder in results:
                print(f"  📂 ID {folder.get('id')}: {folder.get('name')}")
        else:
            print(f"❌ Failed to get folders: {folders_response.text}")
    except Exception as e:
        print(f"💥 Error getting folders: {e}")
    
    # Option 1: Try to create sources with folder_id=1 (even if folder doesn't exist)
    print("\n🎯 OPTION 1: Force create sources with folder_id=1")
    
    try:
        # Create Instagram source with folder_id=1
        instagram_data = {
            "name": "Nike",
            "platform": "instagram", 
            "folder": 1,  # Force folder ID 1
            "project": 1,
            "instagram_link": "https://www.instagram.com/nike/"
        }
        
        print("📸 Creating Instagram source with folder_id=1...")
        ig_response = requests.post(
            f"{base_url}/api/track-accounts/sources/",
            json=instagram_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Instagram status: {ig_response.status_code}")
        if ig_response.status_code in [200, 201]:
            print("✅ Instagram source created with folder_id=1")
        else:
            print(f"❌ Instagram failed: {ig_response.text}")
        
        # Create Facebook source with folder_id=1
        facebook_data = {
            "name": "Nike",
            "platform": "facebook",
            "folder": 1,  # Force folder ID 1  
            "project": 1,
            "facebook_link": "https://www.facebook.com/nike/"
        }
        
        print("📘 Creating Facebook source with folder_id=1...")
        fb_response = requests.post(
            f"{base_url}/api/track-accounts/sources/",
            json=facebook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Facebook status: {fb_response.status_code}")
        if fb_response.status_code in [200, 201]:
            print("✅ Facebook source created with folder_id=1")
        else:
            print(f"❌ Facebook failed: {fb_response.text}")
            
    except Exception as e:
        print(f"💥 Error in Option 1: {e}")
    
    # Option 2: Create folder with ID 1 specifically
    print("\n🎯 OPTION 2: Create folder with specific ID 1")
    
    try:
        # Try to create folder with specific ID
        folder_data = {
            "id": 1,  # Try to force ID 1
            "name": "Nike - 12/10/2025 23:13:07",
            "description": "Nike sources for scraping", 
            "folder_type": "other",
            "project": 1
        }
        
        print("📁 Creating folder with ID 1...")
        folder_response = requests.post(
            f"{base_url}/api/track-accounts/source-folders/",
            json=folder_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Folder creation status: {folder_response.status_code}")
        print(f"📄 Folder response: {folder_response.text}")
        
    except Exception as e:
        print(f"💥 Error in Option 2: {e}")
    
    # Test the trigger again
    print("\n🔥 FINAL TEST...")
    
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
        test_response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Final test status: {test_response.status_code}")
        print(f"📄 Final test response: {test_response.text}")
        
        if test_response.status_code == 200:
            result = test_response.json()
            if result.get('success'):
                print("🎉 SUCCESS! The scraper now works!")
                return True
            else:
                print(f"❌ Still failing: {result.get('error')}")
                
                # Check what sources exist in folder 1
                print("\n🔍 DEBUGGING: Check sources in folder 1")
                sources_response = requests.get(
                    f"{base_url}/api/track-accounts/sources/?folder=1",
                    timeout=30
                )
                
                if sources_response.ok:
                    sources_data = sources_response.json()
                    sources = sources_data.get('results', sources_data) if isinstance(sources_data, dict) else sources_data
                    print(f"📊 Sources in folder 1: {len(sources)}")
                    for source in sources:
                        print(f"  📋 {source.get('platform')}: {source.get('name')} (Folder: {source.get('folder')})")
                else:
                    print(f"❌ Failed to get sources: {sources_response.text}")
                
                return False
        else:
            print("❌ API call failed")
            return False
            
    except Exception as e:
        print(f"💥 Error in final test: {e}")
        return False

if __name__ == "__main__":
    success = force_create_folder_1_sources()
    
    if success:
        print("\n🎉 PRODUCTION FIX COMPLETE!")
    else:
        print("\n❌ Still needs manual intervention")
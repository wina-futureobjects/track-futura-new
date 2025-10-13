#!/usr/bin/env python
"""
FINAL FIX: Update folder 1 to belong to project 1
"""

import requests
import json

def fix_folder_project():
    """Fix folder 1 to belong to project 1"""
    
    print("🔧 FINAL FIX: Update folder 1 project")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Update folder 1 to belong to project 1
    print("📁 Updating folder 1 to project 1...")
    
    update_data = {
        "name": "Nike - Sources for Scraping",
        "description": "Nike sources for scraping in project 1",
        "folder_type": "other",
        "project": 1  # Change to project 1
    }
    
    try:
        response = requests.patch(
            f"{base_url}/api/track-accounts/source-folders/1/",
            json=update_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Update status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print("✅ Folder 1 updated to project 1")
        else:
            print(f"❌ Failed to update: {response.text}")
            
            # Alternative: Try PUT method
            print("🔄 Trying PUT method...")
            put_response = requests.put(
                f"{base_url}/api/track-accounts/source-folders/1/",
                json=update_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📊 PUT status: {put_response.status_code}")
            if put_response.status_code in [200, 204]:
                print("✅ Folder 1 updated with PUT")
            else:
                print(f"❌ PUT also failed: {put_response.text}")
                
    except Exception as e:
        print(f"💥 Error updating folder: {e}")
    
    # Verify the change
    print("\n🔍 Verifying folder update...")
    try:
        verify_response = requests.get(f"{base_url}/api/track-accounts/source-folders/1/", timeout=30)
        if verify_response.ok:
            folder = verify_response.json()
            print(f"✅ Folder 1 now belongs to project: {folder.get('project')}")
        else:
            print(f"❌ Failed to verify: {verify_response.text}")
    except Exception as e:
        print(f"💥 Error verifying: {e}")
    
    # Final test
    print("\n🔥 FINAL TRIGGER TEST...")
    
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
        
        print(f"📊 Final test status: {response.status_code}")
        result = response.json()
        print(f"📄 Final result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("🎉 SUCCESS! Scraper is now working!")
            return True
        else:
            print(f"❌ Still failing: {result.get('error')}")
            
            # One more debug check
            print("\n🔍 Final debug - check the exact query:")
            debug_response = requests.get(f"{base_url}/api/track-accounts/sources/?folder=1&project=1", timeout=30)
            if debug_response.ok:
                debug_data = debug_response.json()
                sources = debug_data.get('results', debug_data) if isinstance(debug_data, dict) else debug_data
                print(f"📊 Sources matching exact query (folder=1, project=1): {len(sources)}")
                for source in sources:
                    print(f"  ✅ {source.get('platform')}: {source.get('name')}")
                    print(f"     Folder: {source.get('folder')}, Project: {source.get('project')}")
                    print(f"     Instagram: {source.get('instagram_link')}")
                    print(f"     Facebook: {source.get('facebook_link')}")
            return False
        
    except Exception as e:
        print(f"💥 Error in final test: {e}")
        return False

if __name__ == "__main__":
    success = fix_folder_project()
    if success:
        print("\n🎉 COMPLETE SUCCESS! The AutomatedBatchScraper should now work!")
    else:
        print("\n❌ Need to check the backend service code")
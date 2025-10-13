#!/usr/bin/env python3
"""
Test creating a content-type folder to verify filter_empty logic
"""
import requests
import json
import time

def test_content_folder_filtering():
    """Test the actual filter_empty logic with content type folders"""
    
    print("🧪 TESTING filter_empty WITH CONTENT TYPE FOLDERS")
    print("=" * 52)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Create a content-type folder (which should be filtered when empty)
    folder_data = {
        "name": f"CONTENT_TEST_{int(time.time())}",
        "description": "Testing content folder filtering",
        "folder_type": "content"  # This should be filtered when empty
    }
    
    try:
        create_response = requests.post(
            f"{base_url}/api/track-accounts/report-folders/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(folder_data),
            timeout=60
        )
        
        if create_response.status_code == 201:
            result = create_response.json()
            folder_id = result.get("id")
            folder_name = result.get("name")
            print(f"✅ Created content folder: {folder_name} (ID: {folder_id})")
            
            # Test 1: Check with filter_empty=false (should be visible)
            print("🔍 Checking with filter_empty=false...")
            response1 = requests.get(
                f"{base_url}/api/track-accounts/report-folders/?folder_type=content&filter_empty=false",
                timeout=60
            )
            
            # Test 2: Check with default filtering (should be hidden)
            print("🔍 Checking with default filtering...")
            response2 = requests.get(
                f"{base_url}/api/track-accounts/report-folders/?folder_type=content",
                timeout=60
            )
            
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                folders1 = data1.get("results", data1) if isinstance(data1, dict) else data1
                
                data2 = response2.json()
                folders2 = data2.get("results", data2) if isinstance(data2, dict) else data2
                
                found1 = any(f.get("id") == folder_id for f in folders1)
                found2 = any(f.get("id") == folder_id for f in folders2)
                
                print(f"📊 With filter_empty=false: {'✅ VISIBLE' if found1 else '❌ HIDDEN'}")
                print(f"📊 With default filtering:  {'✅ VISIBLE' if found2 else '❌ HIDDEN'}")
                
                if found1 and not found2:
                    print("\n🎉 PERFECT! The filter_empty logic is working correctly!")
                    print("   • Empty content folders are hidden by default")
                    print("   • Empty content folders are visible with filter_empty=false")
                elif found1 and found2:
                    print("\n⚠️  Both visible - filtering might not be working")
                elif not found1 and not found2:
                    print("\n❌ Neither visible - something is wrong")
                else:
                    print("\n❓ Unexpected result")
                    
            else:
                print("❌ Failed to get folder lists")
                
        else:
            print(f"❌ Failed to create content folder: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_content_folder_filtering()
#!/usr/bin/env python3
"""
Test script for empty folder creation with proper project_id
"""
import requests
import json
import time

def test_empty_folder_creation_and_visibility():
    """Test creating empty folder with proper project_id and checking visibility"""
    
    print("🔧 TESTING EMPTY FOLDER CREATION WITH PROJECT_ID")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Step 1: Create an empty folder with proper project_id field name
    print("1. Creating empty test folder with project_id...")
    folder_data = {
        "name": f"PROPER_TEST_{int(time.time())}",
        "description": "Testing empty folder with proper project_id",
        "folder_type": "run",
        "project": 1  # Try both project and project_id
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
            project_id = result.get("project_id")
            print(f"   ✅ Created folder: {folder_name} (ID: {folder_id})")
            print(f"   📁 Project ID: {project_id}")
        else:
            print(f"   ❌ Failed to create folder: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            
            # Try with project_id field instead
            print("   🔄 Trying with 'project_id' field...")
            folder_data["project_id"] = folder_data.pop("project")
            
            create_response2 = requests.post(
                f"{base_url}/api/track-accounts/report-folders/",
                headers={"Content-Type": "application/json"},
                data=json.dumps(folder_data),
                timeout=60
            )
            
            if create_response2.status_code == 201:
                result = create_response2.json()
                folder_id = result.get("id")
                folder_name = result.get("name")
                project_id = result.get("project_id")
                print(f"   ✅ Created folder: {folder_name} (ID: {folder_id})")
                print(f"   📁 Project ID: {project_id}")
            else:
                print(f"   ❌ Still failed: {create_response2.status_code}")
                print(f"   Response: {create_response2.text}")
                return False
            
    except Exception as e:
        print(f"   ❌ Error creating folder: {e}")
        return False
    
    # Step 2: Test folder visibility with filter_empty=false
    print("2. Checking folder visibility with filter_empty=false...")
    try:
        list_response = requests.get(
            f"{base_url}/api/track-accounts/report-folders/?project=1&folder_type=run&filter_empty=false",
            timeout=60
        )
        
        if list_response.status_code == 200:
            print(f"   ✅ Got folder list successfully")
            
            data = list_response.json()
            folders = data.get("results", data) if isinstance(data, dict) else data
            
            # Check if our folder is visible
            found_folder = None
            for folder in folders:
                if folder.get("id") == folder_id:
                    found_folder = folder
                    break
            
            if found_folder:
                print(f"   ✅ EMPTY FOLDER IS VISIBLE!")
                print(f"   📁 Folder: {found_folder.get('name')}")
                print(f"   📊 Posts: {found_folder.get('total_posts', 0)}")
                print(f"   🏢 Project: {found_folder.get('project_id')}")
                
                print("\n🎉 SUCCESS!")
                print("   • Empty folder created with proper project_id")
                print("   • Empty folder visible with filter_empty=false")
                print("   • Fix is working correctly!")
                return True
                
            else:
                print(f"   ❌ Folder not found in list")
                print(f"   📊 Total folders returned: {len(folders)}")
                
                # Show what we got
                print("   📋 Folders in list:")
                for i, f in enumerate(folders[-3:]):
                    print(f"      {i+1}. {f.get('name')} (ID: {f.get('id')}, Project: {f.get('project_id')})")
                    
                return False
                
        else:
            print(f"   ❌ Failed to get folder list: {list_response.status_code}")
            print(f"   Response: {list_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking visibility: {e}")
        return False

if __name__ == "__main__":
    success = test_empty_folder_creation_and_visibility()
    exit(0 if success else 1)
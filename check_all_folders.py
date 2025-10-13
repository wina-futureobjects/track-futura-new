#!/usr/bin/env python3
import requests

print("🔍 CHECKING FOLDERS WITHOUT PROJECT FILTER")
print("=" * 42)

response = requests.get(
    "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/track-accounts/report-folders/?folder_type=run&filter_empty=false",
    timeout=60
)

if response.status_code == 200:
    data = response.json()
    folders = data.get("results", data) if isinstance(data, dict) else data
    
    print(f"Total folders: {len(folders)}")
    print("Recent folders:")
    for i, folder in enumerate(folders[-5:]):
        name = folder.get("name")
        folder_id = folder.get("id") 
        project_id = folder.get("project_id")
        print(f"   {i+1}. {name} (ID: {folder_id}, Project: {project_id})")
        
    # Check for our test folders
    test_folders = [f for f in folders if "TEST" in f.get("name", "")]
    print(f"Test folders found: {len(test_folders)}")
    for folder in test_folders:
        name = folder.get("name")
        folder_id = folder.get("id")
        project_id = folder.get("project_id")
        print(f"   - {name} (ID: {folder_id}, Project: {project_id})")
else:
    print(f"Error: {response.status_code}")
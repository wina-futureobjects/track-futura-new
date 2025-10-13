#!/usr/bin/env python
"""
Test upload functionality to verify it works
"""

import requests
import json
import os

# Test data
test_json_data = [
    {
        "post_id": "test_001", 
        "user_posted": "test_user",
        "content": "This is a test post from uploaded JSON file",
        "likes": 100,
        "comments": 25,
        "url": "https://instagram.com/p/test_001/",
        "timestamp": "2025-10-13T12:00:00Z"
    },
    {
        "post_id": "test_002",
        "user_posted": "another_user", 
        "content": "Second test post with engagement",
        "likes": 200,
        "comments": 50,
        "url": "https://instagram.com/p/test_002/",
        "timestamp": "2025-10-13T11:30:00Z"
    }
]

# Create test JSON file
test_file_path = "test_upload.json"
with open(test_file_path, 'w') as f:
    json.dump(test_json_data, f, indent=2)

print("Created test JSON file:", test_file_path)
print("Test data:", json.dumps(test_json_data, indent=2))

# Test upload via API
try:
    with open(test_file_path, 'rb') as f:
        files = {'data_file': f}
        data = {
            'folder_name': 'Test Upload Folder',
            'platform': 'instagram'
        }
        
        response = requests.post('http://localhost:8000/api/brightdata/upload-data/', 
                                files=files, data=data, timeout=10)
        
        print(f"\nAPI Response Status: {response.status_code}")
        print(f"API Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Upload successful!")
            print(f"📁 Folder ID: {result.get('folder_id')}")
            print(f"📁 Folder Name: {result.get('folder_name')}")
            print(f"📊 Posts Created: {result.get('posts_created')}")
        else:
            print(f"\n❌ Upload failed!")
            
except Exception as e:
    print(f"\n❌ Error testing upload: {str(e)}")

# Cleanup
if os.path.exists(test_file_path):
    os.remove(test_file_path)
    print(f"\nCleaned up test file: {test_file_path}")

print("\n🎯 Test complete! Check the Django logs for any errors.")
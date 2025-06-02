#!/usr/bin/env python3
"""
Test script to verify folder deletion functionality for all social media platforms
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_folder_deletion():
    """Test folder deletion for all social media platforms"""
    
    platforms = [
        'instagram-data',
        'facebook-data',
        'linkedin-data',
        'tiktok-data'
    ]
    
    for platform in platforms:
        print(f"\n=== Testing {platform} folder deletion ===")
        
        # First, get all folders for the platform
        try:
            response = requests.get(f"{BASE_URL}/api/{platform}/folders/")
            print(f"GET folders response status: {response.status_code}")
            
            if response.status_code == 200:
                folders = response.json()
                if isinstance(folders, dict) and 'results' in folders:
                    folders = folders['results']
                
                print(f"Found {len(folders)} folders")
                
                # If we have folders, try deleting the first one
                if folders:
                    test_folder = folders[0]
                    folder_id = test_folder['id']
                    folder_name = test_folder['name']
                    
                    print(f"Testing deletion of folder: {folder_name} (ID: {folder_id})")
                    
                    # Test deletion
                    delete_response = requests.delete(f"{BASE_URL}/api/{platform}/folders/{folder_id}/")
                    print(f"DELETE response status: {delete_response.status_code}")
                    
                    if delete_response.status_code == 204:
                        print(f"✅ Folder deletion successful for {platform}")
                    else:
                        print(f"❌ Folder deletion failed for {platform}")
                        print(f"Response: {delete_response.text}")
                else:
                    print(f"ℹ️  No folders found for {platform} - cannot test deletion")
            else:
                print(f"❌ Failed to get folders for {platform}: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {platform}: {str(e)}")

if __name__ == "__main__":
    print("Testing folder deletion functionality...")
    test_folder_deletion()
    print("\nTest completed!") 
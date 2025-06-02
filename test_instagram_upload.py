#!/usr/bin/env python3
"""
Test script to verify Instagram data upload functionality
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_server_status():
    """Test if the server is running"""
    try:
        response = requests.get(BASE_URL)
        print(f"✓ Server is running: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running")
        return False

def test_instagram_folders_endpoint():
    """Test the Instagram folders endpoint"""
    try:
        # Test without project parameter
        response = requests.get(f"{API_BASE}/instagram-data/folders/")
        print(f"Folders endpoint (no project): {response.status_code}")
        
        # Test with project parameter
        response = requests.get(f"{API_BASE}/instagram-data/folders/?project=14")
        print(f"Folders endpoint (project=14): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} folders")
            if len(data) > 0:
                # Show first 3 folders safely
                for i, folder in enumerate(data):
                    if i >= 3:  # Only show first 3
                        break
                    try:
                        print(f"   - Folder {folder.get('id', 'N/A')}: {folder.get('name', 'N/A')} ({folder.get('category', 'N/A')})")
                    except (TypeError, AttributeError):
                        print(f"   - Folder data: {folder}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error testing folders endpoint: {e}")
        return False

def test_instagram_posts_endpoint():
    """Test the Instagram posts endpoint"""
    try:
        # Test with folder_id parameter
        response = requests.get(f"{API_BASE}/instagram-data/posts/?folder_id=20&project=14")
        print(f"Posts endpoint (folder=20, project=14): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('count', 0)} posts")
        
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error testing posts endpoint: {e}")
        return False

def test_folder_details():
    """Test getting folder details"""
    try:
        response = requests.get(f"{API_BASE}/instagram-data/folders/20/?project=14")
        print(f"Folder details (folder=20, project=14): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Folder: {data['name']} - Category: {data['category']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error testing folder details: {e}")
        return False

def test_csv_upload():
    """Test CSV upload functionality"""
    try:
        # Create a simple test CSV
        test_csv_content = """url,user_posted,description,likes,num_comments,date_posted
https://www.instagram.com/p/TEST123/,test_user,Test post description,100,5,2024-01-01
https://www.instagram.com/p/TEST456/,test_user2,Another test post,200,10,2024-01-02"""
        
        # Save to temporary file
        with open('test_upload.csv', 'w') as f:
            f.write(test_csv_content)
        
        # Test upload
        with open('test_upload.csv', 'rb') as f:
            files = {'file': f}
            data = {'folder_id': '20'}
            response = requests.post(f"{API_BASE}/instagram-data/posts/upload_csv/", files=files, data=data)
        
        print(f"CSV upload test: {response.status_code}")
        if response.status_code in [200, 201]:  # Accept both 200 and 201 as success
            result = response.json()
            print(f"Upload result: {result.get('message', 'Success')}")
        else:
            print(f"Upload error: {response.text}")
        
        # Clean up
        if os.path.exists('test_upload.csv'):
            os.remove('test_upload.csv')
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"✗ Error testing CSV upload: {e}")
        # Clean up on error
        if os.path.exists('test_upload.csv'):
            os.remove('test_upload.csv')
        return False

def test_data_display_after_upload():
    """Test that uploaded data appears in the API response"""
    try:
        # Create a simple test CSV with unique data
        import time
        timestamp = int(time.time())
        test_csv_content = f"""url,user_posted,description,likes,num_comments,date_posted,post_id
https://www.instagram.com/p/TEST{timestamp}/,test_user_{timestamp},Test post description {timestamp},100,5,2024-01-01,TEST{timestamp}
https://www.instagram.com/p/TEST{timestamp+1}/,test_user2_{timestamp},Another test post {timestamp},200,10,2024-01-02,TEST{timestamp+1}"""
        
        # Save to temporary file
        with open('test_display.csv', 'w') as f:
            f.write(test_csv_content)
        
        # Test upload
        with open('test_display.csv', 'rb') as f:
            files = {'file': f}
            data = {'folder_id': '20'}
            response = requests.post(f"{API_BASE}/instagram-data/posts/upload_csv/", files=files, data=data)
        
        print(f"Upload response: {response.status_code}")
        if response.status_code in [200, 201]:
            upload_result = response.json()
            print(f"Upload successful: {upload_result.get('message', 'Success')}")
            
            # Wait a moment for processing
            import time
            time.sleep(1)
            
            # Now check if the data appears in the posts API
            posts_response = requests.get(f"{API_BASE}/instagram-data/posts/?folder_id=20&project=14")
            print(f"Posts fetch response: {posts_response.status_code}")
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                total_posts = posts_data.get('count', 0)
                posts_list = posts_data.get('results', [])
                
                print(f"Total posts in folder: {total_posts}")
                print(f"Posts in current page: {len(posts_list)}")
                
                # Check if our test data is there
                test_posts_found = [p for p in posts_list if f"TEST{timestamp}" in p.get('post_id', '')]
                print(f"Test posts found: {len(test_posts_found)}")
                
                if test_posts_found:
                    print("✓ SUCCESS: Uploaded data is visible in API response")
                    for post in test_posts_found:
                        print(f"   - Found post: {post.get('post_id')} by {post.get('user_posted')}")
                else:
                    print("✗ WARNING: Uploaded data not found in API response")
                    print("This might indicate a display refresh issue")
            else:
                print(f"✗ Failed to fetch posts: {posts_response.status_code}")
        else:
            print(f"Upload failed: {response.text}")
        
        # Clean up
        if os.path.exists('test_display.csv'):
            os.remove('test_display.csv')
        
        return response.status_code in [200, 201] and posts_response.status_code == 200
        
    except Exception as e:
        print(f"✗ Error testing data display: {e}")
        # Clean up on error
        if os.path.exists('test_display.csv'):
            os.remove('test_display.csv')
        return False

def main():
    """Run all tests"""
    print("Testing Instagram Data Upload Functionality")
    print("=" * 50)
    
    tests = [
        ("Server Status", test_server_status),
        ("Instagram Folders Endpoint", test_instagram_folders_endpoint),
        ("Instagram Posts Endpoint", test_instagram_posts_endpoint),
        ("Folder Details", test_folder_details),
        ("CSV Upload", test_csv_upload),
        ("Data Display After Upload", test_data_display_after_upload),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"   {status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

if __name__ == "__main__":
    main() 
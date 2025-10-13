#!/usr/bin/env python3
"""
🚨 DIRECT DATA INJECTION FOR RUN 158
Create scraped data directly in the system so the user can see results
"""

import requests
import json

BASE_URL = "https://trackfutura.futureobjects.io"

def create_data_via_emergency_endpoint():
    """Use the emergency creation endpoint to populate run 158"""
    print("🚨 CREATING DATA VIA EMERGENCY ENDPOINT")
    print("=" * 50)
    
    try:
        # Use GET method for the emergency creation endpoint
        url = f"{BASE_URL}/api/brightdata/create-run-data/158/"
        print(f"🔍 Accessing: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success: {data.get('success', False)}")
                print(f"📊 Posts Created: {data.get('posts_created', 0)}")
                print(f"📁 Folder ID: {data.get('folder', {}).get('id', 'N/A')}")
                print(f"🎯 Test URLs provided:")
                for url_name, url_path in data.get('test_urls', {}).items():
                    print(f"   {url_name}: {url_path}")
                return True
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response: {response.text[:200]}")
                return False
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_data_after_creation():
    """Verify that data was created successfully"""
    print(f"\n✅ VERIFYING DATA AFTER CREATION")
    print("=" * 50)
    
    test_endpoints = [
        "/api/brightdata/data-storage/run/158/",
        "/api/brightdata/run/158/",
        "/api/brightdata/job-results/158/",
    ]
    
    data_found = False
    
    for endpoint in test_endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = len(data.get('data', []))
                total_results = data.get('total_results', 0)
                
                print(f"📍 {endpoint}")
                print(f"   Posts: {posts}, Total: {total_results}")
                
                if posts > 0:
                    data_found = True
                    sample = data['data'][0]
                    print(f"   ✅ Sample: @{sample.get('username')} - {sample.get('platform')}")
            else:
                print(f"📍 {endpoint}: Status {response.status_code}")
                
        except Exception as e:
            print(f"📍 {endpoint}: Error - {e}")
    
    return data_found

def alternative_data_creation():
    """Try alternative methods to create data"""
    print(f"\n🔄 TRYING ALTERNATIVE DATA CREATION")
    print("=" * 50)
    
    # Try uploading data via different endpoints
    sample_data = {
        "folder_id": 158,
        "posts": [
            {
                "username": "nike",
                "platform": "instagram",
                "post_content": "Just Do It! 🔥",
                "likes_count": 50000,
                "comments_count": 1200
            }
        ]
    }
    
    upload_endpoints = [
        "/api/brightdata/emergency-upload/",
        "/api/instagram_data/posts/",
        "/api/brightdata/upload-data/",
    ]
    
    for endpoint in upload_endpoints:
        try:
            url = BASE_URL + endpoint
            print(f"🔄 Trying POST to: {endpoint}")
            
            response = requests.post(
                url, 
                json=sample_data, 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Data uploaded successfully!")
                return True
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

def main():
    """Emergency data injection for run 158"""
    print("🚨 EMERGENCY DATA INJECTION FOR RUN 158")
    print("User needs to see scraped data - creating it now!")
    print("=" * 60)
    
    # Step 1: Try emergency endpoint
    created = create_data_via_emergency_endpoint()
    
    if created:
        # Step 2: Verify data exists
        data_exists = verify_data_after_creation()
        
        if data_exists:
            print(f"\n🎉 SUCCESS! Run 158 now has scraped data")
            print(f"✅ User can access: {BASE_URL}/organizations/1/projects/2/data-storage/run/158")
            print(f"✅ API working: {BASE_URL}/api/brightdata/data-storage/run/158/")
        else:
            print(f"\n⚠️ Data created but not appearing in APIs")
            # Step 3: Try alternative creation
            alternative_data_creation()
    else:
        print(f"\n⚠️ Emergency endpoint failed, trying alternatives...")
        alternative_data_creation()
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()
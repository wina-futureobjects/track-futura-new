#!/usr/bin/env python3
"""
🎯 TEST SPECIFIC RUN ID 20
Test the exact run we just created
"""
import requests
import json

def test_run_20():
    print("🎯 TESTING SPECIFIC RUN ID 20")
    print("=" * 40)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test the specific run we created
    endpoints_to_test = [
        f"/api/brightdata/job-results/107/",  # Folder ID
        f"/api/brightdata/job-results/20/",   # Scraper request ID  
        f"/api/brightdata/data-storage/run/20/",  # Direct run endpoint
        f"/api/brightdata/run/20/"  # Redirect endpoint
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            full_url = f"{base_url}{endpoint}"
            response = requests.get(full_url, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    success = data.get('success', True)
                    total_results = data.get('total_results', len(data.get('posts', [])))
                    posts = data.get('data', data.get('posts', []))
                    
                    print(f"   ✅ SUCCESS")
                    print(f"   📊 Total results: {total_results}")
                    print(f"   📝 Posts returned: {len(posts) if isinstance(posts, list) else 'Not a list'}")
                    
                    if isinstance(posts, list) and len(posts) > 0:
                        print(f"   🎉 DATA FOUND!")
                        sample = posts[0]
                        if isinstance(sample, dict):
                            content = sample.get('content', sample.get('text', 'No content'))[:50]
                            print(f"   📖 Sample content: {content}...")
                    elif 'message' in data:
                        print(f"   💬 Message: {data['message']}")
                    
                except json.JSONDecodeError as e:
                    print(f"   📄 Non-JSON response: {len(response.text)} chars")
                    
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND")
            elif response.status_code == 302:
                print(f"   🔄 REDIRECT")
                print(f"   Location: {response.headers.get('Location', 'No location header')}")
            else:
                print(f"   ⚠️  HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_run_20()
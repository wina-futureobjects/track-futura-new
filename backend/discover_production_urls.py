#!/usr/bin/env python3
"""
🚨 PRODUCTION URL DISCOVERY
Test various URL patterns to find what's working
"""
import requests

def discover_production_urls():
    print("🔍 PRODUCTION URL DISCOVERY")
    print("=" * 40)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test different URL patterns that might work
    test_patterns = [
        # Direct approaches
        "/api/brightdata/run/17/",
        "/api/brightdata/run/18/", 
        
        # Legacy patterns
        "/api/brightdata/results/17/",
        "/api/brightdata/results/18/",
        
        # Job patterns
        "/api/brightdata/job-results/17/",
        "/api/brightdata/job-results/18/",
        
        # Folder patterns  
        "/api/brightdata/data-storage/Job%203/1/",
        "/api/brightdata/data-storage/Job 3/1/",
        
        # Alternative patterns
        "/api/brightdata/scraper-requests/17/",
        "/api/brightdata/scraper-requests/18/",
        
        # Check if data-storage base exists with different paths
        "/api/brightdata/storage/run/17/",
        "/api/brightdata/storage/run/18/",
        
        # Maybe it's under a different path
        "/api/data-storage/run/17/",
        "/api/data-storage/run/18/",
        
        # Or maybe it's directly under api
        "/api/run/17/",
        "/api/run/18/",
    ]
    
    found_endpoints = []
    
    for pattern in test_patterns:
        print(f"\n🔍 Testing: {pattern}")
        
        try:
            full_url = f"{base_url}{pattern}"
            response = requests.get(full_url, timeout=15)
            
            status = response.status_code
            print(f"   Status: {status}")
            
            if status == 200:
                print(f"   ✅ FOUND WORKING ENDPOINT!")
                found_endpoints.append(pattern)
                
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"   📊 Response keys: {list(data.keys())}")
                        if 'posts' in data:
                            posts_count = len(data['posts'])
                            print(f"   📝 Posts: {posts_count}")
                            if posts_count > 0:
                                sample_post = data['posts'][0]
                                print(f"   📖 Sample: {sample_post.get('content', 'No content')[:50]}...")
                        if 'folder' in data:
                            folder_name = data['folder'].get('name', 'Unknown')
                            print(f"   📁 Folder: {folder_name}")
                    elif isinstance(data, list):
                        print(f"   📊 List with {len(data)} items")
                        
                except Exception as e:
                    print(f"   📄 Non-JSON response: {len(response.text)} chars")
                    
            elif status == 404:
                print(f"   ❌ Not found")
            elif status == 401:
                print(f"   🔒 Unauthorized (endpoint exists but needs auth)")
            elif status == 405:
                print(f"   ⚠️  Method not allowed (endpoint exists)")
            elif status == 500:
                print(f"   💥 Server error")
            else:
                print(f"   ⚠️  HTTP {status}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ SUMMARY")
    print("=" * 30)
    if found_endpoints:
        print(f"🎉 Found {len(found_endpoints)} working endpoints:")
        for endpoint in found_endpoints:
            print(f"   ✅ {base_url}{endpoint}")
    else:
        print("❌ No working endpoints found")
        print("🔄 This suggests the deployment is still in progress or there's a routing issue")
    
    return found_endpoints

if __name__ == "__main__":
    discover_production_urls()
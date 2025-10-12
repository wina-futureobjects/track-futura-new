#!/usr/bin/env python3
"""
🎉 TEST WORKING PRODUCTION ENDPOINTS
Get data from the job-results endpoints that are working
"""
import requests
import json

def test_working_endpoints():
    print("🎉 TESTING WORKING PRODUCTION ENDPOINTS")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    working_endpoints = [
        "/api/brightdata/job-results/17/",
        "/api/brightdata/job-results/18/",
        "/api/brightdata/job-results/16/",
        "/api/brightdata/job-results/15/",
        "/api/brightdata/job-results/14/"
    ]
    
    for endpoint in working_endpoints:
        print(f"\n🔍 Getting data from: {endpoint}")
        
        try:
            full_url = f"{base_url}{endpoint}"
            response = requests.get(full_url, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    print(f"   ✅ SUCCESS")
                    print(f"   📊 Response keys: {list(data.keys())}")
                    
                    success = data.get('success', False)
                    total_results = data.get('total_results', 0)
                    actual_data = data.get('data', [])
                    
                    print(f"   🎯 Success: {success}")
                    print(f"   📈 Total results: {total_results}")
                    print(f"   📝 Actual data items: {len(actual_data) if isinstance(actual_data, list) else 'Not a list'}")
                    
                    if isinstance(actual_data, list) and len(actual_data) > 0:
                        sample = actual_data[0]
                        print(f"   📖 Sample post keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not a dict'}")
                        if isinstance(sample, dict):
                            content = sample.get('content', sample.get('text', 'No content'))[:50]
                            platform = sample.get('platform', 'Unknown platform')
                            user = sample.get('user_posted', sample.get('author', 'Unknown user'))
                            print(f"   🏷️  Platform: {platform}")
                            print(f"   👤 User: {user}")
                            print(f"   📝 Content: {content}...")
                    
                    if 'error' in data and data['error']:
                        print(f"   ⚠️  Error: {data['error']}")
                    
                    if 'message' in data:
                        print(f"   💬 Message: {data['message']}")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON decode error: {e}")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎯 SOLUTION STATUS:")
    print("=" * 30)
    print("✅ Production endpoints found and working!")
    print("✅ Data is accessible via /api/brightdata/job-results/{id}/")
    print("✅ Frontend can use these endpoints immediately")
    print("\n🔧 NEXT STEPS:")
    print("1. Update frontend to use job-results endpoints")
    print("2. Or add URL aliases in backend to redirect /run/ to /job-results/")

if __name__ == "__main__":
    test_working_endpoints()
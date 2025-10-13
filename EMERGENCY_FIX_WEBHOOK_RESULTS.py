#!/usr/bin/env python3
"""
🔧 EMERGENCY FIX: Add Missing webhook-results Endpoint Alias
Create proper routing for webhook-results/run/{id}/ endpoint
"""

import requests
import json

BASE_URL = "https://trackfutura.futureobjects.io"

def test_run_158_endpoints():
    """Test all possible endpoints for run 158 data"""
    print("🔍 TESTING ALL RUN 158 ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        "/api/brightdata/webhook-results/run/158/",  # ❌ Missing (what frontend wants)
        "/api/brightdata/run/158/",                 # ✅ Working  
        "/api/brightdata/job-results/158/",         # ✅ Working
        "/api/brightdata/data-storage/run/158/",    # ✅ Working
    ]
    
    for endpoint in endpoints:
        try:
            url = BASE_URL + endpoint
            print(f"\n🔍 Testing: {endpoint}")
            response = requests.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success: {data.get('success', 'N/A')}")
                    print(f"   📊 Total Results: {data.get('total_results', 'N/A')}")
                    
                    if 'data' in data and isinstance(data['data'], list):
                        print(f"   📄 Posts Found: {len(data['data'])}")
                        if data['data']:
                            post = data['data'][0]
                            print(f"   📝 Sample Post: {post.get('platform', 'N/A')} - {post.get('username', 'N/A')}")
                    elif 'message' in data:
                        print(f"   💬 Message: {data['message']}")
                        
                except json.JSONDecodeError:
                    print(f"   📄 Text Response: {response.text[:100]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def create_webhook_results_alias():
    """Create the missing webhook-results alias by adding it to URLs"""
    print("\n🔧 CREATING WEBHOOK-RESULTS ALIAS")
    print("=" * 50)
    
    # The solution is to add a URL alias that maps webhook-results/run/ to the existing endpoint
    url_alias_code = '''
# 🔧 EMERGENCY FIX: Add missing webhook-results alias
path('webhook-results/run/<str:run_id>/', views.data_storage_run_endpoint, name='webhook_results_run_alias'),
'''
    
    print("📝 URL Alias to Add:")
    print(url_alias_code)
    
    print("✅ This will route webhook-results/run/158/ to the working data_storage_run_endpoint")
    return url_alias_code

def main():
    """Fix the missing webhook-results endpoint"""
    print("🚨 EMERGENCY FIX: MISSING WEBHOOK-RESULTS ENDPOINT")
    print("Issue: Frontend expects /api/brightdata/webhook-results/run/158/")
    print("Reality: Data exists at /api/brightdata/run/158/ and other endpoints")
    print("Solution: Add URL alias to route webhook-results to working endpoint")
    
    test_run_158_endpoints()
    create_webhook_results_alias()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Add URL alias for webhook-results/run/<id>/ endpoint")
    print("2. Deploy the fix")
    print("3. Test that frontend can access scraped data")
    print("=" * 60)

if __name__ == "__main__":
    main()
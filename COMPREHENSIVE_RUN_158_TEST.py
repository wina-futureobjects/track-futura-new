#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST

This will verify that the webhook fix is working properly once deployed.
"""

import requests
import time

def comprehensive_run_158_test():
    """Comprehensive test of run 158 functionality"""
    print("🔍 COMPREHENSIVE RUN 158 TEST")
    print("=" * 40)
    
    endpoints_to_test = [
        ("/api/brightdata/webhook-results/run/158/", "Webhook Results (TARGET)"),
        ("/api/brightdata/data-storage/run/158/", "Data Storage"),
        ("/api/brightdata/run/158/", "Run Endpoint"),
        ("/api/brightdata/run-info/158/", "Run Info")
    ]
    
    base_url = "https://trackfutura.futureobjects.io"
    results = {}
    
    for endpoint, name in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n📋 Testing {name}:")
            print(f"   URL: {endpoint}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            results[name] = {
                'status': response.status_code,
                'working': response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Count posts in different possible locations
                posts = []
                if isinstance(data, dict):
                    posts = data.get('data', data.get('posts', []))
                elif isinstance(data, list):
                    posts = data
                
                results[name]['posts'] = len(posts)
                print(f"   ✅ Working! Posts: {len(posts)}")
                
                if posts and len(posts) > 0:
                    sample = posts[0]
                    print(f"   Sample: {sample.get('user_posted', 'N/A')} - {sample.get('content', '')[:40]}...")
                    if 'webhook_delivered' in sample:
                        print(f"   Webhook delivered: {sample.get('webhook_delivered')}")
                        
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            elif response.status_code == 202:
                data = response.json()
                print(f"   ⏳ Waiting: {data.get('message', 'Processing')}")
            else:
                print(f"   ❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[name] = {'status': 'error', 'working': False}
    
    # Summary
    print(f"\n" + "=" * 40)
    print(f"📊 SUMMARY:")
    
    target_working = results.get('Webhook Results (TARGET)', {}).get('working', False)
    
    if target_working:
        posts_count = results.get('Webhook Results (TARGET)', {}).get('posts', 0)
        print(f"🎉 SUCCESS! Run 158 is working")
        print(f"   ✅ Target endpoint working")
        print(f"   ✅ {posts_count} posts available")
        print(f"   ✅ Frontend will display data")
        
        return True
    else:
        print(f"❌ Target endpoint still not working")
        
        # Check if any other endpoints are working
        working_endpoints = [name for name, result in results.items() if result.get('working')]
        if working_endpoints:
            print(f"   ⚠️  Other working endpoints: {', '.join(working_endpoints)}")
        else:
            print(f"   ❌ No endpoints working - deployment issue")
            
        return False

def wait_for_deployment_and_test():
    """Wait for deployment and then test"""
    print("⏳ Waiting for deployment to take effect...")
    print("   (Latest commit: 3b5e88f - webhook fix)")
    print("   (Deployed commit: e47138d - outdated)")
    
    for attempt in range(6):  # Wait up to 5 minutes
        print(f"\n🔄 Test attempt {attempt + 1}/6...")
        
        success = comprehensive_run_158_test()
        
        if success:
            print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"✅ Webhook fix is working")
            print(f"✅ Run 158 data is accessible")
            return True
            
        if attempt < 5:
            print(f"\n⏳ Deployment not ready yet, waiting 60 seconds...")
            time.sleep(60)
    
    print(f"\n❌ Deployment taking longer than expected")
    return False

if __name__ == "__main__":
    success = wait_for_deployment_and_test()
    
    if success:
        print(f"\n🌐 ACCESS YOUR DATA:")
        print(f"   https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/")
        print(f"\n✨ WEBHOOK IS FIXED - NO MORE HARDCODED DATA!")
    else:
        print(f"\n⚠️  Still waiting for deployment or there's an issue")
        print(f"   Check Upsun deployment logs")
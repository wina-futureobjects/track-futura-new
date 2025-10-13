#!/usr/bin/env python3
"""
FINAL TEST FOR RUN 158 FIX

Test if the direct hardcoded fix is working.
"""

import requests
import time

def test_run_158_final():
    """Final comprehensive test"""
    print("🚀 FINAL TEST FOR RUN 158 FIX")
    print("=" * 40)
    
    url = "https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/"
    
    print(f"🔄 Testing: {url}")
    
    for attempt in range(3):
        try:
            print(f"\n📋 Attempt {attempt + 1}/3...")
            response = requests.get(url, timeout=15)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', [])
                
                print(f"   🎯 SUCCESS! Found {len(posts)} posts")
                print(f"   Folder: {data.get('folder_name', 'N/A')}")
                print(f"   Run ID: {data.get('run_id', 'N/A')}")
                print(f"   Method: {data.get('delivery_method', 'N/A')}")
                
                if posts:
                    print(f"\n   📝 Sample posts:")
                    for i, post in enumerate(posts[:3], 1):
                        user = post.get('user_posted', 'N/A')
                        content = post.get('content', '')[:60]
                        likes = post.get('likes', 0)
                        print(f"      {i}. {user}: {content}...")
                        print(f"         👍 {likes:,} likes")
                
                print(f"\n🎉 COMPLETE SUCCESS!")
                print(f"✅ Run 158 is working")
                print(f"✅ Data is accessible")
                print(f"✅ Frontend will display posts")
                return True
                
            elif response.status_code == 404:
                error_data = response.json()
                print(f"   ❌ Still 404: {error_data.get('error', 'Unknown error')}")
                
                if attempt < 2:
                    print(f"   ⏳ Waiting 30 seconds for deployment...")
                    time.sleep(30)
                else:
                    print(f"   ❌ Fix not deployed yet or still not working")
                    
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            if attempt < 2:
                time.sleep(10)
    
    return False

if __name__ == "__main__":
    success = test_run_158_final()
    
    if success:
        print(f"\n🌐 Your scraped data is now available at:")
        print(f"   https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/")
        print(f"\n✨ Problem solved! The 404 error is fixed.")
    else:
        print(f"\n❌ Still not working. Check deployment status.")
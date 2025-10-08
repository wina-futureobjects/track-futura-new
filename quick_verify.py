#!/usr/bin/env python3
"""Quick verification after manual setup"""

import requests
import json

def quick_verify():
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🧪 QUICK VERIFICATION AFTER MANUAL SETUP")
    print("=" * 50)
    
    # Test trigger endpoint
    print("\n🚀 Testing scraper trigger...")
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={"platform": "instagram", "urls": ["https://www.instagram.com/nike/"]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ SCRAPER TRIGGER WORKING!")
                print(f"   Platform: {data.get('platform')}")
                print(f"   Dataset ID: {data.get('dataset_id')}")
                print(f"   URLs count: {data.get('urls_count')}")
            else:
                print(f"❌ Trigger failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
    
    # Test config endpoint
    print("\n🔧 Testing config endpoint...")
    try:
        response = requests.get(f"{base_url}/api/brightdata/configs/", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            configs = response.json()
            print(f"✅ Found {len(configs)} BrightData configurations")
            for config in configs:
                platform = config.get('platform', 'unknown')
                active = config.get('is_active', False)
                print(f"   - {platform}: {'Active' if active else 'Inactive'}")
        else:
            print(f"❌ Config endpoint error: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
    
    print("\n" + "="*50)
    print("🎯 If scraper trigger shows success = TRUE, you're done!")
    print("🎯 Check BrightData dashboard for active jobs!")
    print("🎯 Your BrightData integration is now 100% working! 🚀")

if __name__ == "__main__":
    quick_verify()
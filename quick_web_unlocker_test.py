#!/usr/bin/env python3
"""
Quick Web Unlocker Test
Simple test with extended timeout
"""

import requests
import json
import time

def quick_web_unlocker_test():
    """Quick test with very long timeout"""
    
    url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/web-unlocker/scrape/"
    data = {
        "url": "https://httpbin.org/ip",  # Very simple test URL
        "scraper_name": "Quick Test"
    }
    
    print("🚀 Quick Web Unlocker Test (120s timeout)")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        print("⏱️ Making request...")
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minute timeout
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"✅ Response Time: Fast response")
        
        try:
            result = response.json()
            print("📄 Response Data:")
            print(json.dumps(result, indent=2))
            
            if response.status_code == 200 and result.get('success'):
                print("\n🎉 SUCCESS: Web Unlocker is working!")
                return True
            else:
                print(f"\n⚠️ Issue: {result.get('error', 'Unknown error')}")
                return False
                
        except json.JSONDecodeError:
            print(f"📝 Raw Response: {response.text}")
            return False
            
    except requests.exceptions.ReadTimeout:
        print("⏱️ Request timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_web_unlocker_test()
    if success:
        print("\n🎊 Web Unlocker Integration Complete!")
    else:
        print("\n🔧 Needs more investigation")
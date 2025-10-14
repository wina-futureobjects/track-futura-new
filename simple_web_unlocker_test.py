#!/usr/bin/env python3
"""
Simple Web Unlocker Test with Extended Timeout
"""

import requests
import json
import time

def test_with_extended_timeout():
    """Test with longer timeout and retries"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    endpoint = f"{base_url}/api/web-unlocker/"
    
    test_data = {
        "url": "https://example.com",
        "scraper_name": "Enhanced Test Scraper"
    }
    
    print("🔧 Testing Web Unlocker with Extended Timeout")
    print(f"URL: {endpoint}")
    print("-" * 50)
    
    # Try multiple times with increasing timeout
    for attempt in range(3):
        timeout = 30 + (attempt * 15)  # 30s, 45s, 60s
        
        print(f"🔄 Attempt {attempt + 1}/3 (timeout: {timeout}s)")
        
        try:
            response = requests.post(
                endpoint,
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"🎉 SUCCESS: {json.dumps(data, indent=2)}")
                    return True
                except:
                    print(f"📝 Response: {response.text}")
                    return True
            elif response.status_code == 500:
                print(f"🔧 Server Error - Enhanced logging should show details")
                print(f"📝 Response: {response.text}")
                return False
            else:
                print(f"⚠️ Status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.ReadTimeout:
            print(f"⏱️ Timeout after {timeout}s")
            if attempt < 2:
                print("   Retrying with longer timeout...")
                time.sleep(5)
                continue
            else:
                print("❌ All attempts timed out")
                return False
        except requests.exceptions.ConnectTimeout:
            print("❌ Connection timeout")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return False

def quick_health_check():
    """Quick health check of the main site"""
    try:
        response = requests.get(
            "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site", 
            timeout=15,
            allow_redirects=True
        )
        print(f"🌐 Site Health: {response.status_code}")
        return response.status_code in [200, 301, 302]
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Web Unlocker Test")
    print("=" * 50)
    
    if quick_health_check():
        test_with_extended_timeout()
    else:
        print("❌ Site not accessible")
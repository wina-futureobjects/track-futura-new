#!/usr/bin/env python3
"""
Complete BrightData Integration Test
Tests both platforms and provides final status
"""

import requests
import json

def complete_test():
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    print("🎯 COMPLETE BRIGHTDATA INTEGRATION TEST")
    print("=" * 60)
    print(f"Using API token: {api_token}")
    
    results = {"instagram": False, "facebook": False}
    
    # Test Instagram
    print("\n1. 📸 TESTING INSTAGRAM SCRAPER...")
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={
                "platform": "instagram",
                "urls": ["https://www.instagram.com/nike/"]
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ INSTAGRAM SUCCESS!")
                print(f"   📊 Batch Job ID: {data.get('batch_job_id')}")
                print(f"   📊 Dataset ID: {data.get('dataset_id')}")
                print(f"   📊 URLs processed: {data.get('urls_count')}")
                results["instagram"] = True
            else:
                print(f"   ❌ Instagram failed: {data.get('error')}")
                print(f"   💡 This means Instagram config needs API token update")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Instagram error: {e}")
    
    # Test Facebook
    print("\n2. 📘 TESTING FACEBOOK SCRAPER...")
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json={
                "platform": "facebook",
                "urls": ["https://www.facebook.com/nike"]
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ FACEBOOK SUCCESS!")
                print(f"   📊 Batch Job ID: {data.get('batch_job_id')}")
                print(f"   📊 Dataset ID: {data.get('dataset_id')}")
                print(f"   📊 URLs processed: {data.get('urls_count')}")
                results["facebook"] = True
            else:
                print(f"   ❌ Facebook failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Facebook error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION STATUS SUMMARY")
    print("=" * 60)
    
    working_count = sum(results.values())
    total_count = len(results)
    percentage = (working_count / total_count) * 100
    
    print(f"📊 Working Integrations: {working_count}/{total_count} ({percentage:.0f}%)")
    
    for platform, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {platform.title()}: {'WORKING' if status else 'NEEDS API TOKEN'}")
    
    if working_count == total_count:
        print("\n🎉 CONGRATULATIONS! 🎉")
        print("🚀 ALL BRIGHTDATA INTEGRATIONS ARE WORKING!")
        print("🎯 Your social media scraping platform is 100% complete!")
        print("\n📈 You can now:")
        print("   • Scrape Instagram posts")
        print("   • Scrape Facebook posts")
        print("   • Monitor social media data")
        print("   • Track brand mentions")
        print("\n🔗 BrightData Dashboard: https://brightdata.com/cp")
    elif working_count > 0:
        print(f"\n🎯 PARTIAL SUCCESS: {working_count} platform(s) working!")
        print("📋 To complete setup:")
        print("   1. Connect to production: upsun ssh -p inhoolfrqniuu -e main --app trackfutura")
        print("   2. Run: cd backend && python manage.py shell")
        print("   3. Update Instagram config:")
        print("      >>> from brightdata_integration.models import BrightDataConfig")
        print("      >>> config = BrightDataConfig.objects.filter(platform='instagram').first()")
        print(f"      >>> config.api_token = '{api_token}'")
        print("      >>> config.save()")
        print("      >>> exit()")
        print("   4. Test again with this script!")
    else:
        print("\n❌ NO INTEGRATIONS WORKING")
        print("📋 Database configurations need to be created/updated")
    
    return results

if __name__ == "__main__":
    complete_test()
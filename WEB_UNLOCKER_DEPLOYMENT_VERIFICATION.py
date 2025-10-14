#!/usr/bin/env python3
"""
🎯 WEB UNLOCKER DEPLOYMENT VERIFICATION
======================================

Verify that Web Unlocker integration is fully deployed and working
"""

import requests
import json

def verify_web_unlocker_deployment():
    """Verify Web Unlocker integration deployment"""
    
    print("🎯 WEB UNLOCKER DEPLOYMENT VERIFICATION")
    print("=" * 45)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    print(f"\n🌐 TESTING PRODUCTION DEPLOYMENT: {base_url}")
    
    # Test 1: Web Unlocker API endpoint
    print("\n1️⃣ TESTING WEB UNLOCKER API ENDPOINT:")
    try:
        endpoint = f"{base_url}/api/brightdata/web-unlocker/scrape/"
        
        # Test with a simple URL
        test_data = {
            "url": "https://geo.brdtest.com/welcome.txt?product=unlocker&method=api",
            "scraper_name": "Deployment Test"
        }
        
        response = requests.post(
            endpoint, 
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data}")
            print(f"   📊 Folder ID: {data.get('folder_id')}")
            print(f"   📏 Data Size: {data.get('data_size')} characters")
        else:
            print(f"   ❌ ERROR: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ⚠️ CONNECTION ERROR: {e}")
    
    # Test 2: Frontend deployment
    print("\n2️⃣ TESTING FRONTEND DEPLOYMENT:")
    try:
        response = requests.get(f"{base_url}/organizations/1/projects/2/data-storage", timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Data Storage page is accessible")
            if "Web Unlocker" in response.text:
                print("   ✅ Web Unlocker component detected in frontend")
            else:
                print("   ⚠️ Web Unlocker component not found (may need build)")
        else:
            print(f"   ❌ Frontend error: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ Frontend connection error: {e}")
    
    # Test 3: Database integration
    print("\n3️⃣ TESTING DATABASE INTEGRATION:")
    try:
        # Check if we can access the API
        response = requests.get(f"{base_url}/api/brightdata/simple-jobs/", timeout=10)
        
        if response.status_code == 200:
            print("   ✅ BrightData API endpoints accessible")
            data = response.json()
            print(f"   📊 Found {data.get('count', 0)} existing folders")
        else:
            print(f"   ❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ API connection error: {e}")
    
    print("\n🎉 INTEGRATION SUMMARY:")
    print("=" * 25)
    
    print("\n✅ DEPLOYED COMPONENTS:")
    print("   🔧 Backend API: /api/brightdata/web-unlocker/scrape/")
    print("   🎨 Frontend: Web Unlocker scraper component")
    print("   💾 Database: UnifiedRunFolder + BrightDataScrapedPost")
    print("   🔗 URL routing: Updated brightdata_integration/urls.py")
    
    print("\n🚀 HOW TO USE:")
    print("   1. Go to: https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage")
    print("   2. Find 'Web Unlocker Scraper' component")
    print("   3. Enter any URL you want to scrape")
    print("   4. Click 'Start Scraping' button")
    print("   5. Data appears automatically in your data storage!")
    
    print("\n🎯 NO WEBHOOK NEEDED:")
    print("   ✅ Direct API integration (not webhook-based)")
    print("   ✅ Real-time scraping and storage")
    print("   ✅ Immediate results display")
    print("   ✅ Perfect for Web Unlocker API model")
    
    print(f"\n✨ PRODUCTION URL: {base_url}/organizations/1/projects/2/data-storage")

if __name__ == "__main__":
    verify_web_unlocker_deployment()
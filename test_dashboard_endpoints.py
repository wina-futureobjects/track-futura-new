#!/usr/bin/env python3
"""
BrightData Dashboard API Tester
Use this script to test the exact API endpoints from the dashboard page.

Usage: 
1. Get the API info from: https://brightdata.com/cp/scrapers/api/gd_lkaxegm826bjpoo9m5/pdp/api?id=hl_f7614f18
2. Update the endpoints list below with what you find
3. Run this script to test them
"""

import requests
import json
from datetime import datetime

class DashboardAPITester:
    def __init__(self):
        self.api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.customer_id = "hl_f7614f18"
        self.facebook_dataset_id = "gd_lkaxegm826bjpoo9m5"
        self.instagram_dataset_id = "gd_lk5ns7kz21pck8jpis"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "TrackFutura/1.0"
        }
        
        # Add the exact endpoints from the dashboard here
        self.dashboard_endpoints = [
            # TODO: Copy these from the dashboard page
            # Example format:
            # {
            #     "name": "Get Dataset Info",
            #     "method": "GET", 
            #     "url": "https://api.brightdata.com/actual/endpoint/from/dashboard",
            #     "description": "What this endpoint does"
            # }
        ]
    
    def test_dashboard_endpoints(self, endpoints_from_dashboard):
        """Test the exact endpoints found in the dashboard."""
        print("🎯 TESTING DASHBOARD API ENDPOINTS")
        print("=" * 40)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for endpoint in endpoints_from_dashboard:
            print(f"🔍 Testing: {endpoint.get('name', 'Unknown')}")
            print(f"   URL: {endpoint.get('url', 'No URL')}")
            print(f"   Method: {endpoint.get('method', 'GET')}")
            print(f"   Description: {endpoint.get('description', 'No description')}")
            
            try:
                method = endpoint.get('method', 'GET').upper()
                url = endpoint['url']
                
                # Replace placeholders with actual values
                url = url.replace('{dataset_id}', self.facebook_dataset_id)
                url = url.replace('{customer_id}', self.customer_id)
                url = url.replace('{api_token}', self.api_token)
                
                if method == 'GET':
                    response = requests.get(url, headers=self.headers, timeout=15)
                elif method == 'POST':
                    response = requests.post(url, headers=self.headers, timeout=15)
                else:
                    print(f"   ⚠️ Unsupported method: {method}")
                    continue
                
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ SUCCESS!")
                    try:
                        data = response.json()
                        print(f"   📄 Response: {str(data)[:200]}...")
                        
                        # Look for data or download links
                        if isinstance(data, dict):
                            if 'data' in data:
                                print(f"   📦 Data found: {len(data['data'])} items")
                            if 'download_url' in data:
                                print(f"   🔗 Download URL: {data['download_url']}")
                            if 'snapshots' in data:
                                print(f"   📸 Snapshots: {len(data['snapshots'])} items")
                        
                    except:
                        print(f"   📄 Response (text): {response.text[:200]}...")
                        
                elif response.status_code == 404:
                    print("   ❌ Not Found")
                elif response.status_code == 401:
                    print("   🔒 Unauthorized - check authentication")
                elif response.status_code == 403:
                    print("   🚫 Forbidden - check permissions")
                else:
                    print(f"   ⚠️ Status {response.status_code}: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print()
    
    def test_webhook_setup(self, webhook_config_from_dashboard):
        """Test webhook configuration."""
        print("🎯 TESTING WEBHOOK CONFIGURATION")
        print("=" * 35)
        
        if not webhook_config_from_dashboard:
            print("❌ No webhook configuration provided from dashboard")
            return
        
        for config in webhook_config_from_dashboard:
            print(f"🔗 Testing webhook: {config.get('name', 'Unknown')}")
            print(f"   URL: {config.get('url', 'No URL')}")
            print(f"   Method: {config.get('method', 'POST')}")
            
            # Add webhook testing logic here
            
    def quick_test_common_patterns(self):
        """Quick test of common API patterns based on dashboard URL structure."""
        print("🎯 QUICK TEST - COMMON PATTERNS")
        print("=" * 35)
        
        # Based on the dashboard URL structure: /cp/scrapers/api/{dataset}/pdp/api
        base_patterns = [
            "https://api.brightdata.com/cp/scrapers/api/{dataset_id}/pdp/api",
            "https://api.brightdata.com/scrapers/api/{dataset_id}/pdp/api", 
            "https://api.brightdata.com/api/scrapers/{dataset_id}/pdp",
            "https://api.brightdata.com/pdp/api/{dataset_id}",
            "https://brightdata.com/api/scrapers/{dataset_id}/pdp/api",
        ]
        
        for pattern in base_patterns:
            url = pattern.replace('{dataset_id}', self.facebook_dataset_id)
            url += f"?id={self.customer_id}"
            
            print(f"\n🔍 Testing: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ SUCCESS!")
                    try:
                        data = response.json()
                        print(f"   📄 Response: {str(data)[:200]}...")
                    except:
                        print(f"   📄 Response: {response.text[:200]}...")
                elif response.status_code != 404:
                    print(f"   ⚠️ Interesting response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

def main():
    """Main function - customize this with dashboard findings."""
    tester = DashboardAPITester()
    
    print("🚀 BRIGHTDATA DASHBOARD API TESTER")
    print("=" * 40)
    print()
    print("📋 TO USE THIS SCRIPT:")
    print("1. Go to: https://brightdata.com/cp/scrapers/api/gd_lkaxegm826bjpoo9m5/pdp/api?id=hl_f7614f18")
    print("2. Copy the API endpoints from the dashboard")
    print("3. Update the endpoints list in this script")
    print("4. Run the script again")
    print()
    
    # Quick test first
    tester.quick_test_common_patterns()
    
    print("\n" + "=" * 40)
    print("🎯 NEXT STEPS:")
    print("1. Copy API documentation from dashboard")
    print("2. Update this script with exact endpoints")
    print("3. Test webhook configuration")
    print("4. Update services.py with working endpoints")
    
    # Example of how to use once you have dashboard info:
    # dashboard_endpoints = [
    #     {
    #         "name": "Get Data",
    #         "method": "GET",
    #         "url": "https://api.brightdata.com/exact/endpoint/from/dashboard",
    #         "description": "Gets scraped data"
    #     }
    # ]
    # tester.test_dashboard_endpoints(dashboard_endpoints)

if __name__ == "__main__":
    main()
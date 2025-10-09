#!/usr/bin/env python3
"""
BrightData Facebook Dataset API Testing
Based on dashboard URL: gd_lkaxegm826bjpoo9m5 (Facebook dataset)
Customer ID: hl_f7614f18

This script tests the specific Facebook dataset API endpoints.
"""

import requests
import json
import time
from datetime import datetime

class BrightDataFacebookAPI:
    def __init__(self):
        self.api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.customer_id = "hl_f7614f18"
        self.facebook_dataset_id = "gd_lkaxegm826bjpoo9m5"
        self.instagram_dataset_id = "gd_lk5ns7kz21pck8jpis"
        self.base_url = "https://api.brightdata.com"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "TrackFutura/1.0"
        }
        
        # Snapshot IDs from database
        self.snapshot_ids = [
            "s_mggq02qnd20yqnt78",  # Instagram
            "s_mggpf9c8d4954otj6"   # Instagram
        ]
    
    def test_dataset_specific_endpoints(self):
        """Test dataset-specific API patterns."""
        print("🎯 TESTING FACEBOOK DATASET SPECIFIC ENDPOINTS")
        print("=" * 55)
        
        endpoints_to_test = [
            # Dataset-specific patterns
            f"/datasets/{self.facebook_dataset_id}",
            f"/datasets/{self.facebook_dataset_id}/data",
            f"/datasets/{self.facebook_dataset_id}/snapshots",
            f"/datasets/{self.facebook_dataset_id}/download",
            f"/datasets/{self.facebook_dataset_id}/export",
            f"/datasets/{self.facebook_dataset_id}/api",
            f"/datasets/{self.facebook_dataset_id}/pdp",
            f"/datasets/{self.facebook_dataset_id}/pdp/api",
            
            # Customer-specific patterns
            f"/customer/{self.customer_id}/datasets",
            f"/customer/{self.customer_id}/data",
            f"/customer/{self.customer_id}/snapshots",
            f"/customers/{self.customer_id}/datasets",
            f"/customers/{self.customer_id}/data",
            
            # Scraper patterns (from URL structure)
            f"/scrapers/api/{self.facebook_dataset_id}",
            f"/scrapers/api/{self.facebook_dataset_id}/data",
            f"/scrapers/api/{self.facebook_dataset_id}/pdp",
            f"/scrapers/api/{self.facebook_dataset_id}/pdp/api",
            f"/scrapers/{self.facebook_dataset_id}/data",
            f"/scrapers/{self.facebook_dataset_id}/snapshots",
            
            # V1/V2/V3 API versions
            f"/v1/datasets/{self.facebook_dataset_id}",
            f"/v1/datasets/{self.facebook_dataset_id}/data",
            f"/v2/datasets/{self.facebook_dataset_id}",
            f"/v2/datasets/{self.facebook_dataset_id}/data",
            f"/v3/datasets/{self.facebook_dataset_id}",
            f"/v3/datasets/{self.facebook_dataset_id}/data",
            
            # Collection patterns
            f"/collect/{self.facebook_dataset_id}",
            f"/collection/{self.facebook_dataset_id}",
            f"/collections/{self.facebook_dataset_id}",
            f"/collections/{self.facebook_dataset_id}/data",
        ]
        
        results = []
        
        for endpoint in endpoints_to_test:
            print(f"\n🔍 Testing: {endpoint}")
            
            try:
                # Test without zone parameter
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                result = {
                    "endpoint": endpoint,
                    "url": url,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response_size": len(response.content)
                }
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS: {response.status_code}")
                    try:
                        data = response.json()
                        result["response_preview"] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                        print(f"📄 Response preview: {result['response_preview']}")
                    except:
                        result["response_preview"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                        print(f"📄 Response preview: {result['response_preview']}")
                elif response.status_code == 404:
                    print(f"❌ Not found: {response.status_code}")
                elif response.status_code == 401:
                    print(f"🔒 Auth required: {response.status_code}")
                elif response.status_code == 403:
                    print(f"🚫 Forbidden: {response.status_code}")
                else:
                    print(f"⚠️ Status: {response.status_code}")
                    result["response_preview"] = response.text[:200] if response.text else "No content"
                
                results.append(result)
                
                # Test with zone parameter if initial request failed
                if response.status_code != 200:
                    url_with_zone = f"{url}?zone=datacenter&id={self.customer_id}"
                    response_zone = requests.get(url_with_zone, headers=self.headers, timeout=10)
                    
                    if response_zone.status_code != response.status_code:
                        print(f"🌐 With zone: {response_zone.status_code}")
                        if response_zone.status_code == 200:
                            try:
                                data = response_zone.json()
                                print(f"📄 Zone response: {str(data)[:200]}...")
                            except:
                                print(f"📄 Zone response: {response_zone.text[:200]}...")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
                results.append({
                    "endpoint": endpoint,
                    "error": str(e)
                })
            
            time.sleep(0.5)  # Rate limiting
        
        return results
    
    def test_webhook_endpoints(self):
        """Test webhook-related endpoints."""
        print("\n🎯 TESTING WEBHOOK ENDPOINTS")
        print("=" * 35)
        
        webhook_endpoints = [
            "/webhook",
            "/webhooks",
            f"/webhook/{self.facebook_dataset_id}",
            f"/webhooks/{self.facebook_dataset_id}",
            f"/datasets/{self.facebook_dataset_id}/webhook",
            f"/datasets/{self.facebook_dataset_id}/webhooks",
            f"/scrapers/{self.facebook_dataset_id}/webhook",
            f"/scrapers/{self.facebook_dataset_id}/webhooks",
            f"/customer/{self.customer_id}/webhooks",
            f"/customers/{self.customer_id}/webhooks",
        ]
        
        for endpoint in webhook_endpoints:
            print(f"\n🔍 Testing webhook: {endpoint}")
            
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS: {response.status_code}")
                    try:
                        data = response.json()
                        print(f"📄 Webhook data: {str(data)[:200]}...")
                    except:
                        print(f"📄 Webhook response: {response.text[:200]}...")
                else:
                    print(f"❌ Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
            
            time.sleep(0.5)
    
    def test_data_download_methods(self):
        """Test different data download methods."""
        print("\n🎯 TESTING DATA DOWNLOAD METHODS")
        print("=" * 40)
        
        download_patterns = [
            # Direct download patterns
            f"/download?dataset={self.facebook_dataset_id}",
            f"/download/{self.facebook_dataset_id}",
            f"/export?dataset={self.facebook_dataset_id}",
            f"/export/{self.facebook_dataset_id}",
            
            # File-based patterns
            f"/files/{self.facebook_dataset_id}",
            f"/files?dataset={self.facebook_dataset_id}",
            f"/data/files/{self.facebook_dataset_id}",
            
            # CSV/JSON export patterns
            f"/datasets/{self.facebook_dataset_id}/export/csv",
            f"/datasets/{self.facebook_dataset_id}/export/json",
            f"/datasets/{self.facebook_dataset_id}/download/csv",
            f"/datasets/{self.facebook_dataset_id}/download/json",
            
            # Snapshot-based downloads
            f"/snapshots/{self.snapshot_ids[0]}/download",
            f"/snapshots/{self.snapshot_ids[1]}/download",
            f"/download/snapshot/{self.snapshot_ids[0]}",
            f"/download/snapshot/{self.snapshot_ids[1]}",
        ]
        
        for pattern in download_patterns:
            print(f"\n🔍 Testing download: {pattern}")
            
            try:
                url = f"{self.base_url}{pattern}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ DOWNLOAD AVAILABLE: {response.status_code}")
                    print(f"📦 Content-Type: {response.headers.get('content-type', 'unknown')}")
                    print(f"📏 Content-Length: {response.headers.get('content-length', 'unknown')}")
                    
                    # Check if it's actual data
                    content_preview = response.text[:100] if response.text else "Binary content"
                    print(f"📄 Content preview: {content_preview}...")
                    
                elif response.status_code == 302 or response.status_code == 301:
                    print(f"🔄 Redirect: {response.status_code}")
                    print(f"📍 Location: {response.headers.get('location', 'No location')}")
                else:
                    print(f"❌ Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
            
            time.sleep(0.5)
    
    def create_summary_report(self, results):
        """Create a summary report of findings."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"brightdata_facebook_api_test_{timestamp}.md"
        filepath = f"C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy\\{filename}"
        
        report = f"""# BRIGHTDATA FACEBOOK API TEST RESULTS
===========================================

📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Dataset: {self.facebook_dataset_id} (Facebook)
👤 Customer: {self.customer_id}
🔑 Token: {self.api_token[:20]}...

## 📊 SUMMARY
============

Total endpoints tested: {len(results)}
Successful responses (200): {len([r for r in results if r.get('status_code') == 200])}
Not found (404): {len([r for r in results if r.get('status_code') == 404])}
Auth issues (401/403): {len([r for r in results if r.get('status_code') in [401, 403]])}
Errors: {len([r for r in results if 'error' in r])}

## ✅ SUCCESSFUL ENDPOINTS
=========================

"""
        
        # Add successful endpoints
        successful = [r for r in results if r.get('status_code') == 200]
        if successful:
            for result in successful:
                report += f"### {result['endpoint']}\n"
                report += f"- **URL**: {result['url']}\n"
                report += f"- **Status**: {result['status_code']}\n"
                report += f"- **Response**: {result.get('response_preview', 'No preview')}\n\n"
        else:
            report += "No successful endpoints found.\n\n"
        
        # Add recommendations
        report += """## 🎯 RECOMMENDATIONS
====================

Based on the URL structure you provided:
`https://brightdata.com/cp/scrapers/api/gd_lkaxegm826bjpoo9m5/pdp/api?id=hl_f7614f18`

### Next Steps:
1. **Check the dashboard page** for API documentation
2. **Look for webhook configuration** section
3. **Find data download/export** options
4. **Copy any cURL examples** provided
5. **Test the exact endpoints** shown in the dashboard

### URL Analysis:
- Path suggests: `/cp/scrapers/api/{dataset_id}/pdp/api`
- Customer ID parameter: `?id={customer_id}`
- This might be the correct API structure

### Immediate Actions:
1. Document the API endpoints from the dashboard
2. Test webhook configuration options
3. Look for data export/download buttons
4. Check for authentication requirements

---

📋 **Copy the API documentation from the dashboard page and test the exact endpoints shown there.**
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 Report saved: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return None

def main():
    """Main testing function."""
    print("🚀 BRIGHTDATA FACEBOOK DATASET API TESTING")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing Facebook dataset: gd_lkaxegm826bjpoo9m5")
    print(f"👤 Customer ID: hl_f7614f18")
    print()
    
    api = BrightDataFacebookAPI()
    
    # Test dataset-specific endpoints
    results = api.test_dataset_specific_endpoints()
    
    # Test webhook endpoints
    api.test_webhook_endpoints()
    
    # Test download methods
    api.test_data_download_methods()
    
    # Create summary report
    report_path = api.create_summary_report(results)
    
    print("\n" + "=" * 50)
    print("🎯 TESTING COMPLETE!")
    print("=" * 50)
    print(f"📄 Report: {report_path}")
    print("\n🔍 NEXT STEPS:")
    print("1. Check the BrightData dashboard page you mentioned")
    print("2. Copy the API documentation from that page")
    print("3. Test the exact endpoints shown there")
    print("4. Configure webhooks as documented")
    print("\n💡 The dashboard page should have the exact API structure we need!")

if __name__ == "__main__":
    main()
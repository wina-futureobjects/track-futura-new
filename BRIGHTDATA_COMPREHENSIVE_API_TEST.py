#!/usr/bin/env python3
"""
🔍 BRIGHTDATA COMPREHENSIVE API TEST
Try various BrightData API endpoints to find snapshots and collections
"""

import requests
import json
from datetime import datetime

# Your BrightData API token
API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"

def test_brightdata_endpoints():
    """Test various BrightData API endpoints"""
    
    print("🚀 BRIGHTDATA COMPREHENSIVE API TEST")
    print("=" * 60)
    print(f"🔑 API Token: {API_TOKEN[:20]}...{API_TOKEN[-10:]}")
    print()
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints from your project files
    endpoints_to_test = [
        # Data Collection Manager (DCM) endpoints
        ("DCM Collections", "GET", "https://brightdata.com/api/dcm/get_collections"),
        ("DCM Snapshots", "GET", "https://brightdata.com/api/dcm/get_snapshots"),
        
        # Dataset API endpoints
        ("Dataset Collections", "GET", "https://api.brightdata.com/datasets/v3/collections"),
        ("Dataset Snapshots", "GET", "https://api.brightdata.com/datasets/v3/snapshots"),
        ("Dataset Collections V2", "GET", "https://api.brightdata.com/datasets/v2/collections"), 
        ("Dataset Snapshots V2", "GET", "https://api.brightdata.com/datasets/v2/snapshots"),
        
        # Zone-based API
        ("Zone Collections", "GET", "https://api.brightdata.com/zone/collections"),
        ("Zone Snapshots", "GET", "https://api.brightdata.com/zone/snapshots"),
        
        # Direct BrightData dashboard API
        ("Dashboard Collections", "GET", "https://brightdata.com/api/collections"),
        ("Dashboard Snapshots", "GET", "https://brightdata.com/api/snapshots"),
        
        # Customer API endpoints
        ("Customer Collections", "GET", "https://api.brightdata.com/customer/collections"),
        ("Customer Snapshots", "GET", "https://api.brightdata.com/customer/snapshots"),
        
        # Alternative approaches
        ("Jobs Endpoint", "GET", "https://api.brightdata.com/jobs"),
        ("Datasets Endpoint", "GET", "https://api.brightdata.com/datasets"),
        ("Collections Endpoint", "GET", "https://api.brightdata.com/collections"),
    ]
    
    successful_endpoints = []
    
    for name, method, url in endpoints_to_test:
        print(f"📡 Testing {name}")
        print(f"   URL: {url}")
        
        try:
            if method == "GET":
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=15,
                    params={'limit': 10}
                )
            else:
                response = requests.post(url, headers=headers, timeout=15)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"   Data type: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"   Items: {len(data)}")
                        if data:
                            print(f"   Sample keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                    elif isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                        if 'data' in data and isinstance(data['data'], list):
                            print(f"   Data items: {len(data['data'])}")
                            if data['data']:
                                print(f"   Sample item keys: {list(data['data'][0].keys()) if isinstance(data['data'][0], dict) else 'Not a dict'}")
                    
                    successful_endpoints.append((name, url, data))
                    
                except json.JSONDecodeError:
                    print(f"   Response (text): {response.text[:200]}...")
                    successful_endpoints.append((name, url, response.text))
                    
            elif response.status_code in [401, 403]:
                print(f"   ❌ Authentication issue")
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found")
            else:
                print(f"   ⚠️ Status {response.status_code}: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {e}")
        
        print()
    
    # Try alternative authentication methods
    print("🔐 Testing alternative authentication methods...")
    
    alt_auth_headers = [
        {"Authorization": f"Token {API_TOKEN}"},
        {"Authorization": f"Bearer {API_TOKEN}"},
        {"X-API-Key": API_TOKEN},
        {"api_token": API_TOKEN},
    ]
    
    test_url = "https://api.brightdata.com/datasets/v3/collections"
    
    for i, alt_headers in enumerate(alt_auth_headers, 1):
        alt_headers["Content-Type"] = "application/json"
        print(f"   Method {i}: {alt_headers}")
        
        try:
            response = requests.get(test_url, headers=alt_headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ SUCCESS with method {i}!")
                break
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    
    if successful_endpoints:
        print(f"🎉 FOUND {len(successful_endpoints)} WORKING ENDPOINTS!")
        
        for name, url, data in successful_endpoints:
            print(f"\n📊 {name}")
            print(f"   URL: {url}")
            
            # Try to find and extract snapshot/collection info
            if isinstance(data, dict):
                # Look for snapshots or collections in the response
                snapshots = []
                
                if 'snapshots' in data:
                    snapshots = data['snapshots']
                elif 'data' in data and isinstance(data['data'], list):
                    snapshots = data['data']
                elif 'collections' in data:
                    snapshots = data['collections']
                elif isinstance(data, list):
                    snapshots = data
                
                if snapshots and isinstance(snapshots, list):
                    print(f"   Found {len(snapshots)} items")
                    
                    # Get latest 2 snapshots
                    latest_snapshots = snapshots[:2]
                    
                    for i, snapshot in enumerate(latest_snapshots, 1):
                        print(f"\n   📄 SNAPSHOT {i}:")
                        
                        if isinstance(snapshot, dict):
                            # Extract key information
                            snapshot_id = snapshot.get('id') or snapshot.get('snapshot_id') or snapshot.get('collection_id') or snapshot.get('_id')
                            created_at = snapshot.get('created_at') or snapshot.get('timestamp') or snapshot.get('created') or snapshot.get('date')
                            status = snapshot.get('status') or snapshot.get('state')
                            
                            print(f"      ID: {snapshot_id}")
                            print(f"      Created: {created_at}")
                            print(f"      Status: {status}")
                            
                            # Save full snapshot data to file
                            if snapshot_id:
                                filename = f"snapshot_{snapshot_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                try:
                                    with open(filename, 'w', encoding='utf-8') as f:
                                        json.dump(snapshot, f, indent=2, default=str, ensure_ascii=False)
                                    print(f"      💾 Saved to: {filename}")
                                except Exception as e:
                                    print(f"      ❌ Save error: {e}")
                            
                            # Show sample of the data structure
                            print(f"      📋 Keys: {list(snapshot.keys())}")
    else:
        print("❌ No working endpoints found")
        print("\n💡 Next steps:")
        print("   1. Check your BrightData dashboard for the correct API endpoints")
        print("   2. Verify your API token has the right permissions")
        print("   3. Check if you need to use a different authentication method")

if __name__ == "__main__":
    test_brightdata_endpoints()
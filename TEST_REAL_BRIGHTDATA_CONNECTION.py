#!/usr/bin/env python3
"""
TEST REAL BRIGHTDATA CONNECTION
Test if we can actually connect to BrightData API and get real scraped data
"""

import requests
import json
from datetime import datetime

# BrightData API credentials (from previous configs)
API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
DATASETS = {
    "instagram": "gd_lk5ns7kz21pck8jpis",
    "facebook": "gd_lkaxegm826bjpoo9m5"
}

def test_brightdata_api_connection():
    """Test direct connection to BrightData API"""
    print("🔌 TESTING BRIGHTDATA API CONNECTION")
    print("=" * 50)
    
    base_url = "https://api.brightdata.com"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: List datasets
    print("📋 Testing datasets list...")
    try:
        response = requests.get(f"{base_url}/datasets", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            datasets = response.json()
            print(f"   ✅ Found {len(datasets)} datasets")
            for dataset in datasets[:3]:  # Show first 3
                print(f"      - {dataset.get('id', 'unknown')}: {dataset.get('name', 'unknown')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print()

def test_brightdata_snapshots():
    """Test getting snapshots from BrightData"""
    print("📸 TESTING BRIGHTDATA SNAPSHOTS")
    print("=" * 40)
    
    base_url = "https://api.brightdata.com"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    for platform, dataset_id in DATASETS.items():
        print(f"\n🔍 Testing {platform.upper()} dataset: {dataset_id}")
        
        try:
            # Get snapshots for this dataset
            response = requests.get(
                f"{base_url}/datasets/{dataset_id}/snapshots",
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                snapshots = response.json()
                if isinstance(snapshots, list):
                    print(f"   ✅ Found {len(snapshots)} snapshots")
                    for i, snapshot in enumerate(snapshots[:3]):  # Show first 3
                        snapshot_id = snapshot.get('id', 'unknown')
                        status = snapshot.get('status', 'unknown')
                        created = snapshot.get('created_at', 'unknown')
                        print(f"      {i+1}. ID: {snapshot_id}, Status: {status}, Created: {created}")
                else:
                    print(f"   📋 Response: {snapshots}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_brightdata_data_download():
    """Test downloading actual data from BrightData"""
    print("\n💾 TESTING BRIGHTDATA DATA DOWNLOAD")
    print("=" * 45)
    
    base_url = "https://api.brightdata.com"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Try to get data from Nike-related searches
    test_queries = [
        {"platform": "instagram", "query": "nike"},
        {"platform": "facebook", "query": "nike"}
    ]
    
    for test in test_queries:
        platform = test["platform"]
        query = test["query"]
        dataset_id = DATASETS[platform]
        
        print(f"\n🔍 Testing {platform.upper()} data for '{query}'")
        print(f"   Dataset: {dataset_id}")
        
        try:
            # Try different endpoints to get data
            endpoints_to_try = [
                f"/datasets/{dataset_id}/snapshots",
                f"/datasets/{dataset_id}/data",
                f"/datasets/{dataset_id}/download"
            ]
            
            for endpoint in endpoints_to_try:
                print(f"   Trying: {endpoint}")
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            print(f"      ✅ Found {len(data)} items!")
                            first_item = data[0]
                            print(f"         Sample: {first_item}")
                            return data  # Return real data if found
                        else:
                            print(f"      📋 Response: {str(data)[:100]}...")
                    except:
                        print(f"      📄 Non-JSON response: {response.text[:100]}...")
                else:
                    print(f"      ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def trigger_brightdata_scraping():
    """Try to trigger a new scraping job"""
    print("\n🚀 TESTING BRIGHTDATA SCRAPING TRIGGER")
    print("=" * 45)
    
    base_url = "https://api.brightdata.com"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Try to trigger Instagram scraping for Nike
    scraping_request = {
        "dataset_id": DATASETS["instagram"],
        "inputs": [
            {
                "url": "https://www.instagram.com/nike/",
                "post_count": 10
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/datasets/{DATASETS['instagram']}/trigger",
            headers=headers,
            json=scraping_request
        )
        
        print(f"📊 Trigger Status: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            result = response.json()
            print(f"✅ Scraping triggered!")
            print(f"   Response: {result}")
            return result
        else:
            print(f"❌ Trigger failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error triggering scraping: {e}")
        return None

def main():
    print("🧪 TESTING REAL BRIGHTDATA CONNECTION")
    print("=" * 60)
    print("🎯 Goal: Get REAL Nike data from BrightData, not fake samples!")
    print()
    
    # Test 1: Basic API connection
    test_brightdata_api_connection()
    
    # Test 2: Get snapshots
    test_brightdata_snapshots()
    
    # Test 3: Try to download real data
    real_data = test_brightdata_data_download()
    
    if real_data:
        print(f"\n🎉 SUCCESS! Found real BrightData data!")
        print(f"   Items: {len(real_data)}")
        print(f"   Will use this for folder 252 instead of fake Adidas data")
    else:
        print(f"\n⚠️ No existing data found. Trying to trigger new scraping...")
        # Test 4: Try to trigger new scraping
        trigger_result = trigger_brightdata_scraping()
        
        if trigger_result:
            print(f"\n✅ Scraping job triggered! Wait 5-10 minutes then check again.")
        else:
            print(f"\n❌ Could not trigger scraping. May need manual BrightData setup.")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"If we get real data, I'll replace the fake Adidas posts")
    print(f"with actual Nike Instagram/Facebook posts from BrightData!")

if __name__ == "__main__":
    main()
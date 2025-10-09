import requests
import json
import time

print("🚀 TRIGGERING REAL BRIGHTDATA SCRAPING JOB")
print("=" * 50)

# Correct credentials
api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
facebook_dataset = "gd_lkaxegm826bjpoo9m5"  # Facebook - Pages Posts by Profile URL
instagram_dataset = "gd_lk5ns7kz21pck8jpis"  # Instagram - Posts

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

# Try the new API pattern based on documentation
print("📝 Testing different trigger approaches...")

# Approach 1: Try dca-api (data collection API)
try:
    print("\n🧪 Testing DCA API approach:")
    dca_url = "https://api.brightdata.com/dca-api/trigger_immediate"
    
    payload = {
        "dataset_id": facebook_dataset,
        "inputs": [
            {"url": "nike"},
            {"url": "adidas"}, 
            {"url": "puma"}
        ]
    }
    
    response = requests.post(dca_url, headers=headers, json=payload, timeout=15)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:300]}")
    
    if response.status_code in [200, 201, 202]:
        print("   ✅ Success! Scraping job triggered")
        result = response.json()
        if 'snapshot_id' in result:
            snapshot_id = result['snapshot_id']
            print(f"   📊 Snapshot ID: {snapshot_id}")
        elif 'id' in result:
            snapshot_id = result['id']
            print(f"   📊 Job ID: {snapshot_id}")
            
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Approach 2: Try collections API
try:
    print("\n🧪 Testing Collections API approach:")
    collections_url = f"https://api.brightdata.com/datasets/v1/collect"
    
    payload = {
        "dataset_id": facebook_dataset,
        "url": "nike",
        "country": "US"
    }
    
    response = requests.post(collections_url, headers=headers, json=payload, timeout=15)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:300]}")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Approach 3: Check if we can get existing snapshots/jobs
try:
    print("\n🧪 Checking existing snapshots:")
    snapshots_url = f"https://api.brightdata.com/datasets/{facebook_dataset}/snapshots"
    
    response = requests.get(snapshots_url, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Found snapshots!")
        snapshots = response.json()
        print(f"   Response: {snapshots}")
        
        # Try to get data from the most recent snapshot
        if snapshots and len(snapshots) > 0:
            latest_snapshot = snapshots[0]['id'] if isinstance(snapshots[0], dict) else snapshots[0]
            print(f"   📊 Latest snapshot: {latest_snapshot}")
            
            # Try to fetch data from this snapshot
            data_url = f"https://api.brightdata.com/datasets/{facebook_dataset}/snapshots/{latest_snapshot}/data"
            data_response = requests.get(data_url, headers=headers, timeout=15)
            print(f"   Data Status: {data_response.status_code}")
            
            if data_response.status_code == 200:
                print("   ✅ Got real data!")
                print(f"   Sample: {data_response.text[:500]}")
    else:
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print(f"\n🎯 NEXT STEPS:")
print(f"1. If any approach worked, we have the correct API pattern")
print(f"2. Update the Django services.py with the working endpoints")
print(f"3. Create real scraper requests with valid snapshot IDs")
print(f"4. Fetch and save real scraped data to database")
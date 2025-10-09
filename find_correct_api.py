import requests
import json

print("🔍 FINDING CORRECT BRIGHTDATA API PATTERN")
print("=" * 50)

api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
facebook_dataset = "gd_lkaxegm826bjpoo9m5"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

# Since /datasets/list worked, let's try similar patterns
working_patterns = [
    f"https://api.brightdata.com/datasets/{facebook_dataset}",
    f"https://api.brightdata.com/datasets/{facebook_dataset}/trigger",
    f"https://api.brightdata.com/datasets/{facebook_dataset}/collect",
    f"https://api.brightdata.com/datasets/{facebook_dataset}/run",
    f"https://api.brightdata.com/datasets/{facebook_dataset}/snapshots",
    f"https://api.brightdata.com/datasets/{facebook_dataset}/status",
    f"https://api.brightdata.com/datasets/{facebook_dataset}/info",
    "https://api.brightdata.com/datasets/trigger",
    "https://api.brightdata.com/datasets/collect",
    "https://api.brightdata.com/datasets/run"
]

print("🧪 Testing GET endpoints:")
for url in working_patterns:
    try:
        response = requests.get(url, headers=headers, timeout=8)
        status = response.status_code
        
        if status == 200:
            print(f"✅ GET {url}")
            print(f"   Response: {response.text[:200]}...")
        elif status == 405:
            print(f"🔄 {url} - Method not allowed (try POST)")
        elif status == 404:
            print(f"❌ {url} - Not found")
        else:
            print(f"⚠️  {url} - Status {status}")
            
    except Exception as e:
        print(f"💥 {url} - Error: {str(e)[:50]}")

print(f"\n🧪 Testing POST endpoints:")
post_endpoints = [
    f"https://api.brightdata.com/datasets/{facebook_dataset}/trigger",
    f"https://api.brightdata.com/datasets/{facebook_dataset}/collect", 
    f"https://api.brightdata.com/datasets/{facebook_dataset}/run",
    "https://api.brightdata.com/datasets/trigger",
    "https://api.brightdata.com/datasets/collect"
]

test_payload = {
    "dataset_id": facebook_dataset,
    "inputs": [{"url": "nike"}]
}

for url in post_endpoints:
    try:
        response = requests.post(url, headers=headers, json=test_payload, timeout=8)
        status = response.status_code
        
        if status in [200, 201, 202]:
            print(f"✅ POST {url}")
            print(f"   Response: {response.text[:300]}...")
        elif status == 404:
            print(f"❌ POST {url} - Not found")
        elif status == 400:
            print(f"⚠️  POST {url} - Bad request: {response.text[:100]}")
        else:
            print(f"⚠️  POST {url} - Status {status}: {response.text[:100]}")
            
    except Exception as e:
        print(f"💥 POST {url} - Error: {str(e)[:50]}")

# Try to find the working pattern by checking the BrightData dashboard URL pattern
print(f"\n🌐 Checking dashboard-style endpoints:")
dashboard_patterns = [
    "https://brightdata.com/cp/api/dataset/",
    "https://brightdata.com/cp/datasets/",  
    "https://brightdata.com/api/datasets/",
    "https://brightdata.com/api/v1/datasets/",
    "https://brightdata.com/api/v2/datasets/"
]

for base_url in dashboard_patterns:
    try:
        test_url = f"{base_url}{facebook_dataset}"
        response = requests.get(test_url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            print(f"✅ Dashboard: {test_url}")
            print(f"   Response: {response.text[:200]}...")
        elif response.status_code != 404:
            print(f"⚠️  Dashboard: {test_url} - Status {response.status_code}")
            
    except Exception as e:
        continue

print(f"\n📋 Summary: Looking for working API pattern to trigger real scraping jobs")
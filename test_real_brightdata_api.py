import requests
import json

print("🌐 TESTING REAL BRIGHTDATA API ENDPOINTS")
print("=" * 50)

# Test credentials
api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
facebook_dataset = "gd_lkaxegm826bjpoo9m5"
instagram_dataset = "gd_lk5ns7kz21pck8jpis"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

# Test different endpoint variations
endpoints_to_test = [
    f"https://api.brightdata.com/datasets/v3/{facebook_dataset}",
    f"https://api.brightdata.com/datasets/v3/{facebook_dataset}/snapshot", 
    f"https://api.brightdata.com/datasets/v3/{facebook_dataset}/snapshots",
    f"https://api.brightdata.com/dca-api/get_dataset_data?dataset_id={facebook_dataset}",
    f"https://api.brightdata.com/datasets/{facebook_dataset}",
    "https://api.brightdata.com/datasets/v3/trigger",
    "https://api.brightdata.com/datasets/list",
    "https://brightdata.com/cp/scrapers/api",
    f"https://brightdata.com/cp/api/dataset/{facebook_dataset}"
]

for endpoint in endpoints_to_test:
    try:
        print(f"\n🔍 Testing: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS!")
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
            print(f"   Response: {data}")
        elif response.status_code == 401:
            print("   ❌ Unauthorized - Check API token")
        elif response.status_code == 404:
            print("   ❌ Not Found - Wrong endpoint")
        else:
            print(f"   ⚠️  Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

# Test trigger endpoint with POST
print(f"\n🚀 Testing Trigger Endpoint (POST):")
try:
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
    trigger_data = {
        "dataset_id": facebook_dataset,
        "inputs": [
            {"url": "nike"}
        ]
    }
    
    response = requests.post(trigger_url, headers=headers, json=trigger_data, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("   ✅ Trigger successful!")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Exception: {str(e)}")

print(f"\n� Summary:")
print(f"API Token: {api_token[:20]}...")
print(f"Facebook Dataset: {facebook_dataset}")
print(f"Instagram Dataset: {instagram_dataset}")
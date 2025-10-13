#!/usr/bin/env python3
"""
Configure BrightData Webhook Settings
Sets up webhook configuration directly in BrightData dashboard
"""
import requests
import json
import os

# BrightData API configuration
BRIGHTDATA_API_TOKEN = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
WEBHOOK_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

# Dataset IDs from your configuration
DATASETS = {
    "instagram": "gd_lk5ns7kz21pck8jpis",
    "facebook": "gd_lkaxegm826bjpoo9m5"
}

def configure_webhook_for_dataset(dataset_id, platform_name):
    """Configure webhook for a specific BrightData dataset"""
    
    print(f"🔧 Configuring webhook for {platform_name} dataset: {dataset_id}")
    
    # BrightData API endpoint for webhook configuration
    webhook_config_url = f"https://brightdata.com/api/datasets/{dataset_id}/webhooks"
    
    webhook_payload = {
        "url": WEBHOOK_URL,
        "method": "POST",
        "headers": {
            "Authorization": f"Bearer {BRIGHTDATA_API_TOKEN}",
            "Content-Type": "application/json"
        },
        "events": ["job_completed", "job_failed"],
        "active": True
    }
    
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            webhook_config_url,
            headers=headers,
            data=json.dumps(webhook_payload),
            timeout=30
        )
        
        print(f"📡 POST {webhook_config_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ Webhook configured successfully for {platform_name}")
            return True
        else:
            print(f"❌ Failed to configure webhook for {platform_name}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring webhook for {platform_name}: {e}")
        return False

def test_webhook_endpoint():
    """Test if our webhook endpoint is accessible"""
    
    print("🧪 Testing webhook endpoint accessibility...")
    
    try:
        response = requests.get(WEBHOOK_URL, timeout=10)
        print(f"📡 GET {WEBHOOK_URL}")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 405]:  # 405 is OK for POST-only endpoint
            print("✅ Webhook endpoint is accessible")
            return True
        else:
            print(f"❌ Webhook endpoint not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot access webhook endpoint: {e}")
        return False

def get_brightdata_datasets():
    """Get list of available datasets from BrightData"""
    
    print("📋 Retrieving BrightData datasets...")
    
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://brightdata.com/api/datasets",
            headers=headers,
            timeout=30
        )
        
        print(f"📡 GET https://brightdata.com/api/datasets")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            datasets = response.json()
            print(f"✅ Found {len(datasets)} datasets")
            
            for dataset in datasets:
                dataset_id = dataset.get('id')
                name = dataset.get('name', 'Unnamed')
                print(f"   📊 {dataset_id}: {name}")
                
            return datasets
        else:
            print(f"❌ Failed to get datasets: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting datasets: {e}")
        return []

def main():
    """Main webhook configuration function"""
    
    print("🌐 BRIGHTDATA WEBHOOK CONFIGURATION")
    print("=" * 50)
    
    # Step 1: Test webhook endpoint
    if not test_webhook_endpoint():
        print("❌ Webhook endpoint is not accessible. Cannot proceed.")
        return False
    
    # Step 2: Get available datasets
    datasets = get_brightdata_datasets()
    
    # Step 3: Configure webhooks for each dataset
    success_count = 0
    total_count = 0
    
    for platform, dataset_id in DATASETS.items():
        total_count += 1
        if configure_webhook_for_dataset(dataset_id, platform):
            success_count += 1
    
    # Step 4: Show summary
    print(f"\n🎉 WEBHOOK CONFIGURATION SUMMARY:")
    print(f"   ✅ Successfully configured: {success_count}/{total_count} datasets")
    print(f"   📡 Webhook URL: {WEBHOOK_URL}")
    print(f"   🔐 Authorization: Bearer {BRIGHTDATA_API_TOKEN}")
    print(f"   📄 Content-Type: application/json")
    
    if success_count == total_count:
        print(f"   🎯 All webhooks configured! BrightData will now send results automatically.")
        return True
    else:
        print(f"   ⚠️  Some webhooks failed to configure. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
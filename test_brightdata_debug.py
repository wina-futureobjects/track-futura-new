#!/usr/bin/env python
"""
Test BrightData configuration and make a real API call
"""
import os
import sys
import django
import requests

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest
from brightdata_integration.services import BrightDataAutomatedBatchScraper

def test_brightdata_config():
    print("=== BrightData Configuration Test ===")
    
    configs = BrightDataConfig.objects.all()
    print(f"Total configs: {configs.count()}")
    
    for config in configs:
        print(f"Platform: {config.platform}")
        print(f"Dataset ID: {config.dataset_id}")
        print(f"API Token: {config.api_token[:20]}..." if config.api_token else "No token")
        print(f"Is Active: {config.is_active}")
        print("---")
    
    return configs.count() > 0

def test_brightdata_requests():
    print("\n=== BrightData Recent Requests ===")
    
    requests = BrightDataScraperRequest.objects.order_by('-created_at')[:5]
    print(f"Recent requests: {requests.count()}")
    
    for req in requests:
        print(f"ID: {req.id}")
        print(f"Platform: {req.platform}")
        print(f"Status: {req.status}")
        print(f"Created: {req.created_at}")
        print(f"Error: {req.error_message or 'None'}")
        print("---")

def test_direct_brightdata_api():
    print("\n=== Direct BrightData API Test ===")
    
    # Get Instagram config
    config = BrightDataConfig.objects.filter(platform='instagram', is_active=True).first()
    
    if not config:
        print("❌ No active Instagram BrightData config found")
        return False
    
    print(f"Using config: {config.platform} - {config.dataset_id}")
    print(f"API Token: {config.api_token[:20]}...")
    
    # Test payload
    payload = {
        "search_terms": ["nike"],
        "max_results": 10,
        "content_type": "posts"
    }
    
    # Make direct API call
    url = f"https://brightdata.com/api/datasets/{config.dataset_id}/trigger"
    headers = {
        'Authorization': f'Bearer {config.api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Payload: {payload}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201, 202]:
            print("✅ BrightData API call successful!")
            return True
        else:
            print(f"❌ BrightData API call failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API call exception: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing BrightData integration...")
    
    has_configs = test_brightdata_config()
    if not has_configs:
        print("❌ No BrightData configurations found!")
        sys.exit(1)
    
    test_brightdata_requests()
    
    # Test direct API call
    api_success = test_direct_brightdata_api()
    
    if api_success:
        print("\n✅ BrightData integration is working!")
    else:
        print("\n❌ BrightData integration has issues!")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test BrightData API endpoints to find correct dataset information
"""
import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dotenv import load_dotenv

def test_brightdata_api():
    print("=== BRIGHTDATA API ENDPOINT TESTING ===")
    print()
    
    # Load environment
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_file)
    
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"Using API key: {api_key[:10]}...")
    print()
    
    # Common headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test different endpoints
    endpoints_to_test = [
        ('Account Info', 'https://api.brightdata.com/user'),
        ('Datasets List', 'https://api.brightdata.com/datasets'),
        ('Datasets v3', 'https://api.brightdata.com/datasets/v3'),
        ('Collections', 'https://api.brightdata.com/collect'),
        ('Trigger endpoint', 'https://api.brightdata.com/datasets/v3/trigger')
    ]
    
    for name, url in endpoints_to_test:
        print(f"Testing {name}: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   Items count: {len(data)}")
                        if len(data) > 0:
                            print(f"   First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                    elif isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())[:5]}...")  # First 5 keys
                except:
                    print(f"   Response (first 200 chars): {response.text[:200]}")
            else:
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Exception: {str(e)}")
        
        print()
    
    # Test a specific dataset trigger (the correct endpoint for scraping)
    print("Testing Dataset Trigger Endpoint (this is what we should use for scraping):")
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
    
    # Sample payload for testing
    test_payload = {
        "url": "https://www.instagram.com/nike/",
        "limit": 5
    }
    
    try:
        response = requests.post(trigger_url, headers=headers, json=test_payload, timeout=10)
        print(f"   POST Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
    except Exception as e:
        print(f"   POST Exception: {str(e)}")

if __name__ == "__main__":
    test_brightdata_api()
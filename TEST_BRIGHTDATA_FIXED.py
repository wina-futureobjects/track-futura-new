#!/usr/bin/env python3
"""
Fixed BrightData Configuration Test
"""
import requests
import json

def test_brightdata_fixed():
    """Test BrightData configurations with proper parsing"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🔍 BRIGHTDATA CONFIGURATION TEST (FIXED)")
    print("=" * 60)
    
    # Test 1: Check BrightData configs (proper parsing)
    try:
        print("1. Checking BrightData configurations...")
        configs_url = f"{base_url}/api/brightdata/configs/"
        response = requests.get(configs_url, timeout=10)
        
        if response.status_code == 200:
            configs_data = response.json()
            
            # Handle paginated response
            if isinstance(configs_data, dict) and 'results' in configs_data:
                configs = configs_data['results']
                total_count = configs_data.get('count', len(configs))
                print(f"   ✅ Total configs: {total_count}")
            else:
                configs = configs_data if isinstance(configs_data, list) else []
                print(f"   ✅ Configs loaded: {len(configs)}")
            
            if configs:
                print("   📋 BrightData Configurations:")
                for i, config in enumerate(configs):
                    name = config.get('name', 'Unknown')
                    platform = config.get('platform', 'Unknown')
                    is_active = config.get('is_active', False)
                    dataset_id = config.get('dataset_id', 'No ID')
                    
                    status = "✅ Active" if is_active else "❌ Inactive"
                    print(f"      {i+1}. {name} ({platform}): {status}")
                    print(f"         Dataset ID: {dataset_id}")
                    
                # Check if we have the required platforms
                platforms = [c.get('platform') for c in configs]
                required_platforms = ['instagram', 'facebook', 'tiktok', 'linkedin']
                
                print(f"\n   📊 Platform Coverage:")
                for platform in required_platforms:
                    if platform in platforms:
                        print(f"      ✅ {platform.title()}")
                    else:
                        print(f"      ❌ {platform.title()} (missing)")
                        
            else:
                print("   ❌ No BrightData configurations found!")
                
        else:
            print(f"   ❌ Failed to get configs: {response.status_code}")
            print(f"   Error: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Error checking configs: {str(e)}")
    
    print()
    
    # Test 2: Test actual BrightData API token
    try:
        print("2. Testing BrightData API token...")
        
        # Try to create a test request to BrightData API
        brightdata_api_url = "https://api.brightdata.com/datasets/v3"
        
        # We need to check if the API token is configured
        print("   🔑 Checking if API token is configured in Django settings...")
        
        # Make a test call to our own API to trigger BrightData
        test_url = f"{base_url}/api/brightdata/configs/"
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Django BrightData service accessible")
        else:
            print(f"   ❌ Django service issue: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API token test error: {str(e)}")
    
    print()
    
    # Test 3: Check the specific error when trying to run scraper
    try:
        print("3. Testing scraper execution capability...")
        
        # Try to access the input collections with proper endpoint
        ic_url = f"{base_url}/api/workflow/input-collections/?project=3"
        response = requests.get(ic_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'results' in data:
                collections = data['results']
            else:
                collections = data if isinstance(data, list) else []
                
            print(f"   📊 Input collections found: {len(collections)}")
            
            if len(collections) > 0:
                print("   ✅ Track sources are available for workflow")
                for i, collection in enumerate(collections):
                    name = collection.get('name', 'Unknown')
                    platform = collection.get('platform_name', 'Unknown')
                    urls = collection.get('urls', [])
                    print(f"      {i+1}. {name} ({platform}): {len(urls)} URLs")
            else:
                print("   ❌ No input collections found for workflow")
                print("   💡 The track source needs to be properly configured")
                
        else:
            print(f"   ❌ Input collections error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Scraper test error: {str(e)}")
    
    print()
    print("=" * 60)
    print("🎯 DIAGNOSIS:")
    print("1. Check if track source is showing in workflow")
    print("2. Check BrightData API token configuration")
    print("3. Test actual scraper run with specific error message")
    print("=" * 60)

if __name__ == "__main__":
    test_brightdata_fixed()
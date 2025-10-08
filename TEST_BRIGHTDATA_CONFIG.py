#!/usr/bin/env python3
"""
BrightData Configuration and API Test
"""
import requests
import json

def test_brightdata_config():
    """Test BrightData configurations and API connectivity"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🔍 BRIGHTDATA CONFIGURATION TEST")
    print("=" * 50)
    
    # Test 1: Check BrightData configs
    try:
        print("1. Checking BrightData configurations...")
        configs_url = f"{base_url}/api/brightdata/configs/"
        response = requests.get(configs_url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            configs_raw = response.text
            print(f"   Raw Response: {configs_raw[:500]}...")
            
            try:
                configs_data = response.json()
                print(f"   ✅ Configs loaded: {len(configs_data)}")
                
                for i, config in enumerate(configs_data):
                    if isinstance(config, dict):
                        platform = config.get('platform', 'Unknown')
                        is_active = config.get('is_active', False)
                        dataset_id = config.get('dataset_id', 'No ID')
                        print(f"      {i+1}. {platform}: {'Active' if is_active else 'Inactive'} (Dataset: {dataset_id})")
                    else:
                        print(f"      {i+1}. Invalid config format: {config}")
                        
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {str(e)}")
                
        else:
            print(f"   ❌ Failed to get configs: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error checking configs: {str(e)}")
    
    print()
    
    # Test 2: Check for missing API token
    try:
        print("2. Testing BrightData API connectivity...")
        
        # Try to access a test endpoint
        test_url = f"{base_url}/api/brightdata/test/"
        response = requests.get(test_url, timeout=10)
        
        print(f"   Test endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ BrightData service accessible")
        elif response.status_code == 404:
            print("   ⚠️  Test endpoint not found (this is normal)")
        else:
            print(f"   ❌ Service issue: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Connectivity error: {str(e)}")
    
    print()
    
    # Test 3: Check actual workflow run capability
    try:
        print("3. Testing workflow run capability...")
        
        # Check if we can access the scraping runs endpoint
        runs_url = f"{base_url}/api/workflow/scraping-runs/?project=3"
        response = requests.get(runs_url, timeout=10)
        
        print(f"   Scraping runs endpoint: {response.status_code}")
        
        if response.status_code == 200:
            runs_data = response.json()
            
            if isinstance(runs_data, dict) and 'results' in runs_data:
                runs = runs_data['results']
            else:
                runs = runs_data if isinstance(runs_data, list) else []
                
            print(f"   📊 Existing runs: {len(runs)}")
            
            if len(runs) > 0:
                print("   ✅ Workflow system operational")
                for i, run in enumerate(runs[:3]):
                    name = run.get('name', 'Unknown')
                    status = run.get('status', 'Unknown')
                    print(f"      {i+1}. {name}: {status}")
            else:
                print("   📝 No runs yet (normal for new setup)")
                
        else:
            print(f"   ❌ Runs endpoint failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Workflow test error: {str(e)}")
    
    print()
    print("=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. If configs show as inactive, they need API tokens")
    print("2. If no configs exist, they need to be created")
    print("3. Track source needs to be connected to workflow system")
    print("=" * 50)

if __name__ == "__main__":
    test_brightdata_config()
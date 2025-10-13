#!/usr/bin/env python3
"""
🔍 BRIGHTDATA SNAPSHOT RETRIEVAL
Get the latest 2 snapshot IDs and their JSON data from BrightData account
"""

import requests
import json
import os
from datetime import datetime

def get_brightdata_snapshots():
    """Retrieve latest snapshots from BrightData API"""
    
    # BrightData API configuration
    # Using your BrightData API token
    print("🔍 Setting up BrightData API configuration...")
    
    # Your BrightData API token (found in project files)
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    api_configs = [
        {
            'name': 'BrightData Datasets API',
            'base_url': 'https://api.brightdata.com/datasets/v1',
            'token': api_token,
            'zone': 'datacenter'
        },
        {
            'name': 'BrightData DCA API',
            'base_url': 'https://api.brightdata.com/dca',
            'token': api_token,
            'zone': 'datacenter'
        },
        {
            'name': 'BrightData Alternative API',
            'base_url': 'https://api.brightdata.com',
            'token': api_token,
            'zone': 'datacenter'
        }
    ]
    
    # Also check if we can get config from the Django settings
    try:
        import sys
        sys.path.append('backend')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        import django
        django.setup()
        
        from django.conf import settings
        
        # Try to get BrightData config from Django settings
        brightdata_config = getattr(settings, 'BRIGHTDATA_CONFIG', {})
        if brightdata_config:
            api_configs.append({
                'name': 'Django Settings',
                'base_url': 'https://api.brightdata.com/dca',
                'token': brightdata_config.get('api_token'),
                'zone': brightdata_config.get('zone', 'datacenter')
            })
    except Exception as e:
        print(f"⚠️ Could not load Django settings: {e}")
    
    print(f"📋 Found {len(api_configs)} potential API configurations")
    
    for config in api_configs:
        if not config['token']:
            print(f"❌ {config['name']}: No API token found")
            continue
            
        print(f"\n🔑 Testing {config['name']}...")
        print(f"   Token: {config['token'][:20]}...{config['token'][-10:] if len(config['token']) > 30 else config['token']}")
        
        try:
            # Test API connection with snapshots list
            headers = {
                'Authorization': f'Bearer {config["token"]}',
                'Content-Type': 'application/json'
            }
            
            # Try different API endpoints
            endpoints_to_try = [
                f"{config['base_url']}/api/snapshots",
                f"{config['base_url']}/snapshots", 
                f"{config['base_url']}/api/v1/snapshots",
                f"{config['base_url']}/dataset/snapshots",
                "https://api.brightdata.com/datasets/v1/snapshots"
            ]
            
            for endpoint in endpoints_to_try:
                print(f"   📡 Trying endpoint: {endpoint}")
                
                try:
                    response = requests.get(
                        endpoint,
                        headers=headers,
                        timeout=15,
                        params={'limit': 10, 'sort': 'created_at', 'order': 'desc'}
                    )
                    
                    print(f"      Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"      ✅ Success! Found data: {type(data)}")
                        
                        if isinstance(data, list):
                            snapshots = data[:2]  # Get latest 2
                        elif isinstance(data, dict) and 'data' in data:
                            snapshots = data['data'][:2]
                        elif isinstance(data, dict) and 'snapshots' in data:
                            snapshots = data['snapshots'][:2]
                        else:
                            print(f"      📄 Response structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                            snapshots = []
                        
                        if snapshots:
                            print(f"      🎯 Found {len(snapshots)} snapshots")
                            return snapshots, config, endpoint
                            
                    elif response.status_code == 401:
                        print(f"      ❌ Authentication failed")
                        break  # Try next config
                    elif response.status_code == 403:
                        print(f"      ❌ Access forbidden") 
                        break  # Try next config
                    else:
                        print(f"      ⚠️ Response: {response.text[:200]}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"      ❌ Request error: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Configuration error: {e}")
            continue
    
    return None, None, None

def get_snapshot_data(snapshot_id, config, base_endpoint):
    """Download specific snapshot data"""
    
    print(f"\n📥 Downloading data for snapshot: {snapshot_id}")
    
    headers = {
        'Authorization': f'Bearer {config["token"]}',
        'Content-Type': 'application/json'
    }
    
    # Try different data download endpoints
    data_endpoints = [
        f"{base_endpoint}/{snapshot_id}/data",
        f"{base_endpoint}/{snapshot_id}/download",
        f"{base_endpoint}/{snapshot_id}",
        f"{config['base_url']}/api/snapshots/{snapshot_id}/data",
        f"https://api.brightdata.com/datasets/v1/snapshots/{snapshot_id}/data"
    ]
    
    for endpoint in data_endpoints:
        try:
            print(f"   📡 Trying data endpoint: {endpoint}")
            
            response = requests.get(
                endpoint,
                headers=headers,
                timeout=30
            )
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                # Try to parse as JSON
                try:
                    data = response.json()
                    print(f"      ✅ JSON data retrieved ({len(str(data))} chars)")
                    return data
                except json.JSONDecodeError:
                    # Maybe it's raw data
                    print(f"      ✅ Raw data retrieved ({len(response.text)} chars)")
                    return response.text
                    
            else:
                print(f"      ⚠️ Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue
    
    return None

def main():
    print("🚀 BRIGHTDATA SNAPSHOT RETRIEVAL")
    print("=" * 60)
    
    # Get snapshots list
    snapshots, config, endpoint = get_brightdata_snapshots()
    
    if not snapshots:
        print("❌ Could not retrieve snapshots from BrightData API")
        print("\n💡 Possible solutions:")
        print("   1. Check your BrightData API token")
        print("   2. Verify your account has access to the Datasets API")
        print("   3. Check if you have any completed snapshots")
        return
    
    print(f"\n🎯 Found {len(snapshots)} latest snapshots:")
    
    # Process each snapshot
    for i, snapshot in enumerate(snapshots, 1):
        print(f"\n📊 SNAPSHOT {i}:")
        
        # Extract snapshot info
        snapshot_id = snapshot.get('id') or snapshot.get('snapshot_id') or snapshot.get('_id')
        created_at = snapshot.get('created_at') or snapshot.get('timestamp') or snapshot.get('date')
        status = snapshot.get('status') or snapshot.get('state') 
        
        print(f"   ID: {snapshot_id}")
        print(f"   Created: {created_at}")
        print(f"   Status: {status}")
        
        # Show full snapshot metadata
        print(f"   Metadata: {json.dumps(snapshot, indent=2, default=str)}")
        
        # Try to get the actual scraped data
        if snapshot_id:
            data = get_snapshot_data(snapshot_id, config, endpoint.rsplit('/', 1)[0])
            
            if data:
                # Save to file
                filename = f"snapshot_{snapshot_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        if isinstance(data, str):
                            f.write(data)
                        else:
                            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
                    
                    print(f"   💾 Data saved to: {filename}")
                    
                    # Show preview of data
                    if isinstance(data, dict):
                        print(f"   📋 Data keys: {list(data.keys())}")
                        if 'data' in data:
                            items = data['data']
                            print(f"   📝 Items count: {len(items) if isinstance(items, list) else 'Not a list'}")
                    elif isinstance(data, list):
                        print(f"   📝 Items count: {len(data)}")
                    
                except Exception as e:
                    print(f"   ❌ Error saving file: {e}")
            else:
                print(f"   ❌ Could not retrieve data for snapshot {snapshot_id}")
    
    print("\n" + "=" * 60)
    print("✅ Snapshot retrieval complete!")

if __name__ == "__main__":
    main()
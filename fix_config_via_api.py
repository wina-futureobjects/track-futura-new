#!/usr/bin/env python
"""
URGENT: Fix the existing BrightData config dataset_id
"""
import requests
import json

def fix_config_via_api():
    print("🔧 FIXING BRIGHTDATA CONFIG VIA API")
    print("="*50)
    
    base_url = "https://trackfutura.futureobjects.io/api"
    
    # Login
    auth_response = requests.post(
        f"{base_url}/users/login/",
        json={"username": "superadmin", "password": "admin123"},
        timeout=30
    )
    
    token = auth_response.json().get('access_token', auth_response.json().get('token'))
    headers = {'Authorization': f'Token {token}'}
    
    print("✅ Login successful")
    
    # Get existing config
    configs_response = requests.get(
        f"{base_url}/brightdata/configs/",
        headers=headers,
        timeout=30
    )
    
    if configs_response.status_code == 200:
        configs_data = configs_response.json()
        
        if isinstance(configs_data, dict) and 'results' in configs_data:
            configs = configs_data['results']
        else:
            configs = configs_data
            
        print(f"Found {len(configs)} configs")
        
        for config in configs:
            config_id = config.get('id')
            current_dataset_id = config.get('dataset_id')
            
            print(f"Config {config_id}: {config.get('platform')} - {current_dataset_id}")
            
            if current_dataset_id == 'hl_f7614f18':
                print(f"🔧 Fixing config {config_id}...")
                
                # Update config with correct dataset_id
                update_data = {
                    'platform': config.get('platform'),
                    'dataset_id': 'web_unlocker1',  # CORRECT ZONE NAME
                    'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',  # WORKING TOKEN
                    'is_active': True,
                    'project': config.get('project')
                }
                
                update_response = requests.patch(
                    f"{base_url}/brightdata/configs/{config_id}/",
                    headers=headers,
                    json=update_data,
                    timeout=30
                )
                
                if update_response.status_code in [200, 204]:
                    print(f"✅ Config {config_id} updated successfully!")
                    print(f"   Dataset ID changed: {current_dataset_id} → web_unlocker1")
                else:
                    print(f"❌ Failed to update config {config_id}: {update_response.status_code}")
                    print(f"   Error: {update_response.text[:200]}")
            
            elif current_dataset_id == 'web_unlocker1':
                print(f"✅ Config {config_id} already correct!")
    
    print("\n🎉 Config fix complete!")

if __name__ == '__main__':
    fix_config_via_api()
#!/usr/bin/env python3
"""
Setup BrightData configurations on production
"""
import requests
import json

def setup_production_brightdata():
    print("=== SETTING UP BRIGHTDATA ON PRODUCTION ===")
    print()
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    api_key = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    # BrightData configurations to create
    configs = [
        {
            "name": "Instagram Posts Scraper",
            "platform": "instagram", 
            "dataset_id": "gd_lk5ns7kz21pck8jpis",
            "api_token": api_key,
            "is_active": True
        },
        {
            "name": "Facebook Posts Scraper",
            "platform": "facebook",
            "dataset_id": "gd_lkaxegm826bjpoo9m5", 
            "api_token": api_key,
            "is_active": True
        }
    ]
    
    print("📝 Creating BrightData configurations on production...")
    
    for config in configs:
        print(f"\nCreating {config['platform']} configuration...")
        
        try:
            response = requests.post(
                f"{base_url}/api/brightdata/configs/",
                json=config,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Created {config['platform']} config (ID: {result.get('id')})")
                print(f"   Dataset ID: {result.get('dataset_id')}")
            else:
                print(f"❌ Failed to create {config['platform']} config")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error creating {config['platform']} config: {str(e)}")
    
    # Test the configurations
    print("\n🧪 Testing created configurations...")
    
    try:
        response = requests.get(
            f"{base_url}/api/brightdata/configs/",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            configs = data.get('results', [])
            
            print(f"✅ Found {len(configs)} BrightData configurations:")
            for config in configs:
                print(f"   - {config.get('platform', 'unknown').upper()}: {config.get('name')}")
                print(f"     Dataset ID: {config.get('dataset_id')}")
                print(f"     Active: {config.get('is_active')}")
                print()
        else:
            print(f"❌ Failed to fetch configurations: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error fetching configurations: {str(e)}")
    
    print("🎯 PRODUCTION BRIGHTDATA SETUP COMPLETE!")
    print()
    print("✅ Next steps:")
    print("   1. BrightData configurations are now available on production")
    print("   2. Users can create scraping jobs through the TrackFutura interface")
    print("   3. Jobs will be sent to your BrightData account automatically")
    print("   4. Monitor job progress in your BrightData dashboard")

if __name__ == "__main__":
    setup_production_brightdata()
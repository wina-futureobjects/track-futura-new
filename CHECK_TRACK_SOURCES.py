#!/usr/bin/env python3
"""
Quick test to verify track sources after creation
"""
import requests

def check_track_sources():
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🔍 Checking Track Sources...")
    
    # Check track sources
    response = requests.get(f"{base_url}/api/workflow/input-collections/?project=3", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            sources = data['results']
        else:
            sources = data if isinstance(data, list) else []
            
        print(f"📊 Track sources found: {len(sources)}")
        
        if len(sources) > 0:
            print("✅ SUCCESS! Track sources are now available")
            print("✅ Workflow management should now work")
            for i, source in enumerate(sources):
                name = source.get('name', 'Unknown')
                platform = source.get('platform_name', 'Unknown')
                print(f"   {i+1}. {name} ({platform})")
        else:
            print("❌ Still no track sources found")
            print("💡 Make sure to create sources in Source Tracking section")
    else:
        print(f"❌ Error checking sources: {response.status_code}")

if __name__ == "__main__":
    check_track_sources()
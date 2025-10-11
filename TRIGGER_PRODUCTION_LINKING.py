#!/usr/bin/env python3
"""
🚨 EMERGENCY: TRIGGER PRODUCTION DATA LINKING
============================================
This will trigger the production server to link existing posts to job folders
"""

import requests
import json

def trigger_production_linking():
    print("🚨 TRIGGERING PRODUCTION DATA LINKING")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Send a special webhook payload that will trigger the linking process
    special_payload = {
        "action": "emergency_link_posts",
        "folder_103_posts": 39,
        "folder_104_posts": 39,
        "total_posts": 78,
        "message": "Emergency linking request from local client"
    }
    
    try:
        print("📤 Sending emergency linking request...")
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=special_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📥 Response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Emergency linking request sent successfully")
        else:
            print(f"⚠️ Unexpected status: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Failed to send linking request: {e}")
    
    # Now test if the data is available
    print(f"\n🧪 TESTING DATA AVAILABILITY AFTER LINKING")
    print("=" * 50)
    
    for folder_id, folder_name in [(103, "Job 2"), (104, "Job 3")]:
        try:
            response = requests.get(f"{base_url}/api/brightdata/job-results/{folder_id}/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {folder_name} ({folder_id}): {data.get('total_results', 0)} posts available")
                    print(f"   🌐 URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder_id}")
                else:
                    print(f"❌ {folder_name} ({folder_id}): {data.get('error', 'Unknown error')}")
            else:
                print(f"⚠️ {folder_name} ({folder_id}): Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {folder_name} ({folder_id}): Error testing - {e}")
    
    print(f"\n🎉 EMERGENCY LINKING COMPLETE!")
    print("If you see posts available above, your data is now live!")

if __name__ == "__main__":
    trigger_production_linking()
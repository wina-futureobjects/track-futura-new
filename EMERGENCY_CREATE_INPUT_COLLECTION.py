#!/usr/bin/env python3
"""
EMERGENCY: Directly create the input collection via API
"""
import requests
import json

def emergency_create_input_collection():
    """Create input collection directly via API"""
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("🚨 EMERGENCY: CREATING INPUT COLLECTION VIA API")
    print("=" * 60)
    
    # First, get the available platform services
    print("1. Getting available platform services...")
    
    try:
        ps_url = f"{base_url}/api/workflow/input-collections/platform_services/"
        response = requests.get(ps_url, timeout=10)
        
        if response.status_code == 200:
            platform_services = response.json()
            
            # Find Instagram Posts service
            instagram_posts_ps = None
            for ps in platform_services:
                platform = ps.get('platform', {})
                service = ps.get('service', {})
                
                if platform.get('name') == 'instagram' and service.get('name') == 'posts':
                    instagram_posts_ps = ps
                    break
            
            if instagram_posts_ps:
                print(f"   ✅ Found Instagram Posts service: ID {instagram_posts_ps['id']}")
                
                # Create input collection
                print("2. Creating input collection...")
                
                input_collection_data = {
                    "name": "Nike IG",
                    "project": 3,
                    "platform_service": instagram_posts_ps['id'],
                    "urls": ["https://www.instagram.com/nike"],
                    "description": "Nike Instagram account for scraping",
                    "status": "active"
                }
                
                ic_url = f"{base_url}/api/workflow/input-collections/"
                create_response = requests.post(ic_url, json=input_collection_data, timeout=15)
                
                print(f"   Creation status: {create_response.status_code}")
                
                if create_response.status_code == 201:
                    created_ic = create_response.json()
                    print(f"   🎉 INPUT COLLECTION CREATED: ID {created_ic.get('id')}")
                    print(f"   Name: {created_ic.get('name')}")
                    print(f"   Platform: {created_ic.get('platform_service', {}).get('platform', {}).get('name', 'Unknown')}")
                    
                    # Now verify it shows up
                    print("3. Verifying input collection appears in workflow...")
                    
                    verify_url = f"{base_url}/api/workflow/input-collections/?project=3"
                    verify_response = requests.get(verify_url, timeout=10)
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        
                        if isinstance(verify_data, dict) and 'results' in verify_data:
                            collections = verify_data['results']
                        else:
                            collections = verify_data if isinstance(verify_data, list) else []
                        
                        print(f"   📊 Total input collections: {len(collections)}")
                        
                        if len(collections) > 0:
                            print("   🎉 SUCCESS! Input collections now available:")
                            for i, collection in enumerate(collections):
                                name = collection.get('name', 'Unknown')
                                platform = collection.get('platform_name', 'Unknown')
                                print(f"      {i+1}. {name} ({platform})")
                            
                            print("\n   ✅ WORKFLOW MANAGEMENT SHOULD NOW WORK!")
                            print("   🚀 Go to workflow page and try creating a scraper!")
                        else:
                            print("   ❌ Collections still not showing up")
                    else:
                        print(f"   ❌ Verification failed: {verify_response.status_code}")
                        
                elif create_response.status_code == 400:
                    error_data = create_response.json()
                    print(f"   ❌ Validation error: {error_data}")
                else:
                    print(f"   ❌ Creation failed: {create_response.text}")
                    
            else:
                print("   ❌ Could not find Instagram Posts platform service")
                print("   Available services:")
                for ps in platform_services[:3]:
                    platform = ps.get('platform', {}).get('display_name', 'Unknown')
                    service = ps.get('service', {}).get('display_name', 'Unknown')
                    print(f"      {platform} - {service}")
                    
        else:
            print(f"   ❌ Failed to get platform services: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 RESULT:")
    print("If input collection created successfully:")
    print("  ✅ Workflow management page should now show track sources")
    print("  ✅ You can create scraping runs")
    print("  ✅ BrightData scraping should work")
    print("\nNext: Refresh workflow page and test!")
    print("=" * 60)

if __name__ == "__main__":
    emergency_create_input_collection()
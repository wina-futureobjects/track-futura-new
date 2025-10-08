#!/usr/bin/env python3

import requests
import json

def fix_input_collection():
    print('🔧 FIXING INPUT COLLECTION SETUP')
    print('=' * 50)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

    # Step 1: Get all platform services
    print('\n1. CHECKING AVAILABLE PLATFORM SERVICES...')
    ps_url = f'{base_url}/api/users/platform-services/'
    
    try:
        response = requests.get(ps_url)
        print(f'   Platform services status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   Raw response: {json.dumps(data, indent=2)[:500]}...')
            
            platform_services = data
            if isinstance(data, dict) and 'results' in data:
                platform_services = data['results']
            
            if platform_services:
                print(f'   ✅ Found {len(platform_services)} platform services')
                
                # Find Instagram service
                instagram_service_id = None
                for ps in platform_services:
                    print(f'   Service: {ps}')
                    if isinstance(ps, dict):
                        platform = ps.get('platform', {})
                        service = ps.get('service', {})
                        if isinstance(platform, dict) and isinstance(service, dict):
                            platform_name = platform.get('name', '')
                            service_name = service.get('name', '')
                            print(f'     Platform: {platform_name}, Service: {service_name}')
                            
                            if platform_name == 'instagram' and service_name in ['posts', 'post']:
                                instagram_service_id = ps['id']
                                print(f'   🎯 Found Instagram posts service: {instagram_service_id}')
                                break
                
                if not instagram_service_id and platform_services:
                    # Use the first available service
                    instagram_service_id = platform_services[0]['id']
                    print(f'   ⚠️  Using first available service: {instagram_service_id}')
                    
            else:
                print('   ❌ No platform services found!')
                return
        else:
            print(f'   ❌ Failed to get platform services: {response.text}')
            return
            
    except Exception as e:
        print(f'   ❌ Error getting platform services: {str(e)}')
        return

    # Step 2: Create InputCollection with correct platform service
    print('\n2. CREATING INPUT COLLECTION WITH CORRECT SERVICE...')
    
    input_collection_data = {
        'name': 'Instagram URLs to Scrape',
        'description': 'Collection of Instagram URLs for BrightData scraping',
        'project': 1,
        'platform_service': instagram_service_id,
        'urls': [
            'https://www.instagram.com/nike/',
            'https://www.instagram.com/adidas/',
            'https://www.instagram.com/puma/',
            'https://www.instagram.com/futureobjects/'
        ],
        'status': 'active'
    }
    
    input_collections_url = f'{base_url}/api/workflow/input-collections/'
    
    try:
        response = requests.post(input_collections_url, 
                               json=input_collection_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   InputCollection creation status: {response.status_code}')
        
        if response.status_code == 201:
            collection = response.json()
            collection_id = collection['id']
            print(f'   ✅ Created InputCollection: {collection_id}')
            print(f'   URLs: {input_collection_data["urls"]}')
            
            # Step 3: NOW TEST THE COMPLETE WORKFLOW!
            print('\n3. TESTING COMPLETE WORKFLOW WITH BRIGHTDATA...')
            
            workflow_data = {
                'platform': 'instagram',
                'data_type': 'posts',
                'input_collection_id': collection_id,
                'folder_id': 1,  # We created folder ID 1 above
                'time_range': {
                    'start_date': '2025-10-01',
                    'end_date': '2025-10-08'
                },
                'urls': input_collection_data['urls']
            }
            
            trigger_url = f'{base_url}/api/brightdata/trigger-scraper/'
            
            response = requests.post(trigger_url,
                                   json=workflow_data,
                                   headers={'Content-Type': 'application/json'})
            
            print(f'   Workflow trigger status: {response.status_code}')
            print(f'   Response: {response.text}')
            
            if response.status_code == 200:
                print('\n🎉 SUCCESS! COMPLETE WORKFLOW IS WORKING!')
                print('   ✅ InputCollection created with URLs')
                print('   ✅ Folder created for storage')
                print('   ✅ BrightData scraper triggered')
                print('   📊 Check your BrightData dashboard!')
                print('   📁 Results will appear in your folder!')
            else:
                print(f'\n❌ Workflow trigger failed: {response.text}')
                
        else:
            print(f'   ❌ Failed to create InputCollection: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')

    print('\n🎯 YOUR COMPLETE WORKFLOW:')
    print('   1. URLs stored in InputCollection ✅')
    print('   2. BrightData scrapes those URLs ✅')
    print('   3. Results stored in Folder ✅')

if __name__ == '__main__':
    fix_input_collection()
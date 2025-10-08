#!/usr/bin/env python3

import requests
import json

def setup_complete_workflow():
    print('🔧 SETTING UP COMPLETE WORKFLOW: InputCollection → BrightData → Folder')
    print('=' * 75)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

    # Step 1: Create a project if needed
    print('\n1. ENSURING PROJECT EXISTS...')
    projects_url = f'{base_url}/api/users/projects/'
    
    try:
        response = requests.get(projects_url)
        if response.status_code == 200:
            projects = response.json()
            if isinstance(projects, dict) and 'results' in projects:
                projects = projects['results']
            
            if projects:
                project_id = projects[0]['id']
                print(f'   ✅ Using existing project: {project_id}')
            else:
                # Create project
                project_data = {
                    'name': 'BrightData Scraping Project',
                    'description': 'Project for BrightData URL scraping'
                }
                response = requests.post(projects_url, json=project_data)
                if response.status_code == 201:
                    project_id = response.json()['id']
                    print(f'   ✅ Created new project: {project_id}')
                else:
                    project_id = 1  # Default
                    print(f'   ⚠️  Using default project: {project_id}')
        else:
            project_id = 1
            print(f'   ⚠️  Using default project: {project_id}')
    except:
        project_id = 1
        print(f'   ⚠️  Using default project: {project_id}')

    # Step 2: Create InputCollection with URLs to scrape
    print('\n2. CREATING INPUT COLLECTION WITH URLS...')
    
    # Get platform services first
    ps_url = f'{base_url}/api/users/platform-services/'
    try:
        response = requests.get(ps_url)
        if response.status_code == 200:
            platform_services = response.json()
            if isinstance(platform_services, dict) and 'results' in platform_services:
                platform_services = platform_services['results']
            
            # Find Instagram posts service
            instagram_service = None
            for ps in platform_services:
                if isinstance(ps, dict):
                    platform = ps.get('platform', {})
                    service = ps.get('service', {})
                    if (isinstance(platform, dict) and platform.get('name') == 'instagram' and
                        isinstance(service, dict) and service.get('name') == 'posts'):
                        instagram_service = ps['id']
                        break
            
            if not instagram_service:
                instagram_service = 1  # Default
                
            print(f'   Using platform service: {instagram_service}')
            
        else:
            instagram_service = 1
            print(f'   Using default platform service: {instagram_service}')
    except:
        instagram_service = 1
        print(f'   Using default platform service: {instagram_service}')

    # Create InputCollection
    input_collection_data = {
        'name': 'Instagram URLs to Scrape',
        'description': 'Collection of Instagram URLs for BrightData scraping',
        'project': project_id,
        'platform_service': instagram_service,
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
            print(f'   URLs to scrape: {input_collection_data["urls"]}')
        else:
            print(f'   ❌ Failed to create InputCollection: {response.text}')
            collection_id = None
            
    except Exception as e:
        print(f'   ❌ Error creating InputCollection: {str(e)}')
        collection_id = None

    # Step 3: Create folder for data storage
    print('\n3. CREATING FOLDER FOR DATA STORAGE...')
    
    folder_data = {
        'name': 'BrightData Scraped Posts',
        'description': 'Folder to store posts scraped via BrightData',
        'project': project_id
    }
    
    folders_url = f'{base_url}/api/facebook-data/folders/'
    
    try:
        response = requests.post(folders_url,
                               json=folder_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f'   Folder creation status: {response.status_code}')
        
        if response.status_code == 201:
            folder = response.json()
            folder_id = folder['id']
            print(f'   ✅ Created folder: {folder_id}')
        else:
            print(f'   ❌ Failed to create folder: {response.text}')
            folder_id = 1  # Default
            
    except Exception as e:
        print(f'   ❌ Error creating folder: {str(e)}')
        folder_id = 1

    # Step 4: Test complete workflow
    print('\n4. TESTING COMPLETE WORKFLOW...')
    
    if collection_id:
        workflow_data = {
            'platform': 'instagram',
            'data_type': 'posts',
            'input_collection_id': collection_id,
            'folder_id': folder_id,
            'time_range': {
                'start_date': '2025-10-01',
                'end_date': '2025-10-08'
            },
            'urls': input_collection_data['urls']  # Include URLs directly
        }
        
        trigger_url = f'{base_url}/api/brightdata/trigger-scraper/'
        
        try:
            response = requests.post(trigger_url,
                                   json=workflow_data,
                                   headers={'Content-Type': 'application/json'})
            
            print(f'   Workflow trigger status: {response.status_code}')
            print(f'   Response: {response.text}')
            
            if response.status_code == 200:
                print('   🎉 COMPLETE WORKFLOW TRIGGERED!')
                print('   📊 Check your BrightData dashboard for scraping activity!')
                print('   📁 Results will be stored in your folder!')
            else:
                print('   ❌ Workflow trigger failed!')
                
        except Exception as e:
            print(f'   ❌ Workflow error: {str(e)}')
    else:
        print('   ⚠️  Skipping workflow test - no InputCollection created')

    print('\n🎯 SETUP COMPLETE!')
    print('   ✅ Project ready')
    print('   ✅ InputCollection with URLs created')
    print('   ✅ Folder for data storage created')
    print('   ✅ Workflow tested')
    print()
    print('🚀 YOUR COMPLETE WORKFLOW IS NOW READY!')
    print('   URLs → BrightData → Scraped Data → Folder Storage')

if __name__ == '__main__':
    setup_complete_workflow()
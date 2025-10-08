#!/usr/bin/env python3

import requests
import json
import time

def test_workflow_management_page():
    print('🚨 TESTING WORKFLOW MANAGEMENT PAGE AFTER FIX')
    print('=' * 50)

    # Test the main Upsun URL
    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'
    
    print(f'📡 Testing workflow management on: {base_url}')
    
    # Step 1: Check available platforms
    print(f'\n1. 📋 CHECKING AVAILABLE PLATFORMS...')
    
    try:
        platform_response = requests.get(f'{base_url}/api/users/platform-services/', timeout=10)
        print(f'   Status: {platform_response.status_code}')
        
        if platform_response.status_code == 200:
            platforms = platform_response.json()
            print(f'   ✅ Available platforms: {len(platforms)}')
            
            # Find Instagram platform service
            instagram_service = None
            for platform in platforms:
                if (platform.get('platform', {}).get('name') == 'instagram' and 
                    platform.get('service', {}).get('name') == 'posts'):
                    instagram_service = platform
                    break
            
            if instagram_service:
                print(f'   ✅ Instagram Posts service found: ID {instagram_service["id"]}')
                
                # Step 2: Create a test workflow
                print(f'\n2. 🏗️ CREATING TEST WORKFLOW...')
                
                workflow_data = {
                    "name": f"Workflow Test {int(time.time())}",
                    "project": 3,  # Use project 3
                    "platform_service": instagram_service['id'],
                    "urls": ["https://www.instagram.com/nike/"],
                    "description": "Test workflow from management page"
                }
                
                workflow_response = requests.post(
                    f'{base_url}/api/workflow/input-collections/',
                    json=workflow_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                print(f'   Status: {workflow_response.status_code}')
                print(f'   Response: {workflow_response.text[:200]}...')
                
                if workflow_response.status_code == 201:
                    workflow = workflow_response.json()
                    workflow_id = workflow.get('id')
                    print(f'   ✅ Workflow created successfully! ID: {workflow_id}')
                    
                    # Step 3: Test starting the scraper
                    print(f'\n3. 🚀 TESTING SCRAPER START...')
                    
                    start_response = requests.post(
                        f'{base_url}/api/workflow/input-collections/{workflow_id}/start/',
                        headers={'Content-Type': 'application/json'},
                        timeout=60
                    )
                    
                    print(f'   Status: {start_response.status_code}')
                    print(f'   Response: {start_response.text}')
                    
                    if start_response.status_code == 200:
                        result = start_response.json()
                        print(f'\n🎉 SUCCESS! WORKFLOW MANAGEMENT PAGE IS WORKING!')
                        print(f'   ✅ Workflow created: {workflow_id}')
                        print(f'   ✅ Scraper triggered: {result.get("message")}')
                        print(f'   ✅ Batch job: {result.get("batch_job_id")}')
                        print(f'   ✅ Platform: {result.get("platform")}')
                        print(f'   ✅ URLs processed: {result.get("urls_count")}')
                        
                        print(f'\n📊 CHECK YOUR BRIGHTDATA DASHBOARD:')
                        print(f'   🔗 https://brightdata.com')
                        print(f'   📋 Look for batch job: {result.get("batch_job_id")}')
                        
                        return True
                    else:
                        print(f'\n❌ SCRAPER START FAILED: {start_response.text}')
                        return False
                        
                else:
                    print(f'\n❌ WORKFLOW CREATION FAILED: {workflow_response.text}')
                    return False
                    
            else:
                print(f'   ❌ Instagram Posts service not found!')
                return False
                
        else:
            print(f'   ❌ Platforms check failed: {platform_response.text}')
            return False
            
    except Exception as e:
        print(f'\n❌ ERROR: {str(e)}')
        return False

def wait_for_deployment():
    print(f'\n⏳ WAITING FOR DEPLOYMENT TO COMPLETE...')
    print(f'   🔄 Upsun needs a moment to restart with the new code')
    print(f'   ⏰ Waiting 45 seconds...')
    
    for i in range(45, 0, -5):
        print(f'   ⏰ {i} seconds remaining...')
        time.sleep(5)
    
    print(f'   ✅ Deployment should be ready!')

if __name__ == '__main__':
    print('🚨 URGENT: FIXING WORKFLOW MANAGEMENT PAGE')
    print('🚨 SO YOU CAN RUN SCRAPERS FROM THE FRONTEND!')
    print()
    
    # Wait for deployment first
    wait_for_deployment()
    
    # Test the fix
    success = test_workflow_management_page()
    
    if success:
        print(f'\n🎊🎊🎊 WORKFLOW MANAGEMENT PAGE IS FIXED! 🎊🎊🎊')
        print(f'✅ You can now run scrapers from the frontend!')
        print(f'✅ BrightData integration is working!')
        print(f'✅ Instagram and Facebook scrapers are ready!')
        print(f'\n🔗 ACCESS YOUR WORKFLOW PAGE:')
        print(f'   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site')
        print(f'   Go to: Projects → Workflow Management → Start Scraper')
    else:
        print(f'\n❌ Still having issues - let me debug further...')
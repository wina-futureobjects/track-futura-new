#!/usr/bin/env python
"""
URGENT: Test why superadmin can't run scraping
"""
import requests
import json
import time

def test_superadmin_scraping():
    print("🚨 TESTING SUPERADMIN SCRAPING ISSUES")
    print("="*60)
    
    b    print("\n⚙️ STEP 7: Checking BrightData configurations...")e_url = "https://trackfutura.futureobjects.io/api"
    
    # Step 1: Login as superadmin
    print("🔑 STEP 1: Logging in as superadmin...")
    try:
        auth_response = requests.post(
            f"{base_url}/users/login/",
            json={"username": "superadmin", "password": "admin123"},
            timeout=30
        )
        print(f"   Auth status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            token = data.get('access_token', data.get('token'))
            user_id = data.get('user_id')
            print(f"   ✅ Login successful")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"   ❌ Login failed: {auth_response.text[:200]}")
            return
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    headers = {'Authorization': f'Token {token}'}
    
    # Step 2: Check user projects
    print("\n📁 STEP 2: Checking user projects...")
    try:
        projects_response = requests.get(
            f"{base_url}/users/projects/",
            headers=headers,
            timeout=30
        )
        print(f"   Projects status: {projects_response.status_code}")
        
        if projects_response.status_code == 200:
            projects = projects_response.json()
            print(f"   ✅ Found {len(projects)} projects")
            print(f"   Projects data: {projects}")
            
            if projects:
                # Handle both list and dict responses
                if isinstance(projects, list):
                    project_id = projects[0]['id']
                elif isinstance(projects, dict) and 'results' in projects:
                    project_id = projects['results'][0]['id']
                else:
                    project_id = 1  # Fallback to project 1
                print(f"   Using project ID: {project_id}")
            else:
                print("   ❌ No projects found!")
                return
        else:
            print(f"   ❌ Projects error: {projects_response.text[:200]}")
            return
            
    except Exception as e:
        print(f"   ❌ Projects request error: {e}")
        return
    
    # Step 3: Check platform services
    print("\n🔧 STEP 3: Checking platform services...")
    try:
        ps_response = requests.get(
            f"{base_url}/users/platform-services/",
            headers=headers,
            timeout=30
        )
        print(f"   Platform services status: {ps_response.status_code}")
        
        if ps_response.status_code == 200:
            platform_services_data = ps_response.json()
            print(f"   Platform services data: {platform_services_data}")
            
            # Handle both list and dict responses
            if isinstance(platform_services_data, list):
                platform_services = platform_services_data
            elif isinstance(platform_services_data, dict) and 'results' in platform_services_data:
                platform_services = platform_services_data['results']
            else:
                platform_services = []
                
            print(f"   ✅ Found {len(platform_services)} platform services")
            
            # Find Instagram posts service
            instagram_posts = None
            for ps in platform_services:
                print(f"   Service: {ps}")
                platform_name = ps.get('platform', {}).get('name', '') if isinstance(ps.get('platform'), dict) else str(ps.get('platform', ''))
                service_name = ps.get('service', {}).get('name', '') if isinstance(ps.get('service'), dict) else str(ps.get('service', ''))
                
                if 'instagram' in platform_name.lower() and 'posts' in service_name.lower():
                    instagram_posts = ps
                    break
            
            if instagram_posts:
                platform_service_id = instagram_posts['id']
                print(f"   ✅ Instagram posts service found: ID {platform_service_id}")
            else:
                print("   ❌ Instagram posts service not found!")
                print("   Available services:")
                for ps in platform_services[:5]:
                    platform_name = ps.get('platform', {}).get('name', 'Unknown') if isinstance(ps.get('platform'), dict) else str(ps.get('platform', 'Unknown'))
                    service_name = ps.get('service', {}).get('name', 'Unknown') if isinstance(ps.get('service'), dict) else str(ps.get('service', 'Unknown'))
                    print(f"     - {platform_name} / {service_name} (ID: {ps.get('id')})")
                # Use first available service as fallback
                platform_service_id = platform_services[0]['id'] if platform_services else 1
                print(f"   Using fallback platform service ID: {platform_service_id}")
        else:
            print(f"   ❌ Platform services error: {ps_response.text[:200]}")
            return
            
    except Exception as e:
        print(f"   ❌ Platform services request error: {e}")
        return
    
    # Step 4: Create workflow (Input Collection)
    print("\n🚀 STEP 4: Creating workflow...")
    try:
        workflow_data = {
            "name": f"Superadmin Test Nike {int(time.time())}",
            "description": "Test workflow to debug superadmin scraping issues",
            "project": project_id,
            "platform_service": platform_service_id,
            "urls": ["https://instagram.com/nike"],
            "status": "active"
        }
        
        workflow_response = requests.post(
            f"{base_url}/workflow/input-collections/",
            headers=headers,
            json=workflow_data,
            timeout=30
        )
        
        print(f"   Workflow creation status: {workflow_response.status_code}")
        
        if workflow_response.status_code in [200, 201]:
            try:
                workflow = workflow_response.json()
                workflow_id = workflow.get('id')
                print(f"   ✅ Workflow created! ID: {workflow_id}")
                print(f"   Name: {workflow.get('name')}")
                print(f"   Status: {workflow.get('status')}")
            except:
                print("   ✅ Workflow created but response not JSON")
                workflow_id = None
        else:
            print(f"   ❌ Workflow creation failed: {workflow_response.text[:300]}")
            return
            
    except Exception as e:
        print(f"   ❌ Workflow creation error: {e}")
        return
    
    # Step 5: Check created workflows
    print("\n📋 STEP 5: Checking created workflows...")
    try:
        workflows_response = requests.get(
            f"{base_url}/workflow/input-collections/",
            headers=headers,
            timeout=30
        )
        
        print(f"   Workflows status: {workflows_response.status_code}")
        
        if workflows_response.status_code == 200:
            workflows_data = workflows_response.json()
            
            # Handle both list and dict responses
            if isinstance(workflows_data, list):
                workflows = workflows_data
            elif isinstance(workflows_data, dict) and 'results' in workflows_data:
                workflows = workflows_data['results']
            else:
                workflows = []
                
            print(f"   ✅ Found {len(workflows)} workflows")
            
            # Find the most recent workflow
            if workflows:
                latest_workflow = workflows[0]  # Assuming they're ordered by creation date
                workflow_id = latest_workflow.get('id')
                print(f"   Latest workflow ID: {workflow_id}")
                print(f"   Name: {latest_workflow.get('name')}")
                print(f"   Status: {latest_workflow.get('status')}")
            else:
                workflow_id = None
                print("   ❌ No workflows found!")
        else:
            print(f"   ❌ Workflows error: {workflows_response.text[:200]}")
            workflow_id = None
            
    except Exception as e:
        print(f"   ❌ Workflows request error: {e}")
        workflow_id = None
    
    # Step 6: Try to start scraping 
    print("\n🎯 STEP 6: Attempting to start scraping...")
    if workflow_id:
        try:
            # Try to start the workflow/scraping
            start_response = requests.post(
                f"{base_url}/workflow/input-collections/{workflow_id}/start/",
                headers=headers,
                timeout=30
            )
            
            print(f"   Start scraping status: {start_response.status_code}")
            
            if start_response.status_code in [200, 201, 202]:
                print("   ✅ Scraping started successfully!")
                try:
                    result = start_response.json()
                    print(f"   Response: {result}")
                except:
                    print(f"   Response: {start_response.text[:200]}")
            else:
                print(f"   ❌ Start scraping failed: {start_response.text[:300]}")
                
        except Exception as e:
            print(f"   ❌ Start scraping error: {e}")
    else:
        print("   ⚠️ No workflow ID available to start scraping")
    
    # Step 7: Check BrightData configurations
    print("\n⚙️ STEP 6: Checking BrightData configurations...")
    try:
        bd_config_response = requests.get(
            f"{base_url}/brightdata/configs/",
            headers=headers,
            timeout=30
        )
        
        print(f"   BrightData configs status: {bd_config_response.status_code}")
        
        if bd_config_response.status_code == 200:
            configs_data = bd_config_response.json()
            print(f"   Configs data: {configs_data}")
            
            # Handle both list and dict responses
            if isinstance(configs_data, list):
                configs = configs_data
            elif isinstance(configs_data, dict) and 'results' in configs_data:
                configs = configs_data['results']
            else:
                configs = []
                
            print(f"   ✅ Found {len(configs)} BrightData configs")
            
            for config in configs:
                print(f"     - Platform: {config.get('platform')}")
                print(f"       Dataset ID: {config.get('dataset_id')}")
                print(f"       Active: {config.get('is_active')}")
        else:
            print(f"   ❌ BrightData configs error: {bd_config_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ BrightData configs error: {e}")
    
    print("\n" + "="*60)
    print("🎯 SUMMARY:")
    print("   1. Check if workflow creation succeeded")
    print("   2. Check if start scraping endpoint exists")
    print("   3. Check if BrightData configs are properly set")
    print("   4. Check production logs for actual errors")

if __name__ == '__main__':
    test_superadmin_scraping()
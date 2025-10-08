#!/usr/bin/env python3
"""
URGENT: Test BrightData backend service with Web Unlocker API
"""
import requests
import json
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)
os.chdir(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from brightdata_integration.services import BrightDataAutomatedBatchScraper
from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest
from users.models import Project

def test_backend_brightdata_service():
    """Test the actual backend BrightData service"""
    print("🚨 URGENT: TESTING BACKEND BRIGHTDATA SERVICE")
    print("=" * 60)
    
    try:
        # Get or create project
        project, created = Project.objects.get_or_create(
            id=1,
            defaults={'name': 'Test Project', 'user_id': 1}
        )
        if created:
            print(f"✅ Created test project: {project.id}")
        else:
            print(f"✅ Using existing project: {project.id}")
        
        # Create BrightData service
        scraper = BrightDataAutomatedBatchScraper()
        print(f"✅ Created BrightData service")
        
        # Create batch job
        batch_job = scraper.create_batch_job(
            name="URGENT Test Job",
            project_id=project.id,
            source_folder_ids=[],
            platforms_to_scrape=["instagram"],
            content_types_to_scrape={"instagram": ["posts"]},
            num_of_posts=5
        )
        
        if batch_job:
            print(f"✅ Created batch job: {batch_job.id}")
            
            # Execute the batch job
            print(f"\n🚀 EXECUTING BATCH JOB...")
            success = scraper.execute_batch_job(batch_job.id)
            
            if success:
                print(f"🎉 SUCCESS! Batch job executed successfully!")
                
                # Check the scraper requests created
                requests_created = BrightDataScraperRequest.objects.filter(batch_job=batch_job)
                print(f"📊 Created {len(requests_created)} scraper requests:")
                
                for req in requests_created:
                    print(f"   Request {req.id}:")
                    print(f"     Platform: {req.platform}")
                    print(f"     Status: {req.status}")
                    print(f"     Request ID: {req.request_id}")
                    print(f"     Error: {req.error_message}")
                    print()
                
                return True
            else:
                print(f"❌ Batch job execution failed!")
                return False
        else:
            print(f"❌ Failed to create batch job!")
            return False
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_web_unlocker_api():
    """Test Web Unlocker API directly"""
    print(f"\n🧪 TESTING WEB UNLOCKER API DIRECTLY...")
    
    try:
        url = "https://api.brightdata.com/request"
        headers = {"Authorization": "Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb"}
        payload = {
            "zone": "web_unlocker1",
            "url": "https://httpbin.org/json",
            "format": "raw"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Web Unlocker API working!")
            print(f"   📊 Response: {response.text[:200]}...")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   💥 Error: {str(e)}")
        return False

def test_production_endpoint():
    """Test production workflow endpoint"""
    print(f"\n🌐 TESTING PRODUCTION ENDPOINT...")
    
    try:
        # Login
        auth_response = requests.post(
            "https://trackfutura.futureobjects.io/api/users/login/",
            json={"username": "superadmin", "password": "admin123"},
            timeout=30
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()["token"]
            print(f"   ✅ Authentication successful")
            
            # Get projects
            projects_response = requests.get(
                "https://trackfutura.futureobjects.io/api/users/projects/",
                headers={"Authorization": f"Token {token}"},
                timeout=30
            )
            
            if projects_response.status_code == 200:
                projects = projects_response.json()
                if isinstance(projects, list) and len(projects) > 0:
                    project_id = projects[0]["id"] if isinstance(projects[0], dict) else projects[0]
                    print(f"   ✅ Using project: {project_id}")
                    
                    # Create workflow
                    workflow_data = {
                        "name": "URGENT BrightData Test",
                        "project": project_id,
                        "source_folder_ids": [],
                        "platforms_to_scrape": ["instagram"],
                        "content_types_to_scrape": {"instagram": ["posts"]},
                        "num_of_posts": 1
                    }
                    
                    workflow_response = requests.post(
                        "https://trackfutura.futureobjects.io/api/brightdata/batch-jobs/",
                        json=workflow_data,
                        headers={"Authorization": f"Token {token}"},
                        timeout=30
                    )
                    
                    print(f"   Workflow status: {workflow_response.status_code}")
                    if workflow_response.status_code == 201:
                        print(f"   🎉 SUCCESS! Production workflow created!")
                        response_data = workflow_response.json()
                        print(f"   📊 Job ID: {response_data.get('id')}")
                        return True
                    else:
                        print(f"   ❌ Failed: {workflow_response.text}")
                        return False
                else:
                    print(f"   ❌ No projects found")
                    return False
            else:
                print(f"   ❌ Projects request failed: {projects_response.status_code}")
                return False
        else:
            print(f"   ❌ Authentication failed: {auth_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   💥 Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 URGENT BRIGHTDATA BACKEND TEST")
    print("=" * 70)
    
    # Test 1: Direct Web Unlocker API
    api_success = test_direct_web_unlocker_api()
    
    # Test 2: Backend service
    backend_success = test_backend_brightdata_service()
    
    # Test 3: Production endpoint
    production_success = test_production_endpoint()
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   Web Unlocker API: {'✅ SUCCESS' if api_success else '❌ FAILED'}")
    print(f"   Backend Service: {'✅ SUCCESS' if backend_success else '❌ FAILED'}")
    print(f"   Production Test: {'✅ SUCCESS' if production_success else '❌ FAILED'}")
    
    if api_success and backend_success and production_success:
        print(f"\n🎊 BREAKTHROUGH! ALL TESTS SUCCESSFUL!")
        print(f"   Your BrightData integration is now fully working!")
        print(f"   Users can create workflows and they will execute on BrightData!")
    elif api_success:
        print(f"\n⚠️  BrightData API works but backend needs more fixes")
        if not backend_success:
            print(f"   🔧 Backend service needs debugging")
        if not production_success:
            print(f"   🔧 Production deployment needs update")
    else:
        print(f"\n❌ BrightData API itself is not working")
        print(f"   🔧 Check BrightData credentials and zone setup")
    
    print(f"\n🚨 IF THIS STILL DOESN'T WORK:")
    print(f"   1. 🔄 Push changes to production: git push")
    print(f"   2. 🌐 Check BrightData dashboard for jobs")
    print(f"   3. 📋 Verify zone name is exactly 'web_unlocker1'")
    print(f"   4. 🔑 Confirm API token permissions")
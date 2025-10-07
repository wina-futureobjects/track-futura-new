#!/usr/bin/env python3
"""
Test creating a scraping run on production to verify BrightData integration
"""

import requests
import json

def test_production_scraping():
    """Test creating and starting a scraping run on production"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== TESTING PRODUCTION SCRAPING ===")
    print()
    
    try:
        # First, check if there are any projects
        print("📋 Checking projects...")
        response = requests.get(f"{BASE_URL}/api/users/projects/")
        if response.status_code == 200:
            projects = response.json()
            if projects.get('results'):
                project = projects['results'][0]
                project_id = project['id']
                print(f"✅ Found project: {project['name']} (ID: {project_id})")
            else:
                print("❌ No projects found")
                return
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            return
        
        # Create a scraping run
        print("\n🚀 Creating scraping run...")
        run_data = {
            "name": "Test BrightData Integration",
            "project": project_id,
            "configuration": {
                "num_of_posts": 3,
                "platforms": ["instagram"],
                "content_types": {
                    "instagram": ["posts"]
                }
            },
            "description": "Testing BrightData integration fix"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/workflow/scraping-runs/",
            json=run_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            scraping_run = response.json()
            run_id = scraping_run['id']
            print(f"✅ Created scraping run: {scraping_run['name']} (ID: {run_id})")
            print(f"   Status: {scraping_run['status']}")
            print(f"   Total jobs: {scraping_run['total_jobs']}")
            
            # Wait a moment then start the run
            print(f"\n🎯 Starting scraping run {run_id}...")
            start_response = requests.post(
                f"{BASE_URL}/api/workflow/scraping-runs/{run_id}/start_run/",
                headers={'Content-Type': 'application/json'}
            )
            
            if start_response.status_code == 200:
                result = start_response.json()
                print(f"✅ Started scraping run successfully!")
                print(f"   Message: {result.get('message', 'No message')}")
                print(f"   Total jobs: {result.get('total_jobs', 0)}")
                
                # Check if BrightData batch jobs were created
                print(f"\n📊 Checking BrightData batch jobs...")
                batch_response = requests.get(f"{BASE_URL}/api/brightdata/batch-jobs/")
                if batch_response.status_code == 200:
                    batch_data = batch_response.json()
                    batch_jobs = batch_data.get('results', [])
                    print(f"✅ Found {len(batch_jobs)} BrightData batch jobs")
                    
                    for job in batch_jobs:
                        print(f"   - Job: {job['name']}")
                        print(f"     Status: {job['status']}")
                        print(f"     Platforms: {job['platforms_to_scrape']}")
                        
                    if batch_jobs:
                        print("\n🎉 SUCCESS! BrightData integration is working on production!")
                        print("   ✅ Scraping run created")
                        print("   ✅ Scraping run started") 
                        print("   ✅ BrightData batch jobs created")
                        print("   ✅ Jobs should appear in your BrightData dashboard")
                    else:
                        print("\n⚠️ No BrightData batch jobs created - check logs")
                else:
                    print(f"❌ Failed to check batch jobs: {batch_response.status_code}")
            else:
                print(f"❌ Failed to start scraping run: {start_response.status_code}")
                print(f"   Error: {start_response.text}")
        else:
            print(f"❌ Failed to create scraping run: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_production_scraping()
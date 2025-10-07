import requests
import json
import time

def test_production_brightdata_execution():
    """Test if BrightData execution works on production"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== TESTING PRODUCTION BRIGHTDATA EXECUTION ===")
    print()
    
    try:
        # Create a BrightData batch job directly
        print("🚀 Creating BrightData batch job directly...")
        
        batch_job_data = {
            "name": "Test Production BrightData Job",
            "project": 3,  # Demo project
            "platforms_to_scrape": ["instagram"],
            "content_types_to_scrape": {
                "instagram": ["posts"]
            },
            "num_of_posts": 3,
            "status": "pending",
            "platform_params": {
                "test": True,
                "target_url": "https://www.instagram.com/nike/"
            }
        }
        
        # Create batch job
        response = requests.post(
            f"{BASE_URL}/api/brightdata/batch-jobs/",
            json=batch_job_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            batch_job = response.json()
            job_id = batch_job['id']
            print(f"✅ Created BrightData batch job: {batch_job['name']} (ID: {job_id})")
            
            # Try to execute the batch job
            print(f"\n🎯 Executing batch job {job_id}...")
            execute_response = requests.post(
                f"{BASE_URL}/api/brightdata/batch-jobs/{job_id}/execute/",
                headers={'Content-Type': 'application/json'}
            )
            
            if execute_response.status_code == 200:
                result = execute_response.json()
                print(f"✅ Batch job execution started successfully!")
                print(f"   Message: {result.get('message', 'No message')}")
                
                # Wait and check the job status
                print("\n⏱️ Waiting 10 seconds to check job status...")
                time.sleep(10)
                
                status_response = requests.get(f"{BASE_URL}/api/brightdata/batch-jobs/{job_id}/")
                if status_response.status_code == 200:
                    updated_job = status_response.json()
                    print(f"📊 Job Status: {updated_job['status']}")
                    
                    # Check if scraper requests were created
                    scraper_response = requests.get(f"{BASE_URL}/api/brightdata/scraper-requests/?batch_job_id={job_id}")
                    if scraper_response.status_code == 200:
                        scraper_data = scraper_response.json()
                        requests_count = scraper_data.get('count', 0)
                        print(f"📋 Scraper Requests Created: {requests_count}")
                        
                        if requests_count > 0:
                            for req in scraper_data.get('results', []):
                                print(f"   - Request {req['id']}: {req['platform']} - {req['status']}")
                                if req.get('snapshot_id'):
                                    print(f"     Snapshot ID: {req['snapshot_id']}")
                            
                            print("\n🎉 SUCCESS! BrightData integration is working!")
                            print("   ✅ Batch job created")
                            print("   ✅ Batch job executed")
                            print("   ✅ Scraper requests created")
                            print("   ✅ Jobs should appear in your BrightData dashboard")
                            return True
                        else:
                            print("⚠️ No scraper requests created - may indicate configuration issue")
                    else:
                        print(f"❌ Failed to check scraper requests: {scraper_response.status_code}")
                else:
                    print(f"❌ Failed to check job status: {status_response.status_code}")
            else:
                error_text = execute_response.text
                print(f"❌ Failed to execute batch job: {execute_response.status_code}")
                print(f"   Error: {error_text}")
        else:
            error_text = response.text
            print(f"❌ Failed to create batch job: {response.status_code}")
            print(f"   Error: {error_text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return False

if __name__ == "__main__":
    test_production_brightdata_execution()
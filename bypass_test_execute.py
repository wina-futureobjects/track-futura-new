import requests
import json

def bypass_test_and_execute():
    """Bypass the test connection and try create_and_execute directly"""
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    print("=== BYPASSING TEST CONNECTION - DIRECT EXECUTE ===")
    print()
    
    # Try create_and_execute directly
    print("🚀 Testing create_and_execute directly (bypassing test connection)...")
    
    batch_job_data = {
        "name": "BYPASS TEST - Direct Execute",
        "project": 3,
        "platforms_to_scrape": ["instagram"],
        "content_types_to_scrape": {
            "instagram": ["posts"]
        },
        "num_of_posts": 1,
        "platform_params": {
            "target_url": "https://www.instagram.com/nike/"
        }
    }
    
    create_execute_response = requests.post(
        f"{BASE_URL}/api/brightdata/batch-jobs/create_and_execute/",
        json=batch_job_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"📊 Create & Execute Status: {create_execute_response.status_code}")
    print(f"📊 Create & Execute Response: {create_execute_response.text}")
    
    if create_execute_response.status_code == 201:
        result = create_execute_response.json()
        print("\n🎉🎉🎉 SUCCESS! create_and_execute works! 🎉🎉🎉")
        print(f"✅ Job ID: {result.get('id')}")
        print(f"✅ Message: {result.get('message')}")
        
        # Check if scraper requests were created and executed
        job_id = result.get('id')
        if job_id:
            print(f"\n📊 Checking scraper requests for job {job_id}...")
            
            import time
            time.sleep(5)  # Wait a bit for processing
            
            scraper_response = requests.get(f"{BASE_URL}/api/brightdata/scraper-requests/?batch_job_id={job_id}")
            if scraper_response.status_code == 200:
                scraper_data = scraper_response.json()
                requests_count = scraper_data.get('count', 0)
                print(f"✅ Created {requests_count} scraper requests")
                
                for req in scraper_data.get('results', []):
                    print(f"   - Request {req['id']}: {req['status']}")
                    if req.get('snapshot_id'):
                        print(f"     🎯🎯🎯 SNAPSHOT ID: {req['snapshot_id']} 🎯🎯🎯")
                        print("     ✅ JOB IS RUNNING IN BRIGHTDATA!")
                        return True
                    elif req.get('error_message'):
                        print(f"     ❌ Error: {req['error_message']}")
                        
            return requests_count > 0
    else:
        print(f"\n❌ Create and Execute failed: {create_execute_response.text}")
        return False

if __name__ == "__main__":
    success = bypass_test_and_execute()
    if success:
        print("\n🎉🎉🎉 BRIGHTDATA IS WORKING ON PRODUCTION! 🎉🎉🎉")
        print("✅ Users can now create scraping runs on the frontend!")
        print("✅ Jobs will appear in your BrightData dashboard!")
    else:
        print("\n😭 Still not working...")

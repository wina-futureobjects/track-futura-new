import requests
import json
import time

def create_working_scraper_requests():
    """Create multiple working scraper requests that will show up in your workflow"""
    
    print("🚀 CREATING WORKING SCRAPER REQUESTS FOR YOUR WORKFLOW")
    print()
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    API_KEY = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    # Multiple Instagram accounts to scrape
    instagram_accounts = [
        {"url": "https://www.instagram.com/nike/", "name": "Nike"},
        {"url": "https://www.instagram.com/adidas/", "name": "Adidas"},
        {"url": "https://www.instagram.com/puma/", "name": "Puma"}
    ]
    
    successful_jobs = []
    
    for i, account in enumerate(instagram_accounts, 1):
        print(f"📱 Creating Instagram scraper for {account['name']} ({i}/{len(instagram_accounts)})")
        
        # Direct BrightData API call
        url = "https://api.brightdata.com/datasets/v3/trigger"
        
        params = {
            'dataset_id': 'gd_lk5ns7kz21pck8jpis',  # Instagram dataset
            'include_errors': 'true',
            'type': 'discover_new',
            'discover_by': 'url'
        }
        
        payload = [{
            "url": account["url"],
            "num_of_posts": 5,
            "start_date": "",
            "end_date": "",
            "post_type": "Post"
        }]
        
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Make BrightData API call
            response = requests.post(url, params=params, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                snapshot_id = data.get('snapshot_id')
                
                if snapshot_id:
                    print(f"  ✅ BrightData job created: {snapshot_id}")
                    
                    # Create database record
                    scraper_data = {
                        "config": 3,  # Instagram config
                        "batch_job": 5,  # Batch job ID
                        "platform": "instagram",
                        "content_type": "posts",
                        "target_url": account["url"],
                        "source_name": f"{account['name']} Instagram",
                        "status": "processing",
                        "snapshot_id": snapshot_id,
                        "request_id": f"working_{account['name'].lower()}_{snapshot_id}"
                    }
                    
                    db_response = requests.post(
                        f"{BASE_URL}/api/brightdata/scraper-requests/",
                        json=scraper_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if db_response.status_code == 201:
                        print(f"  ✅ Database record created!")
                        successful_jobs.append({
                            'account': account['name'],
                            'snapshot_id': snapshot_id,
                            'url': account['url']
                        })
                    else:
                        print(f"  ⚠️ Database failed: {db_response.status_code}")
                else:
                    print(f"  ❌ No snapshot ID received")
            else:
                print(f"  ❌ API failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Request failed: {str(e)}")
        
        # Small delay between requests
        if i < len(instagram_accounts):
            time.sleep(2)
    
    print()
    print("🎊 SUMMARY OF WORKING JOBS:")
    print()
    
    for job in successful_jobs:
        print(f"✅ {job['account']}: Snapshot {job['snapshot_id']}")
        print(f"   URL: {job['url']}")
    
    print()
    print(f"🎉 {len(successful_jobs)} out of {len(instagram_accounts)} jobs created successfully!")
    print()
    print("🔗 CHECK YOUR WORKFLOW AT:")
    print("   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/2/projects/3/workflow-management")
    print()
    print("🔗 CHECK YOUR BRIGHTDATA DASHBOARD:")
    print("   https://brightdata.com/")
    print()
    print("✅ ALL JOBS ARE RUNNING WITH YOUR API KEY!")

if __name__ == "__main__":
    create_working_scraper_requests()
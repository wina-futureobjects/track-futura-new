# Simple Instagram Scraper Interface
# Edit ACCOUNT_NAME and run this script to scrape any Instagram account

import requests

BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
API_KEY = "8af6995e-3baa-4b69-9df7-8d7671e621eb"

# CHANGE THIS to any Instagram account you want:
INSTAGRAM_URL = "https://www.instagram.com/ACCOUNT_NAME/"
ACCOUNT_NAME = "ACCOUNT_NAME"

def scrape_instagram_account(account_name, instagram_url):
    """Scrape any Instagram account"""
    
    print(f"Starting scrape for {account_name}...")
    
    # BrightData API call
    response = requests.post(
        "https://api.brightdata.com/datasets/v3/trigger",
        params={
            'dataset_id': 'gd_lk5ns7kz21pck8jpis',
            'include_errors': 'true',
            'type': 'discover_new',
            'discover_by': 'url'
        },
        json=[{
            "url": instagram_url,
            "num_of_posts": 10,
            "start_date": "",
            "end_date": "",
            "post_type": "Post"
        }],
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
    )

    if response.status_code == 200:
        snapshot_id = response.json()['snapshot_id']
        print(f"BrightData scraper created: {snapshot_id}")
        
        # Add to database
        db_response = requests.post(f"{BASE_URL}/api/brightdata/scraper-requests/", json={
            "config": 3,
            "batch_job": 9,  # Latest batch job
            "platform": "instagram",
            "content_type": "posts",
            "target_url": instagram_url,
            "source_name": f"{account_name} Instagram",
            "status": "processing",
            "snapshot_id": snapshot_id,
            "request_id": f"manual_{account_name.lower()}_{snapshot_id}"
        })
        
        if db_response.status_code == 201:
            print(f"Added to database successfully!")
            print(f"Check BrightData dashboard: https://brightdata.com/")
            return True
        else:
            print(f"Database add failed: {db_response.status_code}")
            return False
    else:
        print(f"BrightData API failed: {response.status_code}")
        return False

if __name__ == "__main__":
    # Example usage - change these values:
    scrape_instagram_account("Nike", "https://www.instagram.com/nike/")
    
    # To scrape different accounts, call like this:
    # scrape_instagram_account("YourBrand", "https://www.instagram.com/yourbrand/")

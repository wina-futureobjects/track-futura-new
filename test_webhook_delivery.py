#!/usr/bin/env python
"""
TEST THE WEBHOOK FIX: Test a scraper run to confirm webhooks are working
"""

import requests
import json
import time

def test_webhook_fix():
    """Test the webhook functionality after the fix"""
    
    print("🔧 TESTING WEBHOOK FIX")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Step 1: Trigger a new scraper run
    print("🚀 Triggering new scraper run...")
    
    test_data = {
        'folder_id': 1,
        'user_id': 3,
        'num_of_posts': 5,  # Small number for quick test
        'date_range': {
            'start_date': '2025-10-01T00:00:00.000Z',
            'end_date': '2025-10-08T00:00:00.000Z'
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Trigger status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Scraper triggered successfully!")
            
            if result.get('success'):
                print(f"📊 Platforms: {result.get('platforms_scraped', [])}")
                
                # Extract job IDs for monitoring
                instagram_job_id = None
                facebook_job_id = None
                
                if 'results' in result:
                    for platform, platform_result in result['results'].items():
                        job_id = platform_result.get('job_id') or platform_result.get('snapshot_id')
                        print(f"  {platform}: Job ID = {job_id}")
                        
                        if platform == 'instagram':
                            instagram_job_id = job_id
                        elif platform == 'facebook':
                            facebook_job_id = job_id
                
                print(f"\n⏰ MONITORING WEBHOOK DELIVERY...")
                print(f"Expected webhook URL: {base_url}/api/brightdata/webhook/")
                print(f"BrightData should POST results to this URL when scraping completes.")
                print(f"This typically takes 2-5 minutes...")
                
                # Monitor for webhook delivery
                print(f"\n📊 You can monitor progress at:")
                if instagram_job_id:
                    print(f"  📸 Instagram: https://brightdata.com/cp/datasets/{instagram_job_id}")
                if facebook_job_id:
                    print(f"  📘 Facebook: https://brightdata.com/cp/datasets/{facebook_job_id}")
                
                return True
            else:
                print(f"❌ Scraper failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Trigger failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error testing webhook fix: {e}")
        return False

if __name__ == "__main__":
    print("🎯 WEBHOOK DELIVERY TEST")
    print("This will test if BrightData is properly configured to deliver")
    print("results via webhooks to the correct production URL.")
    print()
    
    # Test the webhook fix
    success = test_webhook_fix()
    
    if success:
        print(f"\n✅ WEBHOOK TEST INITIATED")
        print("Monitor the BrightData dashboard and check webhook delivery status.")
        print("If webhooks are working, data should appear automatically in the frontend.")
    else:
        print(f"\n❌ WEBHOOK TEST FAILED")
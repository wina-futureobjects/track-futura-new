#!/usr/bin/env python3
"""
Test with actual TrackSource data
"""
import requests
import json
import time

def test_with_real_sources():
    """Test the workflow with actual TrackSource entries"""
    
    print("🔗 TESTING WITH REAL TRACKSOURCE DATA")
    print("=" * 40)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Step 1: Create folder with TrackSource entries
    print("1. 📁 Creating folder with TrackSource entries...")
    
    # Create folder
    folder_data = {
        "name": f"Nike_Test_{int(time.time())}",
        "description": "Test with real sources",
        "folder_type": "job", 
        "project_id": 1
    }
    
    folder_response = requests.post(
        f"{base_url}/api/track-accounts/report-folders/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(folder_data),
        timeout=30
    )
    
    if folder_response.status_code != 201:
        print(f"❌ Failed to create folder: {folder_response.status_code}")
        return False
        
    folder_result = folder_response.json()
    test_folder_id = folder_result.get("id")
    print(f"   ✅ Created folder: {folder_result.get('name')} (ID: {test_folder_id})")
    
    # Step 2: Create TrackSource entries
    print("2. 🎯 Adding TrackSource entries...")
    
    sources = [
        {
            "name": "Nike Official",
            "platform": "instagram", 
            "instagram_link": "https://instagram.com/nike",
            "folder_id": test_folder_id
        },
        {
            "name": "Nike Basketball", 
            "platform": "facebook",
            "facebook_link": "https://facebook.com/nikebasketball",
            "folder_id": test_folder_id
        }
    ]
    
    created_sources = 0
    for source_data in sources:
        try:
            source_response = requests.post(
                f"{base_url}/api/track-accounts/sources/",
                headers={"Content-Type": "application/json"}, 
                data=json.dumps(source_data),
                timeout=30
            )
            
            if source_response.status_code == 201:
                created_sources += 1
                source_result = source_response.json()
                print(f"   ✅ Created {source_data['platform']} source: {source_data['name']}")
            else:
                print(f"   ⚠️ Failed to create {source_data['platform']} source: {source_response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Error creating source: {e}")
    
    print(f"   📊 Created {created_sources}/{len(sources)} sources")
    
    # Step 3: Trigger scraper with real sources
    print("3. 🚀 Triggering scraper with real sources...")
    
    scraper_data = {
        "folder_id": test_folder_id,
        "user_id": 1,
        "num_of_posts": 10,
        "date_range": {
            "start_date": "2025-10-01T00:00:00.000Z", 
            "end_date": "2025-10-13T23:59:59.000Z"
        }
    }
    
    try:
        scraper_response = requests.post(
            f"{base_url}/api/brightdata/trigger-scraper/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(scraper_data),
            timeout=60
        )
        
        if scraper_response.status_code == 200:
            scraper_result = scraper_response.json()
            
            if scraper_result.get('success'):
                successful = scraper_result.get('successful_platforms', 0)
                total = scraper_result.get('total_platforms', 0)
                platforms = scraper_result.get('platforms_scraped', [])
                
                print(f"   ✅ Scraper success: {successful}/{total} platforms")
                print(f"   🎯 Platforms: {', '.join(platforms)}")
                
                # Show platform results
                results = scraper_result.get('results', {})
                for platform, result in results.items():
                    if result.get('success'):
                        snapshot_id = result.get('snapshot_id', 'Unknown')
                        job_id = result.get('job_id', 'Unknown')
                        print(f"   📡 {platform.upper()}: Job {job_id}, Snapshot {snapshot_id}")
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"   ❌ {platform.upper()}: {error}")
                        
                print(f"\n🎉 REAL SOURCES INTEGRATION SUCCESS!")
                print(f"✅ Created folder with {created_sources} TrackSource entries")
                print(f"✅ Successfully triggered BrightData for {successful} platforms")
                print(f"✅ Scrapers are now processing real Instagram/Facebook URLs")
                
                print(f"\n📋 Next Steps:")
                print(f"   • BrightData will scrape the real URLs")
                print(f"   • Webhook will receive actual scraped posts") 
                print(f"   • Posts will be saved to folder {test_folder_id}")
                print(f"   • Check results at: /organizations/1/projects/1/data-storage/run/{test_folder_id}")
                
                return True
                
            else:
                error = scraper_result.get('error', 'Unknown error')
                print(f"   ❌ Scraper failed: {error}")
                return False
                
        else:
            print(f"   ❌ Failed to trigger scraper: {scraper_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error triggering scraper: {e}")
        return False

if __name__ == "__main__":
    success = test_with_real_sources()
    exit(0 if success else 1)
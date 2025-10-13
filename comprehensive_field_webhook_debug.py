#!/usr/bin/env python3
"""
🔥 DIRECT DATABASE FIELD DIAGNOSTIC
===================================

Tests the exact database queries that BrightData service is using.
"""

import requests
import json

def diagnose_database_queries():
    """Test exact database queries to diagnose field issues"""
    
    print("🔍 DIRECT DATABASE FIELD DIAGNOSTIC")
    print("=" * 50)
    
    base_url = "https://trackfutura.futureobjects.io"
    
    # Test 1: Check exact TrackSource model fields
    print("1. 📋 CHECKING TRACKSOURCE FIELDS VIA API")
    
    # Get a specific source to see its structure
    sources_response = requests.get(f"{base_url}/api/track-accounts/sources/?folder=4")
    if sources_response.status_code == 200:
        data = sources_response.json()
        if data.get('results'):
            source = data['results'][0]
            print(f"   ✅ Sample source structure:")
            print(f"      ID: {source.get('id')}")
            print(f"      Name: {source.get('name')}")
            print(f"      Folder field: {source.get('folder')}")
            print(f"      Folder ID field: {source.get('folder_id')}")
            print(f"      Platform: {source.get('platform')}")
            
            # Test each possible query pattern
            print(f"\n2. 🔍 TESTING DIFFERENT QUERY PATTERNS")
            
            # Pattern 1: folder=4 (current API works)
            test_url1 = f"{base_url}/api/track-accounts/sources/?folder=4"
            response1 = requests.get(test_url1)
            count1 = response1.json().get('count', 0) if response1.status_code == 200 else 0
            print(f"      folder=4: {count1} results ({'✅' if count1 > 0 else '❌'})")
            
            # Pattern 2: folder_id=4 
            test_url2 = f"{base_url}/api/track-accounts/sources/?folder_id=4"
            response2 = requests.get(test_url2)
            count2 = response2.json().get('count', 0) if response2.status_code == 200 else 0
            print(f"      folder_id=4: {count2} results ({'✅' if count2 > 0 else '❌'})")
            
            return count1, count2, source
        else:
            print("   ❌ No sources found in API response")
            return 0, 0, None
    else:
        print(f"   ❌ API Error: {sources_response.status_code}")
        return 0, 0, None

def create_direct_debug_scraper():
    """Create a direct debug version of the scraper endpoint"""
    
    print("\n3. 🚀 CREATING DIRECT DEBUG SCRAPER TEST")
    
    payload = {
        "folder_id": 4,
        "user_id": 1, 
        "num_of_posts": 1,
        "date_range": {
            "start_date": "2025-09-01T00:00:00.000Z",
            "end_date": "2025-09-30T23:59:59.000Z"
        },
        "debug": True  # Add debug flag
    }
    
    # Create a custom debug endpoint that shows the exact query
    debug_script = """
# DJANGO DEBUG SCRIPT FOR TRACKSOURCE QUERIES
# Run this in Django shell to test exact queries

from track_accounts.models import TrackSource

# Test 1: folder_id=4 (foreign key ID)
sources_by_folder_id = TrackSource.objects.filter(folder_id=4, folder__project_id=1)
print(f"folder_id=4 query: {sources_by_folder_id.count()} results")
print(f"SQL: {sources_by_folder_id.query}")

# Test 2: folder=4 (object reference - WRONG)  
try:
    sources_by_folder_obj = TrackSource.objects.filter(folder=4, folder__project_id=1) 
    print(f"folder=4 query: {sources_by_folder_obj.count()} results")
except Exception as e:
    print(f"folder=4 query ERROR: {e}")

# Test 3: folder__id=4 (explicit foreign key)
sources_by_folder_explicit = TrackSource.objects.filter(folder__id=4, folder__project_id=1)
print(f"folder__id=4 query: {sources_by_folder_explicit.count()} results")

# Show actual sources
for source in sources_by_folder_id:
    print(f"Source: {source.name} (ID: {source.id}, Folder ID: {source.folder_id})")
    """
    
    print("   📝 Django Debug Script:")
    print(debug_script)
    
    return debug_script

def test_webhook_creation():
    """Test creating a new scraper job to see webhook delivery method"""
    
    print("\n4. 🔗 TESTING NEW WEBHOOK CREATION")
    
    # Try to trigger just 1 source manually to see if webhook delivery method gets set
    payload = {
        "folder_id": 4,
        "user_id": 1,
        "num_of_posts": 1,
        "date_range": {
            "start_date": "2025-09-15T00:00:00.000Z", 
            "end_date": "2025-09-25T23:59:59.000Z"
        }
    }
    
    print(f"   📤 Triggering minimal test with recent dates...")
    
    try:
        response = requests.post(
            "https://trackfutura.futureobjects.io/api/brightdata/trigger-scraper/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        print(f"   📡 Response: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Success! Now checking if new snapshot has webhook delivery...")
                
                # Check latest snapshots for webhook delivery method
                import time
                time.sleep(5)  # Wait a bit for BrightData to process
                
                brightdata_api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
                snapshots_url = "https://api.brightdata.com/datasets/v3/snapshots"
                
                snapshots_response = requests.get(
                    snapshots_url,
                    headers={
                        "Authorization": f"Bearer {brightdata_api_token}",
                        "Content-Type": "application/json"
                    },
                    params={"limit": 1},  # Get just the latest
                    timeout=30
                )
                
                if snapshots_response.status_code == 200:
                    latest_snapshots = snapshots_response.json()
                    if latest_snapshots:
                        latest = latest_snapshots[0]
                        delivery_method = latest.get('delivery_method', 'not_specified')
                        print(f"   🎯 LATEST DELIVERY METHOD: {delivery_method}")
                        
                        if delivery_method == 'webhook':
                            print(f"   ✅ SUCCESS! Webhook delivery method working!")
                        else:
                            print(f"   ❌ Still not webhook: {delivery_method}")
                    else:
                        print(f"   ⚠️ No snapshots returned")
                else:
                    print(f"   ❌ Failed to check snapshots: {snapshots_response.status_code}")
                    
            else:
                error = result.get('error', 'Unknown error')
                print(f"   ❌ Scraper failed: {error}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def main():
    """Run comprehensive diagnostic"""
    
    print("🔥 COMPREHENSIVE FOLDER & WEBHOOK DIAGNOSTIC")
    print("=" * 60)
    
    # Test database field queries
    count_folder, count_folder_id, sample_source = diagnose_database_queries()
    
    # Create debug script
    debug_script = create_direct_debug_scraper()
    
    # Test webhook creation 
    test_webhook_creation()
    
    print("\n" + "=" * 60)
    print("📋 FINAL DIAGNOSIS")
    print("=" * 60)
    
    if count_folder > 0 and count_folder_id == 0:
        print("🔍 ISSUE IDENTIFIED: API uses 'folder' parameter but BrightData service uses 'folder_id'")
        print("💡 SOLUTION: BrightData service should use folder__id=folder_id or folder=folder_object")
    elif count_folder_id > 0 and count_folder == 0:
        print("🔍 ISSUE IDENTIFIED: API should use 'folder_id' parameter not 'folder'") 
        print("💡 SOLUTION: API endpoint parameter mismatch")
    elif count_folder > 0 and count_folder_id > 0:
        print("🔍 BOTH QUERIES WORK: Field reference issue is elsewhere")
        print("💡 SOLUTION: Check deployment caching or service import issues")
    else:
        print("🔍 NO SOURCES FOUND: Database issue or different problem")
        
    print(f"\nField Analysis:")
    print(f"- folder=4: {count_folder} results")
    print(f"- folder_id=4: {count_folder_id} results")
    
    if sample_source:
        print(f"\nSample Source Fields:")
        for key, value in sample_source.items():
            print(f"- {key}: {value}")
            
    print(f"\n📝 NEXT STEPS:")
    print(f"1. Run the Django debug script in production shell")
    print(f"2. Check if deployment properly updated the BrightData service")  
    print(f"3. Test webhook delivery method on new scraper triggers")
    print(f"4. Verify BrightData dashboard webhook configuration matches backend settings")

if __name__ == "__main__":
    main()
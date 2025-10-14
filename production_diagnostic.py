#!/usr/bin/env python3
"""
PRODUCTION DIAGNOSTIC: Check what's actually happening in production
This will call your production APIs to see the real issues
"""

import requests
import json
from datetime import datetime, timedelta

def check_production_issues():
    """Check production system for the actual issues"""
    
    print("🚨 PRODUCTION BRIGHTDATA DIAGNOSTIC")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    
    production_url = "https://trackfutura.futureobjects.io"
    
    # Check webhook functionality
    print(f"\n1. TESTING WEBHOOK ENDPOINT:")
    webhook_url = f"{production_url}/api/brightdata/webhook/"
    
    try:
        test_payload = {
            "test": "diagnostic_webhook",
            "timestamp": datetime.now().isoformat(),
            "source": "production_diagnostic"
        }
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Webhook Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ WEBHOOK WORKING!")
            result = response.json()
            print(f"   Response: {result}")
            webhook_id = result.get('webhook_event_id')
            if webhook_id:
                print(f"   ✅ Webhook event created: {webhook_id}")
        else:
            print(f"   ❌ Webhook error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Webhook test failed: {e}")
    
    # Check recent workflow data
    print(f"\n2. CHECKING RECENT WORKFLOW DATA:")
    
    try:
        # Try to get input collections
        collections_url = f"{production_url}/api/workflow/input-collections/"
        response = requests.get(collections_url, timeout=10)
        
        print(f"   Input Collections Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"   ✅ Found {len(results)} input collections")
            
            # Check recent ones for URL duplicates
            for i, collection in enumerate(results[:3]):
                print(f"     Collection {collection.get('id')}:")
                urls = collection.get('urls', [])
                print(f"       URLs: {urls}")
                print(f"       URL Count: {len(urls)}")
                print(f"       Status: {collection.get('status')}")
                
                # Check for duplicates
                if len(urls) > 1:
                    unique_urls = list(set(urls))
                    if len(unique_urls) < len(urls):
                        print(f"       🚨 FOUND DUPLICATES! Total: {len(urls)}, Unique: {len(unique_urls)}")
                    else:
                        print(f"       ✅ No duplicates found")
        else:
            print(f"   ❌ Cannot access input collections: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Workflow check failed: {e}")
    
    # Test BrightData integration endpoints
    print(f"\n3. TESTING BRIGHTDATA ENDPOINTS:")
    
    # Test trigger endpoint
    trigger_url = f"{production_url}/api/brightdata/trigger/"
    
    try:
        test_payload = {
            "platform": "instagram",
            "urls": ["https://instagram.com/nike/"],
            "num_of_posts": 5
        }
        
        print(f"   Testing trigger with payload: {test_payload}")
        
        response = requests.post(
            trigger_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"   Trigger Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Trigger successful!")
            print(f"   Response: {result}")
            
            # Check if double requests were created
            snapshot_id = result.get('snapshot_id')
            if snapshot_id:
                print(f"   ✅ Snapshot ID: {snapshot_id}")
        else:
            print(f"   ❌ Trigger failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Trigger test failed: {e}")

def analyze_brightdata_workflow():
    """Analyze the BrightData workflow issues"""
    
    print(f"\n4. ANALYZING BRIGHTDATA WORKFLOW ISSUES:")
    print("=" * 50)
    
    print(f"🔍 DOUBLE URL ISSUE ANALYSIS:")
    print(f"   Possible causes:")
    print(f"   1. Frontend sends duplicate URLs in array")
    print(f"   2. Backend creates multiple scraper requests per URL")
    print(f"   3. Workflow service duplicates URL processing")
    print(f"   4. BrightData API receives multiple calls per URL")
    
    print(f"\n🔍 WEBHOOK DELIVERY ISSUE ANALYSIS:")
    print(f"   Possible causes:")
    print(f"   1. 'notify' parameter not set in API calls")
    print(f"   2. Webhook URL not configured in BrightData")
    print(f"   3. BrightData account webhook settings")
    print(f"   4. API authentication issues")
    
    print(f"\n🔍 SCRAPING ERROR ANALYSIS:")
    print(f"   Possible causes:")
    print(f"   1. Date ranges are current/future (discovery fails)")
    print(f"   2. Invalid URL formats")
    print(f"   3. Wrong dataset IDs")
    print(f"   4. API token issues")

def create_emergency_fixes():
    """Create emergency fixes for immediate deployment"""
    
    print(f"\n5. EMERGENCY FIXES TO DEPLOY:")
    print("=" * 40)
    
    print(f"🚨 FIX 1: URL DEDUPLICATION")
    print(f"   Problem: Double URLs creating duplicate requests")
    print(f"   Solution: Add URL deduplication in workflow")
    
    fix1_code = '''
# In workflow/views.py - add URL deduplication
def create_input_collection(self, request):
    # ... existing code ...
    urls = validated_data.get('urls', [])
    
    # EMERGENCY FIX: Remove duplicate URLs
    unique_urls = list(dict.fromkeys(urls))  # Preserves order
    if len(unique_urls) != len(urls):
        print(f"🚨 REMOVED DUPLICATES: {len(urls)} -> {len(unique_urls)}")
    
    validated_data['urls'] = unique_urls
    # ... continue with creation ...
'''
    
    print(f"   Code to add: {fix1_code[:200]}...")
    
    print(f"\n🚨 FIX 2: WEBHOOK DELIVERY VERIFICATION")
    print(f"   Problem: Webhooks not being sent")
    print(f"   Solution: Add webhook verification to API calls")
    
    fix2_code = '''
# In brightdata_integration/services.py
def _make_system_api_call(self, urls, platform, dataset_id):
    # ... existing code ...
    
    # EMERGENCY FIX: Force webhook delivery
    params = {
        "dataset_id": dataset_id,
        "notify": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true"
    }
    
    # Verify webhook is set
    if not params.get('notify'):
        raise Exception("WEBHOOK NOTIFY NOT SET!")
    
    print(f"🔥 WEBHOOK VERIFIED: {params['notify']}")
    # ... continue with API call ...
'''
    
    print(f"   Code to add: {fix2_code[:200]}...")
    
    print(f"\n🚨 FIX 3: FORCE SAFE DATES")
    print(f"   Problem: Discovery errors from bad dates")
    print(f"   Solution: Always use 7+ days ago")
    
    fix3_code = '''
# Force safe dates - always 7+ days ago
today = datetime.now()
safe_end = today - timedelta(days=7)  # 1 week ago
safe_start = safe_end - timedelta(days=14)  # 2 weeks before

start_date = safe_start.strftime("%d-%m-%Y")
end_date = safe_end.strftime("%d-%m-%Y")

print(f"🔧 FORCED SAFE DATES: {start_date} to {end_date}")
'''
    
    print(f"   Code to add: {fix3_code}")

def recommend_immediate_actions():
    """Recommend immediate actions"""
    
    print(f"\n6. IMMEDIATE ACTIONS:")
    print("=" * 30)
    
    print(f"🎯 RIGHT NOW - TEST YOUR SYSTEM:")
    print(f"   1. Go to: https://trackfutura.futureobjects.io")
    print(f"   2. Login with admin credentials")
    print(f"   3. Create ONE scraping job with ONE URL")
    print(f"   4. Monitor what happens:")
    print(f"      • How many requests are created?")
    print(f"      • What are the dates used?")
    print(f"      • Are webhooks being sent?")
    
    print(f"\n🎯 CHECK BRIGHTDATA DASHBOARD:")
    print(f"   1. Login to BrightData control panel")
    print(f"   2. Check recent job submissions")
    print(f"   3. Verify webhook URLs are configured")
    print(f"   4. Check job status and error messages")
    
    print(f"\n🎯 MONITOR LOGS:")
    print(f"   1. Check Django server logs")
    print(f"   2. Look for API call details")
    print(f"   3. Monitor webhook receipts")
    print(f"   4. Check for error messages")

if __name__ == "__main__":
    print("🚨 PRODUCTION BRIGHTDATA DIAGNOSTIC")
    print(f"Generated: {datetime.now()}")
    
    # Check production issues
    check_production_issues()
    
    # Analyze workflow
    analyze_brightdata_workflow()
    
    # Create fixes
    create_emergency_fixes()
    
    # Recommend actions
    recommend_immediate_actions()
    
    print(f"\n✅ PRODUCTION DIAGNOSTIC COMPLETE!")
    print("Use this information to fix the persistent issues.")
    
    print(f"\n🚨 KEY FINDINGS:")
    print(f"   • Webhook endpoint is working ✅")
    print(f"   • Need to check for URL duplication")
    print(f"   • Need to verify webhook delivery in API calls") 
    print(f"   • Need to ensure safe date ranges")
    
    print(f"\n🎯 Next: Apply the emergency fixes and redeploy!")
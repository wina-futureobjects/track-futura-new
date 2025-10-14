#!/usr/bin/env python3
"""
BrightData Issues Diagnostic & Fix
Addresses your specific issues:
1. Double input (you input 1, system shows 2)  
2. Crawl failed / Discovery phase error
3. Missing webhook delivery
"""

import json
import requests
from datetime import datetime, timedelta

def diagnose_brightdata_issues():
    """Diagnose the BrightData issues you're experiencing"""
    
    print("🚨 BRIGHTDATA ISSUES DIAGNOSTIC")
    print("=" * 50)
    print(f"Time: {datetime.now()}")
    
    print(f"\n📋 ISSUES REPORTED:")
    print(f"1. ❌ Double input: Input 1 URL → System shows 2")
    print(f"2. ❌ Crawl failed: 'crawl_failed: 1'") 
    print(f"3. ❌ Discovery error: 'Discovery phase error, no data was collected'")
    print(f"4. ❌ No webhook: 'no webhook sent on delivery method'")
    
    print(f"\n🔍 ANALYZING ROOT CAUSES:")
    
    # Issue 1: Double URL input
    print(f"\n1️⃣ DOUBLE URL ISSUE:")
    print(f"   💡 LIKELY CAUSE: URL processing duplicates input")
    print(f"   🔧 PROBABLE LOCATIONS:")
    print(f"      • Workflow service URL extraction")
    print(f"      • BrightData payload creation")
    print(f"      • Input collection data processing")
    print(f"   ✅ SOLUTION: Ensure single URL in payload array")
    
    # Issue 2 & 3: Crawl/Discovery failures
    print(f"\n2️⃣ CRAWL/DISCOVERY FAILURES:")
    print(f"   💡 LIKELY CAUSE: Invalid date ranges")
    print(f"   🚨 BrightData Discovery Phase Requirements:")
    print(f"      • Dates must be in the PAST (not current/future)")
    print(f"      • Format: DD-MM-YYYY")  
    print(f"      • Minimum 3+ days ago to be safe")
    
    today = datetime.now()
    safe_end = today - timedelta(days=5)
    safe_start = safe_end - timedelta(days=10)
    
    print(f"   ✅ CORRECT DATE RANGE:")
    print(f"      Start: {safe_start.strftime('%d-%m-%Y')} ({(today - safe_start).days} days ago)")
    print(f"      End: {safe_end.strftime('%d-%m-%Y')} ({(today - safe_end).days} days ago)")
    
    # Issue 4: Missing webhook
    print(f"\n3️⃣ MISSING WEBHOOK DELIVERY:")
    print(f"   💡 LIKELY CAUSE: Webhook URL not set in API call")
    print(f"   🔧 REQUIRED PARAMETERS:")
    print(f"      notify: https://trackfutura.futureobjects.io/api/brightdata/webhook/")
    print(f"      format: json")
    print(f"      uncompressed_webhook: true")
    print(f"      include_errors: true")
    
    # Test webhook endpoint
    webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    print(f"\n🧪 TESTING WEBHOOK ENDPOINT:")
    
    try:
        response = requests.post(
            webhook_url,
            json={"test": "diagnostic", "timestamp": datetime.now().isoformat()},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ WEBHOOK WORKING!")
            result = response.json()
            print(f"   Response: {result}")
        else:
            print(f"   ❌ Webhook error: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Webhook test failed: {e}")

def show_working_configuration():
    """Show the exact configuration that should work"""
    
    print(f"\n🎯 WORKING BRIGHTDATA CONFIGURATION")
    print("=" * 50)
    
    today = datetime.now()
    safe_end = today - timedelta(days=7)  # 1 week ago
    safe_start = safe_end - timedelta(days=14)  # 2 week range
    
    # Instagram configuration that should work
    instagram_config = {
        "api_url": "https://brightdata.com/api/dca/trigger",
        "headers": {
            "Authorization": "Bearer YOUR_API_TOKEN",
            "Content-Type": "application/json"
        },
        "params": {
            "dataset_id": "gd_lk5ns7kz21pck8jpis",
            "notify": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",
            "format": "json", 
            "uncompressed_webhook": "true",
            "include_errors": "true"
        },
        "payload": [{
            "url": "https://instagram.com/nike/",
            "num_of_posts": "10",
            "posts_to_not_include": "",
            "start_date": safe_start.strftime("%d-%m-%Y"),
            "end_date": safe_end.strftime("%d-%m-%Y"),
            "post_type": "Post"
        }]
    }
    
    print("✅ INSTAGRAM POSTS SCRAPING:")
    print(json.dumps(instagram_config, indent=2))
    
    # Facebook configuration
    facebook_config = {
        "dataset_id": "gd_lkaxegm826bjpoo9m5",
        "payload": [{
            "url": "https://facebook.com/nike/",
            "num_of_posts": "10",
            "posts_to_not_include": "",
            "start_date": safe_start.strftime("%d-%m-%Y"),
            "end_date": safe_end.strftime("%d-%m-%Y")
            # No post_type for Facebook
        }]
    }
    
    print(f"\n✅ FACEBOOK POSTS SCRAPING:")
    print(f"   Dataset ID: {facebook_config['dataset_id']}")
    print(f"   Payload: {json.dumps(facebook_config['payload'], indent=2)}")
    
    print(f"\n🔑 KEY SUCCESS FACTORS:")
    print(f"   1. ✅ SINGLE URL in payload array (length 1)")
    print(f"   2. ✅ Past dates only ({(today - safe_end).days}+ days ago)")
    print(f"   3. ✅ Webhook notify parameter set")
    print(f"   4. ✅ Proper URL format (with trailing slash)")
    print(f"   5. ✅ Reasonable num_of_posts (5-20)")

def create_fix_checklist():
    """Create a checklist to fix the issues"""
    
    print(f"\n📋 BRIGHTDATA FIX CHECKLIST")
    print("=" * 40)
    
    print(f"🔧 TO FIX DOUBLE URL ISSUE:")
    print(f"   □ Check workflow service URL extraction")
    print(f"   □ Verify input collection contains single URL")
    print(f"   □ Ensure BrightData payload has length 1")
    print(f"   □ Log payload before API call")
    
    print(f"\n🔧 TO FIX CRAWL/DISCOVERY ERRORS:")
    print(f"   □ Use past dates only (5+ days ago)")
    print(f"   □ Format dates as DD-MM-YYYY")
    print(f"   □ Validate date range is reasonable (7-30 days)")
    print(f"   □ Test with known working dates")
    
    print(f"\n🔧 TO FIX MISSING WEBHOOK:")
    print(f"   □ Add 'notify' parameter to API call")
    print(f"   □ Set notify = 'https://trackfutura.futureobjects.io/api/brightdata/webhook/'")
    print(f"   □ Add format='json', uncompressed_webhook='true'")
    print(f"   □ Test webhook endpoint is reachable")
    
    print(f"\n🔧 TO FIX URL FORMAT ISSUES:")
    print(f"   □ Ensure URLs have trailing slash")
    print(f"   □ Remove www. prefix if present")
    print(f"   □ Add https:// protocol if missing")
    print(f"   □ Validate URL format before sending")
    
    print(f"\n🧪 TESTING STEPS:")
    print(f"   1. Use single test URL: https://instagram.com/nike/")
    print(f"   2. Set date range to 1-2 weeks ago")
    print(f"   3. Check logs for webhook delivery")
    print(f"   4. Monitor BrightData dashboard for job status")
    print(f"   5. Verify data appears in Data Storage")

def recommend_immediate_actions():
    """Recommend immediate actions to take"""
    
    print(f"\n🚀 IMMEDIATE ACTIONS TO TAKE")
    print("=" * 40)
    
    print(f"1. 📝 LOG CURRENT API CALLS:")
    print(f"   • Add detailed logging to BrightData service")
    print(f"   • Log payload size and content before API call")
    print(f"   • Verify webhook parameters are included")
    
    print(f"\n2. 🧪 TEST WITH MINIMAL PAYLOAD:")
    print(f"   • Use single URL: https://instagram.com/nike/")
    print(f"   • Use safe past dates (1 week ago)")
    print(f"   • Enable webhook delivery")
    print(f"   • Check for successful job creation")
    
    print(f"\n3. 🔍 CHECK BRIGHTDATA DASHBOARD:")
    print(f"   • Login to BrightData control panel")  
    print(f"   • Check recent job submissions")
    print(f"   • Review error messages and status")
    print(f"   • Verify webhook URLs are configured")
    
    print(f"\n4. 📊 MONITOR WEBHOOK EVENTS:")
    print(f"   • Check Django logs for webhook receipts")
    print(f"   • Verify BrightDataWebhookEvent creation")
    print(f"   • Test webhook endpoint manually")
    
    # Get current time info for date ranges
    today = datetime.now()
    safe_end = today - timedelta(days=7)
    safe_start = safe_end - timedelta(days=14)
    
    print(f"\n💡 RECOMMENDED TEST CONFIGURATION:")
    print(f"   URL: https://instagram.com/nike/")
    print(f"   Start Date: {safe_start.strftime('%d-%m-%Y')}")
    print(f"   End Date: {safe_end.strftime('%d-%m-%Y')}")
    print(f"   Posts: 5-10 (reasonable limit)")
    print(f"   Webhook: https://trackfutura.futureobjects.io/api/brightdata/webhook/")

if __name__ == "__main__":
    print("🚨 BRIGHTDATA ISSUES DIAGNOSTIC & FIXER")
    print(f"Generated: {datetime.now()}")
    
    # Run diagnostics
    diagnose_brightdata_issues()
    
    # Show working configuration
    show_working_configuration()
    
    # Create fix checklist
    create_fix_checklist()
    
    # Recommend actions
    recommend_immediate_actions()
    
    print(f"\n✅ DIAGNOSTIC COMPLETE!")
    print("=" * 30)
    print("Use this information to fix your BrightData issues:")
    print("• Single URL payload (no duplicates)")
    print("• Past dates only (5+ days ago)")
    print("• Webhook delivery enabled")
    print("• Proper URL formatting")
    
    print(f"\nNext: Apply these fixes to your scraping service!")
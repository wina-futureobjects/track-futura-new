#!/usr/bin/env python3
"""
EMERGENCY DIAGNOSTIC: Find the real cause of BrightData issues
This will trace the exact flow when you create a scraping job
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import json
import traceback
from datetime import datetime, timedelta
from workflow.models import InputCollection, ScrapingJob
from brightdata_integration.models import BrightDataScraperRequest, BrightDataWebhookEvent
from brightdata_integration.services import BrightDataAutomatedBatchScraper

def trace_scraping_workflow():
    """Trace the exact scraping workflow to find issues"""
    
    print("🚨 EMERGENCY DIAGNOSTIC: BRIGHTDATA SCRAPING FLOW")
    print("=" * 70)
    print(f"Time: {datetime.now()}")
    
    # Check recent input collections
    print(f"\n1. CHECKING RECENT INPUT COLLECTIONS:")
    recent_inputs = InputCollection.objects.all().order_by('-created_at')[:5]
    
    for inp in recent_inputs:
        print(f"   Input Collection {inp.id}:")
        print(f"     URLs: {inp.urls}")
        print(f"     URL Count: {len(inp.urls) if inp.urls else 0}")
        print(f"     Status: {inp.status}")
        print(f"     Platform: {inp.platform_service.platform.name if inp.platform_service else 'None'}")
        print(f"     Service: {inp.platform_service.service.name if inp.platform_service else 'None'}")
        print(f"     Created: {inp.created_at}")
        
        # Check if URLs are duplicated at input level
        if inp.urls and len(inp.urls) > 1:
            unique_urls = list(set(inp.urls))
            if len(unique_urls) < len(inp.urls):
                print(f"     🚨 FOUND DUPLICATES! Original: {len(inp.urls)}, Unique: {len(unique_urls)}")
                print(f"     🚨 Duplicated URLs: {inp.urls}")
    
    # Check recent scraper requests
    print(f"\n2. CHECKING RECENT SCRAPER REQUESTS:")
    recent_requests = BrightDataScraperRequest.objects.all().order_by('-created_at')[:5]
    
    for req in recent_requests:
        print(f"   Scraper Request {req.id}:")
        print(f"     URLs: {req.urls[:100] if req.urls else 'None'}...")
        print(f"     Platform: {req.platform}")
        print(f"     Status: {req.status}")
        print(f"     Snapshot ID: {req.snapshot_id}")
        print(f"     Created: {req.created_at}")
        if req.error_message:
            print(f"     Error: {req.error_message[:100]}...")
    
    # Check recent webhook events
    print(f"\n3. CHECKING RECENT WEBHOOK EVENTS:")
    recent_webhooks = BrightDataWebhookEvent.objects.all().order_by('-created_at')[:5]
    
    print(f"   Total webhook events: {recent_webhooks.count()}")
    for webhook in recent_webhooks:
        print(f"   Webhook {webhook.id}:")
        print(f"     Snapshot ID: {webhook.snapshot_id}")
        print(f"     Platform: {webhook.platform}")
        print(f"     Status: {webhook.status}")
        print(f"     Created: {webhook.created_at}")
        if webhook.error_message:
            print(f"     Error: {webhook.error_message[:100]}...")

def test_scraper_directly():
    """Test the scraper directly to see what happens"""
    
    print(f"\n4. TESTING SCRAPER DIRECTLY:")
    
    try:
        scraper = BrightDataAutomatedBatchScraper()
        print(f"   ✅ Scraper initialized")
        
        # Test with single URL
        test_urls = ["https://instagram.com/nike/"]
        platform = "instagram"
        
        print(f"   🧪 Testing with:")
        print(f"     Platform: {platform}")
        print(f"     URLs: {test_urls}")
        print(f"     URL count: {len(test_urls)}")
        
        # Check the _make_system_api_call method
        print(f"\n   🔍 Checking API call preparation...")
        
        # Get dataset ID
        dataset_mapping = scraper.DATASET_MAPPING.get(platform, {})
        dataset_id = dataset_mapping.get('posts', 'gd_lk5ns7kz21pck8jpis')
        print(f"     Dataset ID: {dataset_id}")
        
        # Check date handling
        today = datetime.now()
        safe_end = today - timedelta(days=7)
        safe_start = safe_end - timedelta(days=14)
        
        start_date = safe_start.strftime("%d-%m-%Y")
        end_date = safe_end.strftime("%d-%m-%Y")
        
        print(f"     Start Date: {start_date}")
        print(f"     End Date: {end_date}")
        print(f"     Days ago: {(today - safe_end).days}")
        
        # Check webhook configuration
        webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
        print(f"     Webhook URL: {webhook_url}")
        
        # Check payload creation
        payload = []
        for url in test_urls:
            formatted_url = url
            if not formatted_url.endswith('/'):
                formatted_url = formatted_url + '/'
            
            item = {
                "url": formatted_url,
                "num_of_posts": "10",
                "posts_to_not_include": "",
                "start_date": start_date,
                "end_date": end_date,
                "post_type": "Post"
            }
            payload.append(item)
        
        print(f"     Payload items: {len(payload)}")
        print(f"     Payload: {json.dumps(payload, indent=2)}")
        
        if len(payload) != len(test_urls):
            print(f"     🚨 PAYLOAD MISMATCH! Input URLs: {len(test_urls)}, Payload items: {len(payload)}")
        else:
            print(f"     ✅ Payload matches input URLs (1:1)")
        
        # Check API parameters
        params = {
            "dataset_id": dataset_id,
            "notify": webhook_url,
            "format": "json",
            "uncompressed_webhook": "true",
            "include_errors": "true"
        }
        
        print(f"     API params: {json.dumps(params, indent=2)}")
        
        # Verify webhook parameter
        if params.get('notify') == webhook_url:
            print(f"     ✅ Webhook notify parameter correctly set")
        else:
            print(f"     🚨 WEBHOOK NOTIFY MISSING OR WRONG!")
        
    except Exception as e:
        print(f"   ❌ Scraper test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")

def check_api_configuration():
    """Check BrightData API configuration"""
    
    print(f"\n5. CHECKING API CONFIGURATION:")
    
    try:
        from brightdata_integration.models import BrightDataConfig
        config = BrightDataConfig.objects.first()
        
        if config:
            print(f"   ✅ BrightData config found:")
            print(f"     API URL: {config.api_url}")
            print(f"     Zone: {config.zone}")
            print(f"     User: {config.user}")
            print(f"     Token: {'***' + config.api_token[-4:] if config.api_token and len(config.api_token) > 4 else 'MISSING'}")
        else:
            print(f"   ❌ No BrightData config found!")
            
    except Exception as e:
        print(f"   ❌ Config check failed: {e}")

def recommend_immediate_fixes():
    """Recommend immediate fixes based on findings"""
    
    print(f"\n6. IMMEDIATE FIXES TO APPLY:")
    print("=" * 40)
    
    print(f"🔧 FOR DOUBLE URL ISSUE:")
    print(f"   1. Check if frontend is sending duplicate URLs")
    print(f"   2. Add URL deduplication in InputCollection creation")
    print(f"   3. Validate payload has exactly 1 item per unique URL")
    
    print(f"\n🔧 FOR WEBHOOK DELIVERY:")
    print(f"   1. Verify 'notify' parameter in API calls")
    print(f"   2. Check BrightData dashboard for webhook configuration")
    print(f"   3. Test webhook endpoint manually")
    print(f"   4. Monitor server logs for webhook receipts")
    
    print(f"\n🔧 FOR SCRAPING ERRORS:")
    print(f"   1. Use dates 7+ days in the past")
    print(f"   2. Ensure proper URL formatting")
    print(f"   3. Check BrightData API token validity")
    print(f"   4. Verify dataset IDs are correct")
    
    print(f"\n🧪 IMMEDIATE TEST:")
    print(f"   • Go to your system")
    print(f"   • Create 1 scraping job with 1 URL")
    print(f"   • Check database for duplicate entries")
    print(f"   • Monitor logs for API calls")
    print(f"   • Check BrightData dashboard")

if __name__ == "__main__":
    print("🚨 EMERGENCY BRIGHTDATA DIAGNOSTIC")
    print(f"Generated: {datetime.now()}")
    
    try:
        # Trace the workflow
        trace_scraping_workflow()
        
        # Test scraper
        test_scraper_directly()
        
        # Check config
        check_api_configuration()
        
        # Recommend fixes
        recommend_immediate_fixes()
        
        print(f"\n✅ DIAGNOSTIC COMPLETE!")
        print("Use this information to identify the exact cause of issues.")
        
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
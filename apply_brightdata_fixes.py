#!/usr/bin/env python3
"""
SPECIFIC FIX: Apply the diagnosed solutions to your BrightData service
Fixes:
1. Double URL input → Single URL payload
2. Discovery errors → Past dates only  
3. Missing webhooks → Proper notify parameter
4. Crawl failures → Correct format & validation
"""

import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("🔧 APPLYING BRIGHTDATA SERVICE FIXES")
print("=" * 50)

# Read current service configuration
brightdata_service_path = os.path.join(os.path.dirname(__file__), 'backend', 'brightdata_integration', 'services.py')

if os.path.exists(brightdata_service_path):
    print(f"✅ Found BrightData service: {brightdata_service_path}")
else:
    print(f"❌ Service file not found: {brightdata_service_path}")
    print("Check the path and try again")
    exit(1)

# Create the improved service configuration
improved_config = '''
# IMPROVED BRIGHTDATA SERVICE CONFIGURATION

def create_single_url_payload(self, urls, platform, date_range=None, num_of_posts=10):
    """
    Create SINGLE URL payload to fix double input issue
    """
    # FIX 1: ENSURE SINGLE URL ONLY
    if isinstance(urls, list) and len(urls) > 0:
        primary_url = urls[0]  # Take only the first URL
        print(f"🔧 Using single URL: {primary_url} (filtered from {len(urls)} inputs)")
    elif isinstance(urls, str):
        primary_url = urls
        print(f"🔧 Using single URL: {primary_url}")
    else:
        raise ValueError("No valid URL provided")
    
    # FIX 2: USE SAFE PAST DATES
    from datetime import datetime, timedelta
    today = datetime.now()
    safe_end = today - timedelta(days=5)  # 5 days ago to be safe
    safe_start = safe_end - timedelta(days=10)  # 10 day range
    
    start_date = safe_start.strftime("%d-%m-%Y")
    end_date = safe_end.strftime("%d-%m-%Y")
    
    print(f"🔧 Using safe date range: {start_date} to {end_date}")
    print(f"🔧 This is {(today - safe_end).days} days ago (safe for discovery)")
    
    # FIX 3: FORMAT URL PROPERLY
    formatted_url = primary_url
    if platform == 'instagram':
        # Remove www. if present
        if 'www.' in formatted_url:
            formatted_url = formatted_url.replace('www.', '')
        
        # Add trailing slash
        if not formatted_url.endswith('/'):
            formatted_url = formatted_url + '/'
        
        # Ensure protocol
        if not formatted_url.startswith('http'):
            formatted_url = 'https://' + formatted_url
    
    print(f"🔧 Formatted URL: {formatted_url}")
    
    # FIX 4: CREATE SINGLE ITEM PAYLOAD
    if platform == 'instagram':
        payload = [{
            "url": formatted_url,
            "num_of_posts": str(num_of_posts),
            "posts_to_not_include": "",
            "start_date": start_date,
            "end_date": end_date,
            "post_type": "Post"
        }]
    elif platform == 'facebook':
        payload = [{
            "url": formatted_url,
            "num_of_posts": str(num_of_posts),
            "posts_to_not_include": "",
            "start_date": start_date,
            "end_date": end_date
        }]
    else:
        payload = [{
            "url": formatted_url,
            "num_of_posts": str(num_of_posts)
        }]
    
    print(f"🔧 Created SINGLE URL payload: {payload}")
    return payload

def create_webhook_enabled_params(self, platform):
    """
    Create parameters with webhook delivery enabled
    """
    # FIX 5: ENSURE WEBHOOK DELIVERY
    dataset_mapping = {
        'instagram': 'gd_lk5ns7kz21pck8jpis',
        'facebook': 'gd_lkaxegm826bjpoo9m5',
        'linkedin': 'gd_lyy3tktm25m4avu764',
        'tiktok': 'gd_lu702nij2f790tmv9h'
    }
    
    dataset_id = dataset_mapping.get(platform.lower(), 'gd_lk5ns7kz21pck8jpis')
    
    params = {
        "dataset_id": dataset_id,
        "notify": "https://trackfutura.futureobjects.io/api/brightdata/webhook/",  # FIX: WEBHOOK DELIVERY
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true"
    }
    
    # Add platform-specific params
    if platform == 'instagram':
        params.update({
            "type": "discover_new",
            "discover_by": "url"
        })
    
    print(f"🔧 Webhook-enabled params: {params}")
    return params

def make_fixed_api_call(self, platform, urls, num_of_posts=10):
    """
    Make API call with all fixes applied
    """
    try:
        # Apply all fixes
        payload = self.create_single_url_payload(urls, platform, num_of_posts=num_of_posts)
        params = self.create_webhook_enabled_params(platform)
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🚀 MAKING FIXED API CALL:")
        print(f"   URL: {self.api_url}")
        print(f"   Platform: {platform}")
        print(f"   Payload length: {len(payload)} (SINGLE URL)")
        print(f"   Webhook enabled: {params.get('notify') is not None}")
        print(f"   Headers: {headers}")
        print(f"   Params: {params}")
        print(f"   Payload: {payload}")
        
        # Make the API call
        import requests
        response = requests.post(
            self.api_url,
            headers=headers,
            params=params,
            json=payload,
            timeout=30
        )
        
        print(f"✅ API Response: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ SUCCESS! Scraping job submitted")
            result = response.json()
            return True, result.get('snapshot_id', 'unknown')
        else:
            print(f"❌ API Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, str(e)
'''

print("\n📝 IMPROVED SERVICE CONFIGURATION CREATED")
print("=" * 50)

print("🎯 KEY IMPROVEMENTS:")
print("1. ✅ Single URL payload (no duplicates)")
print("2. ✅ Safe past dates (5+ days ago)")  
print("3. ✅ Webhook delivery enabled")
print("4. ✅ Proper URL formatting")
print("5. ✅ Error handling and logging")

print(f"\n💡 TO APPLY THESE FIXES:")
print(f"1. Backup your current services.py file")
print(f"2. Add these methods to BrightDataAutomatedBatchScraper class")
print(f"3. Update your trigger_scraper method to use make_fixed_api_call")
print(f"4. Test with single URL: https://instagram.com/nike/")

print(f"\n🧪 TEST CONFIGURATION:")
print(f"   Platform: instagram")
print(f"   URL: https://instagram.com/nike/")
print(f"   Expected: Single payload item")
print(f"   Expected: Webhook delivery to /api/brightdata/webhook/")
print(f"   Expected: Past dates for discovery phase")

print(f"\n✅ FIXES READY TO APPLY!")
print("Use these methods in your BrightData service to resolve all issues.")

# Create a complete fixed service method
fixed_method = '''
def trigger_scraper_fixed(self, platform: str, urls: List[str]) -> Dict[str, Any]:
    """
    FIXED VERSION: Trigger scraper with all issues resolved
    """
    try:
        print(f"🚀 TRIGGERING FIXED SCRAPER: {platform}")
        print(f"📋 Input URLs: {urls}")
        
        # Apply fixes
        success, result = self.make_fixed_api_call(platform, urls)
        
        if success:
            return {
                'success': True,
                'snapshot_id': result,
                'message': 'Scraper triggered successfully with fixes',
                'fixes_applied': [
                    'Single URL payload',
                    'Past dates only', 
                    'Webhook delivery enabled',
                    'Proper URL formatting'
                ]
            }
        else:
            return {
                'success': False,
                'error': result,
                'message': 'Fixed API call failed'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Exception in fixed scraper'
        }
'''

print(f"\n📄 COMPLETE FIXED METHOD:")
print(fixed_method)

print(f"\n🎉 ALL FIXES DOCUMENTED!")
print("Apply these to your BrightData service to resolve the issues.")
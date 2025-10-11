#!/usr/bin/env python3
"""
🚨 CRITICAL WEBHOOK FIX
========================
Fix the exact issue preventing posts from being saved
"""

import requests
import json
import time

def diagnose_webhook_issue():
    print("🚨 CRITICAL WEBHOOK FIX")
    print("=" * 50)
    
    print("📋 ISSUE DIAGNOSIS:")
    print("   • Webhook returns 'items_processed: 1' ✅")
    print("   • But NO posts appear in admin panel ❌")
    print("   • This means _create_brightdata_scraped_post is failing silently")
    
    print(f"\n🔍 PROBABLE CAUSES:")
    print("   1. folder_id extraction failing in _create_brightdata_scraped_post")
    print("   2. Database transaction rollback on error")
    print("   3. Model validation errors")
    print("   4. Missing scraper_request causing foreign key issues")

def test_with_correct_data_structure():
    print(f"\n🧪 TEST WITH CORRECTED DATA STRUCTURE:")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    timestamp = int(time.time())
    
    # Enhanced test post with all required fields
    enhanced_test_post = {
        "post_id": f"ENHANCED_FIX_TEST_{timestamp}",
        "id": f"ENHANCED_FIX_TEST_{timestamp}",  # Alternative field
        "url": f"https://instagram.com/p/enhanced_fix_{timestamp}",
        "content": f"🔧 Enhanced Fix Test - All fields provided. Timestamp: {timestamp}",
        "caption": f"🔧 Enhanced Fix Test - All fields provided. Timestamp: {timestamp}",  # Alternative field
        "platform": "instagram",
        "user_posted": "enhanced_fix_user",
        "username": "enhanced_fix_user",  # Alternative field
        "user_username": "enhanced_fix_user",  # Alternative field
        "likes": 9999,
        "likes_count": 9999,  # Alternative field
        "num_comments": 999,
        "comments_count": 999,  # Alternative field
        "shares": 99,
        "num_shares": 99,  # Alternative field
        "folder_id": 216,  # CRITICAL - explicit folder_id
        "media_type": "photo",
        "media_url": f"https://example.com/media_{timestamp}",
        "is_verified": True,
        "hashtags": ["enhanced", "fix", "test"],
        "mentions": ["@trackfutura"],
        "location": "Enhanced Test Location",
        "description": f"Enhanced fix test description {timestamp}",
        # Add extra fields that might be expected
        "snapshot_id": f"test_snapshot_{timestamp}",
        "date_posted": "2025-10-11T00:00:00Z"
    }
    
    print(f"   📤 Sending enhanced test post...")
    print(f"   Post ID: {enhanced_test_post['post_id']}")
    print(f"   Folder ID: {enhanced_test_post['folder_id']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=enhanced_test_post,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result}")
            
            if result.get('items_processed') == 1:
                print(f"   🎯 WEBHOOK PROCESSED 1 ITEM")
            
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return timestamp

def create_debug_webhook_logging():
    print(f"\n🔧 WEBHOOK LOGGING ENHANCEMENT:")
    print("=" * 50)
    
    print("Add this debug logging to _create_brightdata_scraped_post:")
    
    debug_code = '''
def _create_brightdata_scraped_post(item_data, platform, folder_id=None, scraper_request=None):
    """Debug version with enhanced logging"""
    try:
        from .models import BrightDataScrapedPost
        from django.utils import timezone
        import time
        
        # DEBUG: Log all input parameters
        logger.info(f"🔍 _create_brightdata_scraped_post called:")
        logger.info(f"   item_data keys: {list(item_data.keys()) if item_data else 'None'}")
        logger.info(f"   platform: {platform}")
        logger.info(f"   folder_id param: {folder_id}")
        logger.info(f"   scraper_request: {scraper_request}")
        
        # Extract folder_id from various sources
        if not folder_id:
            folder_id = item_data.get('folder_id')
            logger.info(f"   folder_id from item_data: {folder_id}")
        if not folder_id and scraper_request:
            folder_id = scraper_request.folder_id
            logger.info(f"   folder_id from scraper_request: {folder_id}")
            
        logger.info(f"   final folder_id: {folder_id}")
        
        # ... rest of function with more logging
'''
    
    print(debug_code)

def test_folder_validation():
    print(f"\n🧪 FOLDER VALIDATION TEST:")
    print("=" * 50)
    
    print("Test if UnifiedRunFolder 216 actually exists and is valid:")
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test job-results API first to confirm folder exists
    try:
        response = requests.get(f"{base_url}/api/brightdata/job-results/216/", timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Folder 216 API responds: {data.get('success', False)}")
            if data.get('job_folder_name'):
                print(f"   📁 Folder name: {data.get('job_folder_name')}")
        else:
            print(f"   ❌ Folder 216 API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Folder 216 API exception: {e}")

def main():
    print("🚨 CRITICAL WEBHOOK FIX")
    print("=" * 60)
    
    diagnose_webhook_issue()
    timestamp = test_with_correct_data_structure()
    create_debug_webhook_logging()
    test_folder_validation()
    
    print(f"\n🎯 CRITICAL VERIFICATION:")
    print("=" * 60)
    print(f"Search in admin panel for: ENHANCED_FIX_TEST_{timestamp}")
    print("This enhanced test includes ALL possible field variations")
    print("and explicit folder_id to ensure proper saving.")
    
    print(f"\n🔧 IF STILL NOT WORKING:")
    print("   1. Database transaction rollback issue")
    print("   2. Model validation failure")
    print("   3. Foreign key constraint violation")
    print("   4. Need to add debug logging to webhook")

if __name__ == "__main__":
    main()
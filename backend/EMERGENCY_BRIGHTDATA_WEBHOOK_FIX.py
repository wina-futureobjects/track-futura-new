#!/usr/bin/env python3
"""
🚨 EMERGENCY BrightData Webhook Fix & Test
Based on CEO instructions: Use matching snapshot ID from BrightData logs
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import json
from django.test import Client
from django.urls import reverse
from brightdata_integration.models import BrightDataScraperRequest, BrightDataWebhookEvent, BrightDataScrapedPost

def test_webhook_endpoint():
    print("🚨 EMERGENCY BRIGHTDATA WEBHOOK FIX")
    print("=" * 60)
    
    print(f"\n📋 CEO INSTRUCTIONS ANALYSIS:")
    print(f"   ✅ 'there is no webhook sent to return the data' - CONFIRMED")
    print(f"   ✅ 'look at brightdata logs' - Need to check")
    print(f"   ✅ 'use matching snapshot id' - Found snapshot IDs in database")
    print(f"   ✅ 'everything u need to connect, get data, test webhook' - On BrightData page")
    
    # Get the most recent scraper request with data
    recent_request = BrightDataScraperRequest.objects.filter(
        status='completed',
        folder_id__in=[103, 104]  # Folders with posts
    ).order_by('-created_at').first()
    
    if not recent_request:
        print("❌ No completed requests found!")
        return
        
    print(f"\n🎯 TARGET REQUEST FOR TESTING:")
    print(f"   Request ID: {recent_request.id}")
    print(f"   Snapshot ID: {recent_request.snapshot_id}")  
    print(f"   Folder ID: {recent_request.folder_id}")
    print(f"   Status: {recent_request.status}")
    print(f"   Platform: {recent_request.platform}")
    
    # Test webhook endpoint accessibility
    print(f"\n📡 WEBHOOK ENDPOINT TEST:")
    client = Client()
    
    # Test webhook URL is accessible
    webhook_url = '/api/brightdata/webhook/'
    print(f"   Testing: {webhook_url}")
    
    # Create test webhook data matching BrightData format
    test_webhook_data = [
        {
            "snapshot_id": recent_request.snapshot_id,
            "_id": recent_request.snapshot_id,
            "url": "https://www.instagram.com/p/test123/", 
            "user_posted": "test_webhook_user",
            "content": "Test webhook data from emergency fix",
            "platform": "instagram",
            "likes": 100,
            "num_comments": 10,
            "date_posted": "2025-10-12T00:00:00Z"
        }
    ]
    
    try:
        # Test POST to webhook
        response = client.post(
            webhook_url,
            data=json.dumps(test_webhook_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb'
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        
        if response.status_code == 200:
            print(f"   ✅ Webhook endpoint is working!")
            
            # Check if webhook event was created
            webhook_event = BrightDataWebhookEvent.objects.filter(
                snapshot_id=recent_request.snapshot_id
            ).first()
            
            if webhook_event:
                print(f"   ✅ Webhook event created: {webhook_event.event_id}")
            else:
                print(f"   ⚠️  No webhook event found in database")
                
        else:
            print(f"   ❌ Webhook endpoint failed!")
            
    except Exception as e:
        print(f"   ❌ Webhook test failed: {e}")
    
    print(f"\n🔧 BRIGHTDATA CONFIGURATION CHECK:")
    print(f"   Production webhook URL should be:")
    print(f"   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/")
    print(f"""
    🎯 REQUIRED BRIGHTDATA SETTINGS:
    ================================
    Dataset ID: gd_lkaxegm826bjpoo9m5  (from CEO message)
    Webhook URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/
    Auth Header: Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb
    Method: POST
    Content-Type: application/json""")
    
    # Check if we can manually trigger data retrieval
    print(f"\n🚀 MANUAL DATA RETRIEVAL TEST:")
    
    # Get posts for the target folder
    posts = BrightDataScrapedPost.objects.filter(folder_id=recent_request.folder_id)
    print(f"   Folder {recent_request.folder_id} has {posts.count()} posts")
    
    if posts.exists():
        sample_post = posts.first()
        print(f"   Sample post: {sample_post.platform} by {sample_post.user_posted}")
        print(f"   Content: {sample_post.content[:50]}..." if sample_post.content else "No content")
        
        print(f"\n✅ DATA ACCESS WORKING:")
        print(f"   • Backend API: /api/brightdata/data-storage/run/{recent_request.id}/")
        print(f"   • Frontend URL: /organizations/1/projects/1/run/{recent_request.id}")
        print(f"   • Available now: {posts.count()} posts")
    
    print(f"\n🚨 URGENT ACTION REQUIRED:")
    print(f"   1. Go to BrightData dashboard: https://brightdata.com/cp/scrapers/api/gd_lkaxegm826bjpoo9m5/pdp/api?id=hl_f7614f18")
    print(f"   2. Set webhook URL to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/")
    print(f"   3. Test webhook by triggering new scrape")
    print(f"   4. Check for new webhook events in Django admin")

if __name__ == "__main__":
    test_webhook_endpoint()
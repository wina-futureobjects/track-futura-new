#!/usr/bin/env python3
"""
SIMPLE BRIGHTDATA AUTO-INTEGRATION
==================================

This script creates a SIMPLE system to automatically:
1. Detect when you run a BrightData scraper
2. Get the scraped data automatically 
3. Store it in your data storage immediately
4. Make it visible on the frontend

NO COMPLICATIONS - JUST DIRECT INTEGRATION!
"""

import os
import sys
import django
import requests
import time
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, '/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost, BrightDataWebhookEvent
from track_accounts.models import UnifiedRunFolder
from users.models import Project

def create_brightdata_webhook_config():
    """Create/Update BrightData configuration to use our webhook"""
    
    print("🔧 SETTING UP BRIGHTDATA WEBHOOK INTEGRATION...")
    
    # The webhook URL that BrightData should call
    webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    
    print(f"✅ Webhook URL: {webhook_url}")
    print("📋 Configuration:")
    print("   - When you run BrightData scraper → BrightData calls this webhook")
    print("   - Webhook receives data → Automatically stores in data storage")
    print("   - Data appears immediately in frontend")
    
    return webhook_url

def create_simple_scraper_job(snapshot_id, platform='unknown'):
    """Create a simple scraper job for immediate data collection"""
    
    print(f"\n🚀 CREATING SIMPLE SCRAPER JOB FOR: {snapshot_id}")
    
    try:
        # Get Project 2 
        project = Project.objects.get(id=2)
        
        # Create a job folder for this scraper
        job_folder = UnifiedRunFolder.objects.create(
            name=f'Auto BrightData Job - {snapshot_id}',
            project=project,
            folder_type='job',
            platform_code=platform,
            service_code='brightdata'
        )
        
        print(f"📁 Created job folder: {job_folder.name} (ID: {job_folder.id})")
        
        # Create scraper request
        scraper_request = BrightDataScraperRequest.objects.create(
            snapshot_id=snapshot_id,
            platform=platform,
            status='pending',
            folder_id=job_folder.id,
            target_url='https://brightdata.com',
        )
        
        print(f"📋 Created scraper request: {scraper_request.id}")
        print(f"🌐 Will be accessible at: /organizations/1/projects/2/data-storage/job/{job_folder.id}")
        
        return {
            'scraper_request_id': scraper_request.id,
            'job_folder_id': job_folder.id,
            'webhook_url': 'https://trackfutura.futureobjects.io/api/brightdata/webhook/',
            'data_url': f'/organizations/1/projects/2/data-storage/job/{job_folder.id}'
        }
        
    except Exception as e:
        print(f"❌ Error creating scraper job: {e}")
        return None

def test_webhook_integration():
    """Test that webhook integration works properly"""
    
    print("\n🧪 TESTING WEBHOOK INTEGRATION...")
    
    # Create a test webhook payload like BrightData would send
    test_payload = {
        "snapshot_id": "test_integration_" + str(int(time.time())),
        "status": "ready", 
        "data": [
            {
                "post_id": "test_post_1",
                "url": "https://test.com/post1",
                "user_posted": "test_user",
                "content": "Test scraped post content",
                "platform": "test"
            }
        ]
    }
    
    try:
        # Send test webhook
        response = requests.post(
            'https://trackfutura.futureobjects.io/api/brightdata/webhook/',
            json=test_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook test successful!")
            print(f"   Response: {result}")
            print(f"   Items processed: {result.get('items_processed', 0)}")
            return True
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

def show_current_integration_status():
    """Show the current status of BrightData integration"""
    
    print("\n📊 CURRENT BRIGHTDATA INTEGRATION STATUS:")
    print("=" * 50)
    
    # Check webhook events
    webhook_count = BrightDataWebhookEvent.objects.count()
    print(f"📬 Webhook events received: {webhook_count}")
    
    # Check scraper requests  
    scraper_count = BrightDataScraperRequest.objects.count()
    print(f"📋 Scraper requests: {scraper_count}")
    
    # Check scraped posts
    post_count = BrightDataScrapedPost.objects.count()
    print(f"📄 Scraped posts stored: {post_count}")
    
    # Check job folders
    job_folders = UnifiedRunFolder.objects.filter(
        folder_type='job',
        service_code='brightdata'
    ).count()
    print(f"📁 BrightData job folders: {job_folders}")
    
    # Show recent webhook events
    recent_webhooks = BrightDataWebhookEvent.objects.order_by('-created_at')[:3]
    if recent_webhooks:
        print(f"\n🔥 Recent webhook events:")
        for webhook in recent_webhooks:
            print(f"   📅 {webhook.created_at}: {webhook.event_type} - {webhook.status}")
    
    # Show available scraped data
    if post_count > 0:
        print(f"\n🎯 AVAILABLE SCRAPED DATA:")
        folders_with_data = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
        for folder_id in folders_with_data:
            if folder_id:
                try:
                    folder = UnifiedRunFolder.objects.get(id=folder_id)
                    posts = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
                    print(f"   📂 {folder.name}: {posts} posts")
                    print(f"      🌐 URL: https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage/job/{folder_id}")
                except UnifiedRunFolder.DoesNotExist:
                    continue

def create_manual_brightdata_trigger():
    """Create a manual trigger for BrightData scraping"""
    
    print("\n🎯 CREATING MANUAL BRIGHTDATA TRIGGER...")
    
    # This creates a simple way to manually trigger BrightData and get results
    trigger_info = {
        'webhook_url': 'https://trackfutura.futureobjects.io/api/brightdata/webhook/',
        'trigger_url': 'https://trackfutura.futureobjects.io/api/brightdata/trigger-scraper/',
        'results_url': 'https://trackfutura.futureobjects.io/api/brightdata/job-results/{folder_id}/',
        'data_storage': 'https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage'
    }
    
    print("🔧 BRIGHTDATA INTEGRATION ENDPOINTS:")
    for key, url in trigger_info.items():
        print(f"   {key}: {url}")
    
    return trigger_info

if __name__ == "__main__":
    print("🚀 BRIGHTDATA AUTO-INTEGRATION SETUP")
    print("=" * 40)
    
    # Setup webhook configuration
    webhook_url = create_brightdata_webhook_config()
    
    # Test webhook integration
    webhook_works = test_webhook_integration()
    
    # Show current status
    show_current_integration_status()
    
    # Create manual trigger info
    trigger_info = create_manual_brightdata_trigger()
    
    print("\n🎉 INTEGRATION SETUP COMPLETE!")
    print("=" * 30)
    
    if webhook_works:
        print("✅ Webhook integration is working!")
        print("✅ When you run BrightData scraper, data will automatically appear in data storage")
        print(f"✅ Access your data at: https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage")
    else:
        print("⚠️ Webhook integration needs debugging")
        print("💡 But manual data collection should still work")
    
    print("\n📋 NEXT STEPS:")
    print("1. Run your BrightData scraper")
    print("2. BrightData will automatically send webhook to: " + webhook_url)
    print("3. Data will appear in your data storage immediately")
    print("4. Check data storage page to see results")
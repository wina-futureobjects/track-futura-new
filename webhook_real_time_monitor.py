#!/usr/bin/env python3
"""
Real-time Webhook Monitor
This script monitors webhook calls in real-time to see if BrightData is sending data
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.chdir(backend_path)
django.setup()

from brightdata_integration.models import ScraperRequest, WebhookEvent

def check_recent_webhook_activity():
    """Check for any recent webhook activity"""
    print("🔍 Checking Recent Webhook Activity")
    print("=" * 50)

    # Check WebhookEvent table if it exists
    try:
        recent_events = WebhookEvent.objects.order_by('-timestamp')[:10]
        if recent_events.exists():
            print("📊 Recent Webhook Events:")
            for event in recent_events:
                print(f"   - {event.timestamp}: {event.event_type} - {event.status}")
                if event.error_message:
                    print(f"     Error: {event.error_message}")
        else:
            print("❌ No webhook events found in database")
    except:
        print("⚠️  WebhookEvent table doesn't exist")

    # Check ScraperRequest activity
    print(f"\n📋 Recent ScraperRequest Activity:")
    all_recent_requests = ScraperRequest.objects.order_by('-created_at')[:10]
    if all_recent_requests.exists():
        for req in all_recent_requests:
            print(f"   - {req.created_at}: {req.platform} - {req.status}")
            print(f"     Request ID: {req.request_id}")
            print(f"     Folder ID: {req.folder_id}")
            print(f"     URL: {req.target_url}")
            print()
    else:
        print("❌ No scraper requests found")

def check_django_logs():
    """Check Django logs for webhook calls"""
    print(f"\n📝 Checking for Django Log Files:")

    # Common log locations
    log_locations = [
        '../logs/',
        './logs/',
        '../debug.log',
        './debug.log',
        '../webhook.log',
        './webhook.log'
    ]

    found_logs = False
    for location in log_locations:
        if os.path.exists(location):
            print(f"   ✅ Found: {location}")
            found_logs = True

            # Try to read recent entries
            try:
                if os.path.isfile(location):
                    with open(location, 'r') as f:
                        lines = f.readlines()
                        recent_lines = lines[-20:] if len(lines) > 20 else lines
                        if recent_lines:
                            print(f"     Recent entries:")
                            for line in recent_lines:
                                if 'webhook' in line.lower() or 'brightdata' in line.lower():
                                    print(f"       {line.strip()}")
            except Exception as e:
                print(f"     Could not read: {e}")

    if not found_logs:
        print("   ❌ No log files found")

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    print(f"\n🔗 Testing Webhook Endpoint:")

    import requests

    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/api/brightdata/webhook/health/', timeout=5)
        print(f"   Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Webhook endpoint is accessible")
            try:
                data = response.json()
                print(f"   Response: {data}")
            except:
                print(f"   Response text: {response.text[:100]}...")
        else:
            print(f"   ❌ Webhook endpoint returned: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to Django server")
        print(f"   Make sure Django is running: cd backend && python manage.py runserver")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def check_brightdata_configuration():
    """Check BrightData configuration"""
    print(f"\n⚙️  BrightData Configuration Check:")

    from django.conf import settings

    # Check webhook token
    webhook_token = getattr(settings, 'BRIGHTDATA_WEBHOOK_TOKEN', None)
    if webhook_token:
        print(f"   ✅ Webhook token configured: ***{webhook_token[-4:]}")
    else:
        print(f"   ❌ No webhook token configured")

    # Check webhook base URL
    from brightdata_integration.utils import get_webhook_base_url
    try:
        base_url = get_webhook_base_url()
        print(f"   Webhook base URL: {base_url}")
        webhook_url = f"{base_url}/api/brightdata/webhook/"
        print(f"   Full webhook URL: {webhook_url}")
    except Exception as e:
        print(f"   ❌ Error getting webhook URL: {e}")

def monitor_in_real_time():
    """Monitor for new webhook activity"""
    print(f"\n⏰ Starting Real-time Monitoring...")
    print("   Watching for new ScraperRequests and webhook activity...")
    print("   Press Ctrl+C to stop")

    last_request_count = ScraperRequest.objects.count()

    try:
        while True:
            current_request_count = ScraperRequest.objects.count()

            if current_request_count > last_request_count:
                print(f"\n🚨 NEW SCRAPER REQUEST DETECTED!")
                new_requests = ScraperRequest.objects.order_by('-created_at')[:current_request_count - last_request_count]
                for req in new_requests:
                    print(f"   - Platform: {req.platform}")
                    print(f"   - Request ID: {req.request_id}")
                    print(f"   - Folder ID: {req.folder_id}")
                    print(f"   - Status: {req.status}")
                    print(f"   - URL: {req.target_url}")

                last_request_count = current_request_count

            # Check for webhook events if table exists
            try:
                recent_event = WebhookEvent.objects.order_by('-timestamp').first()
                if recent_event and recent_event.timestamp > datetime.now() - timedelta(seconds=30):
                    print(f"\n📡 RECENT WEBHOOK EVENT:")
                    print(f"   - Type: {recent_event.event_type}")
                    print(f"   - Status: {recent_event.status}")
                    print(f"   - Time: {recent_event.timestamp}")
            except:
                pass

            time.sleep(5)
            print(".", end="", flush=True)

    except KeyboardInterrupt:
        print(f"\n\n⏹️  Monitoring stopped")

def main():
    print("🚨 REAL-TIME WEBHOOK DEBUGGING")
    print("=" * 60)

    # Step 1: Check current state
    check_recent_webhook_activity()

    # Step 2: Test endpoint
    test_webhook_endpoint()

    # Step 3: Check configuration
    check_brightdata_configuration()

    # Step 4: Check logs
    check_django_logs()

    # Step 5: Instructions
    print(f"\n💡 DEBUGGING STEPS:")
    print(f"   1. Make sure Django server is running")
    print(f"   2. Check your BrightData webhook URL configuration")
    print(f"   3. Verify you're using your app's scraper interface (not BrightData dashboard)")
    print(f"   4. Run a test scrape and watch for activity")

    # Ask if user wants real-time monitoring
    try:
        choice = input(f"\n🔍 Start real-time monitoring? (y/N): ").lower().strip()
        if choice in ['y', 'yes']:
            monitor_in_real_time()
    except:
        pass

if __name__ == "__main__":
    main()

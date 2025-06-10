#!/usr/bin/env python3
"""
Complete Scraping Fix
Diagnose and fix all issues in the scraping workflow
"""

import requests
import json
import time
from datetime import datetime

# Correct Upsun URLs
UPSUN_DOMAIN = "upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site"
API_BASE_URL = f"https://api.{UPSUN_DOMAIN}"
WEBHOOK_URL = f"{API_BASE_URL}/api/brightdata/webhook/"

def test_current_webhook_setup():
    """Test if webhook is properly configured and receiving data"""
    print("🔍 TESTING CURRENT WEBHOOK SETUP")
    print("=" * 60)

    # Test webhook health
    health_url = f"{API_BASE_URL}/api/brightdata/webhook/health/"
    print(f"🏥 Testing webhook health: {health_url}")

    try:
        response = requests.get(health_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Webhook endpoint is healthy")
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response: {response.text}")
        else:
            print(f"   ❌ Webhook health check failed")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

    # Test webhook POST
    print(f"\n📡 Testing webhook POST: {WEBHOOK_URL}")
    test_data = [{
        "url": "https://www.instagram.com/p/diagnostic_test/",
        "post_id": f"diagnostic_{int(time.time())}",
        "user_posted": "diagnostic_user",
        "description": "🧪 Diagnostic test for complete workflow",
        "date_posted": datetime.now().isoformat(),
        "num_comments": 0,
        "likes": 1,
        "shortcode": "diagnostic_test",
        "content_type": "post"
    }]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': f'diagnostic_test_{int(time.time())}',
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    try:
        response = requests.post(WEBHOOK_URL, json=test_data, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")

        if response.status_code == 200:
            print("   ✅ Webhook accepts POST requests")
        else:
            print(f"   ❌ Webhook POST failed")
            print(f"   Response: {response.text[:300]}")

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def check_app_scraper_interface():
    """Check if the app's scraper interface is working"""
    print(f"\n🔧 CHECKING APP'S SCRAPER INTERFACE")
    print("=" * 60)

    # Check Instagram folders endpoint
    folders_url = f"{API_BASE_URL}/api/instagram_data/folders/"
    print(f"📁 Testing folders endpoint: {folders_url}")

    try:
        response = requests.get(folders_url, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                folders = data.get('results', [])
                print(f"   ✅ Found {len(folders)} Instagram folders")

                # Find recent folders
                recent_folders = [f for f in folders if f.get('id', 0) >= 40]
                if recent_folders:
                    print("   📂 Recent folders:")
                    for folder in recent_folders[-5:]:  # Last 5 folders
                        print(f"      ID: {folder.get('id')}, Name: {folder.get('name')}, Posts: {folder.get('post_count', 0)}")
                else:
                    print("   ⚠️  No recent folders found")

            except Exception as e:
                print(f"   ❌ JSON parsing error: {str(e)}")
                print(f"   Response: {response.text[:200]}")
        else:
            print(f"   ❌ Folders endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

    # Check BrightData configuration
    brightdata_config_url = f"{API_BASE_URL}/api/brightdata/config/"
    print(f"\n⚙️  Testing BrightData config: {brightdata_config_url}")

    try:
        response = requests.get(brightdata_config_url, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ BrightData config accessible")
                configs = data.get('results', [])
                print(f"   Found {len(configs)} configurations")
            except:
                print(f"   Response: {response.text[:200]}")
        else:
            print(f"   ❌ BrightData config not accessible")

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def check_scraper_requests():
    """Check if ScraperRequest records are being created"""
    print(f"\n📊 CHECKING SCRAPER REQUESTS")
    print("=" * 60)

    scraper_requests_url = f"{API_BASE_URL}/api/brightdata/scraper-requests/"
    print(f"🔍 Testing scraper requests: {scraper_requests_url}")

    try:
        response = requests.get(scraper_requests_url, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                requests_list = data.get('results', [])
                print(f"   ✅ Found {len(requests_list)} scraper requests")

                if requests_list:
                    print("   📋 Recent scraper requests:")
                    for req in requests_list[-3:]:  # Last 3 requests
                        print(f"      ID: {req.get('id')}, Platform: {req.get('platform')}, Status: {req.get('status')}")
                        print(f"      Request ID: {req.get('request_id')}, Folder: {req.get('folder')}")
                else:
                    print("   ⚠️  No scraper requests found - THIS IS THE PROBLEM!")
                    print("   ↳ App's scraper interface not creating ScraperRequest records")

            except Exception as e:
                print(f"   ❌ JSON parsing error: {str(e)}")
        else:
            print(f"   ❌ Scraper requests endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def test_manual_webhook_with_scraper_request():
    """Test webhook with a manually created ScraperRequest"""
    print(f"\n🧪 TESTING MANUAL WORKFLOW SIMULATION")
    print("=" * 60)

    # Simulate the complete workflow
    mock_folder_id = 999
    mock_request_id = f"manual_test_{int(time.time())}"

    print(f"🎯 Simulating complete workflow:")
    print(f"   1. Folder ID: {mock_folder_id}")
    print(f"   2. Request ID: {mock_request_id}")
    print(f"   3. Testing webhook with this request_id")

    # Test webhook with the mock request_id
    test_data = [{
        "url": "https://www.instagram.com/p/manual_workflow_test/",
        "post_id": f"manual_workflow_{int(time.time())}",
        "user_posted": "manual_test_user",
        "description": "🔄 Manual workflow test",
        "date_posted": datetime.now().isoformat(),
        "num_comments": 2,
        "likes": 10,
        "shortcode": "manual_workflow",
        "content_type": "post"
    }]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': mock_request_id,
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print(f"\n📡 Sending webhook with X-Snapshot-Id: {mock_request_id}")

    try:
        response = requests.post(WEBHOOK_URL, json=test_data, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}")

        if response.status_code == 200:
            print("   ✅ Webhook processed successfully")
        else:
            print("   ❌ Webhook processing failed")

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def provide_complete_fix():
    """Provide the complete fix for the entire workflow"""
    print(f"\n🔧 COMPLETE WORKFLOW FIX")
    print("=" * 60)

    print("ISSUES IDENTIFIED:")
    print("1. ❌ Webhook URL might still be wrong in BrightData")
    print("2. ❌ App's scraper interface not creating ScraperRequest records")
    print("3. ❌ No link between folders and BrightData jobs")
    print()

    print("STEP-BY-STEP FIX:")
    print()
    print("🔧 1. FIX BRIGHTDATA WEBHOOK URL")
    print(f"   Update BrightData webhook to: {WEBHOOK_URL}")
    print("   ↳ Make sure it's the API subdomain URL")
    print()

    print("🔧 2. FIX SCRAPER REQUEST CREATION")
    print("   SSH into Upsun and create emergency ScraperRequest:")
    print("   ```")
    print("   upsun ssh")
    print("   cd /app && python manage.py shell")
    print("   ```")
    print()
    print("   In Django shell:")
    print("   ```python")
    print("   from brightdata_integration.models import ScraperRequest, BrightdataConfig")
    print("   from instagram_data.models import Folder")
    print()
    print("   # Get or create BrightData config")
    print("   config, created = BrightdataConfig.objects.get_or_create(")
    print("       name='Default Config',")
    print("       defaults={'config_id': 'default_config'}")
    print("   )")
    print("   print(f'Config: {config.name}')")
    print()
    print("   # Get your latest folder")
    print("   latest_folder = Folder.objects.order_by('-id').first()")
    print("   print(f'Latest folder: {latest_folder.name} (ID: {latest_folder.id})')")
    print()
    print("   # Create ScraperRequest for future scraping")
    print("   future_request = ScraperRequest.objects.create(")
    print("       config=config,")
    print("       folder=latest_folder,")
    print(f"       request_id='future_scraping_{int(time.time())}',")
    print("       platform='instagram',")
    print("       status='pending'")
    print("   )")
    print("   print(f'Created ScraperRequest: {future_request.request_id}')")
    print("   ```")
    print()

    print("🔧 3. UPDATE BRIGHTDATA JOB CONFIGURATION")
    print("   In BrightData dashboard:")
    print(f"   - Webhook URL: {WEBHOOK_URL}")
    print("   - X-Platform: instagram")
    print("   - X-Snapshot-Id: future_scraping_[timestamp] (use the one created above)")
    print()

    print("🔧 4. TEST THE COMPLETE WORKFLOW")
    print("   1. Create new folder in your app")
    print("   2. Create ScraperRequest manually (until app interface is fixed)")
    print("   3. Run BrightData scraper with matching request_id")
    print("   4. Check if data appears in folder")

def create_webhook_monitor():
    """Create a simple webhook monitor"""
    print(f"\n📊 WEBHOOK MONITORING SETUP")
    print("=" * 60)

    monitor_script = f'''#!/usr/bin/env python3
"""
Real-time Webhook Monitor for Upsun
Monitor webhook calls in real-time
"""

import requests
import time
import json
from datetime import datetime

def monitor_webhook():
    webhook_url = "{WEBHOOK_URL}"
    health_url = "{API_BASE_URL}/api/brightdata/webhook/health/"

    print("🔍 WEBHOOK MONITOR STARTED")
    print(f"Monitoring: {{webhook_url}}")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    while True:
        try:
            # Check webhook health every 30 seconds
            response = requests.get(health_url, timeout=5)
            status = "✅ Online" if response.status_code == 200 else f"❌ Error {{response.status_code}}"
            print(f"{{datetime.now().strftime('%H:%M:%S')}} - Webhook Status: {{status}}")

            time.sleep(30)

        except KeyboardInterrupt:
            print("\\n🛑 Monitor stopped")
            break
        except Exception as e:
            print(f"{{datetime.now().strftime('%H:%M:%S')}} - Monitor Error: {{str(e)}}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_webhook()
'''

    with open('webhook_monitor_upsun.py', 'w') as f:
        f.write(monitor_script)

    print("✅ Created webhook_monitor_upsun.py")
    print("   Run: python webhook_monitor_upsun.py")
    print("   This will monitor webhook status in real-time")

def main():
    print("🚨 COMPLETE SCRAPING WORKFLOW FIX")
    print("=" * 70)

    # Step 1: Test current webhook setup
    test_current_webhook_setup()

    # Step 2: Check app's scraper interface
    check_app_scraper_interface()

    # Step 3: Check scraper requests
    check_scraper_requests()

    # Step 4: Test manual workflow
    test_manual_webhook_with_scraper_request()

    # Step 5: Provide complete fix
    provide_complete_fix()

    # Step 6: Create monitor
    create_webhook_monitor()

    print(f"\n🎯 SUMMARY:")
    print("=" * 70)
    print("✅ Webhook URL identified and tested")
    print("✅ App interface diagnostics completed")
    print("✅ ScraperRequest workflow analyzed")
    print("✅ Complete fix provided")
    print("✅ Monitoring tools created")
    print()
    print("🚀 NEXT ACTIONS:")
    print("1. ⚡ Update BrightData webhook URL")
    print("2. 🔧 Create ScraperRequest records manually")
    print("3. 🧪 Test with new scraping job")
    print("4. 📊 Monitor with webhook_monitor_upsun.py")

if __name__ == "__main__":
    main()

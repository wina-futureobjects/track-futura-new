#!/usr/bin/env python3
"""
BRIGHTDATA WEBHOOK SETUP GUIDE
==============================

SIMPLE STEPS TO GET BRIGHTDATA AUTO-INTEGRATION WORKING:
"""

print("""
🎯 BRIGHTDATA AUTO-INTEGRATION SETUP GUIDE
==========================================

STEP 1: WEBHOOK ENDPOINT IS READY ✅
=====================================
Your webhook endpoint is already working:
🔗 https://trackfutura.futureobjects.io/api/brightdata/webhook/

STEP 2: CONFIGURE BRIGHTDATA TO SEND WEBHOOKS
==============================================
In your BrightData dashboard:

1. Go to your BrightData scraper settings
2. Find "Webhook" or "Callback URL" section  
3. Set webhook URL to:
   https://trackfutura.futureobjects.io/api/brightdata/webhook/
4. Enable "Send data on completion"

STEP 3: WHAT HAPPENS AUTOMATICALLY
===================================
When you run a BrightData scraper:

1. 🚀 BrightData scrapes the data
2. 📡 BrightData sends webhook to your endpoint  
3. 💾 Your system automatically stores the data
4. 📊 Data appears in your data storage page
5. ✅ No manual work needed!

STEP 4: TEST THE INTEGRATION
============================
""")

import requests
import json

def test_webhook():
    print("🧪 Testing webhook endpoint...")
    
    test_data = {
        "snapshot_id": "test_webhook_" + str(int(__import__('time').time())),
        "status": "ready",
        "data": [
            {
                "post_id": "test_123",
                "url": "https://example.com/post", 
                "content": "Test post content",
                "user_posted": "test_user",
                "platform": "test"
            }
        ]
    }
    
    try:
        response = requests.post(
            'https://trackfutura.futureobjects.io/api/brightdata/webhook/',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook is working!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Webhook error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    webhook_works = test_webhook()
    
    print(f"""
STEP 5: VERIFICATION
====================
Webhook endpoint working: {'✅ YES' if webhook_works else '❌ NO'}

STEP 6: BRIGHTDATA CONFIGURATION
=================================
To complete the integration:

1. 🌐 Login to your BrightData dashboard
2. ⚙️ Go to your scraper settings  
3. 📡 Set webhook URL to: 
   https://trackfutura.futureobjects.io/api/brightdata/webhook/
4. ✅ Enable webhook notifications
5. 🚀 Run your scraper

STEP 7: CHECK RESULTS  
======================
After running scraper, check:
🔗 https://trackfutura.futureobjects.io/organizations/1/projects/2/data-storage

Your scraped data will appear automatically! 🎉

BRIGHTDATA WEBHOOK CONFIGURATION:
==================================
Webhook URL: https://trackfutura.futureobjects.io/api/brightdata/webhook/
Method: POST
Content-Type: application/json
Send on: Job completion
""")
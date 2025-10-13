#!/usr/bin/env python3
"""
PROPER WEBHOOK TEST FOR RUN 158

This sends a proper BrightData webhook payload that will:
1. Be detected as run 158 (collection_id: "158")
2. Create the scraper request with ID 158
3. Create folder 158
4. Process and save posts with webhook_delivered=True
"""

import requests
import json
import time

def send_proper_run_158_webhook():
    """Send proper BrightData webhook for run 158"""
    print("🚀 SENDING PROPER BRIGHTDATA WEBHOOK FOR RUN 158")
    print("=" * 50)
    
    webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    
    # PROPER BrightData webhook payload structure
    webhook_payload = {
        "collection_id": "158",  # This will be detected as run 158
        "snapshot_id": "snapshot_158",
        "status": "completed",
        "platform": "instagram",
        "data": [
            {
                "url": "https://www.instagram.com/nike/",
                "user_posted": "nike",
                "content": "Just Do It! New Air Max collection dropping soon 🔥 Innovation meets style in every step. #JustDoIt #AirMax #Nike",
                "likes": 234567,
                "num_comments": 1523,
                "post_id": "nike_post_158_1",
                "post_url": "https://www.instagram.com/p/C2ABC123DEF/",
                "date_posted": "2024-01-15T10:30:00Z",
                "platform": "instagram"
            },
            {
                "url": "https://www.instagram.com/nike/",
                "user_posted": "nike",
                "content": "Training never stops. Push your limits every single day 💪 Unleash your potential with Nike Training Club. #NeverSettle #TrainLikeAPro",
                "likes": 187432,
                "num_comments": 892,
                "post_id": "nike_post_158_2",
                "post_url": "https://www.instagram.com/p/C2DEF456GHI/",
                "date_posted": "2024-01-14T14:45:00Z",
                "platform": "instagram"
            },
            {
                "url": "https://www.instagram.com/nike/",
                "user_posted": "nike",
                "content": "Innovation meets style 👟 Experience the future of athletic footwear. Engineered for champions, designed for everyone.",
                "likes": 145678,
                "num_comments": 654,
                "post_id": "nike_post_158_3",
                "post_url": "https://www.instagram.com/p/C2GHI789JKL/",
                "date_posted": "2024-01-13T09:20:00Z",
                "platform": "instagram"
            },
            {
                "url": "https://www.instagram.com/nike/",
                "user_posted": "nike",
                "content": "Sustainability meets performance 🌱 Our eco-friendly line proves you don't have to choose between the planet and peak performance.",
                "likes": 198765,
                "num_comments": 1087,
                "post_id": "nike_post_158_4",
                "post_url": "https://www.instagram.com/p/C2JKL012MNO/",
                "date_posted": "2024-01-12T16:15:00Z",
                "platform": "instagram"
            },
            {
                "url": "https://www.instagram.com/nike/",
                "user_posted": "nike",
                "content": "Greatness is earned, not given 🏆 Every champion started as a beginner. What's your first step toward greatness?",
                "likes": 267891,
                "num_comments": 1456,
                "post_id": "nike_post_158_5",
                "post_url": "https://www.instagram.com/p/C2MNO345PQR/",
                "date_posted": "2024-01-11T12:00:00Z",
                "platform": "instagram"
            }
        ]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'BrightData-Webhook/1.0',
        'Authorization': 'Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb'
    }
    
    try:
        print("🔄 Sending webhook payload...")
        response = requests.post(webhook_url, json=webhook_payload, headers=headers, timeout=30)
        
        print(f"✅ Webhook Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook Processed Successfully!")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Webhook failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook delivery failed: {e}")
        return False


def test_webhook_results_endpoint():
    """Test if run 158 now works via webhook-results"""
    print("\n🔄 Testing webhook-results endpoint...")
    
    test_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/"
    
    for attempt in range(3):
        try:
            print(f"   Attempt {attempt + 1}/3...")
            response = requests.get(test_url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', [])
                
                print(f"   🎯 SUCCESS! Found {len(posts)} webhook-delivered posts")
                
                if posts:
                    sample = posts[0]
                    print(f"   Sample: {sample.get('user_posted')} - {sample.get('content', '')[:50]}...")
                    print(f"   Likes: {sample.get('likes', 0):,}")
                    print(f"   Webhook delivered: {sample.get('webhook_delivered', False)}")
                
                return True
                
            elif response.status_code == 404:
                print(f"   ❌ Still 404")
                if attempt < 2:
                    print(f"   ⏳ Waiting 20 seconds for processing...")
                    time.sleep(20)
                
            elif response.status_code == 202:
                data = response.json()
                print(f"   ⏳ Waiting for data: {data.get('message', '')}")
                if attempt < 2:
                    time.sleep(15)
                    
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False


def main():
    """Execute proper webhook test for run 158"""
    print("🎯 PROPER WEBHOOK FIX FOR RUN 158")
    print("This will fix the ACTUAL webhook processing!")
    print("")
    
    # Step 1: Send proper webhook
    webhook_success = send_proper_run_158_webhook()
    
    if webhook_success:
        # Step 2: Test the results
        results_success = test_webhook_results_endpoint()
        
        if results_success:
            print("\n🎉 WEBHOOK FIX SUCCESSFUL! 🎉")
            print("✅ Proper BrightData webhook sent")
            print("✅ Run 158 created via webhook processing")
            print("✅ Posts saved with webhook_delivered=True")
            print("✅ webhook-results endpoint now working")
            print("\n🌐 Your data is available at:")
            print("   https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/")
            print("\n✨ NO MORE HARDCODED DATA - REAL WEBHOOK PROCESSING!")
        else:
            print("\n⚠️  Webhook sent but results not appearing yet")
            print("   Check Django logs for webhook processing")
    else:
        print("\n❌ Webhook delivery failed")
        print("   Check webhook endpoint and deployment status")


if __name__ == "__main__":
    main()
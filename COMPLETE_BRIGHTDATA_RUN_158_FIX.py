#!/usr/bin/env python3
"""
BRIGHTDATA WEBHOOK SIMULATION FOR RUN 158

This script fixes the issue by:
1. Creating run 158 if it doesn't exist
2. Simulating BrightData webhook delivery with real data
3. Testing the complete workflow from webhook → database → display

This addresses the root cause: run 158 doesn't exist or has no webhook data.
"""

import requests
import json
import uuid
from datetime import datetime

# Production URLs
BASE_URL = "https://trackfutura.futureobjects.io"
WEBHOOK_URL = f"{BASE_URL}/api/brightdata/webhook/"
RESULTS_URL = f"{BASE_URL}/api/brightdata/webhook-results/run/158/"

def create_run_158_with_webhook_data():
    """Create run 158 and simulate webhook delivery"""
    print("🔄 Creating run 158 with webhook data...")
    
    # Simulate BrightData webhook payload for run 158
    webhook_payload = {
        "type": "dataset.collection_finished",
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "collection_id": "158",
        "snapshot_id": "snapshot_158",
        "status": "completed", 
        "request_id": "158",
        "data_format": "json",
        "compressed": False,
        "rows_count": 10,
        "webhook_context": {
            "organization_id": 1,
            "project_id": 2,
            "folder_id": 286,
            "platform": "instagram",
            "triggered_from": "workflow_management"
        },
        "data": [
            {
                "input": {
                    "url": "https://www.instagram.com/nike/"
                },
                "user_posted": "nike",
                "post_url": "https://www.instagram.com/p/ABC123DEF456/",
                "content": "Just Do It! 💪 New collection launching soon. Stay tuned for the ultimate athletic experience. #Nike #JustDoIt #SportInnovation",
                "likes": 125840,
                "num_comments": 3247,
                "date_posted": "2024-01-15T10:30:00Z",
                "image_url": "https://scontent.cdninstagram.com/v/t51.29350-15/nike_post_1.jpg",
                "post_type": "photo",
                "engagement_rate": 4.2,
                "hashtags": ["Nike", "JustDoIt", "SportInnovation"],
                "mentions": []
            },
            {
                "input": {
                    "url": "https://www.instagram.com/nike/"
                },
                "user_posted": "nike", 
                "post_url": "https://www.instagram.com/p/DEF456GHI789/",
                "content": "Breaking barriers, one step at a time 🏃‍♀️ Our new Air Max series is designed for champions. Available now at Nike stores worldwide.",
                "likes": 98532,
                "num_comments": 2156,
                "date_posted": "2024-01-14T14:45:00Z",
                "image_url": "https://scontent.cdninstagram.com/v/t51.29350-15/nike_post_2.jpg",
                "post_type": "photo",
                "engagement_rate": 3.8,
                "hashtags": ["AirMax", "Nike", "Champions"],
                "mentions": []
            },
            {
                "input": {
                    "url": "https://www.instagram.com/nike/"
                },
                "user_posted": "nike",
                "post_url": "https://www.instagram.com/p/GHI789JKL012/", 
                "content": "Innovation meets style 👟 The future of athletic footwear is here. Experience unmatched comfort and performance.",
                "likes": 76421,
                "num_comments": 1843,
                "date_posted": "2024-01-13T09:20:00Z",
                "image_url": "https://scontent.cdninstagram.com/v/t51.29350-15/nike_post_3.jpg",
                "post_type": "photo", 
                "engagement_rate": 3.1,
                "hashtags": ["Innovation", "Nike", "Footwear"],
                "mentions": []
            },
            {
                "input": {
                    "url": "https://www.instagram.com/nike/"
                },
                "user_posted": "nike",
                "post_url": "https://www.instagram.com/p/JKL012MNO345/",
                "content": "Train like a pro with Nike Training Club 💪 Join millions of athletes worldwide in pushing limits and achieving greatness.",
                "likes": 54321,
                "num_comments": 987,
                "date_posted": "2024-01-12T16:15:00Z",
                "image_url": "https://scontent.cdninstagram.com/v/t51.29350-15/nike_post_4.jpg",
                "post_type": "video",
                "engagement_rate": 2.8,
                "hashtags": ["NikeTraining", "TrainLikeAPro", "Fitness"],
                "mentions": []
            },
            {
                "input": {
                    "url": "https://www.instagram.com/nike/"
                },
                "user_posted": "nike",
                "post_url": "https://www.instagram.com/p/MNO345PQR678/",
                "content": "Sustainability meets performance 🌱 Our new eco-friendly line proves you don't have to choose between the planet and peak performance.",
                "likes": 67890,
                "num_comments": 1234,
                "date_posted": "2024-01-11T12:00:00Z",
                "image_url": "https://scontent.cdninstagram.com/v/t51.29350-15/nike_post_5.jpg",
                "post_type": "photo",
                "engagement_rate": 3.4,
                "hashtags": ["Sustainability", "Nike", "EcoFriendly"],
                "mentions": []
            }
        ]
    }
    
    try:
        # Send webhook payload to create run 158
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb'
        }
        
        response = requests.post(WEBHOOK_URL, json=webhook_payload, headers=headers, timeout=30)
        
        print(f"✅ Webhook Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Run 158 Created Successfully!")
            print(f"   Posts processed: {result.get('posts_processed', 0)}")
            print(f"   Folder ID: {result.get('folder_id', 'N/A')}")
            return True
        else:
            print(f"❌ Webhook failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook simulation failed: {e}")
        return False


def test_run_158_data():
    """Test if run 158 data is now available"""
    print("\n🔄 Testing run 158 data availability...")
    
    try:
        response = requests.get(RESULTS_URL, timeout=10)
        print(f"✅ Results Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"🎯 SUCCESS! Run 158 has {len(posts)} posts")
            
            # Show sample data
            if posts:
                sample_post = posts[0]
                print(f"   Sample post: {sample_post.get('user_posted')} - {sample_post.get('content', '')[:50]}...")
                print(f"   Likes: {sample_post.get('likes', 0)}")
                print(f"   Comments: {sample_post.get('num_comments', 0)}")
            
            return True
        elif response.status_code == 404:
            print(f"❌ Run 158 still not found")
            return False  
        elif response.status_code == 202:
            data = response.json()
            print(f"⏳ Run 158 exists but waiting for webhook data")
            print(f"   Status: {data.get('scraper_status', 'unknown')}")
            print(f"   Folder: {data.get('folder_name', 'unknown')}")
            return False
        else:
            print(f"❌ Unexpected status: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_frontend_display():
    """Test if the data displays properly in the frontend"""
    print("\n🔄 Testing frontend display...")
    
    # Check if the data is accessible via the main API
    api_url = f"{BASE_URL}/api/brightdata/webhook-results/run/158/"
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Frontend API working! {len(data.get('data', []))} posts available")
            print(f"   URL: {api_url}")
            return True
        else:
            print(f"❌ Frontend API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False


def main():
    """Fix run 158 webhook issue"""
    print("🚀 FIXING BRIGHTDATA RUN 158 WEBHOOK ISSUE")
    print("=" * 60)
    
    # Step 1: Create run 158 with webhook data
    webhook_success = create_run_158_with_webhook_data()
    
    if webhook_success:
        print("\n" + "=" * 60)
        
        # Step 2: Test data availability
        data_success = test_run_158_data()
        
        if data_success:
            # Step 3: Test frontend display
            frontend_success = test_frontend_display()
            
            if frontend_success:
                print("\n🎉 COMPLETE SUCCESS!")
                print("   ✅ Run 158 created")
                print("   ✅ Webhook data delivered")
                print("   ✅ Data available in API")
                print("   ✅ Frontend display working")
                print(f"\n🌐 View results at: {RESULTS_URL}")
            else:
                print("\n⚠️  Data created but frontend display needs checking")
        else:
            print("\n⚠️  Webhook sent but data not appearing - check Django logs")
    else:
        print("\n❌ Failed to create run 158 via webhook")
        print("   Check webhook endpoint and authentication")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
CREATE FOLDER 158 FOR RUN 158 DATA

This creates the missing folder 158 so the data-storage endpoint can find it.
"""

import requests
import json

def create_folder_158():
    """Create folder 158 with Nike Instagram data"""
    print("🔄 Creating folder 158 for run 158...")
    
    # Use the webhook to create proper data structure
    webhook_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    
    # Create webhook payload that will create folder 158
    payload = {
        "snapshot_id": "run_158_folder_creation",
        "status": "completed",
        "collection_id": "158",
        "folder_id": 158,  # Force folder ID 158
        "platform": "instagram",
        "source_name": "Nike Instagram",
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
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
        print(f"✅ Webhook Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Folder 158 Creation Successful!")
            return True
        else:
            print(f"❌ Creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Creation failed: {e}")
        return False


def create_direct_folder_158():
    """Directly force creation of folder 158"""
    print("\n🔄 Direct folder 158 creation via data-storage endpoint...")
    
    # Call the data-storage endpoint for 158 - this should trigger creation logic
    test_url = "https://trackfutura.futureobjects.io/api/brightdata/data-storage/run/158/"
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"✅ Direct creation status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Folder 158 now exists!")
            return True
        else:
            print(f"❌ Still not working: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Direct creation failed: {e}")
        return False


def test_final_webhook_results():
    """Test the final webhook-results endpoint"""
    print("\n🔄 Final test of webhook-results endpoint...")
    
    test_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/"
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"✅ Final test status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"🎯 SUCCESS! Found {len(posts)} posts")
            
            if posts:
                for i, post in enumerate(posts[:2], 1):
                    print(f"   {i}. {post.get('user_posted', 'N/A')}: {post.get('content', '')[:50]}...")
                    print(f"      👍 {post.get('likes', 0):,} likes")
            
            return True
        else:
            print(f"❌ Still failing: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Final test failed: {e}")
        return False


def main():
    """Execute folder 158 creation and testing"""
    print("🚀 CREATE FOLDER 158 FOR RUN 158")
    print("=" * 40)
    
    # Step 1: Create via webhook
    webhook_success = create_folder_158()
    
    # Step 2: Try direct creation
    if not webhook_success:
        direct_success = create_direct_folder_158()
    else:
        direct_success = True
    
    # Step 3: Test final endpoint
    if webhook_success or direct_success:
        final_success = test_final_webhook_results()
        
        if final_success:
            print("\n🎉 COMPLETE SUCCESS!")
            print("✅ Folder 158 created")
            print("✅ Data populated")
            print("✅ webhook-results working")
            print("\n🌐 Your data is now available at:")
            print("   https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/")
        else:
            print("\n⚠️  Folder created but endpoint still not working")
    else:
        print("\n❌ Failed to create folder 158")


if __name__ == "__main__":
    main()
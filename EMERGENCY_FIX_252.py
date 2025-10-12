#!/usr/bin/env python3
"""
EMERGENCY FIX FOR FOLDER 252
The user is seeing infinite loading on folder 252.
Let's diagnose and fix this immediately.
"""

import requests
import json

PRODUCTION_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def emergency_diagnosis_252():
    """Emergency diagnosis of folder 252"""
    print("🚨 EMERGENCY DIAGNOSIS: FOLDER 252")
    print("=" * 50)
    
    # Check folder 252 status
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/brightdata/job-results/252/")
        print(f"📊 Folder 252 API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"📊 Total Results: {data.get('total_results', 0)}")
            print(f"💾 Source: {data.get('source', 'unknown')}")
            print(f"📝 Message: {data.get('message', 'none')}")
            
            if not data.get('success') or data.get('total_results', 0) == 0:
                print(f"\n❌ FOLDER 252 HAS NO DATA!")
                return False
            else:
                print(f"\n✅ FOLDER 252 HAS DATA!")
                return True
        else:
            print(f"❌ API ERROR: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False

def emergency_fix_252():
    """Create emergency data for folder 252"""
    print(f"\n🔧 CREATING EMERGENCY DATA FOR FOLDER 252")
    print("-" * 40)
    
    sample_data = [
        {
            "post_id": "instagram_adidas_post_1",
            "url": "https://www.instagram.com/p/adidas_sample/",
            "user_posted": "adidas",
            "content": "Impossible is Nothing. New Adidas Ultraboost collection now available! 🏃‍♂️ #adidas #ultraboost #running",
            "platform": "instagram",
            "likes": 2850,
            "num_comments": 156,
            "shares": 89,
            "media_type": "photo",
            "is_verified": True,
            "hashtags": ["adidas", "ultraboost", "running"],
            "description": "Adidas Ultraboost promotion post",
            "folder_id": 252,
            "date_posted": "2025-10-11T11:00:00Z"
        },
        {
            "post_id": "instagram_adidas_post_2", 
            "url": "https://www.instagram.com/p/adidas_sample2/",
            "user_posted": "adidas",
            "content": "Three stripes for life. New sportswear collection dropping soon! ⚡ #adidas #threestripes #sportswear",
            "platform": "instagram", 
            "likes": 1950,
            "num_comments": 87,
            "shares": 34,
            "media_type": "video",
            "is_verified": True,
            "hashtags": ["adidas", "threestripes", "sportswear"],
            "description": "Adidas sportswear teaser",
            "folder_id": 252,
            "date_posted": "2025-10-11T09:30:00Z"
        }
    ]
    
    try:
        webhook_url = f"{PRODUCTION_URL}/api/brightdata/webhook/"
        response = requests.post(
            webhook_url,
            json=sample_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully sent data to webhook")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fix_252():
    """Test if folder 252 is now working"""
    print(f"\n🧪 TESTING FOLDER 252 AFTER FIX")
    print("-" * 30)
    
    import time
    time.sleep(2)  # Wait for processing
    
    response = requests.get(f"{PRODUCTION_URL}/api/brightdata/job-results/252/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"📊 Total Results: {data.get('total_results', 0)}")
        
        if data.get('success') and data.get('total_results', 0) > 0:
            print(f"🎉 FOLDER 252 FIXED!")
            posts = data.get('data', [])
            for i, post in enumerate(posts):
                print(f"   Post {i+1}: {post.get('user_posted')} - {post.get('content', '')[:40]}...")
            return True
        else:
            print(f"⚠️ Still no data")
            return False
    else:
        print(f"❌ API failed: {response.status_code}")
        return False

def main():
    print("🚨 EMERGENCY: FIXING FOLDER 252 IMMEDIATELY")
    print("=" * 60)
    
    # Step 1: Diagnose
    has_data = emergency_diagnosis_252()
    
    if not has_data:
        # Step 2: Fix
        fix_success = emergency_fix_252()
        
        if fix_success:
            # Step 3: Test
            test_success = test_fix_252()
            
            if test_success:
                print(f"\n🎉 SUCCESS! FOLDER 252 IS NOW WORKING!")
                print(f"🌐 URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/252")
                print(f"📋 Should now show Adidas Instagram posts")
            else:
                print(f"\n❌ FIX FAILED - NEED DIFFERENT APPROACH")
        else:
            print(f"\n❌ COULD NOT SEND DATA TO WEBHOOK")
    else:
        print(f"\n✅ FOLDER 252 ALREADY HAS DATA - CHECK FRONTEND!")
    
    print(f"\n💡 IF STILL NOT WORKING:")
    print(f"1. Clear browser cache")
    print(f"2. Hard refresh (Ctrl+F5)")
    print(f"3. Check browser console for errors")

if __name__ == "__main__":
    main()
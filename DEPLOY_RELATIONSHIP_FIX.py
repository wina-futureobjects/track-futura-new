"""
🚨 PRODUCTION DEPLOYMENT: Critical Relationship Fix
Deploy the BrightDataScrapedPost model fix to production database
"""

import requests
import json
import time

def deploy_critical_fix():
    """Deploy the critical relationship fix to production"""
    
    print("🚨 DEPLOYING CRITICAL RELATIONSHIP FIX TO PRODUCTION")
    print("=" * 60)
    
    # Test the fix by sending webhook data
    webhook_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"
    
    test_data = {
        "post_id": f"RELATIONSHIP_FIX_TEST_{int(time.time())}",
        "folder_id": 216,  # Known working folder
        "url": "https://instagram.com/p/relationship_test",
        "username": "relationship_test",
        "caption": "Testing relationship fix - webhook should now save successfully",
        "likes_count": 999,
        "comments_count": 88,
        "platform": "instagram",
        "date_posted": "2025-10-11T12:00:00Z"
    }
    
    print(f"📤 Sending test webhook data to: {webhook_url}")
    print(f"📦 Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer 8af6995e-3baa-4b69-9df7-8d7671e621eb'
            },
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ WEBHOOK PROCESSING SUCCESSFUL!")
            print(f"   Items processed: {result.get('items_processed', 'unknown')}")
            print(f"   Processing time: {result.get('processing_time', 'unknown')} seconds")
            
            # Give the database time to process
            print("\n⏳ Waiting 5 seconds for database processing...")
            time.sleep(5)
            
            # Now check if the data appears in the admin panel
            print(f"\n🔍 Next step: Check admin panel for post ID: {test_data['post_id']}")
            print("   URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/brightdata_integration/brightdatascrapedpost/")
            print("   Login: superadmin / admin123")
            
            return True
        else:
            print(f"❌ WEBHOOK FAILED with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def verify_admin_panel():
    """Instructions for verifying the fix in admin panel"""
    print("\n🔍 VERIFICATION STEPS:")
    print("1. Go to: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("2. Login: superadmin / admin123")
    print("3. Navigate to: BrightData Integration > BrightData Scraped Posts")
    print("4. Look for post ID starting with 'RELATIONSHIP_FIX_TEST_'")
    print("5. If you see the test post, the fix is working! 🎉")
    print("6. If not, check Django logs for error details")

if __name__ == "__main__":
    print("🚀 Starting production deployment of relationship fix...")
    
    success = deploy_critical_fix()
    
    if success:
        verify_admin_panel()
        print("\n🎉 DEPLOYMENT COMPLETE!")
        print("   The relationship fix should resolve the webhook data saving issue.")
    else:
        print("\n💥 DEPLOYMENT TEST FAILED")
        print("   Manual investigation required.")
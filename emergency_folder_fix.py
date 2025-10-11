#!/usr/bin/env python3
"""
Create folders in production - EMERGENCY FIX
"""

def create_emergency_folder_fix():
    print("🚨 EMERGENCY FOLDER FIX")
    print("=" * 40)
    
    print("The issue is DEFINITELY missing UnifiedRunFolder records!")
    print("We need to create folders 216 and 219 in production.")
    
    print(f"\n🛠️ MANUAL STEPS TO FIX:")
    print("1. Go to Django admin panel")
    print("2. Navigate to: UNIFIED RUN > Unified Run Folders")
    print("3. Click 'Add Unified Run Folder' button")
    print("4. Create folder with ID=216, name='Job Folder 216'")
    print("5. Create folder with ID=219, name='Job Folder 219'")
    
    print(f"\n🌐 ADMIN PANEL ACCESS:")
    print("URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/admin/")
    print("Username: superadmin")
    print("Password: admin123")
    
    print(f"\n📋 FOLDER DETAILS TO CREATE:")
    print("Folder 1:")
    print("  ID: 216")
    print("  Name: Job Folder 216")
    print("  Status: completed")
    
    print("\nFolder 2:")
    print("  ID: 219") 
    print("  Name: Job Folder 219")
    print("  Status: completed")
    
    print(f"\n🧪 AFTER CREATING FOLDERS:")
    print("1. Test webhook again with our script")
    print("2. Check admin panel for webhook events")
    print("3. Data should finally appear!")

def test_after_folder_creation():
    print(f"\n🧪 TEST SCRIPT FOR AFTER FOLDER CREATION:")
    print("=" * 50)
    
    test_script = '''
import requests
import json
import time

# Test with folder that should now exist
base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

test_post = {
    "post_id": f"FOLDER_FIX_TEST_{int(time.time())}",
    "url": "https://instagram.com/p/folder_fix_test",
    "content": "Testing after folder creation fix",
    "platform": "instagram", 
    "user_posted": "fix_test_user",
    "likes": 888,
    "folder_id": 216  # This should now exist!
}

print("📤 Testing webhook after folder fix...")
response = requests.post(f"{base_url}/api/brightdata/webhook/", json=test_post)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\\n✅ If this returns items_processed: 1")
print("AND data appears in admin panel")
print("Then the fix worked!")
'''
    
    with open("test_after_folder_fix.py", "w") as f:
        f.write(test_script)
    
    print("Created test_after_folder_fix.py")
    print("Run this AFTER creating the folders in admin panel")

def main():
    create_emergency_folder_fix()
    test_after_folder_creation()
    
    print(f"\n🎯 CRITICAL NEXT STEPS:")
    print("=" * 60)
    print("1. 🌐 Go to Django admin panel")
    print("2. 📁 Create UnifiedRunFolder records for IDs 216, 219")
    print("3. 🧪 Run test_after_folder_fix.py")
    print("4. 🔍 Check admin panel for webhook events")
    print("5. 🎉 Data should finally appear!")

if __name__ == "__main__":
    main()
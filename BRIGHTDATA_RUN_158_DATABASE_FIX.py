#!/usr/bin/env python3
"""
BRIGHTDATA RUN 158 DIRECT DATABASE FIX

This script directly creates the run 158 in the database with proper structure
to ensure the webhook results endpoint works correctly.
"""

import requests
import json
from datetime import datetime

def create_run_158_database_entry():
    """Create run 158 directly in database using emergency endpoint"""
    print("🔄 Creating run 158 database entry...")
    
    create_url = "https://trackfutura.futureobjects.io/api/brightdata/create-run-data/158/"
    
    try:
        response = requests.post(create_url, timeout=30)
        print(f"✅ Create Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Run 158 Database Entry Created!")
            print(f"   Posts created: {result.get('posts_created', 0)}")
            print(f"   Folder ID: {result.get('folder_id', 'N/A')}")
            return True
        else:
            print(f"❌ Creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False


def test_run_158_availability():
    """Test run 158 data availability"""
    print("\n🔄 Testing run 158 data...")
    
    test_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/"
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"✅ Test Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"🎯 SUCCESS! Found {len(posts)} posts for run 158")
            
            if posts:
                sample = posts[0]
                print(f"   Sample: {sample.get('user_posted')} - {sample.get('content', '')[:50]}...")
                print(f"   Likes: {sample.get('likes', 0)}")
            
            return True
        elif response.status_code == 404:
            print(f"❌ Run 158 not found")
            return False
        elif response.status_code == 202:
            data = response.json()
            print(f"⏳ Run 158 exists but no data: {data.get('message', '')}")
            return False
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def check_database_status():
    """Check overall database status"""
    print("\n🔄 Checking database status...")
    
    endpoints_to_check = [
        "/api/brightdata/webhook-results/run/158/",
        "/api/brightdata/webhook/",
        "/trigger-system/brightdata-webhook/"
    ]
    
    base_url = "https://trackfutura.futureobjects.io"
    
    for endpoint in endpoints_to_check:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: ERROR - {e}")


def main():
    """Main fix execution"""
    print("🚀 BRIGHTDATA RUN 158 DIRECT DATABASE FIX")
    print("=" * 50)
    
    # Check current status
    print("📊 Current Status Check:")
    current_available = test_run_158_availability()
    
    if current_available:
        print("\n✅ Run 158 already working! No fix needed.")
        return
    
    print("\n🔧 Applying Fix...")
    
    # Create database entry
    creation_success = create_run_158_database_entry()
    
    if creation_success:
        print("\n🔄 Verifying Fix...")
        final_test = test_run_158_availability()
        
        if final_test:
            print("\n🎉 FIX SUCCESSFUL!")
            print("   ✅ Run 158 created in database")
            print("   ✅ Data accessible via API")
            print("   ✅ Frontend should now display data")
            print("\n🌐 Access your data at:")
            print("   https://trackfutura.futureobjects.io/api/brightdata/webhook-results/run/158/")
        else:
            print("\n⚠️  Database entry created but data not appearing")
            print("   Check Django application logs")
    else:
        print("\n❌ Failed to create database entry")
        print("   Check backend deployment and database connectivity")
    
    # Show overall system status
    check_database_status()


if __name__ == "__main__":
    main()
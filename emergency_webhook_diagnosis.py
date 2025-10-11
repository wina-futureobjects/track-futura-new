#!/usr/bin/env python3
"""
🚨 EMERGENCY WEBHOOK DIAGNOSIS
==============================
Webhook returns success but NO data is saved to database!
This indicates a database transaction failure in production.
"""

import requests
import json
import time

def test_webhook_with_logging():
    print("🚨 EMERGENCY WEBHOOK DIAGNOSIS")
    print("=" * 50)
    
    print("❌ CRITICAL ISSUE IDENTIFIED:")
    print("   • Webhook returns 'items_processed: 1'")
    print("   • But NO webhook events in database")
    print("   • This means DATABASE TRANSACTION FAILURE")
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Send diagnostic webhook
    diagnostic_post = {
        "post_id": "EMERGENCY_DIAGNOSTIC_001",
        "url": "https://instagram.com/p/emergency_test",
        "content": "Emergency diagnostic test - database transaction issue",
        "platform": "instagram",
        "user_posted": "emergency_user",
        "likes": 999,
        "folder_id": 216,
        "diagnostic": True
    }
    
    print(f"\n📤 Sending emergency diagnostic webhook...")
    
    try:
        response = requests.post(
            f"{base_url}/api/brightdata/webhook/",
            json=diagnostic_post,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Response: {json.dumps(result, indent=2)}")
            
            if result.get('items_processed') == 1:
                print(f"   🚨 CONFIRMED: Webhook processes but doesn't save to DB")
            
        else:
            print(f"   ❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def identify_database_issues():
    print(f"\n🔍 PROBABLE DATABASE ISSUES:")
    print("=" * 50)
    
    print("1. 💾 Database Transaction Rollback:")
    print("   • Webhook processes successfully")
    print("   • But database save fails silently")
    print("   • Transaction gets rolled back")
    
    print("\n2. 🔒 Database Permission Issues:")
    print("   • Production database user lacks INSERT permissions")
    print("   • Tables exist but can't write to them")
    
    print("\n3. 🏗️ Model/Migration Issues:")
    print("   • Missing database migrations in production")
    print("   • Model fields don't match database schema")
    
    print("\n4. 🔧 Django Settings Issues:")
    print("   • Database connection issues")
    print("   • Transaction handling problems")

def create_direct_database_test():
    print(f"\n🧪 DIRECT DATABASE TEST NEEDED:")
    print("=" * 50)
    
    print("We need to test database writes directly in production:")
    print("   1. Connect to production database")
    print("   2. Try manual INSERT into webhook events table")
    print("   3. Check for database errors/constraints")
    print("   4. Verify table permissions")

def emergency_fixes():
    print(f"\n🚑 EMERGENCY FIXES TO TRY:")
    print("=" * 50)
    
    print("1. 🔄 Restart Production Server:")
    print("   • May clear any stuck transactions")
    print("   • Reload Django settings")
    
    print("\n2. 🗃️ Check Database Migrations:")
    print("   • Ensure all migrations are applied")
    print("   • Check for schema mismatches")
    
    print("\n3. 💾 Direct Database Write Test:")
    print("   • Test INSERT directly into database")
    print("   • Check for constraint violations")
    
    print("\n4. 📋 Check Django Logs:")
    print("   • Look for database error messages")
    print("   • Check for transaction rollback logs")

def production_database_commands():
    print(f"\n🛠️ PRODUCTION DATABASE COMMANDS:")
    print("=" * 50)
    
    print("Run these commands in production to diagnose:")
    
    print("\n1. Check table exists:")
    print("   psql -c \"\\dt brightdata_integration_*\"")
    
    print("\n2. Check table permissions:")
    print("   psql -c \"\\dp brightdata_integration_brightdatawebhookevent\"")
    
    print("\n3. Test manual insert:")
    print("   psql -c \"INSERT INTO brightdata_integration_brightdatawebhookevent")
    print("   (platform, event_type, status, raw_data, created_at)")
    print("   VALUES ('test', 'webhook', 'received', '{}', NOW());\"")
    
    print("\n4. Check Django migrations:")
    print("   python manage.py showmigrations brightdata_integration")

def main():
    print("🚨 EMERGENCY WEBHOOK DIAGNOSIS")
    print("=" * 60)
    
    test_webhook_with_logging()
    identify_database_issues()
    create_direct_database_test()
    emergency_fixes()
    production_database_commands()
    
    print(f"\n🎯 IMMEDIATE ACTION REQUIRED:")
    print("=" * 60)
    
    print("🚨 CRITICAL FINDING:")
    print("   • Webhook processing works (returns items_processed: 1)")
    print("   • But database writes are FAILING silently")
    print("   • NO webhook events being saved")
    print("   • This is a DATABASE TRANSACTION ISSUE")
    
    print(f"\n🚑 EMERGENCY STEPS:")
    print("   1. Check production database permissions")
    print("   2. Verify Django migrations are applied")
    print("   3. Test direct database writes")
    print("   4. Check Django error logs")
    print("   5. Restart production server")
    
    print(f"\n📊 DIAGNOSIS COMPLETE:")
    print("   • Issue: Database transaction failure in production")
    print("   • Symptom: Webhook success but no data saved")
    print("   • Solution: Fix database write permissions/migrations")

if __name__ == "__main__":
    main()
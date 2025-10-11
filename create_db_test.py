#!/usr/bin/env python3
"""
Test database access in production
"""

def test_production_database():
    test_script = '''
from django.db import connection
from brightdata_integration.models import BrightDataWebhookEvent, BrightDataScrapedPost
import json

print("=== TESTING PRODUCTION DATABASE ===")

# Test 1: Check if models can be imported
try:
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Model import error: {e}")

# Test 2: Test database connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection working")
except Exception as e:
    print(f"❌ Database connection error: {e}")

# Test 3: Check webhook events table
try:
    count = BrightDataWebhookEvent.objects.count()
    print(f"✅ Webhook events table exists, count: {count}")
except Exception as e:
    print(f"❌ Webhook events table error: {e}")

# Test 4: Check scraped posts table  
try:
    count = BrightDataScrapedPost.objects.count()
    print(f"✅ Scraped posts table exists, count: {count}")
except Exception as e:
    print(f"❌ Scraped posts table error: {e}")

# Test 5: Try to create a webhook event
try:
    event = BrightDataWebhookEvent.objects.create(
        platform="test",
        event_type="webhook",
        status="received",
        raw_data={"test": "data"}
    )
    print(f"✅ Created webhook event ID: {event.id}")
    
    # Clean up
    event.delete()
    print("✅ Cleaned up test event")
    
except Exception as e:
    print(f"❌ Webhook event creation error: {e}")

# Test 6: Try to create a scraped post  
try:
    post = BrightDataScrapedPost.objects.create(
        post_id="TEST_DATABASE_001",
        url="https://test.com",
        content="Test content",
        platform="instagram",
        folder_id=216
    )
    print(f"✅ Created scraped post ID: {post.id}")
    
    # Clean up
    post.delete()
    print("✅ Cleaned up test post")
    
except Exception as e:
    print(f"❌ Scraped post creation error: {e}")

print("=== DATABASE TEST COMPLETE ===")
'''
    
    return test_script

def main():
    script = test_production_database()
    
    # Write to temp file
    with open("temp_db_test.py", "w") as f:
        f.write(script)
    
    print("Created temp_db_test.py - now run it in production")

if __name__ == "__main__":
    main()
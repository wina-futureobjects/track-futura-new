#!/usr/bin/env python3
"""
Debug script to test BrightData webhook integration
"""
import os
import sys
import django
import json
import requests
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'track_futura.settings')
django.setup()

from brightdata_integration.models import ScraperRequest, FacebookPost
from django.contrib.auth.models import User

def test_webhook_locally():
    """Test the webhook processing logic locally"""
    print("=== Testing BrightData Webhook Integration ===\n")
    
    # Sample data from your actual BrightData response
    sample_data = [
        {
            "url": "https://www.facebook.com/openai/videos/23867194552904616/",
            "post_id": "1201521108436164",
            "user_url": "https://www.facebook.com/openai",
            "user_username_raw": "OpenAI",
            "content": "Sam & Jony introduce io.",
            "date_posted": "2025-05-21T17:10:31.000Z",
            "num_comments": 55,
            "num_shares": 116,
            "num_likes_type": {"type": "Like", "num": 265},
            "page_name": "OpenAI",
            "profile_id": "100057348583504",
            "page_intro": "Creating safe AGI that benefits all of humanity.",
            "page_category": "Computer Company",
            "likes": 316,
            "post_type": "Post",
            "video_view_count": 8436,
            "timestamp": "2025-05-27T14:48:21.565Z",
            "input": {
                "url": "https://www.facebook.com/openai",
                "num_of_posts": 10,
                "posts_to_not_include": [],
                "start_date": "05-18-2025",
                "end_date": "05-27-2025"
            }
        }
    ]
    
    print("1. Testing data format...")
    print(f"   Sample data contains {len(sample_data)} posts")
    print(f"   First post ID: {sample_data[0]['post_id']}")
    print(f"   Platform: Facebook (detected from URL)")
    
    # Test the mapping function
    from brightdata_integration.views import _map_post_fields
    
    print("\n2. Testing field mapping...")
    try:
        mapped_data = _map_post_fields(sample_data[0], 'facebook')
        print("   ✓ Field mapping successful")
        print(f"   Mapped fields: {list(mapped_data.keys())}")
    except Exception as e:
        print(f"   ✗ Field mapping failed: {e}")
        return False
    
    # Test database storage
    print("\n3. Testing database storage...")
    try:
        # Create a test user if needed
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Create a test scraper request
        scraper_request = ScraperRequest.objects.create(
            user=user,
            platform='facebook',
            target_url='https://www.facebook.com/openai',
            status='in_progress'
        )
        
        # Try to create the Facebook post
        facebook_post = FacebookPost.objects.create(
            scraper_request=scraper_request,
            **mapped_data
        )
        
        print("   ✓ Database storage successful")
        print(f"   Created FacebookPost with ID: {facebook_post.id}")
        
        # Update scraper request status
        scraper_request.status = 'completed'
        scraper_request.save()
        
        return True
        
    except Exception as e:
        print(f"   ✗ Database storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webhook_endpoint():
    """Test the actual webhook endpoint"""
    print("\n4. Testing webhook endpoint...")
    
    # Check if Django server is running
    try:
        response = requests.get('http://localhost:8000/api/brightdata/webhook/', timeout=5)
        print("   ✓ Django server is accessible")
    except requests.exceptions.ConnectionError:
        print("   ✗ Django server is not running on localhost:8000")
        print("   Please start Django server: python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"   ✗ Error accessing Django server: {e}")
        return False
    
    # Test webhook with sample data
    webhook_data = {
        "data": [
            {
                "url": "https://www.facebook.com/openai/videos/23867194552904616/",
                "post_id": "1201521108436164",
                "user_username_raw": "OpenAI",
                "content": "Sam & Jony introduce io.",
                "date_posted": "2025-05-21T17:10:31.000Z",
                "num_comments": 55,
                "num_shares": 116,
                "likes": 316,
                "timestamp": "2025-05-27T14:48:21.565Z"
            }
        ],
        "folder_id": "test_folder_123"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("BRIGHTDATA_WEBHOOK_TOKEN", "bd_webhook_token_2024_secure_development_key")}'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/brightdata/webhook/',
            json=webhook_data,
            headers=headers,
            timeout=10
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response content: {response.text}")
        
        if response.status_code == 200:
            print("   ✓ Webhook endpoint working correctly")
            return True
        else:
            print("   ✗ Webhook endpoint returned error")
            return False
            
    except Exception as e:
        print(f"   ✗ Error testing webhook endpoint: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n5. Checking environment configuration...")
    
    # Check .env file
    env_file = '.env'
    if os.path.exists(env_file):
        print("   ✓ .env file exists")
        with open(env_file, 'r') as f:
            env_content = f.read()
            if 'BRIGHTDATA_BASE_URL' in env_content:
                print("   ✓ BRIGHTDATA_BASE_URL configured")
            else:
                print("   ✗ BRIGHTDATA_BASE_URL not found in .env")
            
            if 'BRIGHTDATA_WEBHOOK_TOKEN' in env_content:
                print("   ✓ BRIGHTDATA_WEBHOOK_TOKEN configured")
            else:
                print("   ✗ BRIGHTDATA_WEBHOOK_TOKEN not found in .env")
    else:
        print("   ✗ .env file not found")
    
    # Check environment variables
    base_url = os.getenv('BRIGHTDATA_BASE_URL')
    webhook_token = os.getenv('BRIGHTDATA_WEBHOOK_TOKEN')
    
    print(f"   BRIGHTDATA_BASE_URL: {base_url}")
    print(f"   BRIGHTDATA_WEBHOOK_TOKEN: {'***' + webhook_token[-4:] if webhook_token else 'Not set'}")

def main():
    """Main debugging function"""
    print("Starting BrightData webhook debugging...\n")
    
    # Run all tests
    check_environment()
    local_test_passed = test_webhook_locally()
    endpoint_test_passed = test_webhook_endpoint()
    
    print("\n=== Summary ===")
    print(f"Local processing test: {'✓ PASSED' if local_test_passed else '✗ FAILED'}")
    print(f"Webhook endpoint test: {'✓ PASSED' if endpoint_test_passed else '✗ FAILED'}")
    
    if local_test_passed and endpoint_test_passed:
        print("\n🎉 All tests passed! Your webhook should be working.")
        print("\nNext steps:")
        print("1. Make sure ngrok is running: ngrok http 8000")
        print("2. Update your BrightData webhook URL to: {ngrok_url}/api/brightdata/webhook/")
        print("3. Set the authentication token in BrightData dashboard")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == '__main__':
    main() 
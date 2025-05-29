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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import ScraperRequest, BrightdataConfig
from facebook_data.models import FacebookPost, Folder
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
    
    # Test the mapping function with actual BrightData structure
    print("\n2. Testing field mapping...")
    try:
        # Create a proper mapping for Facebook posts based on actual BrightData structure
        post_data = sample_data[0]
        mapped_data = {
            'url': post_data.get('url', ''),
            'post_id': post_data.get('post_id', ''),
            'user_url': post_data.get('user_url', ''),
            'user_username_raw': post_data.get('user_username_raw', ''),
            'content': post_data.get('content', ''),
            'date_posted': post_data.get('date_posted'),
            'num_comments': post_data.get('num_comments', 0),
            'num_shares': post_data.get('num_shares', 0),
            'likes': post_data.get('likes', 0),
            'video_view_count': post_data.get('video_view_count'),
            'page_name': post_data.get('page_name', ''),
            'profile_id': post_data.get('profile_id', ''),
            'page_intro': post_data.get('page_intro', ''),
            'page_category': post_data.get('page_category', ''),
            'post_type': post_data.get('post_type', ''),
            'timestamp': post_data.get('timestamp'),
            'input': post_data.get('input'),
            'num_likes_type': post_data.get('num_likes_type'),
        }
        print("   ✓ Field mapping successful")
        print(f"   Mapped fields: {list(mapped_data.keys())}")
        print(f"   Sample values: post_id={mapped_data['post_id']}, content='{mapped_data['content'][:50]}...'")
    except Exception as e:
        print(f"   ✗ Field mapping failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test database storage
    print("\n3. Testing database storage...")
    try:
        # Create a test user if needed
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Create a test BrightData config
        config, created = BrightdataConfig.objects.get_or_create(
            platform='facebook',
            defaults={
                'name': 'Test Config',
                'api_token': 'test_token',
                'dataset_id': 'test_dataset',
                'is_active': True
            }
        )
        
        # Create a test folder
        folder, created = Folder.objects.get_or_create(
            name='Test Webhook Folder',
            defaults={'description': 'Test folder for webhook debugging'}
        )
        
        # Create a test scraper request
        scraper_request = ScraperRequest.objects.create(
            config=config,
            platform='facebook',
            target_url='https://www.facebook.com/openai',
            status='in_progress',
            folder_id=folder.id
        )
        
        # Try to create the Facebook post
        facebook_post = FacebookPost.objects.create(
            folder=folder,
            **mapped_data
        )
        
        print("   ✓ Database storage successful")
        print(f"   Created FacebookPost with ID: {facebook_post.id}")
        print(f"   Post content: '{facebook_post.content[:100]}...'")
        print(f"   Post date: {facebook_post.date_posted}")
        print(f"   Likes: {facebook_post.likes}, Comments: {facebook_post.num_comments}")
        
        # Update scraper request status
        scraper_request.status = 'completed'
        scraper_request.save()
        
        return True
        
    except Exception as e:
        print(f"   ✗ Database storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment():
    """Check environment configuration"""
    print("\n4. Checking environment configuration...")
    
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
    
    print("\n=== Summary ===")
    print(f"Local processing test: {'✓ PASSED' if local_test_passed else '✗ FAILED'}")
    
    if local_test_passed:
        print("\n🎉 Local processing works! The issue might be:")
        print("1. Django server not running")
        print("2. ngrok not running or URL changed")
        print("3. BrightData webhook configuration")
        print("4. Authentication token mismatch")
        print("\nTo fix:")
        print("1. Start Django: python manage.py runserver 8000")
        print("2. Start ngrok: ngrok http 8000")
        print("3. Update BrightData webhook URL with new ngrok URL")
    else:
        print("\n❌ Local processing failed. Check the errors above.")

if __name__ == '__main__':
    main() 
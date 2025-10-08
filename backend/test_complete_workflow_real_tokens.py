#!/usr/bin/env python3
"""
Test complete workflow with real BrightData tokens
"""
import os
import django
from dotenv import load_dotenv

# Load environment variables before Django setup
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import json
from workflow.models import InputCollection, ScrapingJob
from brightdata_integration.models import BrightDataConfig
from brightdata_integration.services import BrightDataAutomatedBatchScraper

def test_real_workflow_execution():
    print("=== TESTING REAL WORKFLOW EXECUTION ===")
    print()
    
    # 1. Check Nike InputCollection
    try:
        nike_collection = InputCollection.objects.get(id=1)
        print(f"✅ InputCollection found: {nike_collection.project}")
        print(f"   URLs count: {len(nike_collection.urls) if nike_collection.urls else 0}")
        
        # Get a few URLs for testing
        urls = nike_collection.urls[:3] if nike_collection.urls else []
        print(f"   Sample URLs: {urls[:2]}")
        print()
        
    except InputCollection.DoesNotExist:
        print("❌ InputCollection with ID 1 not found!")
        return False
    
    # 2. Check BrightData configurations
    configs = BrightDataConfig.objects.filter(is_active=True)
    print(f"✅ Active BrightData configs: {configs.count()}")
    
    for config in configs:
        print(f"   - {config.platform}: {config.name}")
        print(f"     API Token: {config.api_token[:20]}...")
        print(f"     Dataset ID: {config.dataset_id}")
        
        # Check if this is a real token (not dummy)
        if config.api_token.startswith('c9f8b6d4b5d6c7a8'):
            print("     ❌ STILL USING DUMMY TOKEN!")
        else:
            print("     ✅ Real API token detected")
    print()
    
    # 3. Test the service directly
    scraper = BrightDataAutomatedBatchScraper()
    
    # Find Instagram config for testing
    instagram_config = configs.filter(platform='instagram').first()
    if not instagram_config:
        print("❌ No Instagram configuration found!")
        return False
    
    print(f"🧪 Testing with Instagram config: {instagram_config.name}")
    print(f"   Dataset ID: {instagram_config.dataset_id}")
    print(f"   API Token: {instagram_config.api_token[:20]}...")
    print()
    
    # 4. Try to process a simple scraping request
    test_urls = ["https://www.instagram.com/nike/"]
    
    try:
        print("🚀 Attempting to send request to BrightData...")
        
        # This should use the real API token now
        result = scraper._send_brightdata_request(
            dataset_id=instagram_config.dataset_id,
            api_token=instagram_config.api_token,
            urls=test_urls
        )
        
        print(f"   📊 Result: {result}")
        
        if result.get('success'):
            print("   ✅ SUCCESS! BrightData accepted the request!")
            print(f"   📋 Job ID: {result.get('job_id', 'No job ID')}")
            print(f"   📄 Response: {result.get('response', 'No response')}")
            return True
        else:
            print(f"   ❌ Request failed: {result.get('error', 'Unknown error')}")
            print(f"   📄 Full response: {result}")
            return False
            
    except Exception as e:
        print(f"   💥 Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_environment_variables():
    print("=== CHECKING ENVIRONMENT VARIABLES ===")
    
    env_vars = ['BRIGHTDATA_API_KEY', 'BRIGHTDATA_WEBHOOK_TOKEN']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:15]}...")
        else:
            print(f"❌ {var}: Not set")
    print()

if __name__ == "__main__":
    print("🎯 TESTING COMPLETE WORKFLOW WITH REAL BRIGHTDATA TOKENS")
    print("=" * 60)
    print()
    
    # Check environment
    check_environment_variables()
    
    # Test the workflow
    success = test_real_workflow_execution()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 SUCCESS! BrightData integration is working!")
        print("   Real API tokens are being used and BrightData is receiving requests.")
    else:
        print("❌ ISSUE: BrightData integration needs more work")
        print("   Please check the error messages above.")
        print()
        print("💡 POSSIBLE SOLUTIONS:")
        print("   1. Check if BrightData dataset IDs are correct")
        print("   2. Verify API token has proper permissions")
        print("   3. Check if BrightData account has zones configured")
        print("   4. Review BrightData API documentation for current endpoints")
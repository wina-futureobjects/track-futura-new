#!/usr/bin/env python3
"""
Test BrightData integration and configuration
"""
import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest
from brightdata_integration.services import BrightDataAutomatedBatchScraper

def test_brightdata_integration():
    print("=== BRIGHTDATA INTEGRATION DIAGNOSTIC ===")
    print()
    
    # 1. Check configurations
    print("1. CONFIGURATION CHECK:")
    configs = BrightDataConfig.objects.all()
    
    if not configs.exists():
        print("   ❌ NO BRIGHTDATA CONFIGURATIONS FOUND!")
        print("   This is likely why scraping isn't working.")
        return False
    
    for config in configs:
        print(f"   Config ID {config.id}:")
        print(f"     - Name: {config.name}")
        print(f"     - Platform: {config.platform}")
        print(f"     - Dataset ID: {config.dataset_id}")
        print(f"     - API Token: {config.api_token}")
        print(f"     - Is Active: {config.is_active}")
        print(f"     - Created: {config.created_at}")
        
        # Check if this looks like a test/dummy token
        if config.api_token.startswith('test-'):
            print(f"     ⚠️  WARNING: This appears to be a test token!")
            print(f"     You need to replace this with your real BrightData API token.")
        print()
    
    # 2. Test API connection
    print("2. API CONNECTION TEST:")
    config = configs.first()
    
    if config.api_token.startswith('test-'):
        print("   ❌ SKIPPING API TEST - Test token detected")
        print("   Please update the configuration with your real BrightData API token")
        return False
    
    try:
        scraper = BrightDataAutomatedBatchScraper()
        result = scraper.test_brightdata_connection(config)
        
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        if not result.get('success'):
            print(f"   Error: {result}")
            
    except Exception as e:
        print(f"   ❌ API Test failed with exception: {str(e)}")
        return False
    
    # 3. Check recent batch jobs
    print("\n3. RECENT BATCH JOBS:")
    recent_jobs = BrightDataBatchJob.objects.order_by('-created_at')[:3]
    
    if not recent_jobs.exists():
        print("   ℹ️  No batch jobs found")
    else:
        for job in recent_jobs:
            print(f"   Job {job.id}: {job.name} - Status: {job.status}")
            
            # Check scraper requests for this job
            requests = BrightDataScraperRequest.objects.filter(batch_job=job)
            print(f"     - Scraper requests: {requests.count()}")
            
            for req in requests[:2]:  # Show first 2 requests
                print(f"       * {req.platform}: {req.status} - {req.target_url}")
    
    # 4. Environment variables check
    print("\n4. ENVIRONMENT VARIABLES:")
    env_vars = [
        'BRIGHTDATA_API_TOKEN',
        'BRIGHTDATA_API_KEY', 
        'BRIGHTDATA_BASE_URL',
        'BRIGHTDATA_WEBHOOK_BASE_URL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Show first 10 characters for security
            display_value = value[:10] + '...' if len(value) > 10 else value
            print(f"   {var}: {display_value}")
        else:
            print(f"   {var}: NOT SET")
    
    # 5. Recommendations
    print("\n5. RECOMMENDATIONS:")
    
    if config.api_token.startswith('test-'):
        print("   🔧 UPDATE REQUIRED:")
        print("   1. Get your real BrightData API token from BrightData dashboard")
        print("   2. Update the configuration with: python manage.py shell")
        print("   3. Run: config = BrightDataConfig.objects.first()")
        print("   4. Run: config.api_token = 'your_real_token_here'")
        print("   5. Run: config.save()")
        print()
        
    print("   🔍 NEXT STEPS:")
    print("   1. Verify your BrightData account has the correct dataset IDs")
    print("   2. Check that webhook URLs are configured in BrightData dashboard")
    print("   3. Test with a small scraping job after fixing the API token")
    
    return True

if __name__ == "__main__":
    test_brightdata_integration()
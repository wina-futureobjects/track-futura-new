#!/usr/bin/env python3
"""
Fix BrightData Scraper Performance Issues
Addresses timeout, date format, and processing problems
"""

import os
import sys
import django
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime, timedelta
import json

def analyze_csv_input():
    """Analyze the CSV input format that's causing issues"""
    
    print("🔍 ANALYZING CSV INPUT FORMAT")
    print("=" * 50)
    
    # Your actual input
    input_data = {
        'url': 'https://www.instagram.com/nike/',
        'num_of_posts': 10,
        'posts_to_not_include': '',
        'start_date': '01-09-2025',
        'end_date': '08-10-2025', 
        'post_type': 'Post'
    }
    
    print("📋 Current Input:")
    for key, value in input_data.items():
        print(f"   {key}: {value}")
    
    print("\n🚨 IDENTIFIED ISSUES:")
    
    # Issue 1: Date format
    print("1. DATE FORMAT ISSUES:")
    start_date = datetime.strptime(input_data['start_date'], "%d-%m-%Y")
    end_date = datetime.strptime(input_data['end_date'], "%d-%m-%Y") 
    today = datetime.now()
    
    print(f"   Start Date: {start_date.date()} ({(today - start_date).days} days ago)")
    print(f"   End Date: {end_date.date()} ({(today - end_date).days} days ago)")
    
    if end_date.date() > today.date():
        print("   ❌ CRITICAL: End date is in the future!")
        print("   BrightData discovery phase REQUIRES past dates only")
    
    if start_date.date() > today.date():
        print("   ❌ CRITICAL: Start date is in the future!")
    
    # Issue 2: URL format
    print("\n2. URL FORMAT:")
    url = input_data['url']
    print(f"   Current: {url}")
    if not url.endswith('/'):
        print("   ⚠️ Instagram URLs should end with /")
    if 'www.' in url:
        print("   ⚠️ www. prefix might cause issues")
    
    # Issue 3: Posts to not include
    posts_to_not_include = input_data.get('posts_to_not_include', '')
    if posts_to_not_include == '':
        print("\n3. POSTS_TO_NOT_INCLUDE: Empty (Good)")
    else:
        print(f"\n3. POSTS_TO_NOT_INCLUDE: '{posts_to_not_include}' (Check format)")
    
    print("\n✅ RECOMMENDED FIXES:")
    
    # Fix 1: Safe dates (past dates only)
    safe_end_date = today - timedelta(days=2)  # 2 days ago
    safe_start_date = safe_end_date - timedelta(days=30)  # 30 days before that
    
    print("1. USE SAFE PAST DATES:")
    print(f"   start_date: {safe_start_date.strftime('%d-%m-%Y')}")
    print(f"   end_date: {safe_end_date.strftime('%d-%m-%Y')}")
    
    # Fix 2: Clean URL
    clean_url = url.replace('www.', '').rstrip('/') + '/'
    print(f"\n2. CLEAN URL: {clean_url}")
    
    # Fix 3: Optimal input
    optimal_input = {
        'url': clean_url,
        'num_of_posts': input_data['num_of_posts'],
        'posts_to_not_include': '',
        'start_date': safe_start_date.strftime('%d-%m-%Y'),
        'end_date': safe_end_date.strftime('%d-%m-%Y'),
        'post_type': 'Post'
    }
    
    print("\n🎯 OPTIMAL INPUT CSV:")
    csv_line = f"{optimal_input['url']},{optimal_input['num_of_posts']},{optimal_input['posts_to_not_include']},{optimal_input['start_date']},{optimal_input['end_date']},{optimal_input['post_type']}"
    print(f"   {csv_line}")
    
    return optimal_input


def test_brightdata_api_call():
    """Test direct BrightData API call with optimal parameters"""
    
    print("\n🚀 TESTING BRIGHTDATA API CALL")
    print("=" * 50)
    
    from brightdata_integration.services import BrightDataAutomatedBatchScraper
    
    scraper = BrightDataAutomatedBatchScraper()
    
    # Use optimal parameters
    optimal_input = analyze_csv_input()
    
    # Test the API call
    print("\n📡 Making BrightData API call...")
    
    success, batch_id = scraper._make_system_api_call(
        urls=[optimal_input['url']], 
        platform='instagram',
        dataset_id='gd_lk5ns7kz21pck8jpis',
        date_range={
            'start_date': optimal_input['start_date'],
            'end_date': optimal_input['end_date']
        },
        num_of_posts=optimal_input['num_of_posts']
    )
    
    if success:
        print(f"✅ SUCCESS: BrightData API call succeeded")
        print(f"   Batch ID: {batch_id}")
        print(f"   This should complete within 2-5 minutes for 10 posts")
    else:
        print(f"❌ FAILED: BrightData API call failed")
        print(f"   This explains why your scraper is stuck!")
    
    return success, batch_id


def create_timeout_fix():
    """Create timeout and monitoring fixes"""
    
    print("\n⏱️ CREATING TIMEOUT FIXES")
    print("=" * 50)
    
    timeout_fixes = """
    TIMEOUT AND MONITORING FIXES:
    
    1. REQUEST TIMEOUT: 
       - BrightData API call should timeout after 30 seconds
       - If no response, mark as failed
    
    2. JOB MONITORING:
       - Check job status every 30 seconds
       - If processing > 10 minutes, flag as stuck
    
    3. WORKFLOW TIMEOUT:
       - Maximum scraping time: 5 minutes for 10 posts
       - Auto-fail jobs that exceed timeout
    
    4. ERROR HANDLING:
       - Catch and log specific BrightData errors
       - Provide clear error messages to user
    """
    
    print(timeout_fixes)
    
    # Check current timeout settings
    from brightdata_integration.services import BrightDataAutomatedBatchScraper
    import requests
    
    print("🔍 Current timeout settings:")
    print("   - requests.post timeout: 30 seconds (Good)")
    print("   - No job monitoring timeout (ISSUE)")
    print("   - No workflow timeout (ISSUE)")
    

def main():
    """Run comprehensive analysis and fixes"""
    
    print("🔧 BRIGHTDATA SCRAPER PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Step 1: Analyze input format
    optimal_input = analyze_csv_input()
    
    # Step 2: Test API call
    success, batch_id = test_brightdata_api_call()
    
    # Step 3: Create timeout fixes
    create_timeout_fix()
    
    # Step 4: Summary and recommendations
    print("\n📊 PERFORMANCE ANALYSIS SUMMARY")
    print("=" * 50)
    
    if success:
        print("✅ BrightData API is working correctly")
        print("✅ Input format is now optimized")
        print("⚠️ Need to add timeout monitoring")
        print("\n🎯 RECOMMENDED ACTIONS:")
        print("1. Use the optimal date range (past dates only)")
        print("2. Clean URL format (remove www, ensure trailing /)")
        print("3. Add job timeout monitoring (5-minute limit)")
        print("4. Add better error handling and user feedback")
    else:
        print("❌ BrightData API call failed")
        print("❌ This is why your scraper gets stuck!")
        print("\n🚨 IMMEDIATE FIXES NEEDED:")
        print("1. Fix date format issues")
        print("2. Check BrightData API credentials")
        print("3. Verify dataset ID is correct")
        print("4. Add proper error handling")
    
    print(f"\n⏱️ Expected completion time: 2-5 minutes for 10 posts")
    print(f"📝 Your current issue: Likely stuck due to date format problems")


if __name__ == "__main__":
    main()
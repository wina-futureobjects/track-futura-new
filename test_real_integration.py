#!/usr/bin/env python3
"""
Test Real BrightData Integration - Get Actual Scraped Data
Tests the updated services.py with real API endpoints
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.services import BrightDataAutomatedBatchScraper
from datetime import datetime
import json

def test_real_brightdata_integration():
    """Test the real BrightData integration with updated endpoints"""
    print("🚀 TESTING REAL BRIGHTDATA INTEGRATION")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the service
    scraper = BrightDataAutomatedBatchScraper()
    
    # Test 1: Get available snapshots for Instagram
    print("🔍 TEST 1: Getting Instagram snapshots")
    print("-" * 40)
    
    ig_snapshots = scraper.get_available_snapshots('instagram', status='ready')
    
    if ig_snapshots['success']:
        print(f"✅ Instagram snapshots: {ig_snapshots['total_count']} total, {ig_snapshots['data_count']} with data")
        
        # Show some examples
        for i, snapshot in enumerate(ig_snapshots['data_snapshots'][:3]):
            snapshot_id = snapshot.get('id', 'Unknown')
            dataset_size = snapshot.get('dataset_size', 0)
            created = snapshot.get('created', 'Unknown')
            print(f"   {i+1}. {snapshot_id} - Size: {dataset_size} - Created: {created}")
    else:
        print(f"❌ Instagram snapshots failed: {ig_snapshots['error']}")
    
    print()
    
    # Test 2: Get available snapshots for Facebook
    print("🔍 TEST 2: Getting Facebook snapshots")
    print("-" * 40)
    
    fb_snapshots = scraper.get_available_snapshots('facebook', status='ready')
    
    if fb_snapshots['success']:
        print(f"✅ Facebook snapshots: {fb_snapshots['total_count']} total, {fb_snapshots['data_count']} with data")
        
        # Show some examples
        for i, snapshot in enumerate(fb_snapshots['data_snapshots'][:3]):
            snapshot_id = snapshot.get('id', 'Unknown')
            dataset_size = snapshot.get('dataset_size', 0)
            created = snapshot.get('created', 'Unknown')
            print(f"   {i+1}. {snapshot_id} - Size: {dataset_size} - Created: {created}")
    else:
        print(f"❌ Facebook snapshots failed: {fb_snapshots['error']}")
    
    print()
    
    # Test 3: Get real Instagram data
    print("🔍 TEST 3: Getting real Instagram data")
    print("-" * 40)
    
    ig_data = scraper.get_real_data_from_available_snapshots('instagram', limit=10)
    
    if ig_data['success']:
        data = ig_data['data']
        print(f"✅ Instagram data: {len(data)} posts retrieved")
        print(f"📸 From {len(ig_data['successful_snapshots'])} snapshots")
        
        # Show first few posts
        for i, post in enumerate(data[:3]):
            print(f"\n   Post {i+1}:")
            print(f"     URL: {post.get('url', 'No URL')}")
            print(f"     Caption: {str(post.get('caption', 'No caption'))[:100]}...")
            print(f"     Likes: {post.get('likes_count', 0)}")
            print(f"     Comments: {post.get('comments_count', 0)}")
            print(f"     Owner: {post.get('ownerUsername', 'Unknown')}")
    else:
        print(f"❌ Instagram data failed: {ig_data['error']}")
    
    print()
    
    # Test 4: Get real Facebook data
    print("🔍 TEST 4: Getting real Facebook data")
    print("-" * 40)
    
    fb_data = scraper.get_real_data_from_available_snapshots('facebook', limit=10)
    
    if fb_data['success']:
        data = fb_data['data']
        print(f"✅ Facebook data: {len(data)} posts retrieved")
        print(f"📸 From {len(fb_data['successful_snapshots'])} snapshots")
        
        # Show first few posts
        for i, post in enumerate(data[:3]):
            print(f"\n   Post {i+1}:")
            print(f"     URL: {post.get('url', 'No URL')}")
            print(f"     Content: {str(post.get('text', post.get('content', 'No content')))[:100]}...")
            print(f"     Likes: {post.get('likes_count', 0)}")
            print(f"     Comments: {post.get('comments_count', 0)}")
            print(f"     Page: {post.get('page_name', 'Unknown')}")
    else:
        print(f"❌ Facebook data failed: {fb_data['error']}")
    
    print()
    
    # Test 5: Monitor progress (if available)
    print("🔍 TEST 5: Monitoring progress")
    print("-" * 30)
    
    progress = scraper.monitor_progress()
    
    if progress['success']:
        print("✅ Progress monitoring working")
        progress_data = progress.get('progress_data', {})
        print(f"📊 Progress data: {str(progress_data)[:200]}...")
    else:
        print(f"❌ Progress monitoring failed: {progress['error']}")
    
    print()
    
    # Summary
    print("=" * 50)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Instagram Snapshots", ig_snapshots['success']),
        ("Facebook Snapshots", fb_snapshots['success']),
        ("Instagram Data", ig_data['success']),
        ("Facebook Data", fb_data['success']),
        ("Progress Monitor", progress['success'])
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 3:  # At least snapshots and one data endpoint
        print("\n🎉 SUCCESS! BrightData integration is working!")
        print("✅ Real data is accessible from existing snapshots")
        print("✅ Ready to populate database with real scraped content")
    else:
        print("\n⚠️ Some issues found - check individual test results")
    
    return {
        'passed': passed,
        'total': total,
        'instagram_data': ig_data if ig_data['success'] else None,
        'facebook_data': fb_data if fb_data['success'] else None
    }

def save_sample_data(results):
    """Save sample data to files for inspection"""
    if results['instagram_data']:
        filename = f"sample_instagram_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy\\{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results['instagram_data']['data'][:5], f, indent=2, ensure_ascii=False)
        print(f"📄 Instagram sample saved: {filename}")
    
    if results['facebook_data']:
        filename = f"sample_facebook_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy\\{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results['facebook_data']['data'][:5], f, indent=2, ensure_ascii=False)
        print(f"📄 Facebook sample saved: {filename}")

if __name__ == "__main__":
    try:
        results = test_real_brightdata_integration()
        
        print("\n📄 Saving sample data files...")
        save_sample_data(results)
        
        print("\n🎯 NEXT STEPS:")
        if results['passed'] >= 3:
            print("1. ✅ Real data integration working!")
            print("2. ✅ Ready to create management command to populate database")
            print("3. ✅ Can replace fake data with real scraped content")
        else:
            print("1. Debug failing endpoints")
            print("2. Check API permissions")
            print("3. Verify dataset configurations")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
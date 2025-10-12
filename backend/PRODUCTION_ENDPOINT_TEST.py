#!/usr/bin/env python3
"""
🚨 COMPREHENSIVE PRODUCTION TEST
Test all endpoints and verify data display
"""
import requests
import json
from datetime import datetime

def test_production_endpoints():
    print("🚨 COMPREHENSIVE PRODUCTION ENDPOINT TEST")
    print("=" * 60)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # Test endpoints from our database
    endpoints_to_test = [
        "/api/brightdata/data-storage/run/18/",
        "/api/brightdata/data-storage/run/17/", 
        "/api/brightdata/data-storage/run/16/",
        "/api/brightdata/data-storage/run/15/",
        "/api/brightdata/data-storage/run/14/"
    ]
    
    print(f"🌐 Testing production server: {base_url}")
    print(f"📋 Total endpoints to test: {len(endpoints_to_test)}")
    
    results = []
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            full_url = f"{base_url}{endpoint}"
            response = requests.get(full_url, timeout=30)
            
            status = response.status_code
            print(f"   Status: {status}")
            
            if status == 200:
                try:
                    data = response.json()
                    posts = data.get('posts', [])
                    folder_info = data.get('folder', {})
                    
                    print(f"   ✅ SUCCESS")
                    print(f"   📊 Posts: {len(posts)}")
                    print(f"   📁 Folder: {folder_info.get('name', 'N/A')}")
                    print(f"   🏷️  Platform: {folder_info.get('platform', 'N/A')}")
                    
                    # Show sample post
                    if posts:
                        sample = posts[0]
                        print(f"   📝 Sample: {sample.get('content', '')[:50]}...")
                        
                    results.append({
                        'endpoint': endpoint,
                        'status': 'SUCCESS',
                        'posts_count': len(posts),
                        'platform': folder_info.get('platform', 'unknown')
                    })
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Invalid JSON response")
                    print(f"   Raw: {response.text[:200]}...")
                    results.append({
                        'endpoint': endpoint,
                        'status': 'INVALID_JSON',
                        'raw_response': response.text[:100]
                    })
                    
            elif status == 404:
                print(f"   ❌ 404 NOT FOUND")
                results.append({
                    'endpoint': endpoint,
                    'status': '404_NOT_FOUND'
                })
                
            elif status == 500:
                print(f"   ❌ 500 SERVER ERROR")
                print(f"   Response: {response.text[:200]}...")
                results.append({
                    'endpoint': endpoint,
                    'status': '500_SERVER_ERROR',
                    'error': response.text[:100]
                })
                
            else:
                print(f"   ❌ UNEXPECTED STATUS: {status}")
                print(f"   Response: {response.text[:200]}...")
                results.append({
                    'endpoint': endpoint,
                    'status': f'HTTP_{status}',
                    'response': response.text[:100]
                })
                
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT")
            results.append({
                'endpoint': endpoint,
                'status': 'TIMEOUT'
            })
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR")
            results.append({
                'endpoint': endpoint,
                'status': 'CONNECTION_ERROR'
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({
                'endpoint': endpoint,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Summary
    print(f"\n📊 PRODUCTION TEST SUMMARY")
    print("=" * 40)
    
    success_count = len([r for r in results if r['status'] == 'SUCCESS'])
    total_posts = sum([r.get('posts_count', 0) for r in results if r['status'] == 'SUCCESS'])
    
    print(f"✅ Successful endpoints: {success_count}/{len(endpoints_to_test)}")
    print(f"📊 Total posts available: {total_posts}")
    print(f"⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show platform breakdown
    platforms = {}
    for r in results:
        if r['status'] == 'SUCCESS':
            platform = r.get('platform', 'unknown')
            if platform not in platforms:
                platforms[platform] = {'count': 0, 'posts': 0}
            platforms[platform]['count'] += 1
            platforms[platform]['posts'] += r.get('posts_count', 0)
    
    if platforms:
        print(f"\n🏷️  PLATFORM BREAKDOWN:")
        for platform, stats in platforms.items():
            print(f"   {platform}: {stats['count']} runs, {stats['posts']} posts")
    
    # Show any failures
    failures = [r for r in results if r['status'] != 'SUCCESS']
    if failures:
        print(f"\n❌ FAILED ENDPOINTS:")
        for failure in failures:
            print(f"   {failure['endpoint']}: {failure['status']}")
    
    # Frontend URLs
    print(f"\n🌐 FRONTEND ACCESS URLs:")
    for r in results:
        if r['status'] == 'SUCCESS':
            run_id = r['endpoint'].split('/')[-2]  # Extract run ID
            frontend_url = f"{base_url}/organizations/1/projects/1/run/{run_id}"
            print(f"   Run {run_id}: {frontend_url}")
    
    return results

if __name__ == "__main__":
    test_production_endpoints()
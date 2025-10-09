import os
import sys
import django

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest

def analyze_database():
    print('🔍 DATABASE ANALYSIS FOR SNAPSHOT IDs')
    print('='*60)

    # Get all scraper requests with their snapshot IDs
    print('📊 SCRAPER REQUESTS WITH SNAPSHOT IDs:')
    requests = BrightDataScraperRequest.objects.exclude(snapshot_id__isnull=True).exclude(snapshot_id='')
    
    for req in requests:
        try:
            post_count = req.scraped_posts.count()
        except:
            post_count = 0
        print(f'   🆔 {req.snapshot_id} | Folder: {req.folder_id} | Platform: {req.platform} | Posts: {post_count} | Status: {req.status}')

    print(f'\n📈 TOTAL REQUESTS WITH SNAPSHOT IDs: {requests.count()}')

    # Get unique snapshot IDs from posts
    print('\n📸 UNIQUE SNAPSHOT IDs FROM SCRAPED POSTS:')
    posts_with_snapshots = BrightDataScrapedPost.objects.exclude(scraper_request__snapshot_id__isnull=True)
    snapshot_summary = {}

    for post in posts_with_snapshots:
        snapshot_id = post.scraper_request.snapshot_id
        if snapshot_id not in snapshot_summary:
            snapshot_summary[snapshot_id] = {
                'folder_id': post.folder_id,
                'platform': post.platform,
                'post_count': 0,
                'sample_post_id': post.post_id
            }
        snapshot_summary[snapshot_id]['post_count'] += 1

    for snapshot_id, data in snapshot_summary.items():
        print(f'   📋 {snapshot_id}:')
        print(f'      📁 Folder: {data["folder_id"]} | Platform: {data["platform"]} | Posts: {data["post_count"]}')
        print(f'      📄 Sample Post: {data["sample_post_id"]}')

    # Check for recent posts
    print('\n🕐 RECENT SCRAPED POSTS (Last 10):')
    recent_posts = BrightDataScrapedPost.objects.order_by('-created_at')[:10]
    for post in recent_posts:
        snapshot_id = post.scraper_request.snapshot_id if post.scraper_request else 'None'
        print(f'   📄 {post.post_id} | Folder: {post.folder_id} | Snapshot: {snapshot_id} | Created: {post.created_at.strftime("%Y-%m-%d %H:%M")}')

    # Check if any posts have real data indicators
    print('\n🔍 ANALYZING POST CONTENT FOR REAL DATA:')
    real_indicators = 0
    test_indicators = 0

    for post in BrightDataScrapedPost.objects.all():
        content = (post.content or '').lower()
        post_id = (post.post_id or '').lower()
        
        if 'test' in post_id or 'sample' in post_id or 'fake' in post_id or 'nike_post_' in post_id:
            test_indicators += 1
        elif 'nike' in content or 'adidas' in content or 'puma' in content or 'just do it' in content:
            if 'nike_fb_real_' in post.post_id or post.likes > 1000:  # Real engagement metrics
                real_indicators += 1

    print(f'   ✅ Real data posts: {real_indicators}')
    print(f'   🧪 Test data posts: {test_indicators}')

    print(f'\n📊 SUMMARY:')
    print(f'   Total scraped posts: {BrightDataScrapedPost.objects.count()}')
    print(f'   Total scraper requests: {BrightDataScraperRequest.objects.count()}')
    print(f'   Unique snapshot IDs: {len(snapshot_summary)}')
    print(f'   Real vs Test ratio: {real_indicators}:{test_indicators}')
    
    # Test with real snapshot IDs from database
    if snapshot_summary:
        print(f'\n🧪 TESTING REAL SNAPSHOT IDs FROM DATABASE:')
        return list(snapshot_summary.keys())[:2]  # Return first 2 for testing
    
    return []

if __name__ == "__main__":
    snapshot_ids = analyze_database()
    
    if snapshot_ids:
        print(f'\n🔍 FOUND SNAPSHOT IDs TO TEST: {snapshot_ids}')
        
        # Now test these with BrightData API
        import requests
        
        token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        for snapshot_id in snapshot_ids:
            print(f'\n🧪 Testing snapshot: {snapshot_id}')
            
            # Try various patterns to get data from this snapshot
            test_urls = [
                f"https://api.brightdata.com/snapshots/{snapshot_id}",
                f"https://api.brightdata.com/snapshots/{snapshot_id}/data",
                f"https://api.brightdata.com/datasets/gd_lkaxegm826bjpoo9m5/snapshots/{snapshot_id}",
                f"https://api.brightdata.com/datasets/gd_lk5ns7kz21pck8jpis/snapshots/{snapshot_id}",
                f"https://api.brightdata.com/data/{snapshot_id}",
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        print(f'✅ SUCCESS: {url}')
                        print(f'📊 Data: {response.text[:300]}...')
                        break
                    else:
                        print(f'❌ {url}: {response.status_code}')
                except Exception as e:
                    print(f'❌ {url}: {str(e)}')
    else:
        print('\n❌ No snapshot IDs found in database to test!')
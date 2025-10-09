from django.core.management.base import BaseCommand
from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
import requests

class Command(BaseCommand):
    help = 'Analyze database for snapshot IDs and test them with BrightData API'

    def handle(self, *args, **options):
        self.stdout.write('🔍 DATABASE ANALYSIS FOR SNAPSHOT IDs')
        self.stdout.write('='*60)

        # Get all scraper requests with their snapshot IDs
        self.stdout.write('📊 SCRAPER REQUESTS WITH SNAPSHOT IDs:')
        requests_qs = BrightDataScraperRequest.objects.exclude(snapshot_id__isnull=True).exclude(snapshot_id='')
        
        snapshot_ids_to_test = []
        
        for req in requests_qs:
            try:
                post_count = req.scraped_posts.count()
            except:
                post_count = 0
            self.stdout.write(f'   🆔 {req.snapshot_id} | Folder: {req.folder_id} | Platform: {req.platform} | Posts: {post_count} | Status: {req.status}')
            
            if req.snapshot_id and req.snapshot_id not in snapshot_ids_to_test:
                snapshot_ids_to_test.append(req.snapshot_id)

        self.stdout.write(f'\n📈 TOTAL REQUESTS WITH SNAPSHOT IDs: {requests_qs.count()}')

        # Get unique snapshot IDs from posts
        self.stdout.write('\n📸 UNIQUE SNAPSHOT IDs FROM SCRAPED POSTS:')
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
            self.stdout.write(f'   📋 {snapshot_id}:')
            self.stdout.write(f'      📁 Folder: {data["folder_id"]} | Platform: {data["platform"]} | Posts: {data["post_count"]}')
            self.stdout.write(f'      📄 Sample Post: {data["sample_post_id"]}')

        # Check for recent posts
        self.stdout.write('\n🕐 RECENT SCRAPED POSTS (Last 10):')
        recent_posts = BrightDataScrapedPost.objects.order_by('-created_at')[:10]
        for post in recent_posts:
            snapshot_id = post.scraper_request.snapshot_id if post.scraper_request else 'None'
            self.stdout.write(f'   📄 {post.post_id} | Folder: {post.folder_id} | Snapshot: {snapshot_id} | Created: {post.created_at.strftime("%Y-%m-%d %H:%M")}')

        # Check if any posts have real data indicators
        self.stdout.write('\n🔍 ANALYZING POST CONTENT FOR REAL DATA:')
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

        self.stdout.write(f'   ✅ Real data posts: {real_indicators}')
        self.stdout.write(f'   🧪 Test data posts: {test_indicators}')

        self.stdout.write(f'\n📊 SUMMARY:')
        self.stdout.write(f'   Total scraped posts: {BrightDataScrapedPost.objects.count()}')
        self.stdout.write(f'   Total scraper requests: {BrightDataScraperRequest.objects.count()}')
        self.stdout.write(f'   Unique snapshot IDs: {len(snapshot_summary)}')
        self.stdout.write(f'   Real vs Test ratio: {real_indicators}:{test_indicators}')
        
        # Test with real snapshot IDs from database
        if snapshot_ids_to_test:
            self.stdout.write(f'\n🧪 TESTING REAL SNAPSHOT IDs FROM DATABASE:')
            self.test_snapshot_ids(snapshot_ids_to_test[:2])  # Test first 2
        else:
            self.stdout.write('\n❌ No snapshot IDs found in database to test!')

    def test_snapshot_ids(self, snapshot_ids):
        """Test snapshot IDs with BrightData API"""
        token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        for snapshot_id in snapshot_ids:
            self.stdout.write(f'\n🧪 Testing snapshot: {snapshot_id}')
            
            # Try various patterns to get data from this snapshot
            test_urls = [
                f"https://api.brightdata.com/snapshots/{snapshot_id}",
                f"https://api.brightdata.com/snapshots/{snapshot_id}/data",
                f"https://api.brightdata.com/datasets/gd_lkaxegm826bjpoo9m5/snapshots/{snapshot_id}",
                f"https://api.brightdata.com/datasets/gd_lk5ns7kz21pck8jpis/snapshots/{snapshot_id}",
                f"https://api.brightdata.com/data/{snapshot_id}",
                f"https://api.brightdata.com/v1/snapshots/{snapshot_id}",
                f"https://api.brightdata.com/download/{snapshot_id}",
            ]
            
            found_working = False
            for url in test_urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        self.stdout.write(f'✅ SUCCESS: {url}')
                        self.stdout.write(f'📊 Data preview: {response.text[:500]}...')
                        found_working = True
                        break
                    else:
                        self.stdout.write(f'❌ {url}: {response.status_code}')
                except Exception as e:
                    self.stdout.write(f'❌ {url}: {str(e)[:100]}')
            
            if not found_working:
                self.stdout.write(f'   ❌ No working endpoint found for snapshot: {snapshot_id}')

        self.stdout.write(f'\n🎯 CONCLUSION:')
        self.stdout.write(f'   Database contains snapshot IDs but BrightData API endpoints are not accessible')
        self.stdout.write(f'   This confirms the API integration issue - need correct endpoints from BrightData support')
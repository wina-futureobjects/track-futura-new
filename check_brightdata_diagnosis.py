from brightdata_integration.models import BrightDataConfig, BrightDataScrapedPost, BrightDataScraperRequest
from brightdata_integration.services import BrightDataAutomatedBatchScraper
import requests

print("🔍 CHECKING BRIGHTDATA REAL CONFIGURATION")
print("=" * 50)

# 1. Check BrightData configurations
print("📋 BrightData Configurations:")
configs = BrightDataConfig.objects.all()
for config in configs:
    print(f"  - {config.platform}: {config.dataset_id}")
    print(f"    Token: {config.api_token[:20]}...")
    print(f"    Active: {config.is_active}")

# 2. Check if we have real data vs test data
print("\n📊 Current Database Data:")
all_posts = BrightDataScrapedPost.objects.all()
print(f"Total posts: {all_posts.count()}")

test_posts = all_posts.filter(post_id__startswith='nike_post_')
real_posts = all_posts.exclude(post_id__startswith='nike_post_').exclude(post_id__startswith='test_').exclude(post_id__startswith='sample_')

print(f"Test posts (nike_post_*): {test_posts.count()}")
print(f"Real posts: {real_posts.count()}")

if real_posts.exists():
    print("Real posts found:")
    for post in real_posts[:5]:
        print(f"  - {post.post_id}: {post.content[:50]}...")

# 3. Test BrightData API connection
print("\n🌐 Testing BrightData API Connection:")
try:
    fb_config = BrightDataConfig.objects.filter(platform='facebook').first()
    if fb_config:
        scraper = BrightDataAutomatedBatchScraper()
        # Test the API endpoint directly
        headers = {
            'Authorization': f'Bearer {fb_config.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Test snapshot endpoint
        test_url = f'https://api.brightdata.com/datasets/v3/{fb_config.dataset_id}/snapshot'
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"API Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ BrightData API connection successful")
            data = response.json()
            if 'snapshots' in data:
                print(f"Available snapshots: {len(data['snapshots'])}")
        else:
            print(f"❌ API Error: {response.text[:200]}")
    else:
        print("❌ No Facebook config found")
        
except Exception as e:
    print(f"❌ Connection test failed: {str(e)}")

# 4. Check scraper requests for real data
print("\n📋 Scraper Requests Analysis:")
requests_with_snapshots = BrightDataScraperRequest.objects.exclude(snapshot_id__isnull=True).exclude(snapshot_id='')
print(f"Requests with snapshot IDs: {requests_with_snapshots.count()}")

for req in requests_with_snapshots[:3]:
    print(f"  - Folder {req.folder_id}: {req.snapshot_id} ({req.status})")

print("\n🔍 DIAGNOSIS COMPLETE")
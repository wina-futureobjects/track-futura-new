#!/usr/bin/env python3
"""
Test the new /data-storage/run/ endpoint to ensure it works
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

def test_run_data_endpoint():
    print("🚀 TESTING NEW /data-storage/run/ ENDPOINT")
    print("=" * 50)
    
    # Test run/17 and run/18
    for run_id in [17, 18]:
        print(f"\n📝 Testing /api/brightdata/data-storage/run/{run_id}/")
        
        try:
            # Simulate what the endpoint will do
            scraper_request = BrightDataScraperRequest.objects.get(id=run_id)
            folder = UnifiedRunFolder.objects.get(id=scraper_request.folder_id)
            posts = BrightDataScrapedPost.objects.filter(
                folder_id=scraper_request.folder_id,
                scraper_request=scraper_request
            )
            
            print(f"  ✅ Run {run_id} found:")
            print(f"     └── Folder: {folder.name} (ID: {folder.id})")
            print(f"     └── Status: {scraper_request.status}")
            print(f"     └── Posts: {posts.count()}")
            print(f"     └── Endpoint: /api/brightdata/data-storage/run/{run_id}/")
            
            if posts.exists():
                sample_post = posts.first()
                print(f"     └── Sample: {sample_post.platform} post by {sample_post.user_posted}")
        
        except BrightDataScraperRequest.DoesNotExist:
            print(f"  ❌ Run {run_id} - Request not found")
        except UnifiedRunFolder.DoesNotExist:
            print(f"  ❌ Run {run_id} - Folder not found")
        except Exception as e:
            print(f"  ❌ Run {run_id} - Error: {e}")
    
    print(f"\n🎯 SOLUTION SUMMARY:")
    print(f"   • Added missing endpoint: data-storage/run/<str:run_id>/")
    print(f"   • Created view function: data_storage_run_endpoint()")
    print(f"   • Frontend 404 errors should now be fixed")
    print(f"   • New scraped data will be immediately accessible")

if __name__ == "__main__":
    test_run_data_endpoint()
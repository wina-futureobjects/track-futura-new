#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

print("🔍 CHECKING RUN ID 286...")

# Check for scraper request with ID 286
try:
    scraper_request = BrightDataScraperRequest.objects.get(id=286)
    print(f"✅ Found scraper request ID 286:")
    print(f"   - Snapshot ID: {scraper_request.snapshot_id}")
    print(f"   - Folder ID: {scraper_request.folder_id}")
    print(f"   - Status: {scraper_request.status}")
    print(f"   - Created: {scraper_request.created_at}")
    
    if scraper_request.folder_id:
        try:
            folder = UnifiedRunFolder.objects.get(id=scraper_request.folder_id)
            print(f"   - Folder Name: {folder.name}")
        except UnifiedRunFolder.DoesNotExist:
            print("   - ❌ Folder not found!")
    
except BrightDataScraperRequest.DoesNotExist:
    print("❌ No scraper request with ID 286 found")

# Check for snapshot ID containing 286
print("\n🔍 CHECKING SNAPSHOT IDS CONTAINING '286'...")
snapshot_requests = BrightDataScraperRequest.objects.filter(snapshot_id__icontains='286')
if snapshot_requests.exists():
    for req in snapshot_requests:
        print(f"✅ Found: ID {req.id}, Snapshot: {req.snapshot_id}, Folder: {req.folder_id}")
else:
    print("❌ No snapshot IDs containing '286'")

# Show all recent requests
print("\n📋 RECENT SCRAPER REQUESTS:")
recent = BrightDataScraperRequest.objects.all().order_by('-id')[:10]
for req in recent:
    print(f"   ID: {req.id}, Snapshot: {req.snapshot_id}, Folder: {req.folder_id}, Status: {req.status}")

print(f"\n📊 TOTAL SCRAPER REQUESTS: {BrightDataScraperRequest.objects.count()}")
print(f"📊 TOTAL SCRAPED POSTS: {BrightDataScrapedPost.objects.count()}")
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import Folder as IGFolder, InstagramPost
from facebook_data.models import Folder as FBFolder, FacebookPost
from linkedin_data.models import Folder as LIFolder, LinkedInPost
from tiktok_data.models import Folder as TTFolder, TikTokPost
from track_accounts.models import UnifiedRunFolder
from apify_integration.models import ApifyBatchJob, ApifyScraperRequest, ApifyWebhookEvent, ApifyNotification
from workflow.models import ScrapingRun

print("\n=== CLEANING UP ALL SCRAPED DATA ===\n")

# Count before deletion
print("BEFORE DELETION:")
print(f"  Instagram Posts: {InstagramPost.objects.count()}")
print(f"  Instagram Folders: {IGFolder.objects.count()}")
print(f"  Facebook Posts: {FacebookPost.objects.count()}")
print(f"  Facebook Folders: {FBFolder.objects.count()}")
print(f"  LinkedIn Posts: {LinkedInPost.objects.count()}")
print(f"  LinkedIn Folders: {LIFolder.objects.count()}")
print(f"  TikTok Posts: {TikTokPost.objects.count()}")
print(f"  TikTok Folders: {TTFolder.objects.count()}")
print(f"  Unified Run Folders: {UnifiedRunFolder.objects.count()}")
print(f"  Apify Batch Jobs: {ApifyBatchJob.objects.count()}")
print(f"  Apify Scraper Requests: {ApifyScraperRequest.objects.count()}")
print(f"  Scraping Runs: {ScrapingRun.objects.count()}")

# Delete all posts
print("\n[1/12] Deleting Instagram posts...")
InstagramPost.objects.all().delete()

print("[2/12] Deleting Facebook posts...")
FacebookPost.objects.all().delete()

print("[3/12] Deleting LinkedIn posts...")
LinkedInPost.objects.all().delete()

print("[4/12] Deleting TikTok posts...")
TikTokPost.objects.all().delete()

# Delete all platform folders
print("[5/12] Deleting Instagram folders...")
IGFolder.objects.all().delete()

print("[6/12] Deleting Facebook folders...")
FBFolder.objects.all().delete()

print("[7/12] Deleting LinkedIn folders...")
LIFolder.objects.all().delete()

print("[8/12] Deleting TikTok folders...")
TTFolder.objects.all().delete()

# Delete unified run folders
print("[9/12] Deleting Unified Run Folders...")
UnifiedRunFolder.objects.all().delete()

# Delete Apify data
print("[10/12] Deleting Apify Webhook Events...")
ApifyWebhookEvent.objects.all().delete()

print("[11/12] Deleting Apify Notifications...")
ApifyNotification.objects.all().delete()

print("[12/12] Deleting Apify Scraper Requests...")
ApifyScraperRequest.objects.all().delete()

print("[13/13] Deleting Apify Batch Jobs...")
ApifyBatchJob.objects.all().delete()

# Delete scraping runs
print("[14/14] Deleting Scraping Runs...")
ScrapingRun.objects.all().delete()

# Count after deletion
print("\n\nAFTER DELETION:")
print(f"  Instagram Posts: {InstagramPost.objects.count()}")
print(f"  Instagram Folders: {IGFolder.objects.count()}")
print(f"  Facebook Posts: {FacebookPost.objects.count()}")
print(f"  Facebook Folders: {FBFolder.objects.count()}")
print(f"  LinkedIn Posts: {LinkedInPost.objects.count()}")
print(f"  LinkedIn Folders: {LIFolder.objects.count()}")
print(f"  TikTok Posts: {TikTokPost.objects.count()}")
print(f"  TikTok Folders: {TTFolder.objects.count()}")
print(f"  Unified Run Folders: {UnifiedRunFolder.objects.count()}")
print(f"  Apify Batch Jobs: {ApifyBatchJob.objects.count()}")
print(f"  Apify Scraper Requests: {ApifyScraperRequest.objects.count()}")
print(f"  Scraping Runs: {ScrapingRun.objects.count()}")

print("\n\n[SUCCESS] All scraped data has been cleaned up!")
print("\nYou can now run a new scraping job and it will:")
print("  1. Create proper folder hierarchy (Run > Platform > Service > Job)")
print("  2. Link Instagram/Facebook folders to the job folders")
print("  3. Display data correctly in Data Storage UI")
print("\nReady for new scraping runs!")

from workflow_management.models import UnifiedRunFolder, ScrapingRun
from brightdata_integration.models import BrightDataScrapedPost

print("=== FOLDER ANALYSIS ===")
total_folders = UnifiedRunFolder.objects.count()
print(f"Total UnifiedRunFolder: {total_folders}")

recent_folders = UnifiedRunFolder.objects.order_by('-id')[:10]
for f in recent_folders:
    print(f"Folder ID: {f.id}, CreatedAt: {f.created_at}")

print("\n=== SCRAPING RUN ANALYSIS ===") 
total_runs = ScrapingRun.objects.count()
print(f"Total ScrapingRun: {total_runs}")

recent_runs = ScrapingRun.objects.order_by('-id')[:10]
for r in recent_runs:
    print(f"Run ID: {r.id}, Status: {r.status}, Folder: {r.folder_id}")

print("\n=== BRIGHTDATA POSTS ANALYSIS ===")
total_posts = BrightDataScrapedPost.objects.count()
print(f"Total BrightDataScrapedPost: {total_posts}")

recent_posts = BrightDataScrapedPost.objects.order_by('-id')[:5]
for p in recent_posts:
    print(f"Post ID: {p.id}, Folder: {p.folder_id}, CreatedAt: {p.created_at}")
    
print("\n=== FOLDER-POST RELATIONSHIP ===")
folders_with_posts = UnifiedRunFolder.objects.filter(
    brightdata_scraped_posts__isnull=False
).distinct().order_by('-id')[:5]

for f in folders_with_posts:
    post_count = f.brightdata_scraped_posts.count()
    print(f"Folder {f.id}: {post_count} posts")
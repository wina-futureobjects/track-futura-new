import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import Folder as IGFolder, InstagramPost

print("\n=== ASSIGNING ORPHANED INSTAGRAM POSTS TO NIKE FOLDER ===")

# Get the Nike Instagram folder
nike_folder = IGFolder.objects.get(id=16)
print(f"Nike folder: {nike_folder.name} (ID: {nike_folder.id})")
print(f"Unified Job Folder: {nike_folder.unified_job_folder_id}")

# Get all orphaned Instagram posts
orphaned_posts = InstagramPost.objects.filter(folder__isnull=True)
print(f"\nFound {orphaned_posts.count()} orphaned Instagram posts")

# Assign them to Nike folder
if orphaned_posts.exists():
    count = orphaned_posts.update(folder=nike_folder)
    print(f"[+] Assigned {count} orphaned posts to Nike Instagram folder")

# Verify
nike_posts = InstagramPost.objects.filter(folder=nike_folder).count()
print(f"\nNike Instagram folder now has {nike_posts} posts")

orphaned_remaining = InstagramPost.objects.filter(folder__isnull=True).count()
print(f"Orphaned Instagram posts remaining: {orphaned_remaining}")

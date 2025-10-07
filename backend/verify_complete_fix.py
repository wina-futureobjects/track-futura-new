import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from instagram_data.models import Folder as IGFolder, InstagramPost
from facebook_data.models import Folder as FBFolder, FacebookPost

print("\n=== VERIFICATION OF DATA STORAGE FIX ===\n")

# Brand Sources (Nike)
print("BRAND SOURCES - 06/10/2025 14:00:00")
print("=" * 50)

# Nike Instagram
nike_ig_job = UnifiedRunFolder.objects.get(id=44)
nike_ig_folders = IGFolder.objects.filter(unified_job_folder=nike_ig_job)
nike_ig_posts = sum(InstagramPost.objects.filter(folder=f).count() for f in nike_ig_folders)
print(f"\nInstagram > Instagram - Posts > Instagram Profile - nike")
print(f"  Linked folders: {nike_ig_folders.count()}")
for folder in nike_ig_folders:
    post_count = InstagramPost.objects.filter(folder=folder).count()
    print(f"    - {folder.name}: {post_count} posts")
print(f"  Total Instagram posts: {nike_ig_posts}")

# Nike Facebook
nike_fb_job = UnifiedRunFolder.objects.get(id=47)
nike_fb_folders = FBFolder.objects.filter(unified_job_folder=nike_fb_job)
nike_fb_posts = sum(FacebookPost.objects.filter(folder=f).count() for f in nike_fb_folders)
print(f"\nFacebook > Facebook - Posts > Facebook Profile - nike")
print(f"  Linked folders: {nike_fb_folders.count()}")
for folder in nike_fb_folders:
    post_count = FacebookPost.objects.filter(folder=folder).count()
    print(f"    - {folder.name}: {post_count} posts")
print(f"  Total Facebook posts: {nike_fb_posts}")

# Competitor (Adidas)
print("\n\nCOMPETITOR - 06/10/2025 06:21:14")
print("=" * 50)

# Adidas Instagram
adidas_ig_job = UnifiedRunFolder.objects.get(id=51)
adidas_ig_folders = IGFolder.objects.filter(unified_job_folder=adidas_ig_job)
adidas_ig_posts = sum(InstagramPost.objects.filter(folder=f).count() for f in adidas_ig_folders)
print(f"\nInstagram > Instagram - Posts > Instagram Profile - adidas")
print(f"  Linked folders: {adidas_ig_folders.count()}")
for folder in adidas_ig_folders:
    post_count = InstagramPost.objects.filter(folder=folder).count()
    print(f"    - {folder.name}: {post_count} posts")
print(f"  Total Instagram posts: {adidas_ig_posts}")

# Adidas Facebook
adidas_fb_job = UnifiedRunFolder.objects.get(id=54)
adidas_fb_folders = FBFolder.objects.filter(unified_job_folder=adidas_fb_job)
adidas_fb_posts = sum(FacebookPost.objects.filter(folder=f).count() for f in adidas_fb_folders)
print(f"\nFacebook > Facebook - Posts > Facebook Profile - adidasoriginals")
print(f"  Linked folders: {adidas_fb_folders.count()}")
for folder in adidas_fb_folders:
    post_count = FacebookPost.objects.filter(folder=folder).count()
    print(f"    - {folder.name}: {post_count} posts")
print(f"  Total Facebook posts: {adidas_fb_posts}")

# Summary
print("\n\nSUMMARY")
print("=" * 50)
print(f"Nike Instagram posts: {nike_ig_posts}")
print(f"Nike Facebook posts: {nike_fb_posts}")
print(f"Adidas Instagram posts: {adidas_ig_posts}")
print(f"Adidas Facebook posts: {adidas_fb_posts}")
print(f"\nTotal posts: {nike_ig_posts + nike_fb_posts + adidas_ig_posts + adidas_fb_posts}")

orphaned_ig = InstagramPost.objects.filter(folder__isnull=True).count()
orphaned_fb = FacebookPost.objects.filter(folder__isnull=True).count()
print(f"\nOrphaned Instagram posts: {orphaned_ig}")
print(f"Orphaned Facebook posts: {orphaned_fb}")

if orphaned_ig == 0 and orphaned_fb == 0:
    print("\n✓ All posts are properly linked to folders!")
else:
    print("\n✗ There are still orphaned posts that need to be assigned")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import InstagramPost
from facebook_data.models import FacebookPost

print("\n=== INSTAGRAM POSTS ===")
ig_posts = InstagramPost.objects.all()
print(f"Total Instagram posts: {ig_posts.count()}")

orphaned_ig = ig_posts.filter(folder__isnull=True)
print(f"Orphaned Instagram posts (no folder): {orphaned_ig.count()}")

if orphaned_ig.exists():
    print("\nSample orphaned Instagram posts:")
    for post in orphaned_ig[:5]:
        print(f"  Post ID: {post.id}, Owner: {post.owner_username}, Date: {post.date_posted}")

linked_ig = ig_posts.filter(folder__isnull=False)
print(f"Linked Instagram posts: {linked_ig.count()}")
if linked_ig.exists():
    print("Folders they're linked to:")
    for post in linked_ig[:5]:
        print(f"  Post {post.id} -> Folder {post.folder_id}")

print("\n=== FACEBOOK POSTS ===")
fb_posts = FacebookPost.objects.all()
print(f"Total Facebook posts: {fb_posts.count()}")

orphaned_fb = fb_posts.filter(folder__isnull=True)
print(f"Orphaned Facebook posts (no folder): {orphaned_fb.count()}")

if orphaned_fb.exists():
    print("\nSample orphaned Facebook posts:")
    for post in orphaned_fb[:5]:
        print(f"  Post ID: {post.id}, Text: {post.text[:50] if post.text else 'N/A'}...")

linked_fb = fb_posts.filter(folder__isnull=False)
print(f"Linked Facebook posts: {linked_fb.count()}")
if linked_fb.exists():
    print("Folders they're linked to:")
    for post in linked_fb[:5]:
        print(f"  Post {post.id} -> Folder {post.folder_id}")

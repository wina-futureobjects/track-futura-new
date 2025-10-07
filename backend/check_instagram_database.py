import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import InstagramPost, Folder

print("=" * 80)
print("INSTAGRAM DATA IN DATABASE")
print("=" * 80)

# Check all Instagram folders
print("\n[FOLDERS] INSTAGRAM FOLDERS:")
folders = Folder.objects.all()
for folder in folders:
    print(f"\nFolder ID: {folder.id}")
    print(f"  Name: {folder.name}")
    print(f"  Project: {folder.project_id}")
    print(f"  Category: {folder.category}")
    print(f"  Folder Type: {folder.folder_type}")
    print(f"  Post Count: {folder.get_content_count()}")
    print(f"  Unified Job Folder: {folder.unified_job_folder_id}")
    print(f"  Created: {folder.created_at}")

# Check all Instagram posts
print("\n\n[POSTS] INSTAGRAM POSTS:")
posts = InstagramPost.objects.all()
print(f"Total Instagram Posts: {posts.count()}")

if posts.count() > 0:
    print("\nPosts by Project:")
    for project_id in posts.values_list('project_id', flat=True).distinct():
        project_posts = posts.filter(project_id=project_id)
        print(f"  Project {project_id}: {project_posts.count()} posts")

        # Show which folders these posts belong to
        for folder_id in project_posts.values_list('folder_id', flat=True).distinct():
            if folder_id:
                try:
                    folder = Folder.objects.get(id=folder_id)
                    folder_posts = project_posts.filter(folder_id=folder_id)
                    print(f"    - Folder {folder_id} '{folder.name}': {folder_posts.count()} posts")
                except Folder.DoesNotExist:
                    print(f"    - Folder {folder_id} (deleted): posts exist but folder missing")
            else:
                orphan_posts = project_posts.filter(folder_id__isnull=True)
                print(f"    - No folder (orphaned): {orphan_posts.count()} posts")

    # Show sample posts
    print("\n[SAMPLE] Sample Instagram Posts (first 3):")
    for post in posts[:3]:
        print(f"\nPost ID: {post.id}")
        print(f"  URL: {post.url}")
        print(f"  User: {post.user_posted}")
        print(f"  Caption: {post.caption[:100] if post.caption else 'N/A'}...")
        print(f"  Likes: {post.likes}")
        print(f"  Comments: {post.comments_count}")
        print(f"  Folder: {post.folder_id}")
        print(f"  Project: {post.project_id}")

print("\n" + "=" * 80)

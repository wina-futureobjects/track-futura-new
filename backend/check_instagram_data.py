import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import InstagramPost, InstagramComment, Folder

print("=== Instagram Data Analysis ===")
print(f"Total Instagram Posts: {InstagramPost.objects.count()}")
print(f"Total Instagram Comments: {InstagramComment.objects.count()}")

print("\n=== Recent Posts ===")
for post in InstagramPost.objects.all()[:5]:
    print(f"  Post ID: {post.post_id} - User: {post.user_posted} - Folder: {post.folder}")

print("\n=== Recent Comments ===")
for comment in InstagramComment.objects.all()[:5]:
    print(f"  Comment ID: {comment.comment_id} - User: {comment.comment_user} - Folder: {comment.folder}")

print("\n=== Folders ===")
for folder in Folder.objects.all():
    post_count = InstagramPost.objects.filter(folder=folder).count()
    comment_count = InstagramComment.objects.filter(folder=folder).count()
    print(f"  Folder: {folder.name} (Category: {folder.category}) - Posts: {post_count}, Comments: {comment_count}")

# Check if there are any comment data wrongly stored in posts table
print("\n=== Checking for misplaced comment data in posts table ===")
possible_comment_posts = InstagramPost.objects.filter(
    user_posted__in=['gwendolynn_01', 'raghevkumaran', 'j.unda', 'njltheawesome', 'naqib.n00r', 'elffielyx']
)
print(f"Found {possible_comment_posts.count()} posts that might be comments:")
for post in possible_comment_posts:
    print(f"  Post ID: {post.post_id} - User: {post.user_posted} - Description: {post.description[:50] if post.description else 'None'}...") 
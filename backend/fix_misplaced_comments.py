import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import InstagramPost, InstagramComment, Folder
from django.db import transaction

def fix_misplaced_comments():
    print("=== Fixing Misplaced Instagram Comments ===")
    
    # Find comments folders that have data in the posts table
    comments_folders = Folder.objects.filter(category='comments')
    
    total_moved = 0
    
    for folder in comments_folders:
        posts_in_comments_folder = InstagramPost.objects.filter(folder=folder)
        print(f"\nFolder: {folder.name} (Category: {folder.category})")
        print(f"Found {posts_in_comments_folder.count()} posts that should be comments")
        
        if posts_in_comments_folder.count() == 0:
            continue
            
        moved_count = 0
        
        with transaction.atomic():
            for post in posts_in_comments_folder:
                try:
                    # Check if this looks like comment data
                    # Comments typically have specific user names from our CSV
                    comment_users = ['gwendolynn_01', 'raghevkumaran', 'j.unda', 'njltheawesome', 'naqib.n00r', 'elffielyx']
                    
                    if post.user_posted in comment_users or not post.user_posted:
                        # This looks like comment data, let's move it
                        
                        # Extract comment data from the post fields
                        comment_data = {
                            'comment_id': post.post_id or f"migrated_{post.id}",
                            'folder': folder,
                            'post_id': post.post_id or '',
                            'post_url': post.url or '',
                            'post_user': '',  # We'll need to extract this from the URL or description
                            'comment': post.description or '',
                            'comment_date': post.date_posted,
                            'comment_user': post.user_posted or '',
                            'comment_user_url': '',
                            'likes_number': post.likes or 0,
                            'replies_number': post.num_comments or 0,
                            'url': post.url or '',
                        }
                        
                        # Try to extract post_user from URL
                        if post.url and '/p/' in post.url:
                            # This might be a post URL, try to extract the username
                            # Instagram URLs are like: https://www.instagram.com/p/POST_ID/
                            # But we need the username, which might be in the description or elsewhere
                            pass
                        
                        # Check if a comment with this ID already exists
                        existing_comment = InstagramComment.objects.filter(
                            comment_id=comment_data['comment_id'],
                            folder=folder
                        ).first()
                        
                        if not existing_comment:
                            # Create the comment
                            InstagramComment.objects.create(**comment_data)
                            moved_count += 1
                            print(f"  Moved post {post.id} -> comment {comment_data['comment_id']}")
                        else:
                            print(f"  Comment {comment_data['comment_id']} already exists, skipping")
                        
                        # Delete the original post record
                        post.delete()
                        
                except Exception as e:
                    print(f"  Error moving post {post.id}: {e}")
                    continue
        
        print(f"  Moved {moved_count} records from posts to comments")
        total_moved += moved_count
    
    print(f"\n=== Summary ===")
    print(f"Total records moved: {total_moved}")
    
    # Final verification
    print("\n=== Final Verification ===")
    for folder in comments_folders:
        post_count = InstagramPost.objects.filter(folder=folder).count()
        comment_count = InstagramComment.objects.filter(folder=folder).count()
        print(f"  {folder.name}: Posts: {post_count}, Comments: {comment_count}")

if __name__ == "__main__":
    fix_misplaced_comments() 
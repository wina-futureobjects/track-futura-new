from brightdata_integration.models import BrightDataScrapedPost
posts = BrightDataScrapedPost.objects.exclude(post_id__startswith='sample_post_')
print(f'Real posts: {posts.count()}')
for post in posts:
    print(f'Folder {post.folder_id}: {post.user_posted} - {post.content[:30]}...')
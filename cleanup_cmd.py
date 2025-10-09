from brightdata_integration.models import BrightDataScrapedPost
result = BrightDataScrapedPost.objects.filter(post_id__startswith='sample_post_')
print(f'Found {result.count()} sample posts to delete')
result.delete()
print('Sample data cleanup complete')

# Check remaining data
real_posts = BrightDataScrapedPost.objects.exclude(post_id__startswith='sample_post_')
print(f'Real posts remaining: {real_posts.count()}')
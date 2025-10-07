import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from common.data_integration_service import DataIntegrationService

# Test with project ID 6
project_id = 6
data_service = DataIntegrationService(project_id=project_id)

print("=" * 80)
print("TESTING DATA INTEGRATION SERVICE")
print("=" * 80)

# Test getting company posts
print("\n### COMPANY POSTS ###")
company_posts = data_service.get_company_posts(limit=5, days_back=30)
print(f"Found {len(company_posts)} company posts")
for i, post in enumerate(company_posts[:3], 1):
    print(f"\n{i}. {post['platform'].upper()} - @{post['user']}")
    print(f"   Source Type: {post['source_type']}")
    print(f"   Source Folder: {post['source_folder']}")
    print(f"   Likes: {post['likes']}, Comments: {post['comments']}")
    print(f"   Content: {post['content'][:100]}...")

# Test getting competitor posts
print("\n\n### COMPETITOR POSTS ###")
competitor_posts = data_service.get_competitor_posts(limit=5, days_back=30)
print(f"Found {len(competitor_posts)} competitor posts")
for i, post in enumerate(competitor_posts[:3], 1):
    print(f"\n{i}. {post['platform'].upper()} - @{post['user']}")
    print(f"   Source Type: {post['source_type']}")
    print(f"   Source Folder: {post['source_folder']}")
    print(f"   Likes: {post['likes']}, Comments: {post['comments']}")
    print(f"   Content: {post['content'][:100]}...")

# Test engagement metrics
print("\n\n### ENGAGEMENT METRICS ###")
company_metrics = data_service.get_engagement_metrics(days_back=30, source_type='company')
competitor_metrics = data_service.get_engagement_metrics(days_back=30, source_type='competitor')

print("\nCOMPANY METRICS:")
print(f"  Total Posts: {company_metrics.get('total_posts', 0)}")
print(f"  Total Likes: {company_metrics.get('total_likes', 0)}")
print(f"  Total Comments: {company_metrics.get('total_comments', 0)}")
print(f"  Engagement Rate: {company_metrics.get('engagement_rate', 0):.2f}%")

print("\nCOMPETITOR METRICS:")
print(f"  Total Posts: {competitor_metrics.get('total_posts', 0)}")
print(f"  Total Likes: {competitor_metrics.get('total_likes', 0)}")
print(f"  Total Comments: {competitor_metrics.get('total_comments', 0)}")
print(f"  Engagement Rate: {competitor_metrics.get('engagement_rate', 0):.2f}%")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

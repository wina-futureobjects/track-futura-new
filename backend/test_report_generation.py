#!/usr/bin/env python
"""Test report generation with real scraped data"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import ReportTemplate, GeneratedReport
from common.real_data_service import RealDataService

# Test 1: Check if we can fetch real data
print("=" * 80)
print("TEST 1: Fetching real scraped data")
print("=" * 80)

service = RealDataService(batch_job_ids=[13])
posts = service.get_scraped_posts(limit=10)

print(f"\nFetched {len(posts)} posts")
if posts:
    print(f"\nSample post:")
    print(f"  User: {posts[0]['user']}")
    print(f"  Content: {posts[0]['content'][:100]}...")
    print(f"  Likes: {posts[0]['likes']}")
    print(f"  Comments: {posts[0]['comments']}")
    print(f"  Views: {posts[0]['views']}")

# Test 2: Get engagement metrics
print("\n" + "=" * 80)
print("TEST 2: Calculating engagement metrics from real data")
print("=" * 80)

metrics = service.get_real_engagement_metrics()
print(f"\nEngagement Metrics:")
print(f"  Total Posts: {metrics.get('total_posts', 0)}")
print(f"  Total Likes: {metrics.get('total_likes', 0)}")
print(f"  Total Comments: {metrics.get('total_comments', 0)}")
print(f"  Total Views: {metrics.get('total_views', 0)}")
print(f"  Engagement Rate: {metrics.get('engagement_rate', 0)}%")
print(f"  Avg Likes per Post: {metrics.get('avg_likes_per_post', 0)}")

# Test 3: Test report generation endpoint
print("\n" + "=" * 80)
print("TEST 3: Simulating report generation")
print("=" * 80)

# Get engagement template
template = ReportTemplate.objects.filter(template_type='engagement_metrics').first()
if template:
    print(f"\nUsing template: {template.name}")

    # Create a test report
    report = GeneratedReport.objects.create(
        title="Test Report - Real Data",
        template=template,
        configuration={'batch_job_ids': [13]},
        status='processing'
    )

    print(f"Created report ID: {report.id}")

    # Process the report
    from reports.views import GeneratedReportViewSet
    viewset = GeneratedReportViewSet()
    result = viewset._process_engagement_metrics_ONLY_REAL_DATA(report, project_id=1)

    print(f"\nReport processing result:")
    print(f"  Data source count: {result.get('data_source_count', 0)}")
    print(f"  Total posts: {result.get('total_posts', 0)}")
    print(f"  Engagement rate: {result.get('engagement_rate', 0)}%")

    if result.get('insights'):
        print(f"\n  Insights:")
        for insight in result.get('insights', [])[:3]:
            print(f"    - {insight}")

    # Mark report as completed
    report.status = 'completed'
    report.results = result
    report.save()

    print(f"\n✅ Report generated successfully!")
    print(f"   View at: /report/generated/{report.id}")
else:
    print("❌ No engagement metrics template found")

print("\n" + "=" * 80)
print("TESTS COMPLETED")
print("=" * 80)
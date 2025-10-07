#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct Database Test for Sentiment Analysis
Uses direct database queries instead of HTTP requests
"""
import os
import sys
import django
import json
import time

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import ReportTemplate, GeneratedReport
from instagram_data.models import InstagramPost, Folder
from users.models import Project
from common.sentiment_analysis_service import sentiment_service
from django.utils import timezone

def test_sentiment_direct():
    print("=" * 80)
    print("SENTIMENT ANALYSIS REPORT TEST (Direct Database)")
    print("=" * 80)

    # Step 1: Get project
    print("\n1. Getting test project...")
    project = Project.objects.first()
    if not project:
        print("   ❌ No project found")
        return False
    print(f"   ✅ Using project ID: {project.id}")

    # Step 2: Get data directly from database
    print("\n2. Fetching Instagram posts from database...")
    folders_with_posts = Folder.objects.filter(posts__isnull=False).distinct()[:5]

    all_posts = []
    for folder in folders_with_posts:
        posts = folder.posts.all()
        print(f"   📁 Folder: {folder.name} ({posts.count()} posts)")
        all_posts.extend(posts)

    if not all_posts:
        print("   ❌ No posts found in database")
        return False

    print(f"   ✅ Total posts loaded: {len(all_posts)}")

    # Step 3: Prepare sentiment data
    print("\n3. Preparing sentiment analysis data...")
    comments_data = []
    for post in all_posts[:50]:  # Limit to 50 for testing
        if post.description:
            comments_data.append({
                'comment': post.description,
                'comment_id': f"post_{post.id}",
                'platform': 'instagram',
                'comment_user': post.user_posted or 'unknown',
                'likes': post.likes or 0
            })

    print(f"   ✅ Prepared {len(comments_data)} posts for analysis")

    # Step 4: Perform sentiment analysis
    print("\n4. Performing sentiment analysis...")
    start_time = time.time()

    try:
        sentiment_results = sentiment_service.analyze_comment_sentiment(comments_data)
        processing_time = time.time() - start_time

        print(f"   ✅ Analysis completed in {processing_time:.2f} seconds")
        print(f"   💭 Overall Sentiment: {sentiment_results.get('overall_sentiment', 'unknown').upper()}")

        # Display sentiment breakdown
        sentiment_breakdown = sentiment_results.get('sentiment_breakdown', {})
        print(f"\n   Sentiment Breakdown:")
        print(f"      ✅ Positive: {sentiment_breakdown.get('positive', 0)}")
        print(f"      ➖ Neutral: {sentiment_breakdown.get('neutral', 0)}")
        print(f"      ❌ Negative: {sentiment_breakdown.get('negative', 0)}")

        # Display percentages
        sentiment_percentages = sentiment_results.get('sentiment_percentages', {})
        if sentiment_percentages:
            print(f"\n   Sentiment Percentages:")
            print(f"      ✅ Positive: {sentiment_percentages.get('positive', 0):.1f}%")
            print(f"      ➖ Neutral: {sentiment_percentages.get('neutral', 0):.1f}%")
            print(f"      ❌ Negative: {sentiment_percentages.get('negative', 0):.1f}%")

        # Display insights
        insights = sentiment_results.get('insights', [])
        if insights:
            print(f"\n   💡 Insights:")
            for insight in insights[:5]:
                print(f"      • {insight}")

        # Step 5: Build visualization data
        print(f"\n5. Building visualization data...")

        # Pie chart data
        pie_chart = {
            'type': 'pie',
            'title': 'Sentiment Distribution',
            'data': {
                'labels': ['Positive', 'Neutral', 'Negative'],
                'values': [
                    sentiment_breakdown.get('positive', 0),
                    sentiment_breakdown.get('neutral', 0),
                    sentiment_breakdown.get('negative', 0)
                ],
                'colors': ['#4CAF50', '#FFC107', '#F44336']
            }
        }

        # Bar chart data
        bar_chart = {
            'type': 'bar',
            'title': 'Sentiment by Platform',
            'data': {
                'labels': ['Instagram'],
                'datasets': [
                    {
                        'label': 'Positive',
                        'data': [sentiment_breakdown.get('positive', 0)],
                        'backgroundColor': '#4CAF50'
                    },
                    {
                        'label': 'Neutral',
                        'data': [sentiment_breakdown.get('neutral', 0)],
                        'backgroundColor': '#FFC107'
                    },
                    {
                        'label': 'Negative',
                        'data': [sentiment_breakdown.get('negative', 0)],
                        'backgroundColor': '#F44336'
                    }
                ]
            }
        }

        visualizations = {
            'sentiment_distribution': pie_chart,
            'platform_sentiment': bar_chart
        }

        print(f"   ✅ Created {len(visualizations)} visualizations:")
        for viz_name, viz_data in visualizations.items():
            print(f"      📊 {viz_name}: {viz_data['type']} chart - '{viz_data['title']}'")

        # Step 6: Create complete report structure
        print(f"\n6. Creating report structure...")

        report_data = {
            'report_type': 'sentiment_analysis',
            'title': 'Sentiment Analysis Report',
            'summary': f"Analyzed {len(comments_data)} posts from Instagram",
            'overall_sentiment': sentiment_results.get('overall_sentiment', 'neutral'),
            'sentiment_breakdown': sentiment_breakdown,
            'sentiment_percentages': sentiment_percentages,
            'insights': insights,
            'visualizations': visualizations,
            'data_source_count': len(comments_data),
            'processing_time': round(processing_time, 2),
            'generated_at': timezone.now().isoformat()
        }

        # Step 7: Test JSON serialization
        print(f"\n7. Testing JSON serialization...")
        try:
            json_data = json.dumps(report_data, indent=2)
            print(f"   ✅ Report is JSON serializable ({len(json_data)} characters)")
        except Exception as e:
            print(f"   ❌ JSON serialization failed: {e}")
            return False

        # Step 8: Save to database
        print(f"\n8. Saving report to database...")

        template, created = ReportTemplate.objects.get_or_create(
            template_type='sentiment_analysis',
            defaults={
                'name': 'Sentiment Analysis',
                'description': 'Analyze the sentiment of comments and feedback',
                'icon': 'psychology',
                'color': '#9C27B0'
            }
        )

        report = GeneratedReport.objects.create(
            title="Test Sentiment Analysis - Direct DB",
            template=template,
            status='completed',
            results=report_data,
            data_source_count=len(comments_data),
            configuration={'folder_ids': [f.id for f in folders_with_posts]}
        )

        print(f"   ✅ Report saved with ID: {report.id}")
        print(f"   🔗 View at: http://localhost:5173/organizations/1/projects/{project.id}/reports/generated/{report.id}")

        return True

    except Exception as e:
        print(f"   ❌ Error during sentiment analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sentiment_direct()

    print("\n" + "=" * 80)
    if success:
        print("✅ SENTIMENT ANALYSIS TEST PASSED")
        print("   Report generated with visualizations ready for frontend!")
    else:
        print("❌ SENTIMENT ANALYSIS TEST FAILED")
    print("=" * 80)

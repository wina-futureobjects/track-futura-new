#!/usr/bin/env python
"""
Create test reports for demonstration
"""
import os
import sys
import django

# Add backend to the path
sys.path.append('backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import ReportTemplate, GeneratedReport
from django.contrib.auth.models import User
import json
from datetime import datetime

def create_test_reports():
    print("🎯 CREATING TEST REPORTS FOR AUTHENTICATION TESTING")
    print("=" * 60)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@trackfutura.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Create report templates if they don't exist
    templates_data = [
        {
            'name': 'Sentiment Analysis Report',
            'template_type': 'sentiment_analysis',
            'description': 'Analyze sentiment trends across social media posts',
            'is_active': True
        },
        {
            'name': 'Engagement Metrics Report',
            'template_type': 'engagement_metrics',
            'description': 'Track engagement rates and metrics',
            'is_active': True
        },
        {
            'name': 'Content Analysis Report', 
            'template_type': 'content_analysis',
            'description': 'Analyze content patterns and hashtags',
            'is_active': True
        }
    ]
    
    templates = {}
    for template_data in templates_data:
        template, created = ReportTemplate.objects.get_or_create(
            template_type=template_data['template_type'],
            defaults=template_data
        )
        templates[template_data['template_type']] = template
        print(f"   {'✅ Created' if created else '♻️  Found'} template: {template.name}")
    
    # Create sample generated reports
    sample_reports = [
        {
            'template': templates['sentiment_analysis'],
            'title': 'Nike Brand Sentiment Analysis - October 2025',
            'status': 'completed',
            'results': {
                'sentiment_distribution': {
                    'positive': 65,
                    'neutral': 25,
                    'negative': 10
                },
                'total_posts': 1250,
                'sentiment_score': 7.8,
                'key_insights': [
                    'Strong positive sentiment around new product launches',
                    'Customer satisfaction high with recent campaigns',
                    'Minor concerns about pricing in some segments'
                ]
            }
        },
        {
            'template': templates['engagement_metrics'],
            'title': 'Social Media Engagement Report - October 2025',
            'status': 'completed',
            'results': {
                'engagement_rate': 4.2,
                'total_interactions': 15420,
                'average_likes': 95,
                'average_comments': 12, 
                'average_shares': 8,
                'top_performing_posts': [
                    {'post_id': 1, 'engagement': 450},
                    {'post_id': 2, 'engagement': 380},
                    {'post_id': 3, 'engagement': 320}
                ]
            }
        },
        {
            'template': templates['content_analysis'],
            'title': 'Content Performance Analysis - October 2025',
            'status': 'completed',
            'results': {
                'top_hashtags': ['#nike', '#justdoit', '#fitness', '#sports'],
                'content_types': {
                    'video': 45,
                    'image': 40,
                    'text': 15
                },
                'optimal_posting_times': ['10:00 AM', '2:00 PM', '7:00 PM'],
                'content_engagement_by_type': {
                    'video': 5.2,
                    'image': 3.8,
                    'text': 2.1
                }
            }
        }
    ]
    
    for i, report_data in enumerate(sample_reports):
        report, created = GeneratedReport.objects.get_or_create(
            template=report_data['template'],
            title=report_data['title'],
            defaults={
                'status': report_data['status'],
                'results': report_data['results'],
                'user': user,
                'completed_at': datetime.now()
            }
        )
        print(f"   {'✅ Created' if created else '♻️  Found'} report ID {report.id}: {report.title}")
    
    print(f"\n🎉 REPORTS READY FOR TESTING!")
    print(f"📍 Test endpoints:")
    for report in GeneratedReport.objects.all()[:3]:
        template_type = report.template.template_type.replace('_', '-')
        print(f"   📊 http://localhost:8080/api/reports/{template_type}/{report.id}/")
    
    print(f"\n🔑 Use these tokens:")
    print(f"   Authorization: Token e242daf2ea05576f08fb8d808aba529b0c7ffbab")
    print(f"   Authorization: Token temp-token-for-testing")

if __name__ == '__main__':
    create_test_reports()
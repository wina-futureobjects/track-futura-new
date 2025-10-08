#!/usr/bin/env python
"""
Populate report templates in production via API
"""
import requests
import json

def populate_production_templates():
    print("🔧 POPULATING PRODUCTION REPORT TEMPLATES")
    print("="*60)
    
    # Template data that should exist
    templates_data = [
        {
            'name': 'Sentiment Analysis',
            'description': 'Analyze the sentiment of comments and feedback to understand public opinion about your brand, products, or campaigns. Get insights into positive, negative, and neutral responses.',
            'template_type': 'sentiment_analysis',
            'icon': 'psychology',
            'color': '#4caf50',
            'estimated_time': '2-5 minutes',
            'required_data_types': ['comments', 'reviews'],
            'features': [
                'Positive/Negative/Neutral classification',
                'Confidence scores for each sentiment',
                'Trending keywords analysis',
                'Actionable insights and recommendations',
                'Export to CSV for further analysis'
            ]
        },
        {
            'name': 'Engagement Metrics',
            'description': 'Track and analyze engagement rates across your social media posts. Understand what content resonates most with your audience.',
            'template_type': 'engagement_metrics',
            'icon': 'trending_up',
            'color': '#2196f3',
            'estimated_time': '1-3 minutes',
            'required_data_types': ['posts'],
            'features': [
                'Likes, comments, shares analysis',
                'Engagement rate calculations',
                'Best performing content identification',
                'Optimal posting times',
                'Audience interaction patterns'
            ]
        },
        {
            'name': 'Content Analysis',
            'description': 'Deep dive into your content performance and discover what type of content drives the most engagement.',
            'template_type': 'content_analysis',
            'icon': 'description',
            'color': '#ff9800',
            'estimated_time': '3-7 minutes',
            'required_data_types': ['posts', 'comments'],
            'features': [
                'Content type performance comparison',
                'Hashtag effectiveness analysis',
                'Caption length optimization',
                'Media format insights',
                'Content themes identification'
            ]
        },
        {
            'name': 'Trend Analysis',
            'description': 'Identify trending topics, hashtags, and content themes in your industry or niche.',
            'template_type': 'trend_analysis',
            'icon': 'timeline',
            'color': '#9c27b0',
            'estimated_time': '5-10 minutes',
            'required_data_types': ['posts', 'hashtags'],
            'features': [
                'Trending hashtags identification',
                'Content trend patterns',
                'Seasonal content insights',
                'Competitor trend comparison',
                'Future trend predictions'
            ]
        },
        {
            'name': 'Competitive Analysis',
            'description': 'Compare your performance against competitors and discover opportunities for growth.',
            'template_type': 'competitive_analysis',
            'icon': 'compare_arrows',
            'color': '#f44336',
            'estimated_time': '7-12 minutes',
            'required_data_types': ['posts', 'profiles'],
            'features': [
                'Head-to-head performance comparison',
                'Competitor strategy insights',
                'Market share analysis',
                'Growth opportunity identification',
                'Benchmarking reports'
            ]
        },
        {
            'name': 'User Behavior Analysis',
            'description': 'Understand how users interact with your content and what drives them to engage.',
            'template_type': 'user_behavior',
            'icon': 'people',
            'color': '#607d8b',
            'estimated_time': '4-8 minutes',
            'required_data_types': ['interactions', 'comments'],
            'features': [
                'User engagement patterns',
                'Peak activity times',
                'User journey mapping',
                'Conversion funnel analysis',
                'Audience segmentation'
            ]
        }
    ]
    
    base_url = 'https://trackfutura.futureobjects.io/api'
    
    # Login first
    auth_response = requests.post(
        f'{base_url}/users/login/',
        json={'username': 'superadmin', 'password': 'admin123'},
        timeout=30
    )
    
    if auth_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = auth_response.json().get('access_token', auth_response.json().get('token'))
    headers = {'Authorization': f'Token {token}'}
    print("✅ Login successful")
    
    # Try to create templates via Django admin API or direct database access
    print("🔧 Creating templates...")
    
    # Since we can't directly create via REST API (no POST endpoint for templates),
    # let's create a management command to run in production
    print("⚠️  Templates need to be created via Django management command")
    print("   Since there's no REST API for creating templates")
    
    return False

if __name__ == '__main__':
    populate_production_templates()
    
    print("\n🚀 NEXT STEPS:")
    print("   1. SSH into production and run:")
    print("      python manage.py populate_report_templates")
    print("   2. Or manually create via Django admin")
    print("   3. Or deploy a migration that creates the templates")
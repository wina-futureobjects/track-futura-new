#!/usr/bin/env python
"""
Create a specific sentiment analysis report with ID 1 for the frontend
"""
import requests
import json

BASE_URL = "http://localhost:8080/api"
TOKEN = "e242daf2ea05576f08fb8d808aba529b0c7ffbab"

headers = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
}

def create_report_id_1():
    print("🎯 CREATING SENTIMENT ANALYSIS REPORT WITH ID 1")
    print("=" * 60)
    
    # First check if template exists
    response = requests.get(f"{BASE_URL}/reports/templates/", headers=headers)
    print(f"Templates status: {response.status_code}")
    
    if response.status_code == 200:
        templates = response.json()
        sentiment_template = None
        for template in templates:
            if template.get('template_type') == 'sentiment_analysis':
                sentiment_template = template
                break
        
        if sentiment_template:
            print(f"✅ Found sentiment analysis template: {sentiment_template['name']}")
            
            # Create report data that should result in ID 1
            report_data = {
                'title': 'Nike Brand Sentiment Analysis - Report #1',
                'template': sentiment_template['id'],
                'configuration': {
                    'brand': 'Nike',
                    'time_period': '30_days',
                    'platforms': ['instagram', 'facebook']
                },
                'results': {
                    'sentiment_distribution': {
                        'positive': 68,
                        'neutral': 22,
                        'negative': 10
                    },
                    'total_posts': 1500,
                    'sentiment_score': 8.2,
                    'key_insights': [
                        'Overwhelmingly positive response to new Air Max campaign',
                        'Strong brand loyalty reflected in user comments',
                        'Sustainability initiatives driving positive sentiment'
                    ],
                    'trends': {
                        'positive_growth': '+15% vs last month',
                        'engagement_rate': '4.8%',
                        'reach': '2.5M users'
                    }
                },
                'status': 'completed'
            }
            
            # Try to create the report
            response = requests.post(f"{BASE_URL}/reports/generated/", 
                                   headers=headers, 
                                   json=report_data)
            
            print(f"Create report status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                created_report = response.json()
                print(f"✅ Created report with ID: {created_report.get('id')}")
                
                # Test the specific endpoint
                test_id = created_report.get('id', 1)
                test_response = requests.get(f"{BASE_URL}/reports/sentiment-analysis/{test_id}/", headers=headers)
                print(f"✅ Test endpoint status: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    print("🎉 SENTIMENT ANALYSIS ENDPOINT WORKING!")
                    data = test_response.json()
                    print(f"   📊 Title: {data.get('title')}")
                    print(f"   📈 Status: {data.get('status')}")
                    if 'results' in data and 'sentiment_distribution' in data['results']:
                        sentiment = data['results']['sentiment_distribution']
                        print(f"   😊 Positive: {sentiment.get('positive', 0)}%")
                        print(f"   😐 Neutral: {sentiment.get('neutral', 0)}%")
                        print(f"   😟 Negative: {sentiment.get('negative', 0)}%")
                else:
                    print(f"❌ Test failed: {test_response.text}")
            else:
                print(f"❌ Failed to create report: {response.text}")
        else:
            print("❌ No sentiment analysis template found")
    else:
        print(f"❌ Failed to fetch templates: {response.text}")

    # Also test if ID 1 now exists
    print(f"\n🔍 Testing /api/reports/sentiment-analysis/1/")
    response = requests.get(f"{BASE_URL}/reports/sentiment-analysis/1/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("🎉 SUCCESS! Report ID 1 is now working!")
        data = response.json()
        print(f"Title: {data.get('title')}")
    else:
        print(f"Still failing: {response.text}")

if __name__ == '__main__':
    create_report_id_1()
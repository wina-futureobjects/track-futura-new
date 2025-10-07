#!/usr/bin/env python3
"""
Test OpenAI integration and sentiment analysis
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_openai_integration():
    """Test OpenAI API integration"""
    print("Testing OpenAI Integration...")
    
    # Test environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY', '')
    print(f"OpenAI API Key configured: {'Yes' if openai_key.startswith('sk-') else 'No'}")
    print(f"Key length: {len(openai_key)}")
    
    # Test OpenAI service
    try:
        from chat.openai_service import openai_service
        print("OpenAI service imported successfully")
        
        # Test basic response generation
        test_response = openai_service.generate_response(
            "Hello, can you analyze my social media sentiment?",
            project_id=1
        )
        print(f"AI Response: {test_response[:200]}...")
        
    except Exception as e:
        print(f"Error testing OpenAI service: {e}")
    
    # Test sentiment analysis service
    try:
        from common.sentiment_analysis_service import sentiment_service
        print("Sentiment analysis service imported successfully")
        
        # Test with sample comments
        sample_comments = [
            {'comment': 'I love this product!', 'platform': 'instagram'},
            {'comment': 'Not impressed with the quality', 'platform': 'facebook'},
            {'comment': 'Amazing customer service', 'platform': 'linkedin'}
        ]
        
        sentiment_result = sentiment_service.analyze_comment_sentiment(sample_comments)
        print(f"Sentiment Analysis Result: {sentiment_result.get('overall_sentiment', 'unknown')}")
        print(f"Sentiment Breakdown: {sentiment_result.get('sentiment_breakdown', {})}")
        
    except Exception as e:
        print(f"Error testing sentiment analysis: {e}")

def test_report_generation():
    """Test AI-powered report generation"""
    print("\nTesting AI Report Generation...")
    
    try:
        from reports.openai_service import report_openai_service
        print("Report OpenAI service imported successfully")
        
        # Test sentiment analysis report
        sentiment_report = report_openai_service.generate_sentiment_analysis_report(project_id=1)
        print(f"Sentiment Report Generated: {sentiment_report.get('data_source', 'unknown')}")
        print(f"Analysis Method: {sentiment_report.get('analysis_method', 'unknown')}")
        
        # Test engagement metrics report
        engagement_report = report_openai_service.generate_engagement_metrics_report(project_id=1)
        print(f"Engagement Report Generated: {engagement_report.get('data_source_count', 0)} data points")
        
    except Exception as e:
        print(f"Error testing report generation: {e}")

def test_data_integration():
    """Test data integration with real project data"""
    print("\nTesting Data Integration...")
    
    try:
        from common.data_integration_service import DataIntegrationService
        
        # Test with project ID 1
        data_service = DataIntegrationService(project_id=1)
        
        # Get sample data
        posts = data_service.get_all_posts(limit=5)
        comments = data_service.get_all_comments(limit=10)
        metrics = data_service.get_engagement_metrics()
        
        print(f"Posts found: {len(posts)}")
        print(f"Comments found: {len(comments)}")
        print(f"Total engagement: Likes={metrics.get('total_likes', 0)}, Comments={metrics.get('total_comments', 0)}")
        
        if posts:
            print(f"Sample post platform: {posts[0].get('platform', 'unknown')}")
        
        if comments:
            print(f"Sample comment: {comments[0].get('comment', 'No content')[:50]}...")
            
    except Exception as e:
        print(f"Error testing data integration: {e}")

if __name__ == "__main__":
    print("=== Track Futura AI Integration Test ===")
    test_openai_integration()
    test_report_generation()
    test_data_integration()
    print("\n=== Test Complete ===")
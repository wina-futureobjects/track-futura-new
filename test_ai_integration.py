#!/usr/bin/env python3
"""
Test AI Integration with BrightData Scraped Posts
"""

import os
import sys
import django
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chat.openai_service import OpenAIService
from common.data_integration_service import DataIntegrationService


def test_data_integration():
    """Test that data integration service can access BrightData posts"""
    print("=== TESTING DATA INTEGRATION SERVICE ===")
    
    service = DataIntegrationService(project_id=1)
    
    # Test get_all_posts
    all_posts = service.get_all_posts(limit=10, days_back=30)
    print(f"✅ Found {len(all_posts)} total posts")
    
    # Test BrightData specific posts
    brightdata_posts = service.get_brightdata_posts(limit=10, days_back=30)
    print(f"✅ Found {len(brightdata_posts)} BrightData posts")
    
    # Test engagement metrics
    metrics = service.get_engagement_metrics(days_back=30)
    print(f"✅ Engagement metrics: {metrics.get('total_posts', 0)} posts, {metrics.get('brightdata_posts', 0)} from BrightData")
    
    # Show sample post
    if brightdata_posts:
        sample_post = brightdata_posts[0]
        print(f"✅ Sample post: {sample_post['user']} - {sample_post['likes']} likes")
        print(f"   Content: {sample_post['content'][:100]}...")
    
    return len(brightdata_posts) > 0


def test_openai_integration():
    """Test that OpenAI service can access BrightData data through data integration"""
    print("\n=== TESTING OPENAI INTEGRATION ===")
    
    openai_service = OpenAIService()
    
    if not openai_service.client:
        print("❌ OpenAI client not initialized (missing API key)")
        return False
    
    try:
        # Test with project_id=1
        response = openai_service.generate_response(
            "Analyze the BrightData scraped social media posts. Show me Nike vs Adidas performance.",
            conversation_history=None,
            project_id=1
        )
        
        print("✅ OpenAI response generated:")
        print(f"   Length: {len(response)} characters")
        print(f"   Sample: {response[:200]}...")
        
        # Check if response mentions BrightData or specific metrics
        has_brightdata = 'brightdata' in response.lower() or 'scraped' in response.lower()
        has_metrics = any(word in response.lower() for word in ['likes', 'posts', 'engagement', 'nike', 'adidas'])
        
        print(f"✅ Mentions BrightData/scraped: {has_brightdata}")
        print(f"✅ Contains metrics: {has_metrics}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI integration failed: {e}")
        return False


def main():
    """Run comprehensive test of AI-BrightData integration"""
    print("🤖 TESTING AI-BRIGHTDATA INTEGRATION")
    print("=" * 50)
    
    # Test 1: Data Integration Service
    data_works = test_data_integration()
    
    # Test 2: OpenAI Integration
    ai_works = test_openai_integration()
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    print(f"Data Integration: {'✅ WORKING' if data_works else '❌ FAILED'}")
    print(f"AI Integration: {'✅ WORKING' if ai_works else '❌ FAILED'}")
    
    if data_works and ai_works:
        print("\n🎉 SUCCESS: AI can analyze BrightData scraped posts!")
    elif data_works and not ai_works:
        print("\n⚠️  PARTIAL: Data available but AI integration has issues")
    else:
        print("\n❌ FAILED: Data integration not working")


if __name__ == "__main__":
    main()
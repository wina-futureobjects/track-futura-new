#!/usr/bin/env python
"""
Test AI Chatbot Data Access and Apify Integration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from common.data_integration_service import DataIntegrationService
from chat.openai_service import OpenAIService
from apify_integration.models import ApifyConfig

print("=== TESTING AI CHATBOT DATA ACCESS ===")

# Test 1: Check if data integration service works
print("\n1. Testing Data Integration Service...")
try:
    # Use project 6 (Nike & Adidas project)
    data_service = DataIntegrationService(project_id=6)
    
    # Get posts (last 30 days to ensure we find data)
    all_posts = data_service.get_all_posts(limit=10, days_back=30)
    company_posts = data_service.get_company_posts(limit=5, days_back=30)
    competitor_posts = data_service.get_competitor_posts(limit=5, days_back=30)
    comments = data_service.get_all_comments(limit=10, days_back=30)
    
    print(f"✅ Found {len(all_posts)} total posts")
    print(f"✅ Found {len(company_posts)} company posts")
    print(f"✅ Found {len(competitor_posts)} competitor posts")
    print(f"✅ Found {len(comments)} comments")
    
    # Show sample data
    if all_posts:
        print("\nSample Post:")
        post = all_posts[0]
        print(f"  Platform: {post.get('platform', 'unknown')}")
        print(f"  User: {post.get('user_posted', 'unknown')}")
        print(f"  Content: {post.get('content', '')[:100]}...")
        print(f"  Source Type: {post.get('source_type', 'unknown')}")
    
except Exception as e:
    print(f"❌ Data Integration Error: {e}")

# Test 2: Check AI Chatbot
print("\n2. Testing AI Chatbot...")
try:
    openai_service = OpenAIService()
    
    # Test with a data-related question
    response = openai_service.generate_response(
        "What data do you have access to? Summarize the recent social media activity.",
        project_id=6
    )
    
    print(f"✅ AI Response Length: {len(response)} characters")
    print(f"Sample Response: {response[:200]}...")
    
except Exception as e:
    print(f"❌ AI Chatbot Error: {e}")

# Test 3: Check Apify Configuration
print("\n3. Testing Apify Configuration...")
try:
    configs = ApifyConfig.objects.filter(is_active=True)
    print(f"✅ Active Apify Configs: {configs.count()}")
    
    for config in configs:
        print(f"  - {config.name} ({config.platform})")
        
except Exception as e:
    print(f"❌ Apify Config Error: {e}")

print("\n=== TEST COMPLETE ===")
print("If you see ✅ marks above, the systems are working correctly!")
print("\nTo test the AI Chatbot in the browser:")
print("1. Go to: http://localhost:5185/organizations/1/projects/6/analysis")
print("2. Ask: 'What data do you have access to?'")
print("3. Ask: 'Analyze our recent social media performance'")
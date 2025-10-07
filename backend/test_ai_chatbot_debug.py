#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from common.data_integration_service import DataIntegrationService

print("=== TESTING AI CHATBOT DATA ACCESS ===")

# Test with project 6 (Track Futura) which has Nike and Adidas data
data_service = DataIntegrationService(project_id=6)

print("\n1. Testing Data Integration Service...")
all_posts = data_service.get_all_posts(limit=50, days_back=7)
company_posts = data_service.get_company_posts(limit=50, days_back=7)
competitor_posts = data_service.get_competitor_posts(limit=50, days_back=7)

print(f"✅ Found {len(all_posts)} total posts")
print(f"✅ Found {len(company_posts)} company posts")
print(f"✅ Found {len(competitor_posts)} competitor posts")

# Show sample posts with their source types
print("\nSample posts with source classification:")
for i, post in enumerate(all_posts[:5]):
    print(f"  {i+1}. User: {post['user']}, Platform: {post['platform']}, Source Type: {post['source_type']}")

print("\n2. Testing OpenAI Chatbot Service...")
try:
    from chat.openai_service import OpenAIService
    
    chatbot = OpenAIService()
    response = chatbot.generate_response(
        user_message="What data do you have access to? Tell me about Nike vs Adidas performance.",
        project_id=6
    )
    
    print(f"✅ AI Response Length: {len(response)} characters")
    print(f"Sample Response: {response[:200]}...")
    
except Exception as e:
    print(f"❌ Error testing chatbot: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DEBUGGING NIKE VS ADIDAS CLASSIFICATION ===")

# Let's check the source folder mapping
source_mapping = data_service._get_source_folder_mapping()
print(f"Source Folder Mapping: {source_mapping}")

# Check a few specific posts to see why they're not being classified correctly
from instagram_data.models import InstagramPost
from facebook_data.models import FacebookPost

# Sample Instagram posts
instagram_posts = InstagramPost.objects.filter(user_posted__icontains='adidas')[:3]
print(f"\nSample Adidas Instagram posts:")
for post in instagram_posts:
    print(f"  - User: {post.user_posted}")
    # Test the classification function directly
    from track_accounts.models import TrackSource
    
    sources = TrackSource.objects.filter(project_id=6)
    for source in sources:
        if source.instagram_link and post.user_posted:
            if post.user_posted.lower() in source.instagram_link.lower() or 'adidas' in source.instagram_link.lower():
                print(f"    → Should match source: {source.name} ({source.folder.folder_type if source.folder else 'No folder'})")

# Sample Nike posts
nike_posts = InstagramPost.objects.filter(user_posted__icontains='nike')[:3]
print(f"\nSample Nike Instagram posts:")
for post in nike_posts:
    print(f"  - User: {post.user_posted}")
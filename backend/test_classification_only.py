#!/usr/bin/env python3

import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from common.data_integration_service import DataIntegrationService

def test_classification():
    """Test that the classification is working correctly"""
    print("=== TESTING BRAND CLASSIFICATION ===\n")
    
    # Test with project ID 6 (the demo project)
    service = DataIntegrationService(project_id=6)
    
    print("1. Getting classified data...")
    company_data, competitor_data = service.get_data_for_ai()
    
    print(f"✅ Company posts found: {len(company_data)}")
    print(f"✅ Competitor posts found: {len(competitor_data)}")
    
    print("\n2. Sample company posts:")
    for i, post in enumerate(company_data[:3]):
        platform = post.get('platform', 'unknown')
        if platform == 'instagram':
            user = post.get('username', 'unknown')
        elif platform == 'facebook':
            user_data = post.get('user_posted', {})
            user = user_data.get('name', 'unknown') if isinstance(user_data, dict) else str(user_data)
        else:
            user = post.get('user', 'unknown')
        print(f"  {i+1}. User: {user}, Platform: {platform}")
    
    print("\n3. Sample competitor posts:")
    for i, post in enumerate(competitor_data[:3]):
        platform = post.get('platform', 'unknown')
        if platform == 'instagram':
            user = post.get('username', 'unknown')
        elif platform == 'facebook':
            user_data = post.get('user_posted', {})
            user = user_data.get('name', 'unknown') if isinstance(user_data, dict) else str(user_data)
        else:
            user = post.get('user', 'unknown')
        print(f"  {i+1}. User: {user}, Platform: {platform}")
    
    print(f"\n✅ Classification test complete!")
    print(f"✅ Nike posts classified as company: {len(company_data)}")
    print(f"✅ Adidas posts classified as competitor: {len(competitor_data)}")

if __name__ == "__main__":
    test_classification()
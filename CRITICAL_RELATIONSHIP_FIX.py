"""
🚨 CRITICAL RELATIONSHIP FIX
Fix the BrightDataScrapedPost model constraint issue that prevents webhook data from saving
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
import logging

logger = logging.getLogger(__name__)

def fix_scraped_post_relationship():
    """Fix the BrightDataScrapedPost model relationship constraint"""
    
    print("🚨 CRITICAL FIX: Making scraper_request field optional in BrightDataScrapedPost")
    
    try:
        # Create the migration
        print("📝 Creating Django migration...")
        execute_from_command_line(['manage.py', 'makemigrations', 'brightdata_integration'])
        
        # Apply the migration
        print("🔧 Applying migration to database...")
        execute_from_command_line(['manage.py', 'migrate', 'brightdata_integration'])
        
        print("✅ Migration completed successfully!")
        
        # Test the fix by creating a test post
        print("🧪 Testing the fix...")
        
        from brightdata_integration.models import BrightDataScrapedPost
        from django.utils import timezone
        
        test_post = BrightDataScrapedPost.objects.create(
            post_id=f"relationship_fix_test_{int(timezone.now().timestamp())}",
            folder_id=216,  # Using known folder
            platform='instagram',
            user_posted='test_user',
            content='Test post to verify relationship fix',
            likes=100,
            num_comments=5,
            date_posted=timezone.now(),
            # Notice: NO scraper_request provided - this should work now
        )
        
        print(f"✅ Test post created successfully: {test_post.post_id}")
        print(f"   - ID: {test_post.id}")
        print(f"   - Folder ID: {test_post.folder_id}")
        print(f"   - Scraper Request: {test_post.scraper_request}")
        
        # Verify it exists in the database
        retrieved_post = BrightDataScrapedPost.objects.get(id=test_post.id)
        print(f"✅ Post retrieved from database: {retrieved_post.post_id}")
        
        print("🎉 RELATIONSHIP FIX SUCCESSFUL!")
        print("   Webhook processing should now work correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during relationship fix: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = fix_scraped_post_relationship()
    if success:
        print("\n🚀 RELATIONSHIP FIX COMPLETE - Ready to test webhook processing!")
    else:
        print("\n💥 RELATIONSHIP FIX FAILED - Manual intervention required")
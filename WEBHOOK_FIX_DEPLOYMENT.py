#!/usr/bin/env python3
"""
🎯 WEBHOOK PROCESSING FIX
=========================
This creates the exact code changes needed to fix the production webhook issue.
"""

webhook_fix_patch = '''
# PRODUCTION FIX FOR: backend/brightdata_integration/views.py
# ADD THIS FUNCTION AFTER LINE 300 (after brightdata_webhook function)

def _create_brightdata_scraped_post(item_data, platform, folder_id=None, scraper_request=None):
    """
    PRODUCTION FIX: Create BrightDataScrapedPost records from webhook data
    This is the missing piece that links posts to job folders!
    """
    try:
        from .models import BrightDataScrapedPost
        from django.utils import timezone
        
        # Extract folder_id from various sources
        if not folder_id:
            folder_id = item_data.get('folder_id')
        if not folder_id and scraper_request:
            folder_id = scraper_request.folder_id
            
        # Create the BrightDataScrapedPost record
        post_data = {
            'post_id': item_data.get('post_id') or item_data.get('id') or f"webhook_{int(time.time())}",
            'url': item_data.get('url', ''),
            'user_posted': item_data.get('user_posted') or item_data.get('username') or item_data.get('user_username', ''),
            'content': item_data.get('content') or item_data.get('caption') or item_data.get('post_text', ''),
            'platform': platform,
            'likes': item_data.get('likes') or item_data.get('likes_count') or item_data.get('num_likes', 0),
            'num_comments': item_data.get('num_comments') or item_data.get('comments_count', 0),
            'shares': item_data.get('shares') or item_data.get('num_shares', 0),
            'media_type': item_data.get('media_type', 'unknown'),
            'media_url': item_data.get('media_url', ''),
            'is_verified': item_data.get('is_verified', False),
            'hashtags': item_data.get('hashtags', []),
            'mentions': item_data.get('mentions', []),
            'location': item_data.get('location', ''),
            'description': item_data.get('description', ''),
            'folder_id': folder_id,
            'scraper_request': scraper_request,
            'date_posted': timezone.now()
        }
        
        # Get or create the scraped post
        scraped_post, created = BrightDataScrapedPost.objects.get_or_create(
            post_id=post_data['post_id'],
            defaults=post_data
        )
        
        if created:
            logger.info(f"✅ Created BrightDataScrapedPost: {scraped_post.post_id} → Folder {folder_id}")
        else:
            # Update folder_id if it wasn't set before
            if not scraped_post.folder_id and folder_id:
                scraped_post.folder_id = folder_id
                scraped_post.save()
                logger.info(f"🔗 Updated folder link: {scraped_post.post_id} → Folder {folder_id}")
        
        return scraped_post
        
    except Exception as e:
        logger.error(f"❌ Error creating BrightDataScrapedPost: {e}")
        return None


# MODIFY THE _process_brightdata_results FUNCTION (around line 270)
# REPLACE THE EXISTING FUNCTION WITH THIS:

def _process_brightdata_results(data: list, platform: str, scraper_request=None):
    """
    Process BrightData results and store them in appropriate models
    PRODUCTION FIX: Now creates BrightDataScrapedPost records for job folder linking
    """
    try:
        logger.info(f"Processing {len(data)} items for platform {platform}")
        
        # CRITICAL FIX: Process each item and create BrightDataScrapedPost records
        processed_count = 0
        
        for item in data:
            # Extract folder_id from the webhook data
            folder_id = item.get('folder_id')
            if not folder_id and scraper_request:
                folder_id = scraper_request.folder_id
            
            # CREATE THE MISSING BrightDataScrapedPost RECORD
            scraped_post = _create_brightdata_scraped_post(item, platform, folder_id, scraper_request)
            
            if scraped_post:
                processed_count += 1
        
        logger.info(f"✅ Created {processed_count} BrightDataScrapedPost records with folder links")
        
        # Also process results based on platform (keep existing logic)
        if platform == 'instagram':
            _process_instagram_results(scraper_request, data)
        elif platform == 'facebook':
            _process_facebook_results(scraper_request, data)
        elif platform == 'tiktok':
            _process_tiktok_results(scraper_request, data)
        elif platform == 'linkedin':
            _process_linkedin_results(scraper_request, data)
        
        return True
            
    except Exception as e:
        logger.error(f"Error processing BrightData results: {str(e)}")
        return False
'''

git_deploy_commands = '''
# DEPLOYMENT COMMANDS (Run these in the backend directory):

# 1. Add the changes
git add .
git commit -m "Fix webhook processing - add BrightDataScrapedPost creation for job folder linking"

# 2. Push to production
git push

# 3. If using Upsun, trigger deployment
upsun environment:deploy main
'''

manual_fix_steps = '''
MANUAL FIX STEPS:
================

1. Open: backend/brightdata_integration/views.py

2. Add the _create_brightdata_scraped_post function after the brightdata_webhook function (around line 300)

3. Replace the _process_brightdata_results function (around line 270) with the fixed version

4. Save the file

5. Deploy to production using git push

6. Test by sending a webhook post with folder_id

The key issue: Webhook was processing posts but not creating BrightDataScrapedPost records.
The job-results API looks for BrightDataScrapedPost records to display data.
'''

def create_deployment_script():
    """Create a deployment script"""
    
    deployment_script = f'''#!/usr/bin/env python3
"""
DEPLOYMENT SCRIPT - Apply webhook fix to production
"""

import subprocess
import os

def deploy_webhook_fix():
    print("🚀 DEPLOYING WEBHOOK FIX TO PRODUCTION")
    print("=" * 50)
    
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Add and commit changes
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Fix webhook processing - add BrightDataScrapedPost creation'], check=True)
        
        # Push to production
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Code deployed successfully!")
        print("🔄 Production should update automatically")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {{e}}")
    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    deploy_webhook_fix()
'''
    
    return deployment_script

def main():
    print("🎯 WEBHOOK PROCESSING FIX")
    print("=" * 50)
    
    print("📋 ISSUE IDENTIFIED:")
    print("   • Webhook receives posts successfully")
    print("   • Platform models (InstagramPost, FacebookPost) are created")
    print("   • BrightDataScrapedPost records are NOT created")  
    print("   • job-results API looks for BrightDataScrapedPost records")
    print("   • Result: Posts exist but aren't linked to job folders")
    
    print(f"\n🔧 SOLUTION:")
    print("   • Add _create_brightdata_scraped_post function")
    print("   • Modify _process_brightdata_results to create BrightDataScrapedPost records")
    print("   • Ensure folder_id linking from webhook data")
    
    print(f"\n📝 CODE CHANGES NEEDED:")
    print(webhook_fix_patch)
    
    print(f"\n🚀 DEPLOYMENT:")
    print(git_deploy_commands)
    
    print(f"\n📋 MANUAL STEPS:")
    print(manual_fix_steps)
    
    # Create deployment script
    deployment_script = create_deployment_script()
    
    with open('deploy_webhook_fix.py', 'w') as f:
        f.write(deployment_script)
    
    print(f"\n✅ Created deploy_webhook_fix.py")
    print(f"   Run: python deploy_webhook_fix.py")
    
    print(f"\n🎊 AFTER DEPLOYMENT:")
    print("   • Webhook will create BrightDataScrapedPost records")
    print("   • Posts will be linked to job folders via folder_id")
    print("   • job-results API will find and display the data")
    print("   • Your folders 222, 223, 224, 225 will show data!")

if __name__ == "__main__":
    main()
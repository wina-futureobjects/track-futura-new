#!/usr/bin/env python3
"""
PRODUCTION WEBHOOK FIX - Apply this to backend/brightdata_integration/views.py
"""

# STEP 1: Add this function after the brightdata_webhook function (around line 300)

def _create_brightdata_scraped_post(item_data, platform, folder_id=None, scraper_request=None):
    """
    PRODUCTION FIX: Create BrightDataScrapedPost records from webhook data
    This is the missing piece that links posts to job folders!
    """
    try:
        from .models import BrightDataScrapedPost
        from django.utils import timezone
        import time
        
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
            logger.info(f"Created BrightDataScrapedPost: {scraped_post.post_id} -> Folder {folder_id}")
        else:
            # Update folder_id if it wasn't set before
            if not scraped_post.folder_id and folder_id:
                scraped_post.folder_id = folder_id
                scraped_post.save()
                logger.info(f"Updated folder link: {scraped_post.post_id} -> Folder {folder_id}")
        
        return scraped_post
        
    except Exception as e:
        logger.error(f"Error creating BrightDataScrapedPost: {e}")
        return None


# STEP 2: Replace the _process_brightdata_results function (around line 270) with this:

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
        
        logger.info(f"Created {processed_count} BrightDataScrapedPost records with folder links")
        
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


print("""
WEBHOOK FIX DEPLOYMENT GUIDE
============================

ISSUE: Webhook processes posts but doesn't create BrightDataScrapedPost records
RESULT: job-results API can't find data to display in folders

SOLUTION:
1. Add _create_brightdata_scraped_post function (see above)
2. Modify _process_brightdata_results function (see above)
3. Deploy to production

DEPLOYMENT STEPS:
1. Edit backend/brightdata_integration/views.py
2. Add the new function after line 300
3. Replace the existing _process_brightdata_results function
4. Save and commit: git add . && git commit -m "Fix webhook folder linking"
5. Push to production: git push

SUPERADMIN ACCESS:
Username: superadmin
Password: admin123
URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/login

AFTER FIX:
- Folders 222, 223, 224, 225 will show data
- All future webhook posts will link to job folders properly
- Data will appear at: /organizations/1/projects/1/data-storage/job/[FOLDER_ID]
""")
#!/usr/bin/env python3
"""
APPLY WEBHOOK FIX TO PRODUCTION
===============================
This script applies the exact code changes needed to fix the webhook issue.
"""

import os

def apply_webhook_fix():
    views_file = "backend/brightdata_integration/views.py"
    
    if not os.path.exists(views_file):
        print(f"Error: {views_file} not found!")
        return False
    
    print("Reading current views.py...")
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add the new function
    new_function = '''
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

'''
    
    # Find where to insert the new function (after brightdata_webhook function)
    insert_position = content.find("def _process_brightdata_results")
    if insert_position == -1:
        print("Error: Could not find insertion point!")
        return False
    
    # Insert the new function
    content = content[:insert_position] + new_function + "\n\n" + content[insert_position:]
    
    # Replace the existing _process_brightdata_results function
    old_function_start = content.find("def _process_brightdata_results(data: list, platform: str, scraper_request=None):")
    if old_function_start == -1:
        print("Error: Could not find _process_brightdata_results function!")
        return False
    
    # Find the end of the function
    lines = content[old_function_start:].split('\n')
    function_lines = []
    indent_level = None
    
    for i, line in enumerate(lines):
        if i == 0:  # First line is the function definition
            function_lines.append(line)
            continue
            
        if line.strip() == '':  # Empty line
            function_lines.append(line)
            continue
            
        # Check indentation
        if indent_level is None and line.strip():
            # First non-empty line after function def
            indent_level = len(line) - len(line.lstrip())
            function_lines.append(line)
            continue
            
        current_indent = len(line) - len(line.lstrip()) if line.strip() else float('inf')
        
        if line.strip() and current_indent <= indent_level and not line.startswith(' '):
            # This is the start of the next function/class
            break
            
        function_lines.append(line)
    
    old_function = '\n'.join(function_lines)
    
    # New function implementation
    new_function_impl = '''def _process_brightdata_results(data: list, platform: str, scraper_request=None):
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
        return False'''
    
    # Replace the old function with the new one
    content = content.replace(old_function, new_function_impl)
    
    print("Writing updated views.py...")
    with open(views_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Webhook fix applied!")
    print("\nNext steps:")
    print("1. cd backend")
    print("2. git add .")
    print("3. git commit -m 'Fix webhook processing - add BrightDataScrapedPost creation'")
    print("4. git push")
    
    return True

if __name__ == "__main__":
    apply_webhook_fix()
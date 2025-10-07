"""
Manual processor for stuck Apify scraper requests
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

from apify_integration.models import ApifyScraperRequest
from apify_integration.views import _process_apify_results
from django.utils import timezone
from datetime import timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_stuck_requests():
    """Process scraper requests that are stuck in processing state"""
    print("=== Processing Stuck Scraper Requests ===\n")
    
    # Find stuck requests (processing for more than 30 minutes)
    stuck_cutoff = timezone.now() - timedelta(minutes=30)
    
    stuck_requests = ApifyScraperRequest.objects.filter(
        status='processing',
        created_at__lt=stuck_cutoff
    )
    
    print(f"Found {stuck_requests.count()} stuck requests")
    
    for request in stuck_requests:
        print(f"\nProcessing stuck request {request.id}:")
        print(f"  Platform: {request.platform}")
        print(f"  Request ID: {request.request_id}")
        print(f"  Created: {request.created_at}")
        print(f"  Target URL: {request.target_url}")
        
        try:
            # Try to process the results
            print("  Attempting to process results...")
            _process_apify_results(request)
            
            # Update status to completed
            request.status = 'completed'
            request.completed_at = timezone.now()
            request.save()
            
            print("  ✅ Successfully processed and marked as completed")
            
        except Exception as e:
            print(f"  ❌ Error processing request: {str(e)}")
            
            # Mark as failed if processing fails
            request.status = 'failed'
            request.error_message = str(e)
            request.completed_at = timezone.now()
            request.save()
            
            print("  ⚠️ Marked as failed due to processing error")

def check_data_storage_after_fix():
    """Check data storage status after processing stuck requests"""
    print("\n=== Data Storage Status After Fix ===\n")
    
    try:
        from instagram_data.models import InstagramPost, Folder as InstagramFolder
        instagram_posts = InstagramPost.objects.all().count()
        instagram_folders = InstagramFolder.objects.all().count()
        print(f"Instagram posts stored: {instagram_posts}")
        print(f"Instagram folders: {instagram_folders}")
        
        # Show recent Instagram folders
        recent_ig_folders = InstagramFolder.objects.order_by('-created_at')[:3]
        print("Recent Instagram folders:")
        for folder in recent_ig_folders:
            print(f"  - {folder.name} (ID: {folder.id}, Posts: {folder.get_content_count()})")
    except Exception as e:
        print(f"Error checking Instagram data: {e}")
    
    try:
        from facebook_data.models import FacebookPost, Folder as FacebookFolder
        facebook_posts = FacebookPost.objects.all().count()
        facebook_folders = FacebookFolder.objects.all().count()
        print(f"\nFacebook posts stored: {facebook_posts}")
        print(f"Facebook folders: {facebook_folders}")
        
        # Show recent Facebook folders
        recent_fb_folders = FacebookFolder.objects.order_by('-created_at')[:3]
        print("Recent Facebook folders:")
        for folder in recent_fb_folders:
            print(f"  - {folder.name} (ID: {folder.id}, Posts: {folder.get_content_count()})")
    except Exception as e:
        print(f"Error checking Facebook data: {e}")

if __name__ == "__main__":
    process_stuck_requests()
    check_data_storage_after_fix()
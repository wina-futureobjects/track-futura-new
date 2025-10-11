"""
🔧 BRIGHTDATA SCRAPER REQUEST FIXES
Fix the processing status and target URL issues in BrightData Scraper Requests
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import TrackSource
from django.utils import timezone
import json

def analyze_scraper_request_issues():
    """Analyze the current scraper request issues"""
    
    print("🔧 BRIGHTDATA SCRAPER REQUEST ANALYSIS")
    print("=" * 60)
    
    # 1. Check processing requests
    processing_requests = BrightDataScraperRequest.objects.filter(status='processing').order_by('-created_at')
    
    print(f"📊 Processing Requests: {processing_requests.count()}")
    
    for req in processing_requests:
        print(f"\n🔍 Request {req.id}: {req.platform}")
        print(f"   Target URL: {req.target_url}")
        print(f"   Folder ID: {req.folder_id}")
        print(f"   Snapshot ID: {req.snapshot_id}")
        print(f"   Status: {req.status}")
        print(f"   Created: {req.created_at}")
        
        # Check if this has scraped data (meaning it's actually completed)
        scraped_count = BrightDataScrapedPost.objects.filter(
            scraper_request=req
        ).count()
        
        folder_scraped_count = BrightDataScrapedPost.objects.filter(
            folder_id=req.folder_id
        ).count()
        
        print(f"   📊 Scraped posts (by request): {scraped_count}")
        print(f"   📊 Scraped posts (by folder): {folder_scraped_count}")
        
        if folder_scraped_count > 0 and req.status == 'processing':
            print(f"   ⚠️ STATUS MISMATCH: Has data but still 'processing'")
    
    return processing_requests

def fix_target_urls():
    """Fix the target URLs by getting real URLs from TrackSource"""
    
    print(f"\n🔗 FIXING TARGET URLS")
    print("-" * 40)
    
    processing_requests = BrightDataScraperRequest.objects.filter(
        target_url__startswith='System folder'
    )
    
    fixed_count = 0
    
    for req in processing_requests:
        print(f"\n🔧 Fixing Request {req.id}: {req.target_url}")
        
        # Get real URLs from TrackSource for this folder
        if req.folder_id:
            sources = TrackSource.objects.filter(
                folder_id=req.folder_id,
                platform__iexact=req.platform
            )
            
            if sources.exists():
                # Get the appropriate URL based on platform
                real_urls = []
                for source in sources:
                    url = None
                    if req.platform.lower() == 'instagram' and source.instagram_link:
                        url = source.instagram_link
                    elif req.platform.lower() == 'facebook' and source.facebook_link:
                        url = source.facebook_link
                    elif req.platform.lower() == 'linkedin' and source.linkedin_link:
                        url = source.linkedin_link
                    elif req.platform.lower() == 'tiktok' and source.tiktok_link:
                        url = source.tiktok_link
                    
                    if url:
                        real_urls.append(url)
                        req.source_name = source.name
                
                if real_urls:
                    # Use the first URL as target_url, store all in a field if needed
                    req.target_url = real_urls[0]
                    if len(real_urls) > 1:
                        # Store additional URLs in response_data as JSON
                        additional_data = {
                            'all_urls': real_urls,
                            'url_count': len(real_urls)
                        }
                        req.response_data = additional_data
                    
                    req.save()
                    fixed_count += 1
                    
                    print(f"   ✅ Fixed: {req.target_url}")
                    print(f"   📋 Source: {req.source_name}")
                    if len(real_urls) > 1:
                        print(f"   📎 Additional URLs: {len(real_urls) - 1}")
                else:
                    print(f"   ❌ No URLs found for {req.platform}")
            else:
                print(f"   ❌ No TrackSource found for folder {req.folder_id}")
    
    print(f"\n✅ Fixed {fixed_count} target URLs")
    return fixed_count

def fix_processing_status():
    """Fix requests that should be completed but are stuck in processing"""
    
    print(f"\n⚡ FIXING PROCESSING STATUS")
    print("-" * 40)
    
    processing_requests = BrightDataScraperRequest.objects.filter(status='processing')
    fixed_count = 0
    
    for req in processing_requests:
        # Check if this request has scraped data
        scraped_count = BrightDataScrapedPost.objects.filter(
            scraper_request=req
        ).count()
        
        folder_scraped_count = BrightDataScrapedPost.objects.filter(
            folder_id=req.folder_id
        ).count()
        
        print(f"\n🔍 Request {req.id}: {req.platform}")
        print(f"   Scraped (by request): {scraped_count}")
        print(f"   Scraped (by folder): {folder_scraped_count}")
        
        # If we have scraped data, the request should be completed
        if scraped_count > 0 or folder_scraped_count > 0:
            print(f"   🔧 Updating status to 'completed'")
            
            req.status = 'completed'
            req.completed_at = timezone.now()
            
            # If we don't have a started_at, set it
            if not req.started_at:
                # Set started_at to creation time or a bit after
                req.started_at = req.created_at
            
            req.save()
            fixed_count += 1
            
            print(f"   ✅ Status fixed: {req.status}")
        else:
            print(f"   ⏳ Still processing (no data yet)")
    
    print(f"\n✅ Fixed {fixed_count} processing statuses")
    return fixed_count

def create_missing_scraper_requests():
    """Create scraper requests for scraped posts that don't have them"""
    
    print(f"\n📝 CREATING MISSING SCRAPER REQUESTS")
    print("-" * 40)
    
    # Find scraped posts without scraper_request
    orphaned_posts = BrightDataScrapedPost.objects.filter(
        scraper_request__isnull=True
    ).values('folder_id', 'platform').distinct()
    
    created_count = 0
    
    for post_group in orphaned_posts:
        folder_id = post_group['folder_id']
        platform = post_group['platform']
        
        post_count = BrightDataScrapedPost.objects.filter(
            folder_id=folder_id,
            platform=platform,
            scraper_request__isnull=True
        ).count()
        
        print(f"\n📊 Folder {folder_id} ({platform}): {post_count} orphaned posts")
        
        # Check if a scraper request already exists for this folder/platform
        existing_request = BrightDataScraperRequest.objects.filter(
            folder_id=folder_id,
            platform=platform
        ).first()
        
        if existing_request:
            print(f"   🔗 Linking to existing request {existing_request.id}")
            
            # Link orphaned posts to existing request
            BrightDataScrapedPost.objects.filter(
                folder_id=folder_id,
                platform=platform,
                scraper_request__isnull=True
            ).update(scraper_request=existing_request)
            
        else:
            print(f"   📝 Creating new scraper request")
            
            # Get target URL from TrackSource
            target_url = f"Folder {folder_id}"
            source_name = "Unknown"
            
            if folder_id:
                sources = TrackSource.objects.filter(
                    folder_id=folder_id,
                    platform__iexact=platform
                ).first()
                
                if sources:
                    if platform.lower() == 'instagram' and sources.instagram_link:
                        target_url = sources.instagram_link
                        source_name = sources.name
                    elif platform.lower() == 'facebook' and sources.facebook_link:
                        target_url = sources.facebook_link
                        source_name = sources.name
            
            # Create new scraper request
            scraper_request = BrightDataScraperRequest.objects.create(
                platform=platform,
                target_url=target_url,
                source_name=source_name,
                folder_id=folder_id,
                status='completed',  # Since we have data, it's completed
                snapshot_id=f'reconstructed_{folder_id}_{platform}',
                request_id=f'reconstructed_{folder_id}_{platform}',
                started_at=timezone.now() - timezone.timedelta(hours=1),
                completed_at=timezone.now()
            )
            
            # Link all orphaned posts to this request
            BrightDataScrapedPost.objects.filter(
                folder_id=folder_id,
                platform=platform,
                scraper_request__isnull=True
            ).update(scraper_request=scraper_request)
            
            created_count += 1
            print(f"   ✅ Created request {scraper_request.id}")
    
    print(f"\n✅ Created {created_count} missing scraper requests")
    return created_count

if __name__ == "__main__":
    print("🚀 Starting BrightData Scraper Request fixes...")
    print()
    
    try:
        # 1. Analyze current issues
        processing_requests = analyze_scraper_request_issues()
        
        # 2. Fix target URLs
        fixed_urls = fix_target_urls()
        
        # 3. Fix processing status
        fixed_status = fix_processing_status()
        
        # 4. Create missing scraper requests
        created_requests = create_missing_scraper_requests()
        
        print("\n" + "=" * 60)
        print("🎯 FIX SUMMARY:")
        print(f"✅ Fixed {fixed_urls} target URLs")
        print(f"✅ Fixed {fixed_status} processing statuses")
        print(f"✅ Created {created_requests} missing scraper requests")
        print()
        print("🔍 AFTER FIXES:")
        
        # Show current status
        total_requests = BrightDataScraperRequest.objects.count()
        completed_requests = BrightDataScraperRequest.objects.filter(status='completed').count()
        processing_requests = BrightDataScraperRequest.objects.filter(status='processing').count()
        
        print(f"📊 Total Scraper Requests: {total_requests}")
        print(f"✅ Completed: {completed_requests}")
        print(f"⏳ Processing: {processing_requests}")
        
        print("\n🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error during fixes: {e}")
        import traceback
        traceback.print_exc()
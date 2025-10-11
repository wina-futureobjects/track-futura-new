#!/usr/bin/env python3
"""
🚨 DIRECT DATABASE QUERY FIX
=============================
Fix the job-results API to show ALL scraped posts for debugging
"""

def create_debug_job_results_api():
    print("🚨 DIRECT DATABASE QUERY FIX")
    print("=" * 50)
    
    print("📋 CURRENT ISSUE:")
    print("   • Webhook saves posts successfully ✅")
    print("   • Admin panel shows 27 posts ✅")
    print("   • But job-results API can't find folder 216 posts ❌")
    
    print(f"\n🔍 DEBUGGING APPROACH:")
    print("   1. Create a debug endpoint to show ALL posts")
    print("   2. Check if folder 216 posts exist in database")
    print("   3. Fix the job-results API query if needed")
    
    debug_api_code = '''
# Add this debug endpoint to brightdata_integration/views.py

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_scraped_posts(request):
    """Debug endpoint to show all scraped posts"""
    try:
        from .models import BrightDataScrapedPost
        
        # Get all posts
        all_posts = BrightDataScrapedPost.objects.all().order_by('-created_at')
        
        posts_by_folder = {}
        for post in all_posts:
            folder_id = post.folder_id
            if folder_id not in posts_by_folder:
                posts_by_folder[folder_id] = []
            
            posts_by_folder[folder_id].append({
                'post_id': post.post_id,
                'platform': post.platform,
                'created_at': post.created_at.isoformat(),
                'likes': post.likes
            })
        
        return JsonResponse({
            'success': True,
            'total_posts': all_posts.count(),
            'posts_by_folder': posts_by_folder,
            'folder_counts': {str(k): len(v) for k, v in posts_by_folder.items()}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
'''
    
    print(f"\n📝 DEBUG API CODE:")
    print(debug_api_code)
    
    print(f"\n🔧 IMPLEMENTATION PLAN:")
    print("   1. Add debug endpoint to views.py")
    print("   2. Add URL route")
    print("   3. Test the debug endpoint")
    print("   4. Fix job-results API based on findings")

def create_quick_fix():
    print(f"\n⚡ QUICK FIX APPROACH:")
    print("=" * 50)
    
    print("Instead of debugging, let's directly fix the job-results API")
    print("to be more robust and show detailed logging:")
    
    enhanced_api_code = '''
# Enhanced job-results API with detailed logging

# In brightdata_job_results function, add this debugging:

logger.info(f"🔍 Searching for scraped posts with folder_id={job_folder_id}")

existing_scraped_posts = BrightDataScrapedPost.objects.filter(
    folder_id=job_folder_id
)

logger.info(f"📊 Found {existing_scraped_posts.count()} posts for folder {job_folder_id}")

# Log all posts in this folder
for post in existing_scraped_posts:
    logger.info(f"   - {post.post_id} ({post.platform}) created {post.created_at}")

if existing_scraped_posts.exists():
    # ... existing code
else:
    # Add more detailed logging
    logger.warning(f"❌ No scraped posts found for folder {job_folder_id}")
    
    # Check if ANY posts exist
    total_posts = BrightDataScrapedPost.objects.count()
    logger.info(f"📊 Total scraped posts in database: {total_posts}")
    
    # Show folder distribution
    from django.db.models import Count
    folder_counts = BrightDataScrapedPost.objects.values('folder_id').annotate(count=Count('id'))
    logger.info(f"📊 Posts by folder: {list(folder_counts)}")
'''
    
    print(enhanced_api_code)

def main():
    create_debug_job_results_api()
    create_quick_fix()
    
    print(f"\n🎯 NEXT STEPS:")
    print("=" * 50)
    print("1. First, check admin panel search results for:")
    print("   • INVESTIGATION_191_TEST")
    print("   • INVESTIGATION_216_TEST")
    print()
    print("2. This will tell us if posts are being saved correctly")
    print()
    print("3. If both posts exist in admin, the issue is job-results API query")
    print("4. If folder 216 post is missing, the issue is webhook saving")

if __name__ == "__main__":
    main()
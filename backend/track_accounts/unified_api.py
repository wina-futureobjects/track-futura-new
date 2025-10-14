from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Prefetch
from track_accounts.models import UnifiedRunFolder
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder
from linkedin_data.models import Folder as LinkedInFolder
from tiktok_data.models import Folder as TikTokFolder
from brightdata_integration.models import BrightDataScrapedPost
from workflow.models import ScrapingRun
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def unified_data_storage_api(request):
    """
    🎯 UNIFIED DATA STORAGE API
    ==========================
    
    Single endpoint that returns ALL folders in a unified format:
    - UnifiedRunFolders with complete hierarchy
    - Platform-specific folders properly linked
    - BrightData folders included
    - Consistent response format
    """
    
    if request.method == 'GET':
        try:
            # Get all folders with complete hierarchy
            folders_data = get_unified_folder_structure()
            
            return JsonResponse({
                'success': True,
                'count': len(folders_data),
                'folders': folders_data,
                'message': 'Unified folder structure retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Unified API error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'folders': []
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_unified_folder_structure():
    """Get unified folder structure with all data sources"""
    
    folders_data = []
    
    # 1. Get all run folders with their complete hierarchy
    run_folders = UnifiedRunFolder.objects.filter(
        folder_type='run'
    ).prefetch_related(
        'children',
        'children__children',
        'children__children__children'
    ).order_by('-created_at')
    
    for run_folder in run_folders:
        # Build complete hierarchy for this run
        run_data = build_folder_hierarchy(run_folder)
        folders_data.append(run_data)
    
    # 2. Get standalone BrightData folders (not linked to runs)
    standalone_brightdata = get_standalone_brightdata_folders()
    folders_data.extend(standalone_brightdata)
    
    # 3. Get orphaned platform folders
    orphaned_platform = get_orphaned_platform_folders()
    folders_data.extend(orphaned_platform)
    
    return folders_data

def build_folder_hierarchy(run_folder):
    """Build complete folder hierarchy from run folder"""
    
    # Base run folder data
    run_data = {
        'id': run_folder.id,
        'name': run_folder.name,
        'description': run_folder.description,
        'folder_type': 'run',
        'platform': 'unified',
        'category': run_folder.category,
        'category_display': run_folder.category.title() if run_folder.category else 'Posts',
        'created_at': run_folder.created_at.isoformat() if run_folder.created_at else None,
        'scraping_run_id': run_folder.scraping_run_id,
        'post_count': 0,
        'subfolders': []
    }
    
    # Get platform folders
    platform_folders = UnifiedRunFolder.objects.filter(
        parent_folder=run_folder,
        folder_type='platform'
    ).order_by('platform_code')
    
    total_posts = 0
    
    for platform_folder in platform_folders:
        platform_data = {
            'id': platform_folder.id,
            'name': platform_folder.name,
            'description': platform_folder.description,
            'folder_type': 'platform',
            'platform': platform_folder.platform_code,
            'category': platform_folder.category,
            'category_display': platform_folder.category.title() if platform_folder.category else 'Posts',
            'created_at': platform_folder.created_at.isoformat() if platform_folder.created_at else None,
            'post_count': 0,
            'subfolders': []
        }
        
        # Get service folders
        service_folders = UnifiedRunFolder.objects.filter(
            parent_folder=platform_folder,
            folder_type='service'
        ).order_by('service_code')
        
        platform_posts = 0
        
        for service_folder in service_folders:
            service_data = {
                'id': service_folder.id,
                'name': service_folder.name,
                'description': service_folder.description,
                'folder_type': 'service',
                'platform': service_folder.platform_code,
                'service': service_folder.service_code,
                'category': service_folder.category,
                'category_display': service_folder.category.title() if service_folder.category else 'Posts',
                'created_at': service_folder.created_at.isoformat() if service_folder.created_at else None,
                'post_count': 0,
                'subfolders': []
            }
            
            # Get job folders
            job_folders = UnifiedRunFolder.objects.filter(
                parent_folder=service_folder,
                folder_type='job'
            ).order_by('-created_at')
            
            service_posts = 0
            
            for job_folder in job_folders:
                # Count posts in this job folder
                job_posts = count_posts_in_job_folder(job_folder)
                
                job_data = {
                    'id': job_folder.id,
                    'name': job_folder.name,
                    'description': job_folder.description,
                    'folder_type': 'job',
                    'platform': job_folder.platform_code,
                    'service': job_folder.service_code,
                    'category': job_folder.category,
                    'category_display': job_folder.category.title() if job_folder.category else 'Posts',
                    'created_at': job_folder.created_at.isoformat() if job_folder.created_at else None,
                    'post_count': job_posts,
                    'data_url': f'/organizations/1/projects/2/data-storage/job/{job_folder.id}',
                    'api_url': f'/api/{job_folder.platform_code}-data/folders/{job_folder.id}/'
                }
                
                service_data['subfolders'].append(job_data)
                service_posts += job_posts
            
            service_data['post_count'] = service_posts
            platform_data['subfolders'].append(service_data)
            platform_posts += service_posts
        
        platform_data['post_count'] = platform_posts
        run_data['subfolders'].append(platform_data)
        total_posts += platform_posts
    
    run_data['post_count'] = total_posts
    return run_data

def count_posts_in_job_folder(job_folder):
    """Count posts in a job folder across all platform types"""
    
    total_posts = 0
    platform = job_folder.platform_code
    
    if platform == 'instagram':
        # Count posts in linked Instagram folder
        instagram_folder = InstagramFolder.objects.filter(
            unified_job_folder=job_folder
        ).first()
        if instagram_folder:
            from instagram_data.models import Post
            total_posts = Post.objects.filter(folder=instagram_folder).count()
    
    elif platform == 'facebook':
        # Count posts in linked Facebook folder
        facebook_folder = FacebookFolder.objects.filter(
            unified_job_folder=job_folder
        ).first()
        if facebook_folder:
            from facebook_data.models import Post
            total_posts = Post.objects.filter(folder=facebook_folder).count()
    
    elif platform == 'linkedin':
        # Count posts in linked LinkedIn folder
        linkedin_folder = LinkedInFolder.objects.filter(
            unified_job_folder=job_folder
        ).first()
        if linkedin_folder:
            from linkedin_data.models import Post
            total_posts = Post.objects.filter(folder=linkedin_folder).count()
    
    elif platform == 'tiktok':
        # Count posts in linked TikTok folder
        tiktok_folder = TikTokFolder.objects.filter(
            unified_job_folder=job_folder
        ).first()
        if tiktok_folder:
            from tiktok_data.models import Post
            total_posts = Post.objects.filter(folder=tiktok_folder).count()
    
    # Also count BrightData posts linked to this folder
    brightdata_posts = BrightDataScrapedPost.objects.filter(
        folder=job_folder
    ).count()
    
    return total_posts + brightdata_posts

def get_standalone_brightdata_folders():
    """Get BrightData folders not linked to scraping runs"""
    
    standalone_folders = []
    
    # Get UnifiedRunFolders created by BrightData
    brightdata_folders = UnifiedRunFolder.objects.filter(
        Q(created_by__icontains='brightdata') | 
        Q(created_by__icontains='web unlocker'),
        scraping_run__isnull=True
    ).order_by('-created_at')
    
    for folder in brightdata_folders:
        post_count = BrightDataScrapedPost.objects.filter(folder=folder).count()
        
        folder_data = {
            'id': folder.id,
            'name': folder.name,
            'description': folder.description,
            'folder_type': 'brightdata',
            'platform': 'brightdata',
            'category': 'scraped',
            'category_display': 'Scraped Data',
            'created_at': folder.created_at.isoformat() if folder.created_at else None,
            'post_count': post_count,
            'data_url': f'/organizations/1/projects/2/data-storage/job/{folder.id}',
            'api_url': f'/api/brightdata/job-results/{folder.id}/',
            'folder_emoji': '🔓'
        }
        
        standalone_folders.append(folder_data)
    
    return standalone_folders

def get_orphaned_platform_folders():
    """Get platform folders not properly linked to hierarchy"""
    
    orphaned_folders = []
    
    platform_models = {
        'instagram': InstagramFolder,
        'facebook': FacebookFolder, 
        'linkedin': LinkedInFolder,
        'tiktok': TikTokFolder
    }
    
    for platform, model in platform_models.items():
        # Find folders without unified_job_folder link
        orphaned = model.objects.filter(
            unified_job_folder__isnull=True
        ).order_by('-created_at')
        
        for folder in orphaned:
            # Count posts in this folder
            post_count = 0
            if hasattr(folder, 'posts'):
                post_count = folder.posts.count()
            
            folder_data = {
                'id': folder.id,
                'name': folder.name,
                'description': folder.description,
                'folder_type': 'orphaned',
                'platform': platform,
                'category': 'posts',
                'category_display': 'Posts',
                'created_at': folder.created_at.isoformat() if folder.created_at else None,
                'post_count': post_count,
                'data_url': f'/organizations/1/projects/2/data-storage/{platform}/{folder.id}',
                'api_url': f'/api/{platform}-data/folders/{folder.id}/',
                'needs_fixing': True
            }
            
            orphaned_folders.append(folder_data)
    
    return orphaned_folders
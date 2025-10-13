from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from track_accounts.models import SourceFolder, TrackSource
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def fix_folder_4_api(request):
    """
    API endpoint to fix folder 4 sources issue
    This will create folder 4 and populate it with sources
    """
    try:
        # Get or create folder 4
        folder, created = SourceFolder.objects.get_or_create(
            id=4,
            defaults={
                'name': 'Nike - Complete Social Media Collection V2',
                'project_id': 1,  # Ensure consistent project_id
                'description': 'Nike complete social media tracking collection'
            }
        )
        
        logger.info(f"Folder 4: {'created' if created else 'exists'}")
        
        # Check if folder already has sources
        existing_sources = TrackSource.objects.filter(source_folder=folder).count()
        
        if existing_sources > 0:
            return JsonResponse({
                'success': True,
                'message': f'Folder 4 already has {existing_sources} sources',
                'folder_id': folder.id,
                'folder_name': folder.name
            })
        
        # Create sources for folder 4
        sources_created = []
        
        # Nike Instagram
        nike_instagram, created = TrackSource.objects.get_or_create(
            source_folder=folder,
            platform='instagram',
            identifier='nike',
            defaults={
                'project_id': 1,
                'name': 'Nike Instagram',
                'is_active': True,
                'description': 'Nike official Instagram account'
            }
        )
        if created:
            sources_created.append('Nike Instagram')
        
        # Nike Facebook  
        nike_facebook, created = TrackSource.objects.get_or_create(
            source_folder=folder,
            platform='facebook',
            identifier='nike',
            defaults={
                'project_id': 1,
                'name': 'Nike Facebook',
                'is_active': True,
                'description': 'Nike official Facebook page'
            }
        )
        if created:
            sources_created.append('Nike Facebook')
            
        # Adidas Instagram
        adidas_instagram, created = TrackSource.objects.get_or_create(
            source_folder=folder,
            platform='instagram', 
            identifier='adidas',
            defaults={
                'project_id': 1,
                'name': 'Adidas Instagram',
                'is_active': True,
                'description': 'Adidas official Instagram account'
            }
        )
        if created:
            sources_created.append('Adidas Instagram')
        
        # Get final count
        total_sources = TrackSource.objects.filter(source_folder=folder).count()
        
        return JsonResponse({
            'success': True,
            'message': f'Folder 4 fix completed successfully!',
            'folder_id': folder.id,
            'folder_name': folder.name,
            'sources_created': sources_created,
            'total_sources': total_sources,
            'folder_created': created
        })
        
    except Exception as e:
        logger.error(f"Error fixing folder 4: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to fix folder 4: {str(e)}'
        })
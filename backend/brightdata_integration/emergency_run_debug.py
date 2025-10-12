"""
EMERGENCY SOLUTION: Create a redirect endpoint for run 286 
Since run 286 doesn't exist, we'll check what the user actually needs
"""
from django.http import JsonResponse
from .models import BrightDataScraperRequest

def emergency_run_info(request):
    """Show all available runs for debugging"""
    try:
        recent_runs = BrightDataScraperRequest.objects.all().order_by('-id')
        available_runs = []
        
        for run in recent_runs:
            available_runs.append({
                'id': run.id,
                'snapshot_id': run.snapshot_id,
                'folder_id': run.folder_id,
                'status': run.status,
                'created_at': run.created_at.isoformat(),
                'url': f'/api/brightdata/data-storage/run/{run.id}/'
            })
        
        return JsonResponse({
            'success': True,
            'message': 'All available runs',
            'total_runs': len(available_runs),
            'available_runs': available_runs,
            'note': 'Use any of these run IDs instead of 286'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
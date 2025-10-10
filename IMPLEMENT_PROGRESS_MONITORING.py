#!/usr/bin/env python3
"""
REAL-TIME PROGRESS MONITORING INTEGRATION
=========================================
This will implement real-time BrightData progress monitoring in your workflow system.
"""

import os
import sys
import django

# Setup Django
try:
    if not os.path.exists('manage.py'):
        os.chdir('backend')
    
    sys.path.insert(0, os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def create_progress_monitoring_view():
    """Create a view for real-time progress monitoring"""
    
    progress_view_code = '''
import requests
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import BrightDataScraperRequest, BrightDataBatchJob
from workflow.models import ScrapingRun, ScrapingJob

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def brightdata_progress_monitor(request):
    """Monitor BrightData progress in real-time"""
    try:
        # Get BrightData API token
        api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        
        # BrightData progress API endpoint
        url = "https://api.brightdata.com/datasets/v3/progress/"
        headers = {
            "Authorization": f"Bearer {api_token}",
        }
        
        # Get progress from BrightData
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            brightdata_progress = response.json()
            
            # Update local database with progress
            updated_runs = []
            
            # Get all pending/processing scraping runs
            active_runs = ScrapingRun.objects.filter(
                status__in=['pending', 'processing']
            )
            
            for run in active_runs:
                # Get associated scraper requests
                scraper_requests = BrightDataScraperRequest.objects.filter(
                    batch_job__scraping_jobs__scraping_run=run
                ).distinct()
                
                total_requests = scraper_requests.count()
                completed_requests = 0
                failed_requests = 0
                
                # Check each request status
                for req in scraper_requests:
                    if req.status == 'completed':
                        completed_requests += 1
                    elif req.status == 'failed':
                        failed_requests += 1
                    elif req.snapshot_id:
                        # Check if this snapshot_id is in BrightData progress
                        for progress_item in brightdata_progress.get('data', []):
                            if progress_item.get('snapshot_id') == req.snapshot_id:
                                # Update status based on BrightData progress
                                if progress_item.get('status') == 'completed':
                                    req.status = 'completed'
                                    req.progress = 100
                                    req.save()
                                    completed_requests += 1
                                elif progress_item.get('status') == 'failed':
                                    req.status = 'failed'
                                    req.save()
                                    failed_requests += 1
                                elif progress_item.get('status') == 'processing':
                                    req.status = 'processing'
                                    req.progress = progress_item.get('progress', 0)
                                    req.save()
                
                # Update run status and progress
                if total_requests > 0:
                    run.total_jobs = total_requests
                    run.completed_jobs = completed_requests + failed_requests
                    run.successful_jobs = completed_requests
                    run.failed_jobs = failed_requests
                    
                    progress_percentage = int((run.completed_jobs / run.total_jobs) * 100)
                    
                    # Update run status
                    if run.completed_jobs == run.total_jobs:
                        if run.successful_jobs > 0:
                            run.status = 'completed'
                        else:
                            run.status = 'failed'
                        
                        if not run.completed_at:
                            from django.utils import timezone
                            run.completed_at = timezone.now()
                    elif run.completed_jobs > 0:
                        run.status = 'processing'
                        if not run.started_at:
                            from django.utils import timezone
                            run.started_at = timezone.now()
                    
                    run.save()
                    
                    updated_runs.append({
                        'id': run.id,
                        'name': run.name,
                        'status': run.status,
                        'progress': progress_percentage,
                        'completed_jobs': run.completed_jobs,
                        'total_jobs': run.total_jobs,
                        'successful_jobs': run.successful_jobs,
                        'failed_jobs': run.failed_jobs
                    })
            
            return JsonResponse({
                'status': 'success',
                'brightdata_progress': brightdata_progress,
                'updated_runs': updated_runs,
                'message': f'Updated {len(updated_runs)} scraping runs'
            })
        
        else:
            logger.error(f"BrightData API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'status': 'error',
                'message': f'BrightData API error: {response.status_code}'
            }, status=500)
    
    except Exception as e:
        logger.error(f"Progress monitoring error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_workflow_statuses(request):
    """Manually trigger workflow status updates"""
    try:
        # Update all pending runs that have completed scraper requests
        pending_runs = ScrapingRun.objects.filter(status='pending')
        updated_count = 0
        
        for run in pending_runs:
            scraper_requests = BrightDataScraperRequest.objects.filter(
                batch_job__scraping_jobs__scraping_run=run
            ).distinct()
            
            if scraper_requests.exists():
                completed_requests = scraper_requests.filter(status='completed').count()
                failed_requests = scraper_requests.filter(status='failed').count()
                total_requests = scraper_requests.count()
                
                if completed_requests > 0 or failed_requests > 0:
                    run.total_jobs = total_requests
                    run.completed_jobs = completed_requests + failed_requests
                    run.successful_jobs = completed_requests
                    run.failed_jobs = failed_requests
                    
                    if run.completed_jobs == run.total_jobs:
                        run.status = 'completed'
                        if not run.completed_at:
                            from django.utils import timezone
                            run.completed_at = timezone.now()
                    else:
                        run.status = 'processing'
                        if not run.started_at:
                            from django.utils import timezone
                            run.started_at = timezone.now()
                    
                    run.save()
                    updated_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'Updated {updated_count} workflow runs',
            'updated_count': updated_count
        })
    
    except Exception as e:
        logger.error(f"Workflow status update error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
'''
    
    # Write the progress monitoring view to the views.py file
    views_file_path = 'brightdata_integration/views.py'
    
    # Read current views.py content
    try:
        with open(views_file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Check if progress monitoring is already added
        if 'brightdata_progress_monitor' not in current_content:
            # Add the progress monitoring functions at the end
            updated_content = current_content + '\n\n' + progress_view_code
            
            with open(views_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ Added progress monitoring views to brightdata_integration/views.py")
        else:
            print("ℹ️ Progress monitoring already exists in views.py")
            
    except Exception as e:
        print(f"❌ Error updating views.py: {e}")
        return False
    
    return True

def update_urls():
    """Add URLs for progress monitoring endpoints"""
    
    urls_addition = '''
# Progress monitoring endpoints
path('api/brightdata/progress/', brightdata_progress_monitor, name='brightdata_progress_monitor'),
path('api/brightdata/update-workflow-status/', update_workflow_statuses, name='update_workflow_statuses'),
'''
    
    # Find and update the main urls.py file
    urls_files = ['config/urls.py', 'urls.py']
    
    for urls_file in urls_files:
        if os.path.exists(urls_file):
            try:
                with open(urls_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'brightdata_progress_monitor' not in content:
                    # Add import if needed
                    if 'from brightdata_integration.views import' not in content:
                        import_line = "from brightdata_integration.views import brightdata_progress_monitor, update_workflow_statuses"
                        # Add import after existing imports
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith('from ') and 'import ' in line:
                                lines.insert(i + 1, import_line)
                                break
                        content = '\n'.join(lines)
                    
                    # Add URL patterns
                    if 'urlpatterns = [' in content:
                        content = content.replace(
                            'urlpatterns = [',
                            f'urlpatterns = [\n    {urls_addition.strip()}'
                        )
                    
                    with open(urls_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Updated {urls_file} with progress monitoring URLs")
                    break
                else:
                    print(f"ℹ️ Progress monitoring URLs already exist in {urls_file}")
                    
            except Exception as e:
                print(f"❌ Error updating {urls_file}: {e}")

def create_frontend_monitoring_script():
    """Create JavaScript for frontend real-time monitoring"""
    
    frontend_script = '''
// Real-time progress monitoring for Workflow Management
class WorkflowProgressMonitor {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.isMonitoring = false;
        this.intervalId = null;
    }
    
    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        console.log('🚀 Starting real-time workflow monitoring...');
        
        // Initial update
        this.updateProgress();
        
        // Set up periodic updates
        this.intervalId = setInterval(() => {
            this.updateProgress();
        }, this.updateInterval);
    }
    
    stopMonitoring() {
        if (!this.isMonitoring) return;
        
        this.isMonitoring = false;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        console.log('⏹️ Stopped workflow monitoring');
    }
    
    async updateProgress() {
        try {
            const response = await fetch('/api/brightdata/progress/', {
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer YOUR_TOKEN_HERE', // Replace with actual token
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateUI(data.updated_runs);
                console.log('✅ Progress updated:', data.updated_runs.length, 'runs');
            } else {
                console.error('❌ Progress update failed:', response.status);
            }
        } catch (error) {
            console.error('❌ Progress monitoring error:', error);
        }
    }
    
    updateUI(updatedRuns) {
        updatedRuns.forEach(run => {
            // Update progress bars
            const progressBar = document.querySelector(`[data-run-id="${run.id}"] .progress-bar`);
            if (progressBar) {
                progressBar.style.width = `${run.progress}%`;
                progressBar.textContent = `${run.progress}%`;
            }
            
            // Update status
            const statusElement = document.querySelector(`[data-run-id="${run.id}"] .status`);
            if (statusElement) {
                statusElement.textContent = run.status;
                statusElement.className = `status status-${run.status}`;
            }
            
            // Update job counts
            const jobsElement = document.querySelector(`[data-run-id="${run.id}"] .jobs-count`);
            if (jobsElement) {
                jobsElement.textContent = `${run.completed_jobs}/${run.total_jobs} jobs`;
            }
        });
    }
}

// Initialize monitoring when page loads
document.addEventListener('DOMContentLoaded', function() {
    const monitor = new WorkflowProgressMonitor();
    
    // Start monitoring if on workflow management page
    if (window.location.pathname.includes('workflow') || 
        window.location.pathname.includes('management')) {
        monitor.startMonitoring();
        
        // Stop monitoring when leaving page
        window.addEventListener('beforeunload', () => {
            monitor.stopMonitoring();
        });
    }
});

// Manual trigger for workflow status update
async function updateWorkflowStatuses() {
    try {
        const response = await fetch('/api/brightdata/update-workflow-status/', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer YOUR_TOKEN_HERE', // Replace with actual token
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Workflow statuses updated:', data.message);
            location.reload(); // Refresh page to show updates
        } else {
            console.error('❌ Workflow update failed:', response.status);
        }
    } catch (error) {
        console.error('❌ Workflow update error:', error);
    }
}
'''
    
    # Save the frontend script
    with open('../WORKFLOW_PROGRESS_MONITOR.js', 'w', encoding='utf-8') as f:
        f.write(frontend_script)
    
    print("✅ Created frontend monitoring script: WORKFLOW_PROGRESS_MONITOR.js")

def main():
    """Main execution function"""
    print("🔧 IMPLEMENTING REAL-TIME PROGRESS MONITORING")
    print("=" * 60)
    
    # Step 1: Create progress monitoring views
    print("\n📊 STEP 1: Adding progress monitoring views...")
    if create_progress_monitoring_view():
        print("✅ Progress monitoring views added")
    else:
        print("❌ Failed to add progress monitoring views")
    
    # Step 2: Update URLs
    print("\n🌐 STEP 2: Adding progress monitoring URLs...")
    update_urls()
    
    # Step 3: Create frontend monitoring script
    print("\n💻 STEP 3: Creating frontend monitoring script...")
    create_frontend_monitoring_script()
    
    print("\n" + "="*60)
    print("🎉 REAL-TIME PROGRESS MONITORING IMPLEMENTATION COMPLETE!")
    print("="*60)
    
    print("\n📋 WHAT WAS ADDED:")
    print("✅ /api/brightdata/progress/ - Real-time progress monitoring endpoint")
    print("✅ /api/brightdata/update-workflow-status/ - Manual workflow status update")
    print("✅ Frontend JavaScript for automatic UI updates")
    print("✅ BrightData API integration with progress tracking")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Deploy these changes to production")
    print("2. Replace 'YOUR_TOKEN_HERE' with actual authentication token")
    print("3. Add the JavaScript file to your frontend template")
    print("4. Test the workflow management page for real-time updates")

if __name__ == "__main__":
    main()
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import logging

from .models import InputCollection, WorkflowTask, ScheduledScrapingTask, ScrapingRun, ScrapingJob
from .serializers import (
    InputCollectionSerializer, WorkflowTaskSerializer, 
    ScheduledScrapingTaskSerializer, InputCollectionCreateSerializer,
    ScrapingRunSerializer, ScrapingJobSerializer
)
from .services import WorkflowService
from users.models import Platform, Service, PlatformService
from brightdata_integration.services import BrightDataAutomatedBatchScraper

logger = logging.getLogger(__name__)

class WorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow management"""
    permission_classes = [AllowAny]  # For testing, use IsAuthenticated in production
    serializer_class = InputCollectionSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        project_id = self.request.query_params.get('project')
        
        queryset = InputCollection.objects.select_related(
            'project', 
            'platform_service__platform',
            'platform_service__service'
        )
        
        # Filter by project if specified
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by user permissions
        # Skip permission check for unauthenticated users during testing
        if user.is_authenticated and not user.is_superuser:
            user_projects = user.projects.all() | user.accessible_projects.all()
            queryset = queryset.filter(project__in=user_projects)
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return InputCollectionCreateSerializer
        return InputCollectionSerializer
    
    def perform_create(self, serializer):
        """Create input collection and trigger workflow"""
        try:
            # Create input collection with proper user
            input_collection = serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
            
            # Create workflow task using service
            workflow_service = WorkflowService()
            workflow_task = workflow_service.create_scraper_task(input_collection)
            
            if not workflow_task:
                logger.error(f"Failed to create workflow task for input collection {input_collection.id}")
                
        except Exception as e:
            logger.error(f"Error creating input collection: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def available_platforms(self, request):
        """Get all available platforms"""
        platforms = Platform.objects.filter(is_enabled=True)
        data = [
            {
                'id': platform.id,
                'name': platform.name,
                'display_name': platform.display_name,
                'description': platform.description
            }
            for platform in platforms
        ]
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def available_services(self, request, pk=None):
        """Get available services for a platform"""
        platform = get_object_or_404(Platform, pk=pk)
        services = Service.objects.filter(
            platformservices__platform=platform,
            platformservices__is_enabled=True
        ).distinct()
        
        data = [
            {
                'id': service.id,
                'name': service.name,
                'display_name': service.display_name,
                'description': service.description
            }
            for service in services
        ]
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def platform_services(self, request):
        """Get all platform-service combinations"""
        platform_services = PlatformService.objects.filter(
            is_enabled=True,
            platform__is_enabled=True
        ).select_related('platform', 'service')
        
        data = [
            {
                'id': ps.id,
                'platform': {
                    'id': ps.platform.id,
                    'name': ps.platform.name,
                    'display_name': ps.platform.display_name
                },
                'service': {
                    'id': ps.service.id,
                    'name': ps.service.name,
                    'display_name': ps.service.display_name
                },
                'description': ps.description
            }
            for ps in platform_services
        ]
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def workflow_tasks(self, request, pk=None):
        """Get workflow tasks for an input collection"""
        input_collection = get_object_or_404(InputCollection, pk=pk)
        tasks = WorkflowTask.objects.filter(input_collection=input_collection)
        serializer = WorkflowTaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed input collection"""
        try:
            input_collection = get_object_or_404(InputCollection, pk=pk)
            
            # Reset status and create new workflow task
            input_collection.status = 'pending'
            input_collection.save()
            
            workflow_service = WorkflowService()
            workflow_task = workflow_service.create_scraper_task(input_collection)
            
            if workflow_task:
                return Response({'message': 'Input collection retried successfully'})
            else:
                return Response(
                    {'error': 'Failed to retry input collection'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error retrying input collection: {str(e)}")
            return Response(
                {'error': 'Failed to retry input collection'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def configure_job(self, request, pk=None):
        """Configure and create a batch scraper job for an input collection"""
        try:
            logger.info(f"Received configure_job request for input collection {pk}")
            logger.info(f"Request data: {request.data}")
            
            input_collection = get_object_or_404(InputCollection, pk=pk)
            logger.info(f"Found input collection: {input_collection.id}")
            
            # Get job configuration from request
            job_config = {
                'name': request.data.get('name'),
                'num_of_posts': request.data.get('num_of_posts', 10),
                'start_date': request.data.get('start_date'),
                'end_date': request.data.get('end_date'),
                'auto_create_folders': request.data.get('auto_create_folders', True)
            }
            
            logger.info(f"Job config: {job_config}")
            
            # Create batch scraper job using workflow service
            workflow_service = WorkflowService()
            batch_job = workflow_service.configure_input_collection_job(input_collection.id, job_config)
            
            if batch_job:
                logger.info(f"Successfully created batch job {batch_job.id}")
                return Response({
                    'message': 'Batch scraper job configured successfully',
                    'batch_job_id': batch_job.id,
                    'batch_job_name': batch_job.name
                }, status=status.HTTP_201_CREATED)
            else:
                logger.error("Workflow service returned None for batch job")
                return Response(
                    {'error': 'Failed to configure batch scraper job - no BrightData config found or other error'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error configuring job for input collection: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to configure job: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start scraping for an input collection"""
        try:
            logger.info(f"Starting scraping for input collection {pk}")
            
            input_collection = get_object_or_404(InputCollection, pk=pk)
            logger.info(f"Found input collection: {input_collection.id}")
            
            # Check if there's an existing workflow task
            workflow_task = WorkflowTask.objects.filter(input_collection=input_collection).first()
            
            if not workflow_task:
                # Create a new workflow task
                workflow_service = WorkflowService()
                workflow_task = workflow_service.create_scraper_task(input_collection)
                
                if not workflow_task:
                    return Response(
                        {'error': 'Failed to create workflow task'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
                logger.info(f"Created new workflow task: {workflow_task.id}")
            
            # Check if there's a batch job
            batch_job = workflow_task.batch_job
            
            if not batch_job:
                # Create a batch job with default configuration
                workflow_service = WorkflowService()
                batch_job = workflow_service.create_brightdata_batch_job(
                    input_collection_id=input_collection.id,
                    job_config={
                        'name': f"Auto-started job for {input_collection.name}",
                        'num_of_posts': 10,
                        'auto_create_folders': True
                    }
                )
                
                if not batch_job:
                    return Response(
                        {'error': 'Failed to create batch job'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
                logger.info(f"Created new batch job: {batch_job.id}")
            
            # Now trigger the working BrightData scraper directly
            try:
                # Use the new working BrightData trigger endpoint logic
                platform = input_collection.platform_service.platform.name
                urls = input_collection.urls

                # CRITICAL FIX: Create UnifiedRunFolder BEFORE triggering scraper
                from track_accounts.models import UnifiedRunFolder

                # Create a folder for this scraping run
                folder = UnifiedRunFolder.objects.create(
                    name=f"{platform.title()} Data - {input_collection.project.name}",
                    project=input_collection.project,
                    folder_type='job',
                    platform_code=platform.lower(),
                    description=f"Scraped data from {len(urls)} {platform} URL(s)"
                )
                logger.info(f"Created UnifiedRunFolder {folder.id}: {folder.name}")

                # Import the working BrightData scraper
                from brightdata_integration.services import BrightDataAutomatedBatchScraper
                from brightdata_integration.models import BrightDataScraperRequest
                scraper = BrightDataAutomatedBatchScraper()

                # CRITICAL FIX: Create scraper request with folder_id BEFORE triggering
                # This ensures webhook can find and link data properly
                scraper_requests = []
                for url in urls:
                    scraper_request = BrightDataScraperRequest.objects.create(
                        platform=platform.lower(),
                        target_url=url,
                        folder_id=folder.id,  # Link to the folder we just created
                        batch_job=batch_job,
                        status='processing',
                        started_at=timezone.now()
                    )
                    scraper_requests.append(scraper_request)
                    logger.info(f"Created BrightDataScraperRequest {scraper_request.id} for folder {folder.id}")

                # Create and execute batch job with the working format
                batch_job_result = scraper.trigger_scraper(
                    platform=platform,
                    urls=urls
                )

                if batch_job_result and batch_job_result.get('success'):
                    # Update input collection status
                    input_collection.status = 'processing'
                    input_collection.save()

                    # Update scraper requests with snapshot_id from response
                    snapshot_id = batch_job_result.get('snapshot_id')
                    if snapshot_id:
                        for scraper_request in scraper_requests:
                            scraper_request.snapshot_id = snapshot_id
                            scraper_request.save()

                    logger.info(f"Successfully triggered BrightData scraper: {batch_job_result}")
                    return Response({
                        'message': f'BrightData {platform} scraper triggered successfully!',
                        'batch_job_id': batch_job_result.get('batch_job_id'),
                        'folder_id': folder.id,
                        'folder_name': folder.name,
                        'platform': platform,
                        'status': 'processing',
                        'urls_count': len(urls),
                        'data_storage_url': f'/organizations/{input_collection.project.organization_id}/projects/{input_collection.project.id}/data-storage'
                    }, status=status.HTTP_200_OK)
                else:
                    # Clean up folder if scraper failed
                    folder.delete()
                    for scraper_request in scraper_requests:
                        scraper_request.delete()

                    error_msg = batch_job_result.get('error', 'Unknown error') if batch_job_result else 'Failed to trigger scraper'
                    return Response(
                        {'error': f'Failed to trigger BrightData scraper: {error_msg}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as scraper_error:
                logger.error(f"BrightData trigger error: {str(scraper_error)}")
                # Clean up folder and scraper requests on error
                try:
                    if 'folder' in locals():
                        folder.delete()
                    if 'scraper_requests' in locals():
                        for sr in scraper_requests:
                            sr.delete()
                except Exception as cleanup_error:
                    logger.error(f"Cleanup error: {str(cleanup_error)}")

                return Response(
                    {'error': f'BrightData trigger failed: {str(scraper_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error starting scraping for input collection: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to start scraping: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WorkflowTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for workflow task management (read-only)"""
    permission_classes = [AllowAny]  # For testing, use IsAuthenticated in production
    serializer_class = WorkflowTaskSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        project_id = self.request.query_params.get('project')
        
        queryset = WorkflowTask.objects.select_related(
            'input_collection__project', 
            'input_collection__platform_service__platform',
            'input_collection__platform_service__service',
            'batch_job'
        )
        
        # Filter by project if specified
        if project_id:
            queryset = queryset.filter(input_collection__project_id=project_id)
        
        # Filter by user permissions
        # Skip permission check for unauthenticated users during testing
        if user.is_authenticated and not user.is_superuser:
            user_projects = user.projects.all() | user.accessible_projects.all()
            queryset = queryset.filter(input_collection__project__in=user_projects)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get workflow tasks filtered by status"""
        status_filter = request.query_params.get('status')
        if status_filter:
            self.queryset = self.get_queryset().filter(status=status_filter)
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

class ScheduledScrapingTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for scheduled scraping task management"""
    permission_classes = [AllowAny]  # For testing, use IsAuthenticated in production
    serializer_class = ScheduledScrapingTaskSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        project_id = self.request.query_params.get('project')
        
        queryset = ScheduledScrapingTask.objects.select_related(
            'project', 'track_source', 'created_by'
        )
        
        # Filter by project if specified
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by user permissions
        # Skip permission check for unauthenticated users during testing
        if user.is_authenticated and not user.is_superuser:
            user_projects = user.projects.all() | user.accessible_projects.all()
            queryset = queryset.filter(project__in=user_projects)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create scheduled task and set created_by user"""
        try:
            logger.info(f"Creating scheduled task with data: {serializer.validated_data}")
            
            # Handle anonymous user case
            if self.request.user.is_authenticated:
                task = serializer.save(created_by=self.request.user)
            else:
                # For anonymous users, don't set created_by
                task = serializer.save(created_by=None)
            
            logger.info(f"Successfully created scheduled task: {task.id}")
            return task
        except Exception as e:
            logger.error(f"Error creating scheduled task: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Run a scheduled task immediately"""
        try:
            task = get_object_or_404(ScheduledScrapingTask, pk=pk)
            
            # Check if task has a valid platform URL
            platform_url = task.get_platform_url()
            if not platform_url:
                return Response(
                    {'error': f'No {task.platform} URL found for this track source'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a batch scraper job for this task
            from brightdata_integration.models import BrightDataBatchJob
            
            batch_job = BrightDataBatchJob.objects.create(
                name=f"Scheduled_{task.name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
                project=task.project,
                source_folder_ids=[],
                platforms_to_scrape=[task.platform],
                content_types_to_scrape={
                    task.platform: [task.service_type]
                },
                num_of_posts=task.num_of_posts,
                start_date=task.start_date,
                end_date=task.end_date,
                auto_create_folders=task.auto_create_folders,
                status='pending',
                platform_params={
                    'track_source_id': task.track_source.id,
                    'platform': task.platform,
                    'service_type': task.service_type,
                    'scheduled_task_id': task.id,
                    'urls': [platform_url]
                }
            )
            
            # Update task statistics
            task.total_runs += 1
            task.last_run = timezone.now()
            task.update_next_run()
            task.save()
            
            logger.info(f"Created batch job {batch_job.id} for scheduled task {task.id}")
            
            return Response({
                'message': 'Scheduled task executed successfully',
                'batch_job_id': batch_job.id,
                'batch_job_name': batch_job.name
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error running scheduled task: {str(e)}")
            return Response(
                {'error': f'Failed to run scheduled task: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle the active status of a scheduled task"""
        try:
            task = get_object_or_404(ScheduledScrapingTask, pk=pk)
            task.is_active = not task.is_active
            
            if task.is_active:
                task.status = 'active'
                task.update_next_run()
            else:
                task.status = 'paused'
                task.next_run = None
            
            task.save()
            
            return Response({
                'message': f'Scheduled task {"activated" if task.is_active else "paused"} successfully',
                'is_active': task.is_active,
                'status': task.status
            })
            
        except Exception as e:
            logger.error(f"Error toggling scheduled task status: {str(e)}")
            return Response(
                {'error': f'Failed to toggle task status: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ScrapingRunViewSet(viewsets.ModelViewSet):
    """ViewSet for scraping run management"""
    permission_classes = [AllowAny]  # For testing, use IsAuthenticated in production
    serializer_class = ScrapingRunSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        project_id = self.request.query_params.get('project')
        
        queryset = ScrapingRun.objects.select_related(
            'project', 'created_by'
        ).prefetch_related('scraping_jobs')
        
        # Filter by project if specified
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by user permissions
        if user.is_authenticated and not user.is_superuser:
            user_projects = user.projects.all() | user.accessible_projects.all()
            queryset = queryset.filter(project__in=user_projects)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create scraping run with global configuration"""
        try:
            project_id = serializer.validated_data['project'].id
            configuration = serializer.validated_data.get('configuration', {})
            logger.info(f"Creating scraping run for project {project_id} with configuration: {configuration}")
            
            # Create scraping run using service (simplified TrackSource flow)
            workflow_service = WorkflowService()
            scraping_run = workflow_service.create_scraping_run_from_tracksources(
                project_id=project_id,
                configuration=configuration,
                user=self.request.user
            )
            
            # Return the created scraping run
            serializer.instance = scraping_run
            logger.info(f"Successfully created scraping run: {scraping_run.id} - {scraping_run.name}")
            
        except Exception as e:
            logger.error(f"Error creating scraping run: {str(e)}")
            raise
    
    @action(detail=True, methods=['post'])
    def start_run(self, request, pk=None):
        """Start a scraping run"""
        try:
            logger.info(f"Starting scraping run with ID: {pk}")
            scraping_run = get_object_or_404(ScrapingRun, pk=pk)
            logger.info(f"Found scraping run: {scraping_run.id} - {scraping_run.name} - {scraping_run.status}")
            
            if scraping_run.status != 'pending':
                return Response(
                    {'error': 'Run can only be started if it is in pending status'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update run status
            scraping_run.status = 'processing'
            scraping_run.started_at = timezone.now()
            scraping_run.save()
            
            # Start all pending jobs
            pending_jobs = scraping_run.scraping_jobs.filter(status='pending')
            successful_executions = 0
            
            for job in pending_jobs:
                try:
                    # Update job status
                    job.status = 'processing'
                    job.started_at = timezone.now()
                    job.save()
                    
                    # Execute the batch job using BrightData integration
                    if job.batch_job:
                        job.batch_job.status = 'processing'
                        job.batch_job.save()
                        
                        # Execute the batch job
                        scraper = BrightDataAutomatedBatchScraper()
                        success = scraper.execute_batch_job(job.batch_job.id)
                        
                        if success:
                            successful_executions += 1
                            # Job is now processing (sent to BrightData)
                            # Status will be updated to 'completed' or 'failed' via webhook
                            logger.info(f"Successfully sent batch job {job.batch_job.id} to BrightData for scraping job {job.id}")
                        else:
                            job.status = 'failed'
                            job.error_message = 'Failed to execute batch job'
                            job.completed_at = timezone.now()
                            job.save()
                            logger.error(f"Failed to execute batch job {job.batch_job.id} for scraping job {job.id}")
                    else:
                        job.status = 'failed'
                        job.error_message = 'No batch job associated with this scraping job'
                        job.completed_at = timezone.now()
                        job.save()
                        logger.error(f"No batch job found for scraping job {job.id}")
                        
                except Exception as e:
                    job.status = 'failed'
                    job.error_message = str(e)
                    job.save()
                    logger.error(f"Error executing scraping job {job.id}: {str(e)}")
            
            # Run status will be automatically updated by the ScrapingJob.save() method
            # based on the status of individual jobs
            logger.info(f"Scraping run {scraping_run.id} started. Jobs sent to BrightData for processing.")
            
            return Response({
                'message': f'Scraping run started successfully. {successful_executions}/{pending_jobs.count()} jobs sent to BrightData for processing.',
                'total_jobs': pending_jobs.count(),
                'successful_executions': successful_executions
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error starting scraping run: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to start scraping run: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of a scraping run"""
        try:
            scraping_run = get_object_or_404(ScrapingRun, pk=pk)
            
            workflow_service = WorkflowService()
            success = workflow_service.update_scraping_run_status(pk)
            
            if success:
                return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Failed to update status'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error updating scraping run status: {str(e)}")
            return Response(
                {'error': 'Failed to update status'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ScrapingJobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for scraping job management (read-only with retry action)"""
    permission_classes = [AllowAny]  # For testing, use IsAuthenticated in production
    serializer_class = ScrapingJobSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        run_id = self.request.query_params.get('run')
        project_id = self.request.query_params.get('project')
        
        queryset = ScrapingJob.objects.select_related(
            'scraping_run__project', 
            'input_collection__platform_service__platform',
            'input_collection__platform_service__service',
            'batch_job'
        )
        
        # Filter by run if specified
        if run_id:
            queryset = queryset.filter(scraping_run_id=run_id)
        
        # Filter by project if specified
        if project_id:
            queryset = queryset.filter(scraping_run__project_id=project_id)
        
        # Filter by user permissions
        if user.is_authenticated and not user.is_superuser:
            user_projects = user.projects.all() | user.accessible_projects.all()
            queryset = queryset.filter(scraping_run__project__in=user_projects)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed scraping job"""
        try:
            job = get_object_or_404(ScrapingJob, pk=pk)
            
            if job.status != 'failed':
                return Response(
                    {'error': 'Job can only be retried if it is in failed status'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            workflow_service = WorkflowService()
            success = workflow_service.retry_failed_job(pk)
            
            if success:
                return Response({'message': 'Job retry initiated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Failed to retry job'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error retrying job: {str(e)}")
            return Response(
                {'error': 'Failed to retry job'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DirectWorkflowAPIViewSet(viewsets.ViewSet):
    """Direct API endpoints for workflow management"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'], url_path='available-platforms')
    def available_platforms(self, request):
        """Get available platforms for workflow"""
        try:
            platforms = Platform.objects.filter(is_active=True)
            
            platform_data = []
            for platform in platforms:
                # Get available services for this platform
                services = Service.objects.filter(
                    platformservice__platform=platform,
                    platformservice__is_enabled=True
                ).distinct()
                
                platform_info = {
                    'id': platform.id,
                    'name': platform.name,
                    'description': platform.description,
                    'is_active': platform.is_active,
                    'services': [
                        {
                            'id': service.id,
                            'name': service.name,
                            'description': service.description
                        }
                        for service in services
                    ]
                }
                platform_data.append(platform_info)
            
            return Response({
                'platforms': platform_data,
                'count': len(platform_data)
            })
            
        except Exception as e:
            logger.error(f"Error getting available platforms: {str(e)}")
            return Response(
                {'error': 'Failed to get available platforms'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='platform-services')
    def platform_services(self, request):
        """Get available platform-service combinations"""
        try:
            platform_services = PlatformService.objects.filter(
                is_enabled=True
            ).select_related('platform', 'service')
            
            results = [
                {
                    'id': ps.id,
                    'platform': ps.platform.name,
                    'service': ps.service.name,
                    'platform_id': ps.platform.id,
                    'service_id': ps.service.id,
                    'name': f"{ps.platform.name} - {ps.service.name}",
                    'is_enabled': ps.is_enabled,
                    'description': f"{ps.service.description} for {ps.platform.name}" if ps.service.description else f"{ps.platform.name} {ps.service.name}"
                }
                for ps in platform_services
            ]
            
            return Response({
                'platform_services': results,
                'count': len(results)
            })
            
        except Exception as e:
            logger.error(f"Error getting platform services: {str(e)}")
            return Response(
                {'error': 'Failed to get platform services'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

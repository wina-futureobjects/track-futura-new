from typing import List, Optional
from django.db import transaction
from .models import InputCollection, WorkflowTask
from brightdata_integration.models import BatchScraperJob, BrightdataConfig
from users.models import Project, PlatformService
import logging

logger = logging.getLogger(__name__)

class WorkflowService:
    """Service class for managing workflow operations"""
    
    @transaction.atomic
    def create_input_collection(self, project_id: int, platform_service_id: int, urls: List[str]) -> InputCollection:
        """
        Create input collection and trigger workflow
        
        Args:
            project_id: ID of the project
            platform_service_id: ID of the platform-service combination
            urls: List of URLs for scraping
            
        Returns:
            InputCollection: Created input collection instance
        """
        try:
            # Validate project exists
            project = Project.objects.get(id=project_id)
            
            # Validate platform service exists and is enabled
            platform_service = PlatformService.objects.get(
                id=platform_service_id,
                is_enabled=True,
                platform__is_enabled=True
            )
            
            # Create input collection
            input_collection = InputCollection.objects.create(
                project=project,
                platform_service=platform_service,
                urls=urls,
                status='pending'
            )
            
            logger.info(f"Created input collection {input_collection.id} for project {project.name}")
            
            # Auto-create scraper task
            workflow_task = self.create_scraper_task(input_collection)
            
            return input_collection
            
        except Project.DoesNotExist:
            raise ValueError(f"Project with ID {project_id} does not exist")
        except PlatformService.DoesNotExist:
            raise ValueError(f"Platform service with ID {platform_service_id} does not exist or is disabled")
        except Exception as e:
            logger.error(f"Error creating input collection: {str(e)}")
            raise
    
    def create_scraper_task(self, input_collection: InputCollection) -> Optional[WorkflowTask]:
        """
        Create scraper task from input collection
        
        Args:
            input_collection: InputCollection instance
            
        Returns:
            WorkflowTask: Created workflow task instance or None if failed
        """
        try:
            # Get or create BrightData config for the platform-service combination
            config = self._get_or_create_brightdata_config(input_collection.platform_service)
            
            if not config:
                logger.error(f"No BrightData config found for platform service {input_collection.platform_service}")
                input_collection.status = 'failed'
                input_collection.save()
                return None
            
            # Create batch scraper job
            batch_job = self._create_batch_scraper_job(input_collection, config)
            
            if not batch_job:
                logger.error(f"Failed to create batch scraper job for input collection {input_collection.id}")
                input_collection.status = 'failed'
                input_collection.save()
                return None
            
            # Create workflow task
            workflow_task = WorkflowTask.objects.create(
                input_collection=input_collection,
                batch_job=batch_job,
                status='pending'
            )
            
            # Update input collection status
            input_collection.status = 'processing'
            input_collection.save()
            
            logger.info(f"Created workflow task {workflow_task.id} for input collection {input_collection.id}")
            
            return workflow_task
            
        except Exception as e:
            logger.error(f"Error creating scraper task: {str(e)}")
            input_collection.status = 'failed'
            input_collection.save()
            return None
    
    def _get_or_create_brightdata_config(self, platform_service: PlatformService) -> Optional[BrightdataConfig]:
        """
        Get or create BrightData configuration for platform-service combination
        
        Args:
            platform_service: PlatformService instance
            
        Returns:
            BrightdataConfig: Configuration instance or None if not found
        """
        try:
            # Try to find existing config
            config = BrightdataConfig.objects.filter(
                platform__icontains=platform_service.platform.name,
                is_active=True
            ).first()
            
            if config:
                return config
            
            # If no config found, create a default one (this would need dataset_id)
            logger.warning(f"No BrightData config found for {platform_service.platform.name}_{platform_service.service.name}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting BrightData config: {str(e)}")
            return None
    
    def _create_batch_scraper_job(self, input_collection: InputCollection, config: BrightdataConfig) -> Optional[BatchScraperJob]:
        """
        Create batch scraper job from input collection
        
        Args:
            input_collection: InputCollection instance
            config: BrightdataConfig instance
            
        Returns:
            BatchScraperJob: Created batch job instance or None if failed
        """
        try:
            # Determine content type based on service
            service_name = input_collection.platform_service.service.name.lower()
            content_type = self._map_service_to_content_type(service_name)
            
            # Create batch scraper job with platform service information
            batch_job = BatchScraperJob.objects.create(
                name=f"Workflow_{input_collection.id}_{content_type}",
                project=input_collection.project,
                source_folder_ids=[],  # Will be populated by the scraper service
                platforms_to_scrape=[input_collection.platform_service.platform.name],
                content_types_to_scrape={
                    input_collection.platform_service.platform.name: [content_type]
                },
                num_of_posts=10,  # Default value
                auto_create_folders=True,
                status='pending',
                platform_params={
                    'platform_service_id': input_collection.platform_service.id,
                    'platform_name': input_collection.platform_service.platform.name,
                    'service_name': input_collection.platform_service.service.name
                }
            )
            
            logger.info(f"Created batch scraper job {batch_job.id} for input collection {input_collection.id}")
            
            return batch_job
            
        except Exception as e:
            logger.error(f"Error creating batch scraper job: {str(e)}")
            return None
    
    def _map_service_to_content_type(self, service_name: str) -> str:
        """
        Map service name to content type for BrightData
        
        Args:
            service_name: Service name (e.g., 'posts', 'comments', 'reels')
            
        Returns:
            str: Content type for BrightData
        """
        mapping = {
            'posts': 'post',
            'comments': 'comment',
            'reels': 'reel',
            'profiles': 'profile',
            'videos': 'video'
        }
        
        return mapping.get(service_name, 'post')
    
    def update_workflow_status(self, workflow_task_id: int, status: str) -> bool:
        """
        Update workflow task status
        
        Args:
            workflow_task_id: ID of the workflow task
            status: New status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            workflow_task = WorkflowTask.objects.get(id=workflow_task_id)
            workflow_task.status = status
            workflow_task.save()
            
            # Update input collection status based on workflow task status
            if status in ['completed', 'failed']:
                input_collection = workflow_task.input_collection
                input_collection.status = status
                input_collection.save()
            
            logger.info(f"Updated workflow task {workflow_task_id} status to {status}")
            return True
            
        except WorkflowTask.DoesNotExist:
            logger.error(f"Workflow task {workflow_task_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating workflow status: {str(e)}")
            return False 
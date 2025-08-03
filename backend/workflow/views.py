from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import InputCollection, WorkflowTask
from .serializers import (
    InputCollectionSerializer, 
    WorkflowTaskSerializer, 
    InputCollectionCreateSerializer
)
from .services import WorkflowService
from users.models import Platform, PlatformService
from users.serializers import PlatformSerializer, ServiceSerializer
import logging

logger = logging.getLogger(__name__)

class WorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow management"""
    permission_classes = [AllowAny]  # For testing, use IsAuthenticated in production
    serializer_class = InputCollectionSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions and project"""
        user = self.request.user
        project_id = self.request.query_params.get('project')
        
        queryset = InputCollection.objects.select_related(
            'project', 'platform_service__platform', 'platform_service__service'
        )
        
        # Filter by project if specified
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by user permissions (users can only see their own projects)
        # Skip permission check for unauthenticated users during testing
        if user.is_authenticated and not user.is_superuser:
            # For regular users, filter by projects they have access to
            user_projects = user.projects.all() | user.accessible_projects.all()
            queryset = queryset.filter(project__in=user_projects)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return InputCollectionCreateSerializer
        return InputCollectionSerializer
    
    def perform_create(self, serializer):
        """Create input collection using workflow service"""
        try:
            workflow_service = WorkflowService()
            input_collection = workflow_service.create_input_collection(
                project_id=serializer.validated_data['project'].id,
                platform_service_id=serializer.validated_data['platform_service'].id,
                urls=serializer.validated_data['urls']
            )
            return input_collection
        except Exception as e:
            logger.error(f"Error creating input collection: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def available_platforms(self, request):
        """Get available platforms for current user"""
        try:
            platforms = Platform.objects.filter(is_enabled=True)
            serializer = PlatformSerializer(platforms, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting available platforms: {str(e)}")
            return Response(
                {'error': 'Failed to get available platforms'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def available_services(self, request, pk=None):
        """Get available services for platform"""
        try:
            platform = get_object_or_404(Platform, pk=pk, is_enabled=True)
            services = platform.get_available_services()
            serializer = ServiceSerializer([ps.service for ps in services], many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting available services: {str(e)}")
            return Response(
                {'error': 'Failed to get available services'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def platform_services(self, request):
        """Get all available platform-service combinations"""
        try:
            platform_services = PlatformService.objects.filter(
                is_enabled=True,
                platform__is_enabled=True
            ).select_related('platform', 'service')
            
            data = []
            for ps in platform_services:
                data.append({
                    'id': ps.id,
                    'platform': PlatformSerializer(ps.platform).data,
                    'service': ServiceSerializer(ps.service).data,
                    'is_enabled': ps.is_enabled,
                    'description': ps.description
                })
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error getting platform services: {str(e)}")
            return Response(
                {'error': 'Failed to get platform services'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def workflow_tasks(self, request, pk=None):
        """Get workflow tasks for an input collection"""
        try:
            input_collection = get_object_or_404(InputCollection, pk=pk)
            workflow_tasks = WorkflowTask.objects.filter(
                input_collection=input_collection
            ).select_related('batch_job')
            
            serializer = WorkflowTaskSerializer(workflow_tasks, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting workflow tasks: {str(e)}")
            return Response(
                {'error': 'Failed to get workflow tasks'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed input collection"""
        try:
            input_collection = get_object_or_404(InputCollection, pk=pk)
            
            if input_collection.status != 'failed':
                return Response(
                    {'error': 'Only failed input collections can be retried'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
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

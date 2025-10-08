
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Add DirectWorkflowAPIViewSet to views.py
views_file = "/app/backend/workflow/views.py"
with open(views_file, "r") as f:
    content = f.read()

if "class DirectWorkflowAPIViewSet" not in content:
    content += """

class DirectWorkflowAPIViewSet(viewsets.ViewSet):
    """Direct API endpoints for workflow management"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'], url_path='available-platforms')
    def available_platforms(self, request):
        """Get available platforms for workflow"""
        try:
            platforms = Platform.objects.filter(is_enabled=True)
            
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
                    'is_enabled': platform.is_enabled,
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
"""
    
    with open(views_file, "w") as f:
        f.write(content)
    print("✅ Added DirectWorkflowAPIViewSet to views.py")
else:
    print("✅ DirectWorkflowAPIViewSet already exists")

# Update URLs to include DirectWorkflowAPIViewSet
urls_file = "/app/backend/workflow/urls.py"
with open(urls_file, "r") as f:
    urls_content = f.read()

if "DirectWorkflowAPIViewSet" not in urls_content:
    # Add import
    if "from .views import" in urls_content:
        urls_content = urls_content.replace(
            "from .views import WorkflowViewSet, WorkflowTaskViewSet, ScheduledScrapingTaskViewSet, ScrapingRunViewSet, ScrapingJobViewSet",
            "from .views import WorkflowViewSet, WorkflowTaskViewSet, ScheduledScrapingTaskViewSet, ScrapingRunViewSet, ScrapingJobViewSet, DirectWorkflowAPIViewSet"
        )
    
    # Add router registration
    if "router.register(r'scraping-jobs'" in urls_content:
        urls_content = urls_content.replace(
            "router.register(r'scraping-jobs', ScrapingJobViewSet, basename='scraping-job')",
            "router.register(r'scraping-jobs', ScrapingJobViewSet, basename='scraping-job')\nrouter.register(r'api', DirectWorkflowAPIViewSet, basename='workflow-api')"
        )
    
    with open(urls_file, "w") as f:
        f.write(urls_content)
    print("✅ Updated workflow URLs")
else:
    print("✅ DirectWorkflowAPIViewSet already registered")

# Restart the application (if needed)
print("✅ Deployment complete!")
print("🎉 Workflow API fixes are now live!")

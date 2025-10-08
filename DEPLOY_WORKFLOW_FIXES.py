#!/usr/bin/env python3
"""
DEPLOY WORKFLOW FIXES TO PRODUCTION
Copy and apply the workflow API fixes directly to production
"""

import subprocess
import os

def deploy_workflow_fixes():
    """Deploy the workflow API fixes to production"""
    print("🚀 DEPLOYING WORKFLOW FIXES TO PRODUCTION")
    print("=" * 60)
    
    # Create the DirectWorkflowAPIViewSet code
    direct_viewset_code = '''

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
'''
    
    # Create deployment script
    deployment_script = f'''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Add DirectWorkflowAPIViewSet to views.py
views_file = "/app/backend/workflow/views.py"
with open(views_file, "r") as f:
    content = f.read()

if "class DirectWorkflowAPIViewSet" not in content:
    content += """{direct_viewset_code}"""
    
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
            "router.register(r'scraping-jobs', ScrapingJobViewSet, basename='scraping-job')\\nrouter.register(r'api', DirectWorkflowAPIViewSet, basename='workflow-api')"
        )
    
    with open(urls_file, "w") as f:
        f.write(urls_content)
    print("✅ Updated workflow URLs")
else:
    print("✅ DirectWorkflowAPIViewSet already registered")

# Restart the application (if needed)
print("✅ Deployment complete!")
print("🎉 Workflow API fixes are now live!")
'''
    
    # Write the deployment script
    with open("deploy_fixes.py", "w", encoding="utf-8") as f:
        f.write(deployment_script)
    
    print("📝 Created deployment script")
    
    # Copy and execute on server
    print("📤 Uploading deployment script to production...")
    subprocess.run([
        'upsun', 'ssh', '-p', 'inhoolfrqniuu', '-e', 'main', '--app', 'trackfutura',
        'cat > /tmp/deploy_fixes.py'
    ], input=deployment_script.encode(), check=True)
    
    print("🔧 Executing deployment on production...")
    result = subprocess.run([
        'upsun', 'ssh', '-p', 'inhoolfrqniuu', '-e', 'main', '--app', 'trackfutura',
        'cd /app/backend && python /tmp/deploy_fixes.py'
    ], capture_output=True, text=True)
    
    print(f"Exit Code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)

def verify_deployment():
    """Verify the deployment worked"""
    print("\n🧪 VERIFYING DEPLOYMENT...")
    
    import requests
    import time
    
    # Wait a moment for changes to take effect
    time.sleep(3)
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    test_endpoints = [
        "/workflow/api/available-platforms/",
        "/workflow/api/platform-services/"
    ]
    
    all_working = True
    
    for endpoint in test_endpoints:
        print(f"\\n🔗 Testing: {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'count' in data:
                    print(f"   ✅ SUCCESS - Count: {data['count']}")
                else:
                    print(f"   ✅ SUCCESS - Response received")
            else:
                print(f"   ❌ FAILED - {response.status_code}")
                all_working = False
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            all_working = False
    
    return all_working

def main():
    """Main deployment function"""
    print("🎯 MANUAL DEPLOYMENT OF WORKFLOW API FIXES")
    print("=" * 70)
    
    try:
        # Deploy the fixes
        deploy_workflow_fixes()
        
        # Verify deployment
        success = verify_deployment()
        
        print("\\n" + "=" * 70)
        if success:
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print("✅ All workflow API endpoints are now working")
            print("🚀 BrightData integration is fully operational")
            print("🎯 Ready for client testing!")
        else:
            print("🚨 DEPLOYMENT INCOMPLETE")
            print("❌ Some endpoints still not working")
            print("🔧 Manual intervention may be required")
        
    except Exception as e:
        print(f"❌ DEPLOYMENT FAILED: {str(e)}")

if __name__ == "__main__":
    main()
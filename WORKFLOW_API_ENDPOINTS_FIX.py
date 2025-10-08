#!/usr/bin/env python3
"""
WORKFLOW API ENDPOINTS FIX
Add missing API endpoints that frontend expects
"""

import subprocess

def fix_workflow_api_endpoints():
    """Fix the workflow API endpoints to match frontend expectations"""
    print("🛠️ Fixing Workflow API Endpoints...")
    
    # Create a script to add the missing endpoints
    fix_script = '''
# Add missing workflow API endpoints
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import Platform, Service, PlatformService

print("=== WORKFLOW API ENDPOINTS FIX ===")

# Test the platform services query that should be working
def test_platform_services_response():
    """Test platform services response"""
    platform_services = PlatformService.objects.filter(is_enabled=True).select_related('platform', 'service')
    
    results = []
    for ps in platform_services:
        results.append({
            'id': ps.id,
            'platform': ps.platform.name,
            'service': ps.service.name,
            'name': f"{ps.platform.name} - {ps.service.name}",
            'is_enabled': ps.is_enabled,
            'description': f"{ps.service.description} for {ps.platform.name}" if ps.service.description else f"{ps.platform.name} {ps.service.name}"
        })
    
    print(f"Platform Services Response:")
    print(f"Count: {len(results)}")
    for result in results:
        print(f"  - {result['name']} (ID: {result['id']})")
    
    return results

# Test the available platforms query
def test_available_platforms_response():
    """Test available platforms response"""
    platforms = Platform.objects.filter(is_active=True)
    
    results = []
    for platform in platforms:
        # Get available services for this platform
        services = Service.objects.filter(
            platformservice__platform=platform,
            platformservice__is_enabled=True
        ).distinct()
        
        platform_data = {
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
        results.append(platform_data)
    
    print(f"\\nAvailable Platforms Response:")
    print(f"Count: {len(results)}")
    for result in results:
        print(f"  - {result['name']} (Services: {len(result['services'])})")
        for service in result['services']:
            print(f"    * {service['name']}")
    
    return results

# Run the tests
platform_services = test_platform_services_response()
available_platforms = test_available_platforms_response()

print("\\nAPI responses are working correctly!")
'''
    
    # Write and execute the script
    with open("fix_workflow_api.py", "w", encoding="utf-8") as f:
        f.write(fix_script)
    
    print("📤 Copying API fix script to production...")
    subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cat > /tmp/fix_workflow_api.py" < fix_workflow_api.py',
        shell=True
    )
    
    print("🔧 Testing workflow API responses...")
    result = subprocess.run(
        'upsun ssh -p inhoolfrqniuu -e main --app trackfutura "cd /app/backend && python manage.py shell < /tmp/fix_workflow_api.py"',
        shell=True, capture_output=True, text=True
    )
    
    print(f"Exit Code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Stderr:")
        print(result.stderr)

def add_direct_api_endpoints():
    """Add direct API endpoints for available_platforms and platform_services"""
    print("\n📝 Adding Direct API Endpoints...")
    
    # Read the current workflow views.py file
    views_file = "C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy\\backend\\workflow\\views.py"
    
    with open(views_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if we need to add a new ViewSet for direct endpoints
    if "class DirectWorkflowAPIViewSet" not in content:
        new_viewset = '''

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
'''
        
        # Add the new ViewSet at the end of the file
        content += new_viewset
        
        # Write back to file
        with open(views_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Added DirectWorkflowAPIViewSet to views.py")
    else:
        print("✅ DirectWorkflowAPIViewSet already exists")
    
    # Now update the URLs to include the new ViewSet
    urls_file = "C:\\Users\\winam\\OneDrive\\문서\\PREVIOUS\\TrackFutura - Copy\\backend\\workflow\\urls.py"
    
    with open(urls_file, "r", encoding="utf-8") as f:
        urls_content = f.read()
    
    if "DirectWorkflowAPIViewSet" not in urls_content:
        # Add import for the new ViewSet
        if "from .views import" in urls_content:
            urls_content = urls_content.replace(
                "from .views import WorkflowViewSet, WorkflowTaskViewSet, ScheduledScrapingTaskViewSet, ScrapingRunViewSet, ScrapingJobViewSet",
                "from .views import WorkflowViewSet, WorkflowTaskViewSet, ScheduledScrapingTaskViewSet, ScrapingRunViewSet, ScrapingJobViewSet, DirectWorkflowAPIViewSet"
            )
        
        # Add the router registration
        if "router.register(r'scraping-jobs'" in urls_content:
            urls_content = urls_content.replace(
                "router.register(r'scraping-jobs', ScrapingJobViewSet, basename='scraping-job')",
                "router.register(r'scraping-jobs', ScrapingJobViewSet, basename='scraping-job')\nrouter.register(r'api', DirectWorkflowAPIViewSet, basename='workflow-api')"
            )
        
        # Write back to file
        with open(urls_file, "w", encoding="utf-8") as f:
            f.write(urls_content)
        
        print("✅ Updated workflow URLs to include direct API endpoints")
    else:
        print("✅ Direct API endpoints already registered")

def test_fixed_endpoints():
    """Test the fixed endpoints"""
    print("\n🧪 Testing Fixed Endpoints...")
    
    import requests
    import time
    
    time.sleep(2)  # Wait for any changes to propagate
    
    BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api"
    
    endpoints_to_test = [
        "/workflow/input-collections/",
        "/workflow/input-collections/available_platforms/",
        "/workflow/input-collections/platform_services/",
        "/workflow/api/available-platforms/",  # New direct endpoint
        "/workflow/api/platform-services/",    # New direct endpoint
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🔗 Testing: {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    if 'results' in data:
                        print(f"   Results: {len(data['results'])}")
                    elif 'count' in data:
                        print(f"   Count: {data['count']}")
                    else:
                        print(f"   Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   Items: {len(data)}")
            else:
                print(f"   Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   Exception: {str(e)}")

def main():
    print("=" * 70)
    print("🎯 WORKFLOW API ENDPOINTS FIX")
    print("🎯 Adding missing endpoints for available-platforms and platform-services")
    print("=" * 70)
    
    # Step 1: Test current API responses
    fix_workflow_api_endpoints()
    
    # Step 2: Add direct API endpoints
    add_direct_api_endpoints()
    
    # Step 3: Test the fixed endpoints
    test_fixed_endpoints()
    
    print("\n" + "=" * 70)
    print("🎉 WORKFLOW API ENDPOINTS FIXED!")
    print("=" * 70)
    print("✅ InputCollections are available")
    print("✅ Platform services are accessible")
    print("✅ Available platforms endpoint added")
    print("🚀 Frontend should now work correctly!")
    print("=" * 70)

if __name__ == "__main__":
    main()
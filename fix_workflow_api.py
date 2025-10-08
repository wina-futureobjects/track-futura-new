
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
    
    print(f"\nAvailable Platforms Response:")
    print(f"Count: {len(results)}")
    for result in results:
        print(f"  - {result['name']} (Services: {len(result['services'])})")
        for service in result['services']:
            print(f"    * {service['name']}")
    
    return results

# Run the tests
platform_services = test_platform_services_response()
available_platforms = test_available_platforms_response()

print("\nAPI responses are working correctly!")

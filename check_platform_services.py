#!/usr/bin/env python3
"""
Check and fix platform services in production
"""
import requests
import json

BASE_URL = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"

def check_platform_services():
    try:
        print("🔍 CHECKING PLATFORM SERVICES IN PRODUCTION")
        print("=" * 50)
        
        # Check platform services endpoint
        platform_url = f"{BASE_URL}/api/workflow/platform-services/"
        
        print(f"Checking: {platform_url}")
        response = requests.get(platform_url)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            services = response.json()
            print(f"Found {len(services)} platform services:")
            for service in services:
                print(f"  - ID: {service.get('id')} | Platform: {service.get('platform', {}).get('name')} | Service: {service.get('service', {}).get('name')}")
        else:
            print(f"❌ Failed to get platform services")
            
        # Also check individual platform and service endpoints
        print(f"\n🔍 Checking platforms...")
        platforms_url = f"{BASE_URL}/api/workflow/platforms/"
        platforms_response = requests.get(platforms_url)
        print(f"Platforms status: {platforms_response.status_code}")
        if platforms_response.status_code == 200:
            platforms = platforms_response.json()
            print(f"Found {len(platforms)} platforms:")
            for p in platforms:
                print(f"  - {p.get('name')}")
        
        print(f"\n🔍 Checking services...")
        services_url = f"{BASE_URL}/api/workflow/services/"
        services_response = requests.get(services_url)
        print(f"Services status: {services_response.status_code}")
        if services_response.status_code == 200:
            services = services_response.json()
            print(f"Found {len(services)} services:")
            for s in services:
                print(f"  - {s.get('name')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_platform_services()
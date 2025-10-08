#!/usr/bin/env python
"""
Check if report templates exist in production
"""
import requests
import json

def check_production_templates():
    print("🔍 CHECKING PRODUCTION REPORT TEMPLATES")
    print("="*50)
    
    base_url = 'https://trackfutura.futureobjects.io/api'
    
    # Login first
    auth_response = requests.post(
        f'{base_url}/users/login/',
        json={'username': 'superadmin', 'password': 'admin123'},
        timeout=30
    )
    
    if auth_response.status_code == 200:
        token = auth_response.json().get('access_token', auth_response.json().get('token'))
        headers = {'Authorization': f'Token {token}'}
        
        print("✅ Login successful")
        
        # Check templates
        templates_response = requests.get(
            f'{base_url}/reports/templates/',
            headers=headers,
            timeout=30
        )
        
        print(f"Templates API status: {templates_response.status_code}")
        
        if templates_response.status_code == 200:
            templates = templates_response.json()
            print(f"Found {len(templates)} templates")
            
            if len(templates) == 0:
                print("❌ NO TEMPLATES FOUND! This is why the marketplace is empty.")
                print("🔧 Need to populate templates in production database")
                return False
            else:
                print("✅ Templates exist:")
                for t in templates[:5]:
                    name = t.get('name', 'Unknown')
                    template_type = t.get('template_type', 'Unknown')
                    print(f"  - {name} ({template_type})")
                return True
        else:
            print(f"Templates API failed: {templates_response.text[:200]}")
            return False
    else:
        print(f"Login failed: {auth_response.status_code}")
        return False

if __name__ == '__main__':
    success = check_production_templates()
    
    if not success:
        print("\n🚀 SOLUTION:")
        print("   Need to run: python manage.py populate_report_templates")
        print("   Or create templates manually in Django admin")
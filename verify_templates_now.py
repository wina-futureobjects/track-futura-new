#!/usr/bin/env python3
"""
Verify if the report templates are now available after running populate_report_templates
"""

import requests
import json

# Try to get templates from the production API
def check_templates():
    try:
        # Login to get auth token
        login_url = "https://trackfutura-app-api-main-inhoolfrqniuu.up.railway.app/api/auth/login/"
        login_data = {
            'username': 'winam',
            'password': 'Sniped@10'
        }
        
        session = requests.Session()
        response = session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            
            # Set auth header
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # Check templates
            templates_url = "https://trackfutura-app-api-main-inhoolfrqniuu.up.railway.app/api/reports/templates/"
            templates_response = session.get(templates_url, headers=headers)
            
            print(f"🔍 CHECKING TEMPLATES AFTER populate_report_templates")
            print(f"==================================================")
            print(f"Templates API status: {templates_response.status_code}")
            
            if templates_response.status_code == 200:
                templates = templates_response.json()
                print(f"Found {len(templates)} templates")
                
                if len(templates) > 0:
                    print("✅ SUCCESS! Templates are now available:")
                    for template in templates:
                        print(f"   📊 {template.get('name', 'Unknown')} - {template.get('template_type', 'Unknown type')}")
                    print(f"\n🎉 REPORT MARKETPLACE SHOULD NOW BE POPULATED!")
                else:
                    print("❌ Still no templates found")
                    
                return templates
            else:
                print(f"❌ Failed to get templates: {templates_response.text}")
                return None
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking templates: {e}")
        return None

if __name__ == "__main__":
    check_templates()
#!/usr/bin/env python3
"""
Production Folder Diagnostic Script
Diagnoses the "No sources found in folder 1" error in production
"""

import requests
import json

def check_production_folders():
    base_url = 'https://trackfutura.futureobjects.io'
    
    print('🔍 PRODUCTION FOLDER DIAGNOSTIC')
    print('=' * 50)
    
    # Check specific folder 1 endpoints
    print('\n📂 CHECKING FOLDER ID 1:')
    folder_1_endpoints = [
        '/api/brightdata/webhook-results/job/1/',
        '/api/track-accounts/unified-run-folders/1/',
        '/api/track-accounts/report-folders/1/',
        '/api/track-accounts/run-folders/1/'
    ]
    
    for endpoint in folder_1_endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'  📍 {endpoint}')
            print(f'     Status: {response.status_code}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f'     ✅ Response: {json.dumps(data, indent=2)[:200]}...')
                except:
                    print(f'     ✅ Non-JSON response: {response.text[:100]}...')
            elif response.status_code == 404:
                print(f'     ❌ Not Found - Folder 1 does not exist')
            else:
                print(f'     ⚠️  Error {response.status_code}: {response.text[:100]}')
                
        except Exception as e:
            print(f'     🚨 Connection Error: {str(e)[:100]}')
    
    # Check available folders
    print('\n📋 CHECKING AVAILABLE FOLDERS:')
    folder_list_endpoints = [
        '/api/track-accounts/unified-run-folders/',
        '/api/track-accounts/report-folders/',
        '/api/brightdata/webhook-results/'
    ]
    
    for endpoint in folder_list_endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'  📍 {endpoint}')
            print(f'     Status: {response.status_code}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        results = data['results']
                        print(f'     ✅ Found {len(results)} folders')
                        for i, folder in enumerate(results[:3]):
                            folder_id = folder.get('id', 'N/A')
                            folder_name = folder.get('name', 'N/A')
                            print(f'        - ID: {folder_id}, Name: {folder_name}')
                    elif isinstance(data, list):
                        print(f'     ✅ Found {len(data)} items')
                    else:
                        print(f'     ✅ Response: {str(data)[:100]}')
                except:
                    print(f'     ✅ Non-JSON response length: {len(response.text)}')
            else:
                print(f'     ❌ Error {response.status_code}')
                
        except Exception as e:
            print(f'     🚨 Connection Error: {str(e)[:100]}')
    
    # Check webhook endpoints with common folder names
    print('\n🎯 CHECKING WEBHOOK ENDPOINTS:')
    webhook_tests = [
        '/api/brightdata/webhook-results/Job%201/1/',
        '/api/brightdata/webhook-results/Job%202/1/',
        '/api/brightdata/webhook-results/Job%203/1/',
        '/api/brightdata/webhook-results/Test%20Job/1/'
    ]
    
    for endpoint in webhook_tests:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'  📍 {endpoint}')
            print(f'     Status: {response.status_code}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f'     ✅ Webhook data available: {data.get("total_results", 0)} results')
                    else:
                        print(f'     ⚠️  No webhook data: {data.get("message", "Unknown")}')
                except:
                    print(f'     ✅ Response received')
            elif response.status_code == 404:
                print(f'     ❌ Webhook data not found')
            else:
                print(f'     ⚠️  Status {response.status_code}')
                
        except Exception as e:
            print(f'     🚨 Error: {str(e)[:100]}')
    
    print('\n' + '=' * 50)
    print('🎯 DIAGNOSIS COMPLETE')

if __name__ == '__main__':
    check_production_folders()
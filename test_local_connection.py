#!/usr/bin/env python3

import requests
import json

def test_local_connection():
    print('🔧 TESTING LOCAL FRONTEND-BACKEND CONNECTION')
    print('=' * 50)

    # Test backend directly
    print('\n1. TESTING BACKEND DIRECTLY:')
    backend_url = 'http://127.0.0.1:8080'
    
    try:
        # Test health endpoint
        response = requests.get(f'{backend_url}/api/health/', timeout=10)
        print(f'   Health check: {response.status_code}')
        
        if response.status_code == 200:
            print('   ✅ Backend is responding!')
        else:
            print(f'   ❌ Backend issue: {response.text}')
            
    except Exception as e:
        print(f'   ❌ Backend connection failed: {str(e)}')

    # Test BrightData endpoint
    print('\n2. TESTING BRIGHTDATA ENDPOINT:')
    
    test_data = {
        'platform': 'instagram',
        'data_type': 'posts',
        'folder_id': 1,
        'urls': ['https://www.instagram.com/nike/']
    }
    
    try:
        response = requests.post(f'{backend_url}/api/brightdata/trigger-scraper/',
                               json=test_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ BrightData endpoint working!')
            print(f'   Batch Job: {result.get("batch_job_id")}')
        else:
            print(f'   ❌ BrightData failed: {response.text}')
            
    except Exception as e:
        print(f'   ❌ BrightData error: {str(e)}')

    # Test CORS headers
    print('\n3. TESTING CORS CONFIGURATION:')
    
    try:
        # Make a preflight request like the frontend would
        response = requests.options(f'{backend_url}/api/brightdata/trigger-scraper/',
                                  headers={
                                      'Origin': 'http://localhost:5185',
                                      'Access-Control-Request-Method': 'POST',
                                      'Access-Control-Request-Headers': 'Content-Type'
                                  })
        
        print(f'   Preflight status: {response.status_code}')
        print(f'   CORS headers: {dict(response.headers)}')
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        if cors_origin:
            print(f'   ✅ CORS configured: {cors_origin}')
        else:
            print('   ❌ CORS not configured properly!')
            
    except Exception as e:
        print(f'   ❌ CORS test error: {str(e)}')

    print('\n🎯 SOLUTION:')
    print('   Frontend: http://localhost:5185/')
    print('   Backend: http://127.0.0.1:8080/')
    print('   Endpoint: /api/brightdata/trigger-scraper/')

if __name__ == '__main__':
    test_local_connection()
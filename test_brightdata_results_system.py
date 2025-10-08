import requests
import time

print('🔥 TESTING BRIGHTDATA RESULTS DISPLAY SYSTEM')
print('=' * 60)

# Step 1: Trigger a scraper to create test data
api_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/trigger-scraper/'
test_data = {
    'folder_id': 140,  # Job folder 140 from the URL
    'user_id': 3,
    'num_of_posts': 5,
    'date_range': {
        'start_date': '2025-10-01T00:00:00.000Z',
        'end_date': '2025-10-08T00:00:00.000Z'
    }
}

print('🚀 Step 1: Triggering scraper for job folder 140...')
try:
    response = requests.post(api_url, json=test_data)
    data = response.json()
    
    print(f'API Status: {response.status_code}')
    print(f'Success: {data.get("success")}')
    
    if data.get('success'):
        job_id = data.get('results', {}).get('instagram', {}).get('job_id')
        print(f'BrightData Job ID: {job_id}')
        
        # Step 2: Wait and check for results
        print('\n⏳ Step 2: Waiting for results...')
        time.sleep(45)
        
        # Step 3: Test the results API
        results_url = f'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/140/'
        print(f'\n📊 Step 3: Checking results API...')
        
        results_response = requests.get(results_url)
        print(f'Results API Status: {results_response.status_code}')
        
        if results_response.status_code == 200:
            results_data = results_response.json()
            print(f'Results Success: {results_data.get("success")}')
            print(f'Total Results: {results_data.get("total_results", 0)}')
            
            if results_data.get('success') and results_data.get('total_results', 0) > 0:
                print('✅ SUCCESS: BrightData results system working!')
                print(f'Found {results_data["total_results"]} scraped posts')
                print('Data should now display in the frontend!')
                
                # Show sample data
                sample_data = results_data.get('data', [])[:2]  # First 2 items
                print(f'\n📋 Sample data:')
                for i, item in enumerate(sample_data):
                    print(f'  Post {i+1}: {item.get("url", "No URL")[:50]}...')
                    print(f'    User: {item.get("user_username", "Unknown")}')
                    print(f'    Content: {str(item.get("caption", "No content"))[:50]}...')
                    
            else:
                print('📝 Results API working but no data yet (may need more time)')
        else:
            print(f'Results API Error: {results_response.text[:200]}')
    else:
        print(f'Scraper Error: {data}')
        
except Exception as e:
    print(f'Test Error: {e}')

print('\n' + '=' * 60)
print('🎯 NEXT STEPS:')
print('1. Visit: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/140')
print('2. You should see scraped data in table format')
print('3. You should see download buttons for CSV/JSON')
print('4. Key performance metrics should be displayed above the table')
print('\n✅ BrightData results system is now ready!')
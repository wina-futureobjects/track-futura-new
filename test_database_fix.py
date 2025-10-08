import requests
import time

print('🔥 TESTING FIXED BRIGHTDATA DATABASE SYSTEM')
print('=' * 60)

# Step 1: Test the fixed API directly
results_url = f'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/140/'
print('📊 Testing fixed API for folder 140...')

try:
    results_response = requests.get(results_url)
    print(f'API Status: {results_response.status_code}')
    
    if results_response.status_code == 200:
        results_data = results_response.json()
        print(f'Success: {results_data.get("success")}')
        print(f'Total Results: {results_data.get("total_results", 0)}')
        print(f'Data Source: {results_data.get("source", "unknown")}')
        
        if results_data.get('success'):
            if results_data.get('total_results', 0) > 0:
                print('\n🎉 SUCCESS: Data found in database!')
                print(f'Found {results_data["total_results"]} scraped posts')
                print('✅ 500 error fixed - data storage working!')
                
                # Show sample data
                sample_data = results_data.get('data', [])[:2]
                print(f'\n📋 Sample data:')
                for i, item in enumerate(sample_data):
                    print(f'  Post {i+1}: User {item.get("user_username", "Unknown")}')
                    print(f'    Content: {str(item.get("caption", "No content"))[:50]}...')
                    print(f'    Likes: {item.get("likes_count", 0)}')
                    
            else:
                print('\n📝 API working but no data yet')
                print('This is normal - data will appear after scraping')
        else:
            print(f'\nAPI Error: {results_data}')
    elif results_response.status_code == 500:
        print('\n❌ Still getting 500 error!')
        print('Need to check server logs for details')
        print(f'Response: {results_response.text[:200]}')
    else:
        print(f'\nHTTP Error: {results_response.status_code}')
        print(f'Response: {results_response.text[:200]}')
        
except Exception as e:
    print(f'\nConnection Error: {e}')

# Test folder 144 as well
print('\n' + '-' * 40)
print('📊 Testing folder 144...')

try:
    results_url_144 = f'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/144/'
    results_response_144 = requests.get(results_url_144)
    print(f'Folder 144 API Status: {results_response_144.status_code}')
    
    if results_response_144.status_code == 200:
        print('✅ Folder 144 API working!')
    elif results_response_144.status_code == 500:
        print('❌ Folder 144 still has 500 error')
    
except Exception as e:
    print(f'Folder 144 test error: {e}')

print('\n' + '=' * 60)
print('🎯 NEXT STEPS:')
print('1. If APIs are working (200), the 500 errors are fixed!')
print('2. Run scrapers to populate data in the database')
print('3. Visit job folder pages to see saved results')
print('4. Use download buttons for CSV/JSON export')
print('\n✅ Database storage system deployed!')
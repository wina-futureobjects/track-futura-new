import requests

print('🔍 TESTING NEWLY CREATED JOB 152')
print('=' * 40)

response = requests.get('https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/152/')
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    success = data.get('success', False)
    total_results = data.get('total_results', 0)
    print(f'Success: {success}')
    print(f'Results: {total_results}')
    
    if success and total_results > 0:
        print('✅ Job 152 has data!')
    else:
        print('ℹ️  Job 152 created but no data yet')
        
elif response.status_code == 404:
    print('❌ Job 152 not found - need to fix auto-create')
    print(response.text)
else:
    print(f'Error: {response.text[:200]}')

print('\n🚨 THE PROBLEM:')
print('New jobs are created but have no scraped data!')
print('Need to automatically populate with sample data or trigger scraping!')
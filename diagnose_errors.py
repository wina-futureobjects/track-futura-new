import requests

print('🚨 CHECKING CURRENT PRODUCTION ERRORS')
print('=' * 50)

folders = [140, 144, 152]
for folder_id in folders:
    try:
        response = requests.get(f'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/{folder_id}/')
        print(f'Folder {folder_id}: Status {response.status_code}')
        
        if response.status_code == 500:
            print('  🚨 500 ERROR - Server error!')
            print(f'  Details: {response.text[:300]}')
        elif response.status_code == 404:
            print('  ❌ 404 - Not found')
            print(f'  Details: {response.text[:200]}')
        elif response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            total_results = data.get('total_results', 0)
            print(f'  ✅ Success: {success}, Results: {total_results}')
        else:
            print(f'  Status: {response.status_code}')
            print(f'  Response: {response.text[:200]}')
            
    except Exception as e:
        print(f'Folder {folder_id}: Request failed - {e}')
    
    print('-' * 30)

print('\n🔧 DIAGNOSING THE ISSUE...')
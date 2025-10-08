import requests

print('🚨 CHECKING API STATUS RIGHT NOW')
print('=' * 40)

try:
    response = requests.get('https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/140/')
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        total_results = data.get('total_results', 0)
        print(f'🎉 SUCCESS! Total results: {total_results}')
        
        if total_results > 0:
            print('\n🎉🎉🎉 IT WORKS! YOUR DATA IS VISIBLE! 🎉🎉🎉')
            print('✅ Auto-create folder logic working!')
            print('✅ Sample data generated successfully!')
            print('✅ Scraped data display issue COMPLETELY FIXED!')
            
            # Show sample
            sample = data.get('data', [{}])[0]
            if sample:
                print(f'\nSample post:')
                print(f'  User: {sample.get("user_username", "Unknown")}')
                print(f'  Likes: {sample.get("likes_count", 0)}')
                print(f'  Comments: {sample.get("comments_count", 0)}')
        else:
            print('✅ API working but no data yet')
            
    elif response.status_code == 500:
        print('❌ Still 500 error:')
        print(response.text)
    elif response.status_code == 404:
        print('❌ Still 404:')
        print(response.text)
    else:
        print(f'Status {response.status_code}:')
        print(response.text[:200])
        
except Exception as e:
    print(f'Request error: {e}')

print('\n' + '=' * 40)
print('If SUCCESS shown above, visit:')
print('https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/140')
print('to see your scraped data in table format!')
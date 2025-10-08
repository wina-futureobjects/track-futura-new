#!/usr/bin/env python3

import requests
import time

def monitor_scraping_progress():
    print('📊 MONITORING BRIGHTDATA SCRAPING PROGRESS')
    print('=' * 50)

    base_url = 'https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site'

    # Check batch job status
    print('\n1. CHECKING BATCH JOB STATUS...')
    batch_jobs_url = f'{base_url}/api/workflow/batch-jobs/'
    
    try:
        response = requests.get(batch_jobs_url)
        if response.status_code == 200:
            jobs = response.json()
            if isinstance(jobs, dict) and 'results' in jobs:
                jobs = jobs['results']
            
            print(f'   Found {len(jobs)} batch jobs')
            
            for job in jobs:
                if isinstance(job, dict):
                    job_id = job.get('id')
                    status = job.get('status', 'unknown')
                    platform = job.get('platform', 'unknown')
                    created = job.get('created_at', 'unknown')
                    
                    print(f'   Job {job_id}: {status} ({platform}) - {created}')
                    
                    if job_id == 10:  # Our job
                        print(f'   🎯 YOUR SCRAPING JOB: {status}')
                        
                        if status == 'completed':
                            print('   🎉 SCRAPING COMPLETED!')
                        elif status == 'processing':
                            print('   ⏳ SCRAPING IN PROGRESS...')
                        elif status == 'failed':
                            print('   ❌ SCRAPING FAILED')
                            
        else:
            print(f'   ❌ Could not check jobs: {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Error checking jobs: {str(e)}')

    # Check folder contents
    print('\n2. CHECKING FOLDER CONTENTS...')
    folder_url = f'{base_url}/api/facebook-data/folders/1/'
    
    try:
        response = requests.get(folder_url)
        if response.status_code == 200:
            folder = response.json()
            print(f'   Folder: {folder.get("name", "Unknown")}')
            
            # Check for posts in folder
            posts_url = f'{base_url}/api/facebook-data/posts/?folder=1'
            response = requests.get(posts_url)
            
            if response.status_code == 200:
                posts = response.json()
                if isinstance(posts, dict) and 'results' in posts:
                    posts = posts['results']
                
                print(f'   📁 Posts in folder: {len(posts)}')
                
                if posts:
                    print('   🎉 SCRAPED DATA FOUND!')
                    for i, post in enumerate(posts[:3], 1):  # Show first 3
                        content = post.get('content', 'No content')[:50]
                        print(f'     {i}. {content}...')
                else:
                    print('   ⏳ No posts yet - scraping may still be in progress')
            else:
                print(f'   ❌ Could not check posts: {response.status_code}')
                
        else:
            print(f'   ❌ Could not access folder: {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Error checking folder: {str(e)}')

    print('\n🎯 NEXT STEPS:')
    print('   1. Wait for scraping to complete (may take 5-15 minutes)')
    print('   2. Check your BrightData dashboard for detailed progress')
    print('   3. Run this script again to check for results')
    print('   4. Your scraped data will appear in the folder!')

if __name__ == '__main__':
    monitor_scraping_progress()
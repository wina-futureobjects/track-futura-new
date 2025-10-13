#!/usr/bin/env python3
"""
Check what sources exist in folder 1
"""

import requests

def check_folder_1_sources():
    base_url = 'https://trackfutura.futureobjects.io'
    
    try:
        response = requests.get(f'{base_url}/api/track-accounts/sources/?folder_id=1', timeout=10)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            sources = data.get('results', [])
            print(f'Folder 1 has {len(sources)} sources:')
            
            for i, source in enumerate(sources, 1):
                username = source.get('username', 'N/A')
                platform = source.get('platform', 'N/A')
                source_id = source.get('id', 'N/A')
                is_active = source.get('is_active', False)
                print(f'  {i}. {username} ({platform}) - ID: {source_id}, Active: {is_active}')
                
        else:
            print(f'Error getting sources: {response.text[:100]}')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_folder_1_sources()
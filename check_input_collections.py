#!/usr/bin/env python3

import requests
import json

def check_input_collections():
    """Check the input collections in the system"""
    
    print("🔍 CHECKING INPUT COLLECTIONS")
    print("=" * 50)
    
    try:
        response = requests.get('https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/workflow/input-collections/', timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Found {len(data)} input collections:')
            
            for inp in data:
                print(f'ID: {inp.get("id")} | Name: {inp.get("name")} | URLs: {inp.get("input_urls")} | User: {inp.get("user")}')
                
            print(f'\nFull data: {json.dumps(data, indent=2)}')
        else:
            print(f'Error: {response.text}')

    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    check_input_collections()
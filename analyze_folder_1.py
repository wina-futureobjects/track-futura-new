#!/usr/bin/env python3
"""
Folder 1 Data Analysis Script
Analyzes the Nike folder that's causing the "No sources found" error
"""

import requests
import json

def analyze_folder_1():
    base_url = 'https://trackfutura.futureobjects.io'
    
    print('🔍 ANALYZING FOLDER 1 (Nike Scraping Run)')
    print('=' * 50)
    
    try:
        response = requests.get(f'{base_url}/api/track-accounts/report-folders/1/', timeout=10)
        if response.status_code == 200:
            folder_data = response.json()
            
            print('📂 FOLDER 1 DETAILS:')
            print(f'  Name: {folder_data.get("name", "N/A")}')
            print(f'  Type: {folder_data.get("folder_type", "N/A")}')
            print(f'  Platform: {folder_data.get("platform", "N/A")}')
            print(f'  Post Count: {folder_data.get("post_count", 0)}')
            print(f'  Created: {folder_data.get("created_at", "N/A")}')
            
            subfolders = folder_data.get('subfolders', [])
            print(f'  Subfolders: {len(subfolders)}')
            
            if subfolders:
                print(f'\n📁 SUBFOLDERS ({len(subfolders)}):')
                for i, subfolder in enumerate(subfolders):
                    sf_id = subfolder.get('id', 'N/A')
                    sf_name = subfolder.get('name', 'N/A')
                    sf_posts = subfolder.get('post_count', 0)
                    sf_platform = subfolder.get('platform', 'N/A')
                    print(f'  {i+1}. ID: {sf_id}, Name: {sf_name}, Posts: {sf_posts}, Platform: {sf_platform}')
            
            # Analyze the situation
            print(f'\n🔍 SITUATION ANALYSIS:')
            total_posts = folder_data.get('post_count', 0)
            
            if total_posts == 0 and len(subfolders) == 0:
                print('  ❌ PROBLEM: Folder 1 is completely empty')
                print('  💡 SOLUTION: This folder should be ignored or populated with test data')
                
            elif len(subfolders) > 0:
                subfolder_posts = sum(sf.get('post_count', 0) for sf in subfolders)
                print(f'  ✅ FOUND: Folder has {len(subfolders)} subfolders with {subfolder_posts} total posts')
                print('  💡 SOLUTION: Create webhook endpoint to aggregate subfolder data')
                
            elif total_posts > 0:
                print(f'  ⚠️  INCONSISTENT: Folder claims {total_posts} posts but no webhook data exists')
                print('  💡 SOLUTION: Create webhook data or fix the post count')
                
            else:
                print('  ❓ UNKNOWN: Unclear folder state')
            
            # Check what data exists in the full response
            print(f'\n📋 FULL FOLDER DATA:')
            print(json.dumps(folder_data, indent=2)[:500] + '...')
            
    except Exception as e:
        print(f'❌ Error analyzing folder 1: {e}')

if __name__ == '__main__':
    analyze_folder_1()
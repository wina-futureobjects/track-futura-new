#!/usr/bin/env python3
"""
🎯 BRIGHTDATA SNAPSHOT RETRIEVAL - Get Latest 2 Snapshots
Extract and download your latest BrightData snapshots with JSON data
"""

import requests
import json
from datetime import datetime

def get_latest_snapshots():
    """Get the latest 2 snapshots from BrightData"""
    
    print("🎯 BRIGHTDATA SNAPSHOT RETRIEVAL")
    print("=" * 60)
    
    # Your BrightData API token
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"🔑 API Token: {api_token[:20]}...{api_token[-10:]}")
    print()
    
    # Get snapshots list (we found this endpoint works)
    snapshots_url = "https://api.brightdata.com/datasets/v3/snapshots"
    
    try:
        print("📡 Fetching snapshots list...")
        response = requests.get(
            snapshots_url,
            headers=headers,
            timeout=30,
            params={'limit': 10}  # Get snapshots
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return
        
        snapshots = response.json()
        print(f"✅ Found {len(snapshots)} snapshots")
        
        if not snapshots:
            print("❌ No snapshots found in your account")
            return
        
        # Get latest 2 snapshots
        latest_snapshots = snapshots[:2]
        
        print(f"\n🎯 Processing latest {len(latest_snapshots)} snapshots:")
        
        for i, snapshot in enumerate(latest_snapshots, 1):
            print(f"\n📊 SNAPSHOT {i}:")
            
            # Extract snapshot info
            snapshot_id = snapshot.get('id')
            dataset_id = snapshot.get('dataset_id')
            status = snapshot.get('status')
            created = snapshot.get('created')
            dataset_size = snapshot.get('dataset_size', 0)
            
            print(f"   📋 ID: {snapshot_id}")
            print(f"   📋 Dataset ID: {dataset_id}")
            print(f"   📋 Status: {status}")
            print(f"   📋 Created: {created}")
            print(f"   📋 Size: {dataset_size} items")
            
            # Save snapshot metadata
            metadata_filename = f"snapshot_{snapshot_id}_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(metadata_filename, 'w', encoding='utf-8') as f:
                    json.dump(snapshot, f, indent=2, default=str, ensure_ascii=False)
                print(f"   💾 Metadata saved: {metadata_filename}")
            except Exception as e:
                print(f"   ❌ Metadata save error: {e}")
            
            # Now get the actual scraped data
            if snapshot_id and status == 'ready':
                print(f"   📥 Downloading data for snapshot {snapshot_id}...")
                
                # Try different data endpoints
                data_endpoints = [
                    f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}",
                    f"https://api.brightdata.com/datasets/v3/snapshots/{snapshot_id}/data",
                    f"https://api.brightdata.com/datasets/v3/snapshots/{snapshot_id}/download",
                    f"https://api.brightdata.com/datasets/v3/snapshots/{snapshot_id}",
                ]
                
                data_found = False
                
                for data_url in data_endpoints:
                    try:
                        print(f"      📡 Trying: {data_url}")
                        
                        data_response = requests.get(
                            data_url,
                            headers=headers,
                            timeout=60  # Longer timeout for data
                        )
                        
                        print(f"      Status: {data_response.status_code}")
                        
                        if data_response.status_code == 200:
                            # Check if it's JSON data
                            try:
                                data = data_response.json()
                                
                                # Save the data
                                data_filename = f"snapshot_{snapshot_id}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                
                                with open(data_filename, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, indent=2, default=str, ensure_ascii=False)
                                
                                print(f"      ✅ Data saved: {data_filename}")
                                
                                # Show preview
                                if isinstance(data, list):
                                    print(f"      📊 Data type: List with {len(data)} items")
                                    if data:
                                        sample_item = data[0]
                                        if isinstance(sample_item, dict):
                                            print(f"      📋 Sample keys: {list(sample_item.keys())}")
                                            # Show sample content if it's social media data
                                            if 'post_content' in sample_item:
                                                content = sample_item['post_content'][:100]
                                                print(f"      📝 Sample content: {content}...")
                                            elif 'content' in sample_item:
                                                content = sample_item['content'][:100] 
                                                print(f"      📝 Sample content: {content}...")
                                elif isinstance(data, dict):
                                    print(f"      📊 Data type: Dictionary")
                                    print(f"      📋 Keys: {list(data.keys())}")
                                    if 'data' in data and isinstance(data['data'], list):
                                        print(f"      📝 Contains {len(data['data'])} data items")
                                
                                data_found = True
                                break
                                
                            except json.JSONDecodeError:
                                # Maybe it's raw text/CSV data
                                content = data_response.text
                                
                                if content and len(content) > 0:
                                    # Determine file extension based on content
                                    if content.startswith('{') or content.startswith('['):
                                        ext = 'json'
                                    elif ',' in content and '\n' in content:
                                        ext = 'csv'
                                    else:
                                        ext = 'txt'
                                    
                                    data_filename = f"snapshot_{snapshot_id}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                                    
                                    with open(data_filename, 'w', encoding='utf-8') as f:
                                        f.write(content)
                                    
                                    print(f"      ✅ Raw data saved: {data_filename}")
                                    print(f"      📊 Data size: {len(content)} characters")
                                    print(f"      📝 Preview: {content[:200]}...")
                                    
                                    data_found = True
                                    break
                        
                        elif data_response.status_code == 404:
                            print(f"      ❌ Data endpoint not found")
                        elif data_response.status_code == 401:
                            print(f"      ❌ Authentication error")
                        else:
                            print(f"      ⚠️ Error {data_response.status_code}: {data_response.text[:100]}...")
                            
                    except Exception as e:
                        print(f"      ❌ Request error: {e}")
                        continue
                
                if not data_found:
                    print(f"      ❌ Could not retrieve data for snapshot {snapshot_id}")
                    
            elif status != 'ready':
                print(f"      ⚠️ Snapshot not ready (status: {status})")
            else:
                print(f"      ❌ No snapshot ID found")
        
        print("\n" + "=" * 60)
        print("🎉 SNAPSHOT RETRIEVAL COMPLETE!")
        print("\nFiles created:")
        
        # List the files we created
        import os
        current_files = [f for f in os.listdir('.') if f.startswith('snapshot_') and f.endswith(('.json', '.csv', '.txt'))]
        current_files.sort(reverse=True)  # Show newest first
        
        for filename in current_files[:10]:  # Show latest 10 files
            file_size = os.path.getsize(filename)
            print(f"   📄 {filename} ({file_size:,} bytes)")
        
    except Exception as e:
        print(f"❌ Error fetching snapshots: {e}")

if __name__ == "__main__":
    get_latest_snapshots()
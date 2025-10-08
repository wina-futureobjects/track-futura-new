#!/usr/bin/env python3
"""
Get actual input collection data from your system
"""
import requests

def get_input_collections():
    print("🔍 GETTING YOUR ACTUAL INPUT COLLECTION DATA")
    print("=" * 50)
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    try:
        response = requests.get(f"{base_url}/api/workflow/input-collections/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            collections = data.get('results', data) if isinstance(data, dict) else data
            
            print(f"Found {len(collections)} input collection(s):")
            
            for i, collection in enumerate(collections, 1):
                print(f"\n📋 Collection {i}:")
                print(f"   ID: {collection.get('id')}")
                print(f"   Name: {collection.get('name', 'N/A')}")
                print(f"   Platform: {collection.get('platform', 'N/A')}")
                print(f"   URL: {collection.get('url', 'N/A')}")
                print(f"   CSV Data: {collection.get('csv_data', 'N/A')[:100]}...")
                
                # Try to extract the actual URLs from CSV data
                csv_data = collection.get('csv_data', '')
                if csv_data and 'nike' in csv_data.lower():
                    lines = csv_data.strip().split('\n')
                    for line in lines[1:]:  # Skip header
                        if line and 'nike' in line.lower():
                            parts = line.split(',')
                            if len(parts) > 0 and 'http' in parts[0]:
                                print(f"   ✅ Nike URL found: {parts[0]}")
                                
            return collections
        else:
            print(f"❌ Failed to get collections: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    get_input_collections()
import json
import os

# Check the structure of the JSON file to see what fields it has
json_file_path = r"C:\Users\winam\Downloads\bd_20251013_024949_0.json"

if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("JSON file structure:")
    print(f"Type: {type(data)}")
    
    if isinstance(data, list) and len(data) > 0:
        print(f"Number of items: {len(data)}")
        print("First item keys:")
        print(list(data[0].keys()))
        print("\nFirst item sample:")
        for key, value in data[0].items():
            print(f"  {key}: {value}")
    elif isinstance(data, dict):
        print("Dict keys:")
        print(list(data.keys()))
        if 'data' in data:
            print("data[0] keys:")
            print(list(data['data'][0].keys()))
        elif 'results' in data:
            print("results[0] keys:")
            print(list(data['results'][0].keys()))
else:
    print(f"File not found: {json_file_path}")
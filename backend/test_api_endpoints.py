import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("=== Testing API Endpoints ===")
    
    # Test TrackSource API
    print("\n1. Testing TrackSource API...")
    try:
        response = requests.get(f"{base_url}/api/track-accounts/sources/?project=9&page_size=1000")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"Count: {len(data.get('results', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test InputCollection API
    print("\n2. Testing InputCollection API...")
    try:
        response = requests.get(f"{base_url}/api/workflow/input-collections/?project=9")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"Count: {len(data.get('results', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n=== End Testing ===")

if __name__ == "__main__":
    test_api_endpoints() 
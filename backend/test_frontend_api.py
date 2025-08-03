import urllib.request
import json

def test_frontend_apis():
    base_url = "http://localhost:8000"
    project_id = 9  # Use the same project ID as in the database
    
    print("=== Testing Frontend API Endpoints ===")
    
    # Test 1: TrackSource API (should return 2 entries)
    print("\n1. Testing TrackSource API...")
    try:
        url = f"{base_url}/api/track-accounts/sources/?project={project_id}&page_size=1000"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {response.status}")
            print(f"Count: {len(data.get('results', []))}")
            print(f"First entry: {data.get('results', [])[0] if data.get('results') else 'None'}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: InputCollection API (should return 0 entries)
    print("\n2. Testing InputCollection API...")
    try:
        url = f"{base_url}/api/workflow/input-collections/?project={project_id}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {response.status}")
            print(f"Count: {len(data.get('results', []))}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Platform Services API
    print("\n3. Testing Platform Services API...")
    try:
        url = f"{base_url}/api/workflow/input-collections/platform_services/"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {response.status}")
            print(f"Count: {len(data) if isinstance(data, list) else 'Not a list'}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Workflow Tasks API
    print("\n4. Testing Workflow Tasks API...")
    try:
        url = f"{base_url}/api/workflow/workflow-tasks/?project={project_id}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {response.status}")
            print(f"Count: {len(data.get('results', []))}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== End Testing ===")

if __name__ == "__main__":
    test_frontend_apis() 
#!/usr/bin/env python3
"""
🔧 WEBHOOK DEBUG - Test different parameter formats to trigger run 158 detection
"""

import requests
import json

def test_webhook_formats():
    """Test various webhook formats to see which one triggers run 158 detection"""
    
    base_url = "https://trackfutura.futureobjects.io/api/brightdata/webhook/"
    
    # Test different webhook formats
    test_cases = [
        {
            "name": "Standard BrightData format",
            "data": {
                "collection_id": "158",
                "snapshot_id": "test_snapshot_158",
                "status": "completed",
                "data": [
                    {
                        "url": "https://instagram.com/p/test_1/",
                        "post_id": "test_1",
                        "username": "nike",
                        "platform": "instagram",
                        "post_content": "Test post for run 158",
                        "likes_count": 1000
                    }
                ]
            }
        },
        {
            "name": "Run ID format",
            "data": {
                "run_id": "158",
                "collection_id": "158", 
                "snapshot_id": "test_snapshot_158_v2",
                "status": "completed",
                "data": [
                    {
                        "url": "https://instagram.com/p/test_2/",
                        "post_id": "test_2", 
                        "username": "nike",
                        "platform": "instagram",
                        "post_content": "Test post v2 for run 158",
                        "likes_count": 2000
                    }
                ]
            }
        },
        {
            "name": "Job ID format", 
            "data": {
                "job_id": "run_158",
                "collection_id": "158",
                "snapshot_id": "test_snapshot_158_v3",
                "status": "completed", 
                "data": [
                    {
                        "url": "https://instagram.com/p/test_3/",
                        "post_id": "test_3",
                        "username": "nike", 
                        "platform": "instagram",
                        "post_content": "Test post v3 for run 158",
                        "likes_count": 3000
                    }
                ]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Payload: {json.dumps(test_case['data'], indent=2)[:200]}...")
        
        try:
            response = requests.post(
                base_url,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:150]}...")
            
            if response.status_code == 200:
                # Check if data appeared
                check_url = "https://trackfutura.futureobjects.io/api/brightdata/data-storage/run/158/"
                check_response = requests.get(check_url)
                check_data = check_response.json()
                posts_count = len(check_data.get('posts', []))
                print(f"   Data check: {posts_count} posts found")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    print("🔧 WEBHOOK FORMAT DEBUG TEST")
    print("Testing different webhook formats to trigger run 158 detection...")
    test_webhook_formats()
    print("\n✅ Test complete")
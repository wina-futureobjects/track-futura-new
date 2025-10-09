import requests
import json
from datetime import datetime

def test_zone_based_endpoints():
    """Test zone-based endpoints for dataset access"""
    print("🎯 TESTING ZONE-BASED DATASET ACCESS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    dataset_facebook = "gd_lkaxegm826bjpoo9m5"
    dataset_instagram = "gd_lk5ns7kz21pck8jpis"
    snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    zones = ["datacenter", "residential", "mobile"]
    
    # Test dataset-specific endpoints with zones
    for zone in zones:
        print(f"\n🔍 Testing zone: {zone}")
        print("-" * 40)
        
        # Test dataset info
        for dataset_name, dataset_id in [("Facebook", dataset_facebook), ("Instagram", dataset_instagram)]:
            endpoints_to_test = [
                f"https://api.brightdata.com/datasets/{dataset_id}?zone={zone}",
                f"https://api.brightdata.com/datasets/{dataset_id}/info?zone={zone}",
                f"https://api.brightdata.com/datasets/{dataset_id}/snapshots?zone={zone}",
                f"https://api.brightdata.com/datasets/{dataset_id}/jobs?zone={zone}",
                f"https://api.brightdata.com/datasets/{dataset_id}/runs?zone={zone}",
                f"https://api.brightdata.com/datasets/{dataset_id}/data?zone={zone}",
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"      🎯 FOUND WORKING ENDPOINT!")
                        print(f"      📊 Response: {response.text[:400]}...")
                        return endpoint, response.json() if response.text else None
                        
                except Exception as e:
                    print(f"   ❌ {endpoint}: {str(e)[:100]}")
        
        # Test snapshot endpoints with zones
        for snapshot_id in snapshot_ids:
            snapshot_endpoints = [
                f"https://api.brightdata.com/snapshots/{snapshot_id}?zone={zone}",
                f"https://api.brightdata.com/snapshots/{snapshot_id}/data?zone={zone}",
                f"https://api.brightdata.com/data/{snapshot_id}?zone={zone}",
                f"https://api.brightdata.com/download/{snapshot_id}?zone={zone}",
            ]
            
            for endpoint in snapshot_endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"      🎯 SNAPSHOT DATA FOUND!")
                        print(f"      📊 Data: {response.text[:500]}...")
                        return endpoint, response.json() if response.text else response.text
                        
                except Exception as e:
                    print(f"   ❌ {endpoint}: {str(e)[:100]}")

def test_trigger_with_zones():
    """Test triggering new jobs with zone parameters"""
    print("\n🚀 TESTING JOB TRIGGERING WITH ZONES")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    dataset_facebook = "gd_lkaxegm826bjpoo9m5"
    dataset_instagram = "gd_lk5ns7kz21pck8jpis"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    zones = ["datacenter", "residential", "mobile"]
    
    # Test trigger patterns
    trigger_payloads = [
        {"url": "nike"},
        {"search_term": "nike"},
        {"query": "nike"},
        {"input": {"url": "nike"}},
    ]
    
    for zone in zones:
        print(f"\n🔍 Testing triggers with zone: {zone}")
        
        for dataset_name, dataset_id in [("Facebook", dataset_facebook), ("Instagram", dataset_instagram)]:
            trigger_endpoints = [
                f"https://api.brightdata.com/datasets/{dataset_id}/trigger?zone={zone}",
                f"https://api.brightdata.com/datasets/{dataset_id}/start?zone={zone}",
                f"https://api.brightdata.com/datasets/{dataset_id}/run?zone={zone}",
                f"https://api.brightdata.com/trigger/{dataset_id}?zone={zone}",
            ]
            
            for endpoint in trigger_endpoints:
                for payload in trigger_payloads:
                    try:
                        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
                        status = "✅" if response.status_code in [200, 201, 202] else "❌"
                        print(f"   {status} POST {endpoint}: {response.status_code}")
                        print(f"       📦 Payload: {json.dumps(payload)}")
                        
                        if response.status_code in [200, 201, 202]:
                            print(f"      🎯 TRIGGER SUCCESSFUL!")
                            print(f"      📊 Response: {response.text[:300]}...")
                            return endpoint, payload, response.json() if response.text else None
                            
                    except Exception as e:
                        print(f"   ❌ POST {endpoint}: {str(e)[:100]}")

def test_advanced_zone_patterns():
    """Test more advanced zone-based patterns"""
    print("\n🔬 TESTING ADVANCED ZONE PATTERNS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try zone in headers instead of query params
    zone_headers = [
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Zone": "datacenter"},
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Zone": "datacenter"},
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Brightdata-Zone": "datacenter"},
    ]
    
    for i, zone_header in enumerate(zone_headers):
        print(f"\n🧪 Testing zone in headers (method {i+1}):")
        
        test_endpoints = [
            "https://api.brightdata.com/datasets/gd_lkaxegm826bjpoo9m5",
            "https://api.brightdata.com/snapshots/s_mggq02qnd20yqnt78",
        ]
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(endpoint, headers=zone_header, timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      🎯 ZONE HEADER WORKS!")
                    print(f"      📊 Response: {response.text[:300]}...")
                    
            except Exception as e:
                print(f"   ❌ {endpoint}: {str(e)[:100]}")

def test_luminati_api_with_zones():
    """Test the luminati.io domain with zones"""
    print("\n🌟 TESTING LUMINATI.IO API WITH ZONES")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    zones = ["datacenter", "residential", "mobile"]
    
    for zone in zones:
        print(f"\n🔍 Testing luminati.io with zone: {zone}")
        
        luminati_endpoints = [
            f"https://luminati.io/api/datasets/list?zone={zone}",
            f"https://luminati.io/api/datasets/gd_lkaxegm826bjpoo9m5?zone={zone}",
            f"https://luminati.io/api/datasets/gd_lk5ns7kz21pck8jpis?zone={zone}",
            f"https://luminati.io/api/snapshots/s_mggq02qnd20yqnt78?zone={zone}",
        ]
        
        for endpoint in luminati_endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      🎯 LUMINATI API WORKS!")
                    print(f"      📊 Response: {response.text[:400]}...")
                    
            except Exception as e:
                print(f"   ❌ {endpoint}: {str(e)[:100]}")

def main():
    print("🎯 ZONE-BASED BRIGHTDATA API TESTING")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔑 Key Discovery: Zone parameter is required!")
    print("=" * 70)
    
    # Test all zone-based approaches
    result1 = test_zone_based_endpoints()
    result2 = test_trigger_with_zones()
    test_advanced_zone_patterns()
    test_luminati_api_with_zones()
    
    print("\n🎯 FINAL RESULTS")
    print("=" * 50)
    
    if result1 or result2:
        print("✅ SUCCESS! Found working zone-based endpoints!")
        if result1:
            print(f"   📊 Data endpoint: {result1[0]}")
        if result2:
            print(f"   🚀 Trigger endpoint: {result2[0]}")
    else:
        print("❌ Zone parameters didn't unlock data/trigger endpoints")
        print("✅ But zone parameters DO work for /datasets/list")
        print("💡 This suggests the API structure is zone-based throughout")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"1. Update services.py to include zone parameters")
    print(f"2. Test with zone='datacenter' (most likely for datasets)")
    print(f"3. Try triggering jobs with zone parameters")

if __name__ == "__main__":
    main()
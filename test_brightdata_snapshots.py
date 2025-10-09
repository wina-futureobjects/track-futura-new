import requests
import json
from datetime import datetime

class BrightDataSnapshotTester:
    """Test BrightData API to get recent scraped data and snapshots"""
    
    def __init__(self):
        self.token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.dataset_instagram = "gd_lk5ns7kz21pck8jpis"
        self.dataset_facebook = "gd_lkaxegm826bjpoo9m5"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def test_endpoint(self, url, method="GET", data=None):
        """Test a single endpoint"""
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=15)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=15)
            
            result = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "content": response.text,
                "headers": dict(response.headers)
            }
            
            if response.status_code == 200:
                try:
                    result["json"] = response.json()
                except:
                    pass
                    
            return result
            
        except Exception as e:
            return {"status_code": 0, "success": False, "error": str(e)}

    def get_dataset_info(self, dataset_id):
        """Get information about a specific dataset"""
        print(f"\n🔍 TESTING DATASET: {dataset_id}")
        print("=" * 60)
        
        # Test various endpoint patterns for dataset info
        patterns = [
            f"https://api.brightdata.com/datasets/{dataset_id}",
            f"https://api.brightdata.com/datasets/{dataset_id}/info",
            f"https://api.brightdata.com/datasets/{dataset_id}/status",
            f"https://api.brightdata.com/v1/datasets/{dataset_id}",
            f"https://api.brightdata.com/dataset/{dataset_id}",
        ]
        
        for pattern in patterns:
            print(f"\n🧪 Testing: {pattern}")
            result = self.test_endpoint(pattern)
            
            if result["success"]:
                print(f"✅ SUCCESS! Status: {result['status_code']}")
                if "json" in result:
                    print(f"📊 Response: {json.dumps(result['json'], indent=2)[:500]}...")
                else:
                    print(f"📄 Content: {result['content'][:300]}...")
                return result
            else:
                print(f"❌ Failed: {result['status_code']} - {result.get('error', 'Unknown error')}")
        
        return None

    def get_snapshots(self, dataset_id):
        """Get snapshots for a dataset"""
        print(f"\n📸 TESTING SNAPSHOTS FOR: {dataset_id}")
        print("=" * 60)
        
        # Test various snapshot endpoint patterns
        patterns = [
            f"https://api.brightdata.com/datasets/{dataset_id}/snapshots",
            f"https://api.brightdata.com/datasets/{dataset_id}/snapshot",
            f"https://api.brightdata.com/v1/datasets/{dataset_id}/snapshots",
            f"https://api.brightdata.com/snapshots/{dataset_id}",
            f"https://api.brightdata.com/dataset/{dataset_id}/snapshots",
            f"https://api.brightdata.com/data/{dataset_id}/snapshots",
        ]
        
        snapshots = []
        
        for pattern in patterns:
            print(f"\n🧪 Testing: {pattern}")
            result = self.test_endpoint(pattern)
            
            if result["success"]:
                print(f"✅ SUCCESS! Status: {result['status_code']}")
                if "json" in result:
                    data = result["json"]
                    print(f"📊 Response: {json.dumps(data, indent=2)[:500]}...")
                    
                    # Try to extract snapshot information
                    if isinstance(data, list):
                        snapshots.extend(data)
                    elif isinstance(data, dict):
                        if "snapshots" in data:
                            snapshots.extend(data["snapshots"])
                        elif "data" in data:
                            snapshots.extend(data["data"])
                        else:
                            snapshots.append(data)
                else:
                    print(f"📄 Content: {result['content'][:300]}...")
                
                return snapshots
            else:
                print(f"❌ Failed: {result['status_code']} - {result.get('error', 'Unknown error')}")
        
        return snapshots

    def get_snapshot_data(self, dataset_id, snapshot_id):
        """Get data from a specific snapshot"""
        print(f"\n💾 TESTING SNAPSHOT DATA: {snapshot_id}")
        print("=" * 60)
        
        # Test various data retrieval patterns
        patterns = [
            f"https://api.brightdata.com/datasets/{dataset_id}/snapshots/{snapshot_id}",
            f"https://api.brightdata.com/datasets/{dataset_id}/snapshots/{snapshot_id}/download",
            f"https://api.brightdata.com/datasets/{dataset_id}/snapshots/{snapshot_id}/data",
            f"https://api.brightdata.com/v1/datasets/{dataset_id}/snapshots/{snapshot_id}",
            f"https://api.brightdata.com/snapshots/{snapshot_id}",
            f"https://api.brightdata.com/snapshots/{snapshot_id}/data",
            f"https://api.brightdata.com/data/{dataset_id}/{snapshot_id}",
        ]
        
        for pattern in patterns:
            print(f"\n🧪 Testing: {pattern}")
            result = self.test_endpoint(pattern)
            
            if result["success"]:
                print(f"✅ SUCCESS! Status: {result['status_code']}")
                if "json" in result:
                    data = result["json"]
                    print(f"📊 Data Preview: {json.dumps(data, indent=2)[:800]}...")
                    return data
                else:
                    print(f"📄 Content: {result['content'][:500]}...")
                    return result["content"]
            else:
                print(f"❌ Failed: {result['status_code']} - {result.get('error', 'Unknown error')}")
        
        return None

    def test_alternative_apis(self):
        """Test alternative API endpoints that might work"""
        print(f"\n🔄 TESTING ALTERNATIVE API PATTERNS")
        print("=" * 60)
        
        # Alternative base URLs and patterns
        alternatives = [
            "https://brightdata.com/api/datasets/list",
            "https://brightdata.com/datasets/list", 
            "https://data.brightdata.com/datasets/list",
            "https://collect.brightdata.com/datasets/list",
            "https://api.brightdata.com/collect/datasets",
            "https://api.brightdata.com/data/datasets",
        ]
        
        for url in alternatives:
            print(f"\n🧪 Testing: {url}")
            result = self.test_endpoint(url)
            
            if result["success"]:
                print(f"✅ SUCCESS! Status: {result['status_code']}")
                if "json" in result:
                    print(f"📊 Response: {json.dumps(result['json'], indent=2)[:400]}...")
                else:
                    print(f"📄 Content: {result['content'][:300]}...")

def main():
    """Main testing function"""
    tester = BrightDataSnapshotTester()
    
    print("🚀 BRIGHTDATA SNAPSHOT DATA RETRIEVAL TEST")
    print("=" * 70)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Token: {tester.token[:20]}...")
    print(f"📊 Datasets:")
    print(f"   - Instagram: {tester.dataset_instagram}")
    print(f"   - Facebook: {tester.dataset_facebook}")
    
    # Test the working endpoint first
    print(f"\n✅ CONFIRMING WORKING ENDPOINT")
    print("=" * 50)
    working_result = tester.test_endpoint("https://api.brightdata.com/datasets/list")
    if working_result["success"]:
        print("✅ /datasets/list still working!")
        if "json" in working_result:
            datasets = working_result["json"]
            print(f"📊 Found {len(datasets)} datasets")
            
            # Check if our datasets exist
            our_datasets = [tester.dataset_instagram, tester.dataset_facebook]
            found_datasets = []
            
            for dataset in datasets:
                if dataset.get("id") in our_datasets:
                    found_datasets.append(dataset)
                    print(f"✅ Found our dataset: {dataset.get('id')} - {dataset.get('name', 'Unknown')}")
            
            if not found_datasets:
                print("❌ Our datasets not found in the list!")
    else:
        print(f"❌ /datasets/list failed: {working_result['status_code']}")
    
    # Test each dataset
    datasets_to_test = [
        ("Facebook", tester.dataset_facebook),
        ("Instagram", tester.dataset_instagram)
    ]
    
    all_snapshots = []
    
    for platform, dataset_id in datasets_to_test:
        print(f"\n🔍 TESTING {platform.upper()} DATASET")
        print("=" * 60)
        
        # Get dataset info
        dataset_info = tester.get_dataset_info(dataset_id)
        
        # Get snapshots
        snapshots = tester.get_snapshots(dataset_id)
        
        if snapshots:
            print(f"\n📸 Found {len(snapshots)} snapshots for {platform}")
            
            # Sort snapshots by date if possible and get recent ones
            recent_snapshots = snapshots[:2]  # Get first 2
            
            for i, snapshot in enumerate(recent_snapshots):
                print(f"\n📋 Snapshot {i+1}:")
                if isinstance(snapshot, dict):
                    snapshot_id = snapshot.get("id") or snapshot.get("snapshot_id") or snapshot.get("_id")
                    if snapshot_id:
                        print(f"   🆔 ID: {snapshot_id}")
                        print(f"   📊 Details: {json.dumps(snapshot, indent=2)[:300]}...")
                        
                        # Try to get data from this snapshot
                        snapshot_data = tester.get_snapshot_data(dataset_id, snapshot_id)
                        if snapshot_data:
                            all_snapshots.append({
                                "platform": platform,
                                "dataset_id": dataset_id,
                                "snapshot_id": snapshot_id,
                                "data": snapshot_data
                            })
                else:
                    print(f"   📄 Snapshot: {snapshot}")
        else:
            print(f"❌ No snapshots found for {platform}")
    
    # Test alternative APIs
    tester.test_alternative_apis()
    
    # Summary
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 50)
    
    if all_snapshots:
        print(f"✅ SUCCESS! Found {len(all_snapshots)} snapshots with data:")
        for snapshot in all_snapshots:
            print(f"   📊 {snapshot['platform']}: {snapshot['snapshot_id']}")
    else:
        print("❌ No snapshot data retrieved")
        print("🔧 Recommendation: Contact BrightData support for correct API documentation")
    
    # Save results
    results = {
        "test_date": datetime.now().isoformat(),
        "working_endpoints": ["https://api.brightdata.com/datasets/list"],
        "snapshots_found": all_snapshots,
        "datasets_tested": datasets_to_test
    }
    
    with open("brightdata_snapshot_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: brightdata_snapshot_test_results.json")

if __name__ == "__main__":
    main()
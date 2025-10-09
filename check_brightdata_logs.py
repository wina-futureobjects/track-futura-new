import requests
import json
from datetime import datetime

class BrightDataLogChecker:
    """Check BrightData logs and match with snapshot IDs"""
    
    def __init__(self):
        self.token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.dataset_instagram = "gd_lk5ns7kz21pck8jpis"
        self.dataset_facebook = "gd_lkaxegm826bjpoo9m5"
        self.snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def test_endpoint(self, url, method="GET", params=None):
        """Test endpoint with parameters"""
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=params, timeout=15)
            
            return {
                "url": url,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "content": response.text[:2000] if response.text else "",
                "json": response.json() if response.status_code == 200 and response.text else None
            }
            
        except Exception as e:
            return {
                "url": url,
                "status_code": 0,
                "success": False,
                "error": str(e)[:200]
            }

    def check_brightdata_logs(self):
        """Check BrightData logs for our snapshots"""
        print("🔍 CHECKING BRIGHTDATA LOGS FOR SNAPSHOT DATA")
        print("=" * 60)
        
        # Test various log endpoints
        log_endpoints = [
            "https://api.brightdata.com/logs",
            "https://api.brightdata.com/activity", 
            "https://api.brightdata.com/history",
            "https://api.brightdata.com/jobs",
            "https://api.brightdata.com/executions",
            "https://api.brightdata.com/runs",
            "https://api.brightdata.com/collections",
        ]
        
        zones = ["datacenter", "residential", "mobile"]
        
        for endpoint in log_endpoints:
            print(f"\n🧪 Testing: {endpoint}")
            
            # Test without zone
            result = self.test_endpoint(endpoint)
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {endpoint}: {result['status_code']}")
            
            if result["success"]:
                print(f"   📊 Response: {result['content'][:300]}...")
                if result["json"]:
                    self.analyze_log_response(result["json"], endpoint)
            
            # Test with zone parameters
            for zone in zones:
                zone_result = self.test_endpoint(endpoint, params={"zone": zone})
                if zone_result["success"]:
                    print(f"   ✅ With zone {zone}: {zone_result['status_code']}")
                    print(f"   📊 Response: {zone_result['content'][:300]}...")
                    if zone_result["json"]:
                        self.analyze_log_response(zone_result["json"], f"{endpoint}?zone={zone}")

    def check_snapshot_specific_logs(self):
        """Check logs for specific snapshot IDs"""
        print(f"\n🎯 CHECKING LOGS FOR SPECIFIC SNAPSHOT IDs")
        print("=" * 60)
        
        for snapshot_id in self.snapshot_ids:
            print(f"\n🔍 Checking snapshot: {snapshot_id}")
            
            # Try various patterns to get logs for this snapshot
            snapshot_log_patterns = [
                f"https://api.brightdata.com/logs/{snapshot_id}",
                f"https://api.brightdata.com/logs?snapshot_id={snapshot_id}",
                f"https://api.brightdata.com/activity/{snapshot_id}",
                f"https://api.brightdata.com/activity?snapshot_id={snapshot_id}",
                f"https://api.brightdata.com/history/{snapshot_id}",
                f"https://api.brightdata.com/jobs/{snapshot_id}",
                f"https://api.brightdata.com/jobs?snapshot_id={snapshot_id}",
                f"https://api.brightdata.com/executions/{snapshot_id}",
                f"https://api.brightdata.com/runs/{snapshot_id}",
                f"https://api.brightdata.com/collections/{snapshot_id}",
            ]
            
            for pattern in snapshot_log_patterns:
                result = self.test_endpoint(pattern)
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {pattern}: {result['status_code']}")
                
                if result["success"]:
                    print(f"      🎯 FOUND LOG FOR SNAPSHOT!")
                    print(f"      📊 Log data: {result['content'][:500]}...")
                    if result["json"]:
                        self.analyze_snapshot_log(result["json"], snapshot_id)
                    return result

    def check_dataset_logs(self):
        """Check logs for our specific datasets"""
        print(f"\n📊 CHECKING DATASET-SPECIFIC LOGS")
        print("=" * 60)
        
        datasets = [
            ("Facebook", self.dataset_facebook),
            ("Instagram", self.dataset_instagram)
        ]
        
        for platform, dataset_id in datasets:
            print(f"\n🔍 Checking {platform} dataset: {dataset_id}")
            
            dataset_log_patterns = [
                f"https://api.brightdata.com/datasets/{dataset_id}/logs",
                f"https://api.brightdata.com/datasets/{dataset_id}/activity", 
                f"https://api.brightdata.com/datasets/{dataset_id}/history",
                f"https://api.brightdata.com/datasets/{dataset_id}/jobs",
                f"https://api.brightdata.com/datasets/{dataset_id}/executions",
                f"https://api.brightdata.com/datasets/{dataset_id}/runs",
                f"https://api.brightdata.com/logs?dataset_id={dataset_id}",
                f"https://api.brightdata.com/activity?dataset_id={dataset_id}",
            ]
            
            zones = ["datacenter", "residential", "mobile"]
            
            for pattern in dataset_log_patterns:
                # Test without zone
                result = self.test_endpoint(pattern)
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {pattern}: {result['status_code']}")
                
                if result["success"]:
                    print(f"      🎯 FOUND DATASET LOGS!")
                    print(f"      📊 Log data: {result['content'][:400]}...")
                    if result["json"]:
                        self.analyze_dataset_log(result["json"], platform, dataset_id)
                
                # Test with zones
                for zone in zones:
                    zone_result = self.test_endpoint(pattern, params={"zone": zone})
                    if zone_result["success"]:
                        print(f"      ✅ With zone {zone}: Found data!")
                        print(f"      📊 Zone data: {zone_result['content'][:300]}...")
                        if zone_result["json"]:
                            self.analyze_dataset_log(zone_result["json"], platform, dataset_id, zone)

    def check_download_endpoints(self):
        """Check if we can download data using snapshot IDs"""
        print(f"\n⬇️ TESTING DOWNLOAD ENDPOINTS WITH SNAPSHOT IDs")
        print("=" * 60)
        
        for snapshot_id in self.snapshot_ids:
            print(f"\n📥 Testing downloads for: {snapshot_id}")
            
            download_patterns = [
                f"https://api.brightdata.com/download/{snapshot_id}",
                f"https://api.brightdata.com/export/{snapshot_id}",
                f"https://api.brightdata.com/data/{snapshot_id}/download",
                f"https://api.brightdata.com/snapshots/{snapshot_id}/download",
                f"https://api.brightdata.com/collections/{snapshot_id}/download",
                f"https://api.brightdata.com/files/{snapshot_id}",
            ]
            
            zones = ["datacenter", "residential", "mobile"]
            
            for pattern in download_patterns:
                # Test without zone
                result = self.test_endpoint(pattern)
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {pattern}: {result['status_code']}")
                
                if result["success"]:
                    print(f"      🎯 DOWNLOAD AVAILABLE!")
                    print(f"      📊 Content preview: {result['content'][:300]}...")
                    return result
                
                # Test with zones
                for zone in zones:
                    zone_result = self.test_endpoint(pattern, params={"zone": zone})
                    if zone_result["success"]:
                        print(f"      ✅ Download with zone {zone}: Available!")
                        print(f"      📊 Content: {zone_result['content'][:300]}...")
                        return zone_result

    def analyze_log_response(self, data, endpoint):
        """Analyze log response for useful information"""
        print(f"      📋 Analyzing response from {endpoint}:")
        
        if isinstance(data, list):
            print(f"         📊 Found {len(data)} log entries")
            for i, entry in enumerate(data[:3]):  # Show first 3 entries
                if isinstance(entry, dict):
                    # Look for snapshot IDs
                    for key, value in entry.items():
                        if 'snapshot' in key.lower() or 'id' in key.lower():
                            print(f"         🆔 Entry {i+1}: {key} = {value}")
        elif isinstance(data, dict):
            # Look for snapshot IDs in the response
            for key, value in data.items():
                if 'snapshot' in key.lower() or any(sid in str(value) for sid in self.snapshot_ids):
                    print(f"         🎯 Found matching data: {key} = {value}")

    def analyze_snapshot_log(self, data, snapshot_id):
        """Analyze log data for a specific snapshot"""
        print(f"      📋 Snapshot {snapshot_id} log analysis:")
        
        if isinstance(data, dict):
            # Look for status, data location, download URLs
            interesting_keys = ['status', 'state', 'download_url', 'data_url', 'file_url', 'result_url', 'location']
            for key in interesting_keys:
                if key in data:
                    print(f"         🔍 {key}: {data[key]}")

    def analyze_dataset_log(self, data, platform, dataset_id, zone=None):
        """Analyze log data for a specific dataset"""
        zone_info = f" (zone: {zone})" if zone else ""
        print(f"      📋 {platform} dataset log analysis{zone_info}:")
        
        if isinstance(data, list):
            print(f"         📊 Found {len(data)} entries")
            # Look for entries with our snapshot IDs
            matching_entries = []
            for entry in data:
                if isinstance(entry, dict):
                    entry_str = json.dumps(entry)
                    if any(sid in entry_str for sid in self.snapshot_ids):
                        matching_entries.append(entry)
            
            if matching_entries:
                print(f"         🎯 Found {len(matching_entries)} matching entries with our snapshot IDs!")
                for entry in matching_entries[:2]:  # Show first 2 matches
                    print(f"         📄 Match: {json.dumps(entry, indent=4)[:300]}...")

def main():
    """Main function to check BrightData logs"""
    checker = BrightDataLogChecker()
    
    print("🚀 BRIGHTDATA LOG CHECKER")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objective: Find scraped data using snapshot IDs")
    print(f"🆔 Target snapshots: {', '.join(checker.snapshot_ids)}")
    print("=" * 60)
    
    # Check various log endpoints
    checker.check_brightdata_logs()
    
    # Check snapshot-specific logs
    checker.check_snapshot_specific_logs()
    
    # Check dataset-specific logs
    checker.check_dataset_logs()
    
    # Check download endpoints
    checker.check_download_endpoints()
    
    print(f"\n🎯 SUMMARY")
    print("=" * 50)
    print("✅ Tested comprehensive log and download endpoints")
    print("🔍 Searched for snapshot IDs in BrightData logs")
    print("📊 Analyzed responses for data access patterns")
    print("\n💡 Next steps if no data found:")
    print("   1. Check BrightData dashboard web interface")
    print("   2. Look for CSV/JSON export options in dashboard") 
    print("   3. Contact BrightData for data retrieval guidance")

if __name__ == "__main__":
    main()
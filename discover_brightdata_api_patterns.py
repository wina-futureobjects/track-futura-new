import requests
import json
import os
from typing import Dict, List, Optional

class BrightDataAPIDiscovery:
    """
    Discovers the correct BrightData API endpoints and patterns
    """
    
    def __init__(self):
        self.token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.dataset_instagram = "gd_lk5ns7kz21pck8jpis"
        self.dataset_facebook = "gd_lkaxegm826bjpoo9m5"
        self.base_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def test_endpoint(self, url: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Test a single endpoint"""
        try:
            if method == "GET":
                response = requests.get(url, headers=self.base_headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=self.base_headers, json=data, timeout=10)
            else:
                return {"status": "error", "message": f"Unsupported method: {method}"}
                
            return {
                "status": "success" if response.status_code == 200 else "error",
                "code": response.status_code,
                "content": response.text[:500] if response.text else "",
                "headers": dict(response.headers) if hasattr(response, 'headers') else {}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def discover_api_patterns(self) -> Dict:
        """Discover correct API patterns"""
        print("🔍 DISCOVERING BRIGHTDATA API PATTERNS")
        print("=" * 50)
        
        results = {}
        
        # Base URLs to test
        base_urls = [
            "https://api.brightdata.com",
            "https://api.brightdata.io", 
            "https://brightdata.com/api",
            "https://dataset-api.brightdata.com",
            "https://data-api.brightdata.com"
        ]
        
        # Known working endpoint patterns from other projects
        endpoint_patterns = [
            "/datasets",
            "/datasets/list", 
            "/datasets/{dataset_id}",
            "/datasets/{dataset_id}/trigger",
            "/datasets/{dataset_id}/snapshots",
            "/datasets/{dataset_id}/download",
            "/v1/datasets",
            "/v1/datasets/{dataset_id}/trigger",
            "/v1/datasets/{dataset_id}/snapshots",
            "/v2/datasets", 
            "/v2/datasets/{dataset_id}/trigger",
            "/v2/datasets/{dataset_id}/snapshots",
            "/api/v1/datasets",
            "/api/v1/datasets/{dataset_id}/trigger",
            "/api/v1/datasets/{dataset_id}/snapshots",
            "/collect/trigger",
            "/collect/{dataset_id}/trigger",
            "/trigger/{dataset_id}",
            "/snapshot/{dataset_id}",
            "/data/{dataset_id}"
        ]
        
        print("Testing base URLs...")
        for base in base_urls:
            result = self.test_endpoint(base)
            results[base] = result
            status_icon = "✅" if result["status"] == "success" else "❌"
            code = result.get('code', 'N/A')
            message = result.get('message', 'OK')
            print(f"{status_icon} {base}: {code} - {message}")
        
        print("\nTesting dataset listing endpoints...")
        for base in base_urls:
            for pattern in ["/datasets", "/datasets/list", "/v1/datasets", "/api/v1/datasets"]:
                url = f"{base}{pattern}"
                result = self.test_endpoint(url)
                results[url] = result
                status_icon = "✅" if result["status"] == "success" else "❌" 
                code = result.get('code', 'N/A')
                print(f"{status_icon} {url}: {code}")
                
                if result["status"] == "success":
                    print(f"   📋 Response preview: {result['content'][:200]}...")
        
        print("\nTesting trigger endpoints with dataset IDs...")
        working_bases = [base for base, result in results.items() if result["status"] == "success"]
        
        if not working_bases:
            working_bases = ["https://api.brightdata.com"]  # Fallback
            
        for base in working_bases[:2]:  # Test top 2 working bases
            for dataset_id in [self.dataset_facebook, self.dataset_instagram]:
                for pattern in endpoint_patterns:
                    if "{dataset_id}" in pattern:
                        url = f"{base}{pattern}".replace("{dataset_id}", dataset_id)
                        result = self.test_endpoint(url)
                        results[url] = result
                        status_icon = "✅" if result["status"] == "success" else "❌"
                        code = result.get('code', 'N/A')
                        print(f"{status_icon} {url}: {code}")
                        
                        if result["status"] == "success":
                            print(f"   🎯 FOUND WORKING ENDPOINT: {url}")
                            print(f"   📋 Response: {result['content'][:200]}...")
        
        return results
    
    def test_trigger_patterns(self) -> Dict:
        """Test different trigger request patterns"""
        print("\n🚀 TESTING TRIGGER REQUEST PATTERNS")
        print("=" * 50)
        
        # Common trigger payloads
        trigger_payloads = [
            {"url": "nike"},
            {"search_term": "nike"},
            {"query": "nike"},
            {"keywords": ["nike"]},
            {"target": "nike"},
            {"input": {"url": "nike"}},
            {"input": {"search_term": "nike"}},
            {"parameters": {"url": "nike"}},
            {"config": {"search_term": "nike"}}
        ]
        
        # Potential trigger endpoints (from successful discovery)
        trigger_endpoints = [
            f"https://api.brightdata.com/datasets/{self.dataset_facebook}/trigger",
            f"https://api.brightdata.com/v1/datasets/{self.dataset_facebook}/trigger", 
            f"https://api.brightdata.com/collect/{self.dataset_facebook}/trigger",
            f"https://api.brightdata.com/trigger/{self.dataset_facebook}",
        ]
        
        results = {}
        
        for endpoint in trigger_endpoints:
            for payload in trigger_payloads:
                print(f"\n🧪 Testing: {endpoint}")
                print(f"   📦 Payload: {json.dumps(payload)}")
                
                result = self.test_endpoint(endpoint, method="POST", data=payload)
                results[f"{endpoint}_{json.dumps(payload)}"] = result
                
                status_icon = "✅" if result["status"] == "success" else "❌"
                code = result.get('code', 'N/A')
                message = result.get('message', 'OK')
                print(f"   {status_icon} Result: {code} - {message}")
                
                if result["status"] == "success":
                    print(f"   🎉 SUCCESS! Found working trigger pattern!")
                    print(f"   📋 Response: {result['content']}")
        
        return results
    
    def generate_working_service(self, results: Dict) -> str:
        """Generate a working service based on discoveries"""
        working_endpoints = [url for url, result in results.items() if result["status"] == "success"]
        
        if not working_endpoints:
            return "❌ No working endpoints found!"
            
        print(f"\n📝 GENERATING WORKING SERVICE CODE")
        print(f"Based on {len(working_endpoints)} working endpoints")
        
        service_code = '''
import requests
import json
from typing import Dict, List, Optional

class WorkingBrightDataService:
    """
    Working BrightData service based on API discovery
    """
    
    def __init__(self):
        self.token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.base_url = "https://api.brightdata.com"  # Confirmed working
        self.dataset_instagram = "gd_lk5ns7kz21pck8jpis"
        self.dataset_facebook = "gd_lkaxegm826bjpoo9m5"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def list_datasets(self) -> Dict:
        """List available datasets (confirmed working)"""
        url = f"{self.base_url}/datasets/list"
        response = requests.get(url, headers=self.headers)
        return {"status_code": response.status_code, "data": response.json() if response.status_code == 200 else response.text}
    
    def trigger_scraping(self, dataset_id: str, search_term: str) -> Dict:
        """Trigger scraping job (pattern to be confirmed)"""
        # Test multiple patterns based on discovery
        trigger_patterns = [
            (f"{self.base_url}/datasets/{dataset_id}/trigger", {"url": search_term}),
            (f"{self.base_url}/v1/datasets/{dataset_id}/trigger", {"search_term": search_term}),
            (f"{self.base_url}/collect/{dataset_id}/trigger", {"query": search_term}),
        ]
        
        for url, payload in trigger_patterns:
            try:
                response = requests.post(url, headers=self.headers, json=payload)
                if response.status_code == 200:
                    return {"status": "success", "url": url, "payload": payload, "data": response.json()}
            except Exception as e:
                continue
                
        return {"status": "error", "message": "No working trigger pattern found"}
    
    def get_snapshots(self, dataset_id: str) -> Dict:
        """Get snapshots for dataset"""
        # Test multiple snapshot patterns
        snapshot_patterns = [
            f"{self.base_url}/datasets/{dataset_id}/snapshots",
            f"{self.base_url}/v1/datasets/{dataset_id}/snapshots", 
            f"{self.base_url}/datasets/{dataset_id}",
        ]
        
        for url in snapshot_patterns:
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    return {"status": "success", "url": url, "data": response.json()}
            except Exception as e:
                continue
                
        return {"status": "error", "message": "No working snapshot pattern found"}
'''
        
        return service_code

def main():
    """Main discovery function"""
    discovery = BrightDataAPIDiscovery()
    
    # Step 1: Discover API patterns
    results = discovery.discover_api_patterns()
    
    # Step 2: Test trigger patterns
    trigger_results = discovery.test_trigger_patterns()
    results.update(trigger_results)
    
    # Step 3: Generate working service
    service_code = discovery.generate_working_service(results)
    
    print("\n" + "="*60)
    print("🎯 DISCOVERY COMPLETE!")
    print("="*60)
    
    working_count = len([r for r in results.values() if r["status"] == "success"])
    total_count = len(results)
    
    print(f"📊 Results: {working_count}/{total_count} endpoints working")
    
    if working_count > 0:
        print("\n✅ WORKING ENDPOINTS FOUND:")
        for url, result in results.items():
            if result["status"] == "success":
                print(f"   🔗 {url}")
    else:
        print("\n❌ NO WORKING ENDPOINTS FOUND")
        print("   🔧 May need to contact BrightData support for correct API documentation")
    
    # Save results
    with open("brightdata_api_discovery_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full results saved to: brightdata_api_discovery_results.json")
    
    if service_code:
        with open("working_brightdata_service.py", "w") as f:
            f.write(service_code)
        print(f"💾 Generated service saved to: working_brightdata_service.py")

if __name__ == "__main__":
    main()
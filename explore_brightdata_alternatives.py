import requests
import json
from urllib.parse import urljoin
import time

class BrightDataAPIExplorer:
    """Comprehensive exploration of BrightData API to find working endpoints"""
    
    def __init__(self):
        self.token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
        self.dataset_instagram = "gd_lk5ns7kz21pck8jpis"
        self.dataset_facebook = "gd_lkaxegm826bjpoo9m5"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "TrackFutura-API-Client/1.0"
        }
        self.found_endpoints = []
        
    def test_endpoint(self, url, method="GET", data=None, timeout=10):
        """Test endpoint with better error handling"""
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=timeout)
            
            result = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "headers": dict(response.headers),
                "content": response.text[:1000] if response.text else ""
            }
            
            if result["success"]:
                try:
                    result["json"] = response.json()
                except:
                    pass
                self.found_endpoints.append(result)
                
            return result
            
        except Exception as e:
            return {
                "url": url, 
                "method": method,
                "status_code": 0, 
                "success": False, 
                "error": str(e)[:200]
            }

    def explore_api_discovery(self):
        """Use API discovery techniques to find endpoints"""
        print("🔍 API DISCOVERY METHODS")
        print("=" * 50)
        
        # Method 1: Check for API documentation endpoints
        doc_endpoints = [
            "https://api.brightdata.com/docs",
            "https://api.brightdata.com/documentation", 
            "https://api.brightdata.com/swagger",
            "https://api.brightdata.com/openapi",
            "https://api.brightdata.com/api-docs",
            "https://api.brightdata.com/v1/docs",
            "https://api.brightdata.com/.well-known/api",
            "https://api.brightdata.com/spec",
        ]
        
        print("\n📚 Testing documentation endpoints:")
        for endpoint in doc_endpoints:
            result = self.test_endpoint(endpoint)
            status = "✅" if result["success"] else "❌"
            print(f"{status} {endpoint}: {result['status_code']}")
            if result["success"]:
                print(f"   📄 Content preview: {result['content'][:200]}...")

    def explore_rest_patterns(self):
        """Explore RESTful API patterns"""
        print("\n🌐 EXPLORING REST API PATTERNS")
        print("=" * 50)
        
        # Common REST patterns for datasets
        patterns = [
            # Resource-based patterns
            ("/datasets", "GET"),
            ("/datasets/{id}", "GET"),
            ("/datasets/{id}/jobs", "GET"),
            ("/datasets/{id}/runs", "GET"),
            ("/datasets/{id}/executions", "GET"),
            ("/datasets/{id}/collections", "GET"),
            
            # Job/Collection patterns  
            ("/jobs", "GET"),
            ("/jobs/{id}", "GET"),
            ("/collections", "GET"),
            ("/collections/{id}", "GET"),
            ("/runs", "GET"),
            ("/runs/{id}", "GET"),
            
            # Data access patterns
            ("/data", "GET"),
            ("/data/{id}", "GET"),
            ("/exports", "GET"),
            ("/exports/{id}", "GET"),
            ("/downloads", "GET"),
            ("/downloads/{id}", "GET"),
        ]
        
        base_url = "https://api.brightdata.com"
        
        for pattern, method in patterns:
            # Test with dataset IDs
            for dataset_id in [self.dataset_facebook, self.dataset_instagram]:
                url = urljoin(base_url, pattern.replace("{id}", dataset_id))
                result = self.test_endpoint(url, method)
                
                status = "✅" if result["success"] else "❌"
                print(f"{status} {method} {url}: {result['status_code']}")
                
                if result["success"]:
                    print(f"   🎯 FOUND WORKING PATTERN: {pattern}")
                    if "json" in result:
                        print(f"   📊 Response: {json.dumps(result['json'], indent=2)[:300]}...")

    def explore_webhook_endpoints(self):
        """Look for webhook/callback related endpoints"""
        print("\n🔗 EXPLORING WEBHOOK/CALLBACK PATTERNS")
        print("=" * 50)
        
        webhook_patterns = [
            "/webhooks",
            "/callbacks", 
            "/notifications",
            "/events",
            "/status",
            "/jobs/status",
            "/datasets/status",
        ]
        
        base_url = "https://api.brightdata.com"
        
        for pattern in webhook_patterns:
            url = urljoin(base_url, pattern)
            result = self.test_endpoint(url)
            
            status = "✅" if result["success"] else "❌"
            print(f"{status} GET {url}: {result['status_code']}")
            
            if result["success"]:
                print(f"   📋 Content: {result['content'][:200]}...")

    def explore_versioned_apis(self):
        """Test different API versions"""
        print("\n🔢 EXPLORING API VERSIONS")
        print("=" * 50)
        
        versions = ["v1", "v2", "v3", "v4", "api/v1", "api/v2"]
        endpoints = ["datasets", "jobs", "collections", "data", "snapshots"]
        
        for version in versions:
            for endpoint in endpoints:
                url = f"https://api.brightdata.com/{version}/{endpoint}"
                result = self.test_endpoint(url)
                
                status = "✅" if result["success"] else "❌"
                print(f"{status} {url}: {result['status_code']}")
                
                if result["success"]:
                    print(f"   🎯 FOUND WORKING VERSION: {version}/{endpoint}")

    def explore_data_formats(self):
        """Test different data format endpoints"""
        print("\n📊 EXPLORING DATA FORMAT ENDPOINTS")
        print("=" * 50)
        
        # Test known snapshot IDs with different format endpoints
        snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
        formats = ["json", "csv", "jsonl", "ndjson", "parquet"]
        
        patterns = [
            "/data/{snapshot_id}",
            "/export/{snapshot_id}",
            "/download/{snapshot_id}",
            "/snapshots/{snapshot_id}/export",
            "/snapshots/{snapshot_id}/download",
        ]
        
        for snapshot_id in snapshot_ids:
            print(f"\n🔍 Testing snapshot: {snapshot_id}")
            
            for pattern in patterns:
                base_url =f"https://api.brightdata.com{pattern}".replace("{snapshot_id}", snapshot_id)
                
                # Test without format
                result = self.test_endpoint(base_url)
                status = "✅" if result["success"] else "❌"
                print(f"{status} {base_url}: {result['status_code']}")
                
                # Test with formats
                for fmt in formats:
                    url_with_format = f"{base_url}.{fmt}"
                    result = self.test_endpoint(url_with_format)
                    if result["success"]:
                        print(f"✅ FOUND: {url_with_format}")
                        
                    # Also test with query parameter
                    url_with_param = f"{base_url}?format={fmt}"
                    result = self.test_endpoint(url_with_param)
                    if result["success"]:
                        print(f"✅ FOUND: {url_with_param}")

    def explore_graphql_endpoints(self):
        """Test for GraphQL endpoints"""
        print("\n🔍 EXPLORING GRAPHQL ENDPOINTS")
        print("=" * 50)
        
        graphql_endpoints = [
            "https://api.brightdata.com/graphql",
            "https://api.brightdata.com/v1/graphql",
            "https://api.brightdata.com/query",
        ]
        
        # Simple introspection query
        introspection_query = {
            "query": "{ __schema { types { name } } }"
        }
        
        for endpoint in graphql_endpoints:
            result = self.test_endpoint(endpoint, method="POST", data=introspection_query)
            status = "✅" if result["success"] else "❌"
            print(f"{status} {endpoint}: {result['status_code']}")
            
            if result["success"]:
                print(f"   🎯 GRAPHQL ENDPOINT FOUND!")
                print(f"   📊 Response: {result['content'][:300]}...")

    def explore_response_headers(self):
        """Analyze response headers for clues"""
        print("\n📋 ANALYZING RESPONSE HEADERS FOR CLUES")
        print("=" * 50)
        
        if self.found_endpoints:
            for endpoint in self.found_endpoints:
                print(f"\n🔍 Headers from: {endpoint['url']}")
                headers = endpoint.get('headers', {})
                
                # Look for interesting headers
                interesting_headers = [
                    'Link', 'X-API-Version', 'X-Rate-Limit', 
                    'X-Available-Endpoints', 'Allow', 'Access-Control-Allow-Methods'
                ]
                
                for header in interesting_headers:
                    if header in headers:
                        print(f"   📌 {header}: {headers[header]}")

    def test_options_requests(self):
        """Send OPTIONS requests to discover available methods"""
        print("\n🔧 TESTING OPTIONS REQUESTS")
        print("=" * 50)
        
        test_urls = [
            "https://api.brightdata.com/datasets",
            f"https://api.brightdata.com/datasets/{self.dataset_facebook}",
            f"https://api.brightdata.com/snapshots/s_mggq02qnd20yqnt78",
        ]
        
        for url in test_urls:
            try:
                response = requests.options(url, headers=self.headers, timeout=10)
                print(f"OPTIONS {url}: {response.status_code}")
                
                if 'Allow' in response.headers:
                    print(f"   🔧 Allowed methods: {response.headers['Allow']}")
                
                if 'Access-Control-Allow-Methods' in response.headers:
                    print(f"   🌐 CORS methods: {response.headers['Access-Control-Allow-Methods']}")
                    
            except Exception as e:
                print(f"❌ OPTIONS {url}: {str(e)[:100]}")

def main():
    """Main exploration function"""
    explorer = BrightDataAPIExplorer()
    
    print("🚀 COMPREHENSIVE BRIGHTDATA API EXPLORATION")
    print("=" * 70)
    print("Objective: Find working endpoints without contacting support")
    print("=" * 70)
    
    # Run all exploration methods
    explorer.explore_api_discovery()
    explorer.explore_rest_patterns()
    explorer.explore_versioned_apis()
    explorer.explore_webhook_endpoints()
    explorer.explore_data_formats()
    explorer.explore_graphql_endpoints()
    explorer.test_options_requests()
    explorer.explore_response_headers()
    
    # Summary
    print("\n🎯 EXPLORATION RESULTS")
    print("=" * 50)
    
    if explorer.found_endpoints:
        print(f"✅ FOUND {len(explorer.found_endpoints)} WORKING ENDPOINTS:")
        for endpoint in explorer.found_endpoints:
            print(f"   🔗 {endpoint['method']} {endpoint['url']} ({endpoint['status_code']})")
    else:
        print("❌ No new working endpoints discovered")
        print("🔧 Recommendations:")
        print("   1. Check BrightData dashboard for API documentation")
        print("   2. Look for client libraries or SDKs")
        print("   3. Check community forums or Stack Overflow")
        print("   4. Try reverse engineering from browser network tab")
    
    # Save results
    results = {
        "exploration_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "found_endpoints": explorer.found_endpoints,
        "total_endpoints_tested": "100+",
        "success_rate": f"{len(explorer.found_endpoints)}/100+"
    }
    
    with open("brightdata_api_exploration_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: brightdata_api_exploration_results.json")

if __name__ == "__main__":
    main()
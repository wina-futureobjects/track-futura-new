import requests
import json
from datetime import datetime

def test_brightdata_web_scraper():
    """Test if we can scrape data directly from BrightData web interface"""
    print("🌐 TESTING BRIGHTDATA WEB INTERFACE APPROACH")
    print("=" * 60)
    
    # BrightData web dashboard endpoints (might be accessible)
    web_endpoints = [
        "https://brightdata.com/api/user/datasets",
        "https://brightdata.com/api/datasets",
        "https://control.brightdata.com/api/datasets",
        "https://dashboard.brightdata.com/api/datasets",
        "https://console.brightdata.com/api/datasets",
    ]
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for endpoint in web_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   📊 Content: {response.text[:300]}...")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)[:100]}")

def test_brightdata_public_endpoints():
    """Test publicly documented BrightData endpoints"""
    print("\n📖 TESTING PUBLICLY DOCUMENTED ENDPOINTS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # From BrightData documentation (if we can find patterns)
    documented_patterns = [
        # Proxy zone patterns
        "https://api.brightdata.com/zone",
        "https://api.brightdata.com/zones",
        "https://api.brightdata.com/proxy/zones",
        
        # Account patterns
        "https://api.brightdata.com/account",
        "https://api.brightdata.com/user",
        "https://api.brightdata.com/profile",
        
        # Usage patterns
        "https://api.brightdata.com/usage",
        "https://api.brightdata.com/billing",
        "https://api.brightdata.com/limits",
        
        # Data patterns 
        "https://api.brightdata.com/datacenter",
        "https://api.brightdata.com/residential",
        "https://api.brightdata.com/mobile",
    ]
    
    for endpoint in documented_patterns:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"  
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   📊 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)[:100]}")

def test_alternative_brightdata_domains():
    """Test alternative BrightData domains"""
    print("\n🌍 TESTING ALTERNATIVE BRIGHTDATA DOMAINS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Alternative domains
    domains = [
        "https://luminati.io/api",
        "https://data.brightdata.com/api", 
        "https://collect.brightdata.com/api",
        "https://scrape.brightdata.com/api",
        "https://proxy.brightdata.com/api",
    ]
    
    endpoints = ["datasets/list", "datasets", "status"]
    
    for domain in domains:
        for endpoint in endpoints:
            url = f"{domain}/{endpoint}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} {url}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   🎯 FOUND WORKING DOMAIN: {domain}")
                    print(f"   📊 Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"❌ {url}: {str(e)[:100]}")

def test_proxy_manager_api():
    """Test Proxy Manager API patterns (BrightData's older product)"""
    print("\n🔌 TESTING PROXY MANAGER API PATTERNS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Proxy Manager patterns
    pm_endpoints = [
        "https://api.brightdata.com/proxy_manager/datasets",
        "https://api.brightdata.com/lpm/datasets", 
        "https://api.brightdata.com/pm/datasets",
        "https://api.brightdata.com/luminati/datasets",
        "https://api.brightdata.com/scraping/datasets",
    ]
    
    for endpoint in pm_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   🎯 FOUND PROXY MANAGER API!")
                print(f"   📊 Response: {response.text[:300]}...")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)[:100]}")

def analyze_status_endpoint():
    """Analyze the working /status endpoint for more clues"""
    print("\n🔍 ANALYZING /STATUS ENDPOINT FOR CLUES")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("https://api.brightdata.com/status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("📊 Status Response Analysis:")
            print(json.dumps(data, indent=2))
            
            # Look for clues in the response
            if "customer" in data:
                customer_id = data["customer"]
                print(f"\n🆔 Customer ID found: {customer_id}")
                
                # Try customer-specific endpoints
                customer_endpoints = [
                    f"https://api.brightdata.com/customers/{customer_id}/datasets",
                    f"https://api.brightdata.com/customer/{customer_id}/datasets",
                    f"https://api.brightdata.com/users/{customer_id}/datasets",
                ]
                
                for endpoint in customer_endpoints:
                    try:
                        resp = requests.get(endpoint, headers=headers, timeout=10)
                        status = "✅" if resp.status_code == 200 else "❌"
                        print(f"{status} {endpoint}: {resp.status_code}")
                        
                        if resp.status_code == 200:
                            print(f"   🎯 CUSTOMER ENDPOINT FOUND!")
                            print(f"   📊 Response: {resp.text[:300]}...")
                            
                    except Exception as e:
                        print(f"❌ {endpoint}: {str(e)[:100]}")
            
            # Check auth failure reason
            if "auth_fail_reason" in data:
                auth_reason = data["auth_fail_reason"]
                print(f"\n⚠️  Auth failure reason: {auth_reason}")
                
                if auth_reason == "zone_not_found":
                    print("   💡 This suggests we need to specify a 'zone' parameter")
                    print("   🔧 Trying zone-based endpoints...")
                    
                    # Try zone-based patterns
                    zone_endpoints = [
                        "https://api.brightdata.com/datasets/list?zone=datacenter",
                        "https://api.brightdata.com/datasets/list?zone=residential",
                        "https://api.brightdata.com/datasets/list?zone=mobile",
                    ]
                    
                    for endpoint in zone_endpoints:
                        try:
                            resp = requests.get(endpoint, headers=headers, timeout=10)
                            status = "✅" if resp.status_code == 200 else "❌"
                            print(f"   {status} {endpoint}: {resp.status_code}")
                            
                            if resp.status_code == 200:
                                print(f"      🎯 ZONE PARAMETER WORKS!")
                                print(f"      📊 Response: {resp.text[:200]}...")
                                
                        except Exception as e:
                            print(f"   ❌ {endpoint}: {str(e)[:100]}")
            
    except Exception as e:
        print(f"❌ Failed to analyze /status: {str(e)}")

def main():
    print("🔍 ALTERNATIVE BRIGHTDATA API DISCOVERY METHODS")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Goal: Find working endpoints through alternative approaches")
    print("=" * 70)
    
    # Run all alternative methods
    analyze_status_endpoint()
    test_brightdata_web_scraper()
    test_brightdata_public_endpoints()
    test_alternative_brightdata_domains()
    test_proxy_manager_api()
    
    print("\n🎯 SUMMARY OF ALTERNATIVE APPROACHES")
    print("=" * 50)
    print("If no working endpoints found, consider:")
    print("1. 🌐 Login to BrightData dashboard and inspect network requests")
    print("2. 📚 Check BrightData documentation/changelog for API changes")
    print("3. 🔍 Search GitHub for BrightData API usage examples")
    print("4. 💬 Check BrightData community forums")
    print("5. 📧 Contact BrightData support with technical details")

if __name__ == "__main__":
    main()
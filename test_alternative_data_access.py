import requests
import json
from datetime import datetime

def test_brightdata_files_api():
    """Test if BrightData uses a files/storage-based API for snapshot data"""
    print("🗂️ TESTING FILES/STORAGE API PATTERNS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test different file/storage patterns
    base_patterns = [
        "https://storage.brightdata.com",
        "https://files.brightdata.com", 
        "https://data-storage.brightdata.com",
        "https://snapshots.brightdata.com",
        "https://results.brightdata.com",
        "https://downloads.brightdata.com",
    ]
    
    for base in base_patterns:
        print(f"\n🧪 Testing base: {base}")
        
        for snapshot_id in snapshot_ids:
            file_endpoints = [
                f"{base}/{snapshot_id}",
                f"{base}/{snapshot_id}.json",
                f"{base}/{snapshot_id}.csv", 
                f"{base}/snapshots/{snapshot_id}",
                f"{base}/data/{snapshot_id}",
                f"{base}/results/{snapshot_id}",
            ]
            
            for endpoint in file_endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"      🎯 FOUND FILE ACCESS!")
                        print(f"      📊 Content: {response.text[:300]}...")
                        return endpoint, response.text
                        
                except Exception as e:
                    if "Max retries exceeded" not in str(e):
                        print(f"   ❌ {endpoint}: {str(e)[:50]}")

def test_brightdata_s3_patterns():
    """Test if BrightData uses S3-like patterns for data storage"""
    print("\n☁️ TESTING S3-LIKE STORAGE PATTERNS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb" 
    customer_id = "hl_f7614f18"  # From status endpoint
    snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # S3-like patterns
    s3_patterns = [
        f"https://brightdata-data.s3.amazonaws.com",
        f"https://luminati-data.s3.amazonaws.com",
        f"https://brightdata-snapshots.s3.amazonaws.com",
        f"https://s3.amazonaws.com/brightdata-data",
        f"https://s3.amazonaws.com/luminati-data",
    ]
    
    for base in s3_patterns:
        print(f"\n🧪 Testing S3 pattern: {base}")
        
        for snapshot_id in snapshot_ids:
            s3_endpoints = [
                f"{base}/{customer_id}/{snapshot_id}.json",
                f"{base}/{customer_id}/{snapshot_id}.csv",
                f"{base}/snapshots/{customer_id}/{snapshot_id}",
                f"{base}/data/{snapshot_id}",
                f"{base}/{snapshot_id}",
            ]
            
            for endpoint in s3_endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"      🎯 FOUND S3 DATA!")
                        print(f"      📊 Content: {response.text[:300]}...")
                        return endpoint, response.text
                        
                except Exception as e:
                    if "Max retries exceeded" not in str(e):
                        print(f"   ❌ {endpoint}: {str(e)[:50]}")

def test_brightdata_cdn_patterns():
    """Test CDN patterns for data delivery"""
    print("\n🌐 TESTING CDN PATTERNS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # CDN patterns
    cdn_patterns = [
        "https://cdn.brightdata.com",
        "https://static.brightdata.com",
        "https://assets.brightdata.com",
        "https://brightdata.s3.amazonaws.com",
        "https://brightdata-cdn.s3.amazonaws.com",
    ]
    
    for base in cdn_patterns:
        print(f"\n🧪 Testing CDN: {base}")
        
        for snapshot_id in snapshot_ids:
            cdn_endpoints = [
                f"{base}/data/{snapshot_id}",
                f"{base}/snapshots/{snapshot_id}",
                f"{base}/results/{snapshot_id}",
                f"{base}/{snapshot_id}.json",
                f"{base}/{snapshot_id}.csv",
            ]
            
            for endpoint in cdn_endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)  # No auth for CDN
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"      🎯 FOUND CDN DATA!")
                        print(f"      📊 Content: {response.text[:300]}...")
                        return endpoint, response.text
                        
                except Exception as e:
                    if "Max retries exceeded" not in str(e):
                        print(f"   ❌ {endpoint}: {str(e)[:50]}")

def test_brightdata_ftp_patterns():
    """Test if snapshots are accessible via direct URLs"""
    print("\n📁 TESTING DIRECT ACCESS PATTERNS")
    print("=" * 60)
    
    snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
    
    # Direct access patterns (no auth)
    direct_patterns = [
        "https://brightdata.com/downloads",
        "https://brightdata.com/data",
        "https://brightdata.com/snapshots", 
        "https://brightdata.com/exports",
        "https://downloads.brightdata.com",
        "https://exports.brightdata.com",
    ]
    
    for base in direct_patterns:
        print(f"\n🧪 Testing direct access: {base}")
        
        for snapshot_id in snapshot_ids:
            direct_endpoints = [
                f"{base}/{snapshot_id}",
                f"{base}/{snapshot_id}.json",
                f"{base}/{snapshot_id}.csv",
                f"{base}/{snapshot_id}.zip",
                f"{base}/data/{snapshot_id}",
            ]
            
            for endpoint in direct_endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"      🎯 FOUND DIRECT ACCESS!")
                        print(f"      📊 Content: {response.text[:300]}...")
                        return endpoint, response.text
                        
                except Exception as e:
                    if "Max retries exceeded" not in str(e):
                        print(f"   ❌ {endpoint}: {str(e)[:50]}")

def test_alternative_api_formats():
    """Test if the API uses different formats or protocols"""
    print("\n🔄 TESTING ALTERNATIVE API FORMATS")
    print("=" * 60)
    
    token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    snapshot_ids = ["s_mggq02qnd20yqnt78", "s_mggpf9c8d4954otj6"]
    
    # Test XML/SOAP endpoints
    xml_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/xml"
    }
    
    soap_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/xml",
        "SOAPAction": "GetSnapshot"
    }
    
    for snapshot_id in snapshot_ids:
        print(f"\n🧪 Testing alternative formats for: {snapshot_id}")
        
        # XML endpoints
        xml_endpoints = [
            f"https://api.brightdata.com/xml/snapshots/{snapshot_id}",
            f"https://api.brightdata.com/snapshots/{snapshot_id}.xml",
        ]
        
        for endpoint in xml_endpoints:
            try:
                response = requests.get(endpoint, headers=xml_headers, timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} XML {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      🎯 FOUND XML DATA!")
                    print(f"      📊 Content: {response.text[:200]}...")
                    
            except Exception as e:
                if "Max retries exceeded" not in str(e):
                    print(f"   ❌ XML {endpoint}: {str(e)[:50]}")

def main():
    """Test all alternative data access patterns"""
    print("🚀 ALTERNATIVE BRIGHTDATA DATA ACCESS TESTING")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Manager's hint: Look at BrightData logs, use matching snapshot IDs")
    print("🆔 Target snapshots: s_mggq02qnd20yqnt78, s_mggpf9c8d4954otj6")
    print("=" * 70)
    
    # Test all patterns
    results = []
    
    result1 = test_brightdata_files_api()
    if result1:
        results.append(("Files API", result1))
    
    result2 = test_brightdata_s3_patterns()
    if result2:
        results.append(("S3 Storage", result2))
    
    result3 = test_brightdata_cdn_patterns()
    if result3:
        results.append(("CDN Access", result3))
    
    result4 = test_brightdata_ftp_patterns()
    if result4:
        results.append(("Direct Access", result4))
    
    test_alternative_api_formats()
    
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 50)
    
    if results:
        print(f"✅ SUCCESS! Found {len(results)} working data access methods:")
        for method, (url, data) in results:
            print(f"   🔗 {method}: {url}")
            print(f"   📊 Data preview: {data[:200]}...")
    else:
        print("❌ No working data access patterns found")
        print("\n💡 RECOMMENDATIONS:")
        print("   1. 🌐 Check BrightData web dashboard for data export options")
        print("   2. 📧 Contact BrightData support for snapshot data access")
        print("   3. 🔍 Look for webhook URLs in BrightData account settings")
        print("   4. 📋 Check if data was delivered via email or notification")
        print("   5. 🗂️ Search for downloaded files in local system")

if __name__ == "__main__":
    main()
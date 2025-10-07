import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_apify_configs():
    print("\nTesting Apify configs endpoint...")
    response = requests.get(f"{BASE_URL}/api/apify/configs/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data.get('count', 0)} configs")
    if data.get('results'):
        print(f"First config: {data['results'][0]['name']}")
    return response.status_code == 200

def test_batch_jobs():
    print("\nTesting Apify batch jobs endpoint...")
    response = requests.get(f"{BASE_URL}/api/apify/batch-jobs/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data.get('count', 0)} batch jobs")
    if data.get('results'):
        print(f"First job: {data['results'][0]['name']} - Status: {data['results'][0]['status']}")
    return response.status_code == 200

def test_scraper_requests():
    print("\nTesting Apify scraper requests endpoint...")
    response = requests.get(f"{BASE_URL}/api/apify/scraper-requests/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data.get('count', 0)} scraper requests")
    if data.get('results'):
        print(f"First request: {data['results'][0]['platform']} - {data['results'][0]['source_name']}")
    return response.status_code == 200

def test_workflow_scraping_jobs():
    print("\nTesting workflow scraping jobs endpoint...")
    response = requests.get(f"{BASE_URL}/api/workflow/scraping-jobs/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data.get('count', 0)} scraping jobs")
    if data.get('results'):
        print(f"First job: Platform={data['results'][0]['platform']}, Status={data['results'][0]['status']}")
    return response.status_code == 200

def test_dashboard_stats():
    print("\nTesting dashboard stats endpoint...")
    response = requests.get(f"{BASE_URL}/api/dashboard/stats/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total Posts: {data.get('totalPosts', 0)}")
    print(f"Total Accounts: {data.get('totalAccounts', 0)}")
    print(f"Total Reports: {data.get('totalReports', 0)}")
    return response.status_code == 200

def test_reports():
    print("\nTesting reports endpoints...")
    response = requests.get(f"{BASE_URL}/api/reports/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Available endpoints: {list(data.keys())}")

    # Test templates
    response = requests.get(f"{BASE_URL}/api/reports/templates/")
    print(f"Templates status: {response.status_code}")
    templates_data = response.json()
    if isinstance(templates_data, list):
        print(f"Found {len(templates_data)} templates")
    else:
        print(f"Found {templates_data.get('count', 0)} templates")

    return response.status_code == 200

def main():
    print("="*60)
    print("TRACKFUTURA API TEST SUITE")
    print("="*60)

    results = {
        "Health Check": test_health(),
        "Apify Configs": test_apify_configs(),
        "Batch Jobs": test_batch_jobs(),
        "Scraper Requests": test_scraper_requests(),
        "Workflow Jobs": test_workflow_scraping_jobs(),
        "Dashboard Stats": test_dashboard_stats(),
        "Reports": test_reports(),
    }

    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\nAll tests passed successfully!")
    else:
        print(f"\nWarning: {total_tests - passed_tests} test(s) failed")

if __name__ == "__main__":
    main()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataBatchJob
from django.utils import timezone

print("=== BRIGHTDATA SCRAPER REQUEST STATUS ===")
requests = BrightDataScraperRequest.objects.all().order_by("-created_at")
print(f"Total requests: {requests.count()}")

for req in requests[:10]:
    print(f"Request {req.id}:")
    print(f"  Status: {req.status}")
    print(f"  Platform: {req.platform}")
    print(f"  Target: {req.target_url}")
    print(f"  Snapshot ID: {req.snapshot_id}")
    print(f"  Folder ID: {req.folder_id}")
    print(f"  Created: {req.created_at}")
    print()

print("=== BRIGHTDATA BATCH JOBS ===")
jobs = BrightDataBatchJob.objects.all().order_by("-created_at")
print(f"Total batch jobs: {jobs.count()}")

for job in jobs[:5]:
    print(f"Job {job.id}:")
    print(f"  Status: {job.status}")
    print(f"  Collection ID: {job.collection_id}")
    print(f"  Inputs count: {job.inputs_count}")
    print(f"  Created: {job.created_at}")
    print()
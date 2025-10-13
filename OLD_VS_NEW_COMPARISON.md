# OLD (Working) vs NEW (Current) Project Comparison

## Critical Findings

### ✅ OLD Project (TrackFutura-main) - WORKS CORRECTLY

**Location**: `backend/brightdata_integration/services.py:563-614`

#### Folder Creation Flow:
```python
def execute_batch_job(self, job_id: int):
    # 1. Get sources for job
    sources = self._get_sources_for_job(job)

    # 2. For each source and platform:
    for source in sources:
        for platform in platforms:
            # 3. CREATE FOLDER FIRST!
            folder_id = self._get_or_create_output_folder(
                job, platform, source, content_type
            )

            # 4. Then create scraper request WITH folder_id
            scraper_request = self._create_scraper_request(
                job, source, platform, url, config,
                folder_id,  # ← FOLDER ID IS SET!
                content_type
            )

    # 5. Finally trigger BrightData API
    self._execute_batch_requests(scraper_requests)
```

#### `_get_or_create_output_folder()` Function:
```python
def _get_or_create_output_folder(self, job, platform, source, content_type):
    """Create UnifiedRunFolder BEFORE scraping"""

    folder_name = f"{platform.title()} {content_type.title()} - {source.name}"

    # Import UnifiedRunFolder
    from track_accounts.models import UnifiedRunFolder

    # Create or get the folder
    unified_folder, created = UnifiedRunFolder.objects.get_or_create(
        name=folder_name,
        defaults={
            'description': f'Created from batch job: {job.name}',
            'folder_type': 'content',
            'project_id': job.project_id,
            'category': folder_category,
            'service_code': content_type
        }
    )

    return unified_folder.id  # ← Returns folder ID!
```

**Result**: ✅ Folder exists before webhook, data saves correctly

---

### ❌ NEW Project (TrackFutura - Copy) - BROKEN BEFORE FIX

**Location**: `backend/workflow/views.py:268-308` (BEFORE my fix)

#### Original Broken Flow:
```python
@action(detail=True, methods=['post'])
def start(self, request, pk=None):
    # 1. Create batch_job
    batch_job = BrightDataBatchJob.objects.create(...)

    # 2. Trigger scraper IMMEDIATELY
    #    ❌ NO FOLDER CREATED!
    #    ❌ NO SCRAPER REQUEST WITH FOLDER_ID!
    batch_job_result = scraper.trigger_scraper(
        platform=platform,
        urls=urls
    )

    # Webhook arrives → no folder_id → data lost ❌
```

**Result**: ❌ No folder, webhook can't save data

---

### ✅ NEW Project - AFTER MY FIX

**Location**: `backend/workflow/views.py:268-362` (AFTER my fix today)

#### Fixed Flow (Matches OLD Project Pattern):
```python
@action(detail=True, methods=['post'])
def start(self, request, pk=None):
    # 1. CREATE FOLDER FIRST! (NEW!)
    folder = UnifiedRunFolder.objects.create(
        name=f"{platform.title()} Data - {project.name}",
        project=input_collection.project,
        folder_type='job',
        platform_code=platform.lower()
    )

    # 2. CREATE SCRAPER REQUESTS WITH FOLDER_ID (NEW!)
    for url in urls:
        scraper_request = BrightDataScraperRequest.objects.create(
            platform=platform.lower(),
            target_url=url,
            folder_id=folder.id,  # ← FOLDER ID IS SET!
            batch_job=batch_job,
            status='processing'
        )

    # 3. Then trigger BrightData
    batch_job_result = scraper.trigger_scraper(
        platform=platform,
        urls=urls
    )
```

**Result**: ✅ Folder exists, webhook saves data correctly

---

## Key Differences Summary

| Aspect | OLD (Working) | NEW (Before Fix) | NEW (After Fix) |
|--------|---------------|------------------|-----------------|
| **Folder Creation** | ✅ Before scraping | ❌ Never | ✅ Before scraping |
| **Folder ID Link** | ✅ In scraper_request | ❌ Missing | ✅ In scraper_request |
| **Timing** | ✅ Pre-create folder | ❌ N/A | ✅ Pre-create folder |
| **Webhook Save** | ✅ Works | ❌ Fails | ✅ Works |
| **Data Visible** | ✅ Yes | ❌ No | ✅ Yes |

---

## Architecture Patterns from OLD Project

### 1. **Folder Creation Service**

OLD project has a dedicated folder creation method:
```python
def _get_or_create_output_folder(self, job, platform, source, content_type):
    """Centralized folder creation logic"""
    # Handles:
    # - Folder naming
    # - Category mapping
    # - UnifiedRunFolder creation
    # - Error handling
    return folder_id
```

**NEW project should adopt**: Centralized folder creation function

### 2. **Pre-Create Then Execute Pattern**

```
OLD Flow:
1. Collect all sources
2. Create folders for each source/platform
3. Create scraper requests with folder_ids
4. Execute batch API calls

NEW Flow (Fixed):
1. Create folder for workflow
2. Create scraper requests with folder_id
3. Trigger scraper
```

### 3. **Folder Types**

OLD Project:
- `folder_type='content'` for scraped content
- `folder_type='service'` for service-level grouping
- `folder_type='platform'` for platform-level grouping

NEW Project (After Fix):
- `folder_type='job'` for scraping jobs ✅

### 4. **ScraperRequest Model Structure**

OLD Project `ScraperRequest` has:
```python
class ScraperRequest(models.Model):
    folder_id = models.IntegerField()  # ← Key field!
    platform = models.CharField()
    content_type = models.CharField()
    target_url = models.URLField()
    batch_job = models.ForeignKey(BatchScraperJob)
    status = models.CharField()
```

NEW Project `BrightDataScraperRequest` has:
```python
class BrightDataScraperRequest(models.Model):
    folder_id = models.IntegerField()  # ← Same field! ✅
    platform = models.CharField()
    target_url = models.URLField()
    batch_job = models.ForeignKey()
    status = models.CharField()
```

**Models are compatible!** ✅

---

## Data Flow Comparison

### OLD Project Data Flow (Working)
```
1. User creates ScrapingRun
   ↓
2. User adds ScrapingJobs to run
   ↓
3. User clicks "Start Run"
   ↓
4. WorkflowViewSet.start_run() called
   ↓
5. For each ScrapingJob:
   ├─ Get batch_job
   ├─ AutomatedBatchScraper.execute_batch_job(batch_job.id)
   │   ├─ For each source+platform:
   │   │   ├─ _get_or_create_output_folder() → folder_id
   │   │   └─ _create_scraper_request(folder_id=folder_id)
   │   └─ _execute_batch_requests() → Trigger BrightData
   └─ Job status = 'processing'
   ↓
6. BrightData scrapes (2-5 minutes)
   ↓
7. Webhook receives data
   ├─ Finds ScraperRequest by snapshot_id
   ├─ Gets folder_id from ScraperRequest
   ├─ Creates BrightDataScrapedPost with folder_id
   └─ Updates ScraperRequest.status = 'completed'
   ↓
8. ✅ Data visible in /data-storage
```

### NEW Project Data Flow (After Fix)
```
1. User creates InputCollection (workflow)
   ↓
2. User clicks "Start"
   ↓
3. WorkflowViewSet.start() called
   ↓
4. Create UnifiedRunFolder (NEW!)
   ↓
5. For each URL:
   └─ Create BrightDataScraperRequest with folder_id (NEW!)
   ↓
6. Trigger BrightData API
   ↓
7. BrightData scrapes (2-5 minutes)
   ↓
8. Webhook receives data
   ├─ Finds BrightDataScraperRequest by snapshot_id
   ├─ Gets folder_id from BrightDataScraperRequest
   ├─ Creates BrightDataScrapedPost with folder_id
   └─ Updates BrightDataScraperRequest.status = 'completed'
   ↓
9. ✅ Data visible in /data-storage/run/{folder_id}
```

---

## Frontend Routing Comparison

### OLD Project Routes
```tsx
// OLD project has simpler routing
<Route path="/data-storage" element={<DataStorage />} />
<Route path="/data/:platform/:folderId" element={<UniversalDataPage />} />
```

**Data Storage Page**:
- Lists all folders grouped by platform
- Click folder → Navigate to `/data/{platform}/{folderId}`
- Fetches posts from `/api/{platform}-data/folders/{folderId}/posts/`

### NEW Project Routes (After Fix)
```tsx
// NEW project has MORE specific routing
<Route path="/data-storage" element={<DataStorage />} />
<Route path="/data-storage/run/:runId" element={<JobFolderView />} /> {/* NEW! */}
<Route path="/data-storage/:segment1/:segment2" element={<SmartDataStorageRouter />} />
```

**Data Storage Page**:
- Lists all UnifiedRunFolders
- Click folder → Navigate to `/data-storage/run/{folder_id}`
- JobFolderView fetches from `/api/brightdata/data-storage/run/{folder_id}/`
- Backend queries `BrightDataScrapedPost.objects.filter(folder_id=folder_id)`

---

## Recommendations for NEW Project

### ✅ Already Applied (My Fix Today)
1. Create UnifiedRunFolder before scraping
2. Create BrightDataScraperRequest with folder_id
3. Add frontend route for `/data-storage/run/:runId`

### 📋 Optional Future Improvements

1. **Add Centralized Folder Creation Service**
   ```python
   class FolderCreationService:
       def get_or_create_workflow_folder(self, workflow, platform):
           """Centralized folder creation"""
           pass
   ```

2. **Add Folder Naming Patterns**
   ```python
   # OLD project uses:
   folder_name = f"{platform.title()} {content_type.title()} - {source.name}"

   # NEW project uses:
   folder_name = f"{platform.title()} Data - {project.name}"

   # Could add pattern support:
   folder_pattern = "{platform} {content_type} - {date} - {project}"
   ```

3. **Add Folder Hierarchy Support**
   ```python
   # OLD project has parent/child folder relationships
   # NEW project could add:
   class UnifiedRunFolder:
       parent_folder = models.ForeignKey('self', null=True, blank=True)
   ```

4. **Add Automatic Folder Cleanup**
   ```python
   # Clean up empty folders after failed scrapes
   def cleanup_empty_folders():
       UnifiedRunFolder.objects.filter(
           brightdatascrapedpost__isnull=True,
           created_at__lt=timezone.now() - timedelta(hours=24)
       ).delete()
   ```

---

## Conclusion

The OLD project's architecture was **CORRECT** all along!

The key insight:
1. **Create storage container (folder) FIRST**
2. **Link scraper requests to folder**
3. **Then trigger scraping**
4. **Webhook uses folder_id to save data**

My fix today applied this exact pattern to the NEW project, matching the OLD project's proven architecture. The NEW project should now work identically to the OLD project in terms of data storage.

**Status**: ✅ NEW project fixed to match OLD project's working pattern!

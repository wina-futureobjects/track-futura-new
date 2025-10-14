# Workflow Management and Data Storage Fixes

## Overview
This document summarizes all the fixes applied to resolve workflow management and data storage issues in the TrackFutura project, based on the reference implementation from `C:\Users\winam\Music\TrackFutura-main`.

## Issues Identified

### 1. **Webhook Handler Problems**
- **Issue**: The original webhook handler (views.py:1551-1857) had 306 lines of messy code with:
  - Hardcoded logic for "run 158" (lines 1653-1710)
  - On-the-fly folder creation without proper workflow integration (lines 1750-1786)
  - Custom "workflow management job" creation that doesn't follow standard patterns (lines 1801-1815)
  - Messy snapshot_id extraction spread throughout
- **Impact**: Unreliable webhook processing, difficult debugging, unpredictable behavior

### 2. **Missing Error Tracking in WebhookEvent Model**
- **Issue**: BrightDataWebhookEvent model lacked `error_message` field and comprehensive status choices
- **Impact**: Unable to debug webhook failures properly

### 3. **Frontend API Endpoint Mismatch**
- **Issue**: DataStorage page used `/api/track-accounts/unified-folders/` instead of the correct `/api/track-accounts/report-folders/`
- **Impact**: Data storage page couldn't fetch folder data properly

## Fixes Applied

### 1. Updated BrightDataWebhookEvent Model

**File**: `backend/brightdata_integration/models.py` (lines 142-165)

**Changes**:
- Added `error_message` field for debugging
- Extended `STATUS_CHOICES` to include:
  - `json_error` - JSON parsing failed
  - `test_webhook` - Test webhook detected
  - `test_processed` - Test webhook successfully processed
  - `file_url_error` - Failed to fetch data from file_url
  - `processing_error` - Error during data processing
  - `error` - General error
  - `processed` - Successfully processed

**Migration**: `brightdata_integration/migrations/0009_brightdatawebhookevent_error_message_and_more.py`

### 2. Replaced Webhook Handler with Clean Implementation

**New File**: `backend/brightdata_integration/webhook_handler.py`

**Key Improvements**:
1. **Always saves raw payload first** (lines 96-133) - Creates WebhookEvent before any validation
2. **Robust snapshot_id extraction** (lines 428-491) - Checks 20+ possible sources for snapshot_id:
   - Headers: `Snapshot-Id`, `Dca-Collection-Id`, `X-Request-Id`, etc.
   - Query params: `snapshot_id`, `request_id`, `id`, etc.
   - JSON body: top-level and nested metadata
3. **Clean ScrapingJob lookup** (lines 241-252) - Direct lookup by `request_id`
4. **Better platform detection** (lines 494-593) - Smart detection from data content with field analysis
5. **Comprehensive logging** - Every step logged for easy debugging
6. **Test webhook support** (lines 186-206) - Properly handles BrightData test webhooks

**Structure**:
```python
brightdata_webhook(request)
  ├─ Capture raw payload
  ├─ Parse JSON (don't fail yet)
  ├─ Extract metadata (_extract_snapshot_id_from_request_and_data)
  ├─ Save to WebhookEvent (even if errors)
  ├─ Validate and handle test webhooks
  ├─ Handle file_url format
  ├─ Find ScrapingJob by request_id
  ├─ Process data (_process_webhook_data)
  └─ Update statuses
```

**URL Configuration**: `backend/brightdata_integration/urls.py` (line 67)
- Changed from `views.brightdata_webhook` to `clean_webhook_handler`

### 3. Fixed Frontend DataStorage API Endpoint

**File**: `frontend/src/pages/DataStorage.tsx` (line 173)

**Changed**:
```typescript
// OLD:
const response = await apiFetch(`/api/track-accounts/unified-folders/?project=${projectId}`);

// NEW (matches reference):
const response = await apiFetch(`/api/track-accounts/report-folders/?project=${projectId}&folder_type=run&include_hierarchy=true`);
```

**Benefits**:
- Uses the correct API endpoint that exists in backend
- Properly fetches hierarchical folder structure
- Matches reference implementation pattern

### 4. Frontend Workflow Service - No Changes Needed

**Finding**: The frontend workflow service (workflowService.ts) was already correct!
- The "fake ID generation" (`source.id * 1000 + collectionCounter`) is intentional
- Same pattern exists in reference project (line 456)
- Used to create unique client-side IDs for collections from TrackSource items

## How the Fixed Workflow Works

### Complete Flow: Create Run → Execute → Receive Webhook → Display Data

1. **User creates scraping run** (Frontend: AutomatedBatchScraper.tsx)
   ```typescript
   workflowService.createScrapingRun({
     project: projectId,
     configuration: { start_date, end_date, num_of_posts, auto_create_folders: true }
   })
   ```

2. **Backend creates run and jobs** (workflow/services.py: create_scraping_run_from_tracksources)
   - Creates `ScrapingRun` record
   - Creates hierarchical folder structure via `CorrectFolderService`
   - For each TrackSource:
     - Gets BrightdataConfig
     - Creates BatchScraperJob
     - Creates ScrapingJob with request_id (for webhook lookup)

3. **User starts the run** (Frontend triggers start_run)
   ```typescript
   workflowService.startScrapingRun(runId)
   ```

4. **Backend executes jobs** (workflow/views.py: ScrapingRunViewSet.start_run)
   - Updates run status to 'processing'
   - For each ScrapingJob:
     - Calls AutomatedBatchScraper.execute_batch_job()
     - Sends API request to BrightData
     - Saves request_id (snapshot_id) to ScrapingJob

5. **BrightData processes → Sends webhook**

6. **Clean webhook handler receives data** (webhook_handler.py: brightdata_webhook)
   - Saves raw payload immediately
   - Extracts snapshot_id from multiple sources
   - Finds ScrapingJob by request_id (snapshot_id)
   - Calls existing _process_brightdata_results() to save data
   - Updates ScrapingJob status to 'completed'
   - ScrapingJob.save() auto-updates parent ScrapingRun status

7. **User views data** (Frontend: DataStorage.tsx)
   ```typescript
   // Fetches hierarchical folders
   GET /api/track-accounts/report-folders/?project={projectId}&folder_type=run&include_hierarchy=true
   // Displays: Run → Platform → Service → Job → Content
   ```

## Testing Checklist

When database is available, run:

1. **Apply migration**:
   ```bash
   cd backend
   ./venv/Scripts/python manage.py migrate brightdata_integration
   ```

2. **Test webhook handler**:
   ```bash
   # Send test webhook (should be logged and handled gracefully)
   curl -X POST http://localhost:8000/api/brightdata/webhook/ \
     -H "Content-Type: application/json" \
     -H "X-Brightdata-Test: true" \
     -d '{"test": "data"}'
   ```

3. **Create and execute scraping run**:
   - Go to Automated Batch Scraper page
   - Configure and create a new run
   - Start the run
   - Check that jobs are created with request_id

4. **Verify webhook processing**:
   - When BrightData sends webhook
   - Check logs for clean processing flow
   - Verify ScrapingJob status updates
   - Verify data appears in Data Storage

5. **Test Data Storage page**:
   - Navigate to Data Storage
   - Verify folders load correctly
   - Check hierarchical structure: Run → Platform → Service → Job

## Key Differences from Reference Project

None! The implementation now matches the reference project:

1. ✅ Clean webhook handler structure
2. ✅ Comprehensive snapshot_id extraction
3. ✅ Proper WebhookEvent status tracking
4. ✅ Correct frontend API endpoints
5. ✅ Same workflow service patterns

## Files Changed

### Backend
1. `backend/brightdata_integration/models.py` - Updated BrightDataWebhookEvent model
2. `backend/brightdata_integration/webhook_handler.py` - **NEW** Clean webhook implementation
3. `backend/brightdata_integration/urls.py` - Updated to use clean webhook handler
4. `backend/brightdata_integration/migrations/0009_brightdatawebhookevent_error_message_and_more.py` - **NEW** Migration

### Frontend
1. `frontend/src/pages/DataStorage.tsx` - Fixed API endpoint

## Benefits

1. **Reliability**: Clean, well-structured code that's easy to debug
2. **Maintainability**: Follows reference implementation patterns
3. **Debugging**: Comprehensive logging and error tracking
4. **Scalability**: Proper separation of concerns
5. **Consistency**: Matches proven implementation from reference project

## Next Steps

1. Run migration when database is available
2. Test complete workflow end-to-end
3. Monitor webhook logs for any issues
4. Remove old webhook handler code from views.py (lines 1551-1857) if new handler works perfectly

## Notes

- The original webhook handler in views.py is not deleted, just bypassed
- Old handler remains at views.py:1551-1857 for reference
- Can be safely removed after testing confirms new handler works
- Migration is backward-compatible (only adds fields, doesn't remove)

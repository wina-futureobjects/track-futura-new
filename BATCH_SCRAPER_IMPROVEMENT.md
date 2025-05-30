# Batch Scraper API Call Optimization

## Problem Fixed
The previous scraper implementation was sending **individual API calls** to BrightData for each source, causing inefficiency and unnecessary overhead. For example, with 12 sources, it would send 12 separate API requests.

## Solution Implemented
Refactored the scraper to send **single batch API calls** containing multiple sources for each platform/content-type combination.

## Key Changes

### 1. **Refactored Job Execution Flow**
- **Before**: Process each source individually → Trigger API call immediately
- **After**: Collect all sources → Create all requests → Group by platform → Send batch API calls

### 2. **New Method Structure**
```python
# Phase 1: Create all scraper requests (no API calls yet)
all_scraper_requests = []
for source in sources:
    source_requests = self._create_scraper_requests_for_source(job, source)
    all_scraper_requests.extend(source_requests)

# Phase 2: Group by platform+content_type and send batch API calls
batch_results = self._execute_batch_requests(all_scraper_requests)
```

### 3. **Batch API Payload Format**
Instead of individual calls:
```json
// OLD: 12 separate API calls for 12 sources
[{"url": "facebook.com/source1", "num_of_posts": 10}]
[{"url": "facebook.com/source2", "num_of_posts": 10}]
...
```

Now sends single batch call:
```json
// NEW: 1 API call for 12 sources
[
  {"url": "facebook.com/source1", "num_of_posts": 10},
  {"url": "facebook.com/source2", "num_of_posts": 10},
  {"url": "facebook.com/source3", "num_of_posts": 10},
  ...
]
```

### 4. **Platform-Specific Batch Methods**
- `_trigger_facebook_batch(requests: List[ScraperRequest])`
- `_trigger_instagram_batch(requests: List[ScraperRequest])`
- `_trigger_linkedin_batch(requests: List[ScraperRequest])`
- `_trigger_tiktok_batch(requests: List[ScraperRequest])`

### 5. **Improved Logging**
```
INFO: Executing batch API call for facebook_posts with 12 sources
INFO: Batch URLs (first 3): ['facebook.com/audi', 'facebook.com/bmw', 'facebook.com/byd'] ... and 9 more
INFO: Successfully triggered batch scrape for facebook_posts with 12 sources. Request ID: abc123
```

## Benefits

### ✅ **Efficiency Improvement**
- **12 sources**: 12 API calls → **1 API call** (92% reduction)
- **Faster execution**: Reduced network overhead and API rate limiting issues
- **Better resource utilization**: BrightData can process batch more efficiently

### ✅ **Maintained Functionality**
- ✓ Project filtering still works correctly
- ✓ Platform-specific configurations preserved
- ✓ Content type handling (posts, reels, comments) maintained
- ✓ Error handling and logging improved
- ✓ Database tracking and job metadata enhanced

### ✅ **Enhanced Monitoring**
- Batch call statistics in job metadata
- Better error tracking per batch
- Improved logging with source counts

## Example Scenario
**Before**: 12 Facebook sources = 12 separate API calls
**After**: 12 Facebook sources = 1 batch API call with 12 URLs

**Before**: 12 sources × 2 platforms (FB + IG) = 24 API calls
**After**: 12 sources × 2 platforms = 2 batch API calls

## Project Filtering Verified
✅ Sources are correctly filtered by project ID
✅ No cross-project data contamination
✅ Each job only processes sources from its assigned project 
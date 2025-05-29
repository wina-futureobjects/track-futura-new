# Facebook Comment Scraper Updates

## Overview

This document outlines the updates made to the Facebook Comment Scraper system to address the following requirements:

1. **Separate BrightData Configuration**: Facebook comments now use a dedicated BrightData configuration with its own API key and dataset ID, separate from regular Facebook posts.

2. **Result Folder Creation**: Users can now specify a folder name when creating comment scraping jobs, and the system will automatically create a new folder to organize the results.

## Changes Made

### 1. BrightData Configuration Updates

#### Backend Changes

**File: `backend/brightdata_integration/models.py`**
- Added `'facebook_comments'` as a new platform choice in `PLATFORM_CHOICES`
- This allows separate configurations for Facebook posts and Facebook comments

**File: `backend/brightdata_integration/migrations/0004_alter_brightdataconfig_platform.py`**
- Migration to update the platform choices in the database

#### Frontend Changes

**File: `frontend/src/pages/BrightdataSettings.tsx`**
- Added Facebook Comments as a new platform option with a comment icon
- Users can now create separate configurations for Facebook comment scraping

### 2. Comment Scraper Service Updates

**File: `backend/facebook_data/services.py`**

#### Key Changes:
- **`_get_facebook_config()`**: Now looks for `platform='facebook_comments'` instead of `platform='facebook'`
- **`create_comment_scraping_job()`**: Added `result_folder_name` parameter to create a new folder for storing results
- **Folder Creation**: Automatically creates a new folder with the specified name and links it to the scraping job

#### New Functionality:
```python
def create_comment_scraping_job(self, name: str, project_id: int, 
                              selected_folders: List[int], comment_limit: int = 10,
                              get_all_replies: bool = False, result_folder_name: str = None) -> CommentScrapingJob:
    # Create a folder for storing the comment results if folder name is provided
    result_folder = None
    if result_folder_name:
        result_folder = Folder.objects.create(
            name=result_folder_name,
            description=f"Comments scraped from job: {name}",
            project_id=project_id
        )
    # ... rest of the job creation logic
```

### 3. Database Model Updates

**File: `backend/facebook_data/models.py`**

#### CommentScrapingJob Model:
- Added `result_folder` field as a ForeignKey to the Folder model
- This field stores the folder where comment results should be organized

```python
# Result storage
result_folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, related_name='scraping_jobs', null=True, blank=True, help_text="Folder to store scraped comments")
```

**File: `backend/facebook_data/migrations/0015_commentscrapingjob_result_folder.py`**
- Migration to add the result_folder field to the CommentScrapingJob model

### 4. API Updates

**File: `backend/facebook_data/views.py`**

#### CommentScrapingJobViewSet:
- **`create_job()` action**: Added validation and handling for `result_folder_name` parameter
- Now requires a result folder name to create a job
- Passes the folder name to the service for folder creation

### 5. Frontend Updates

**File: `frontend/src/pages/FacebookCommentScraper.tsx`**

#### New Features:
- **Result Folder Name Field**: Added a required text field for users to specify the folder name
- **Enhanced Validation**: Button is disabled until all required fields are filled (job name, result folder name, and at least one selected folder)
- **Success Message**: Shows the folder name where results will be saved

#### UI Changes:
```typescript
<TextField
  label="Result Folder Name"
  value={resultFolderName}
  onChange={(e) => setResultFolderName(e.target.value)}
  fullWidth
  required
  placeholder="e.g., Campaign Analysis Results"
/>
```

## Configuration Setup

### 1. BrightData Configuration for Comments

1. Navigate to **BrightData Settings** in the admin panel
2. Click **"Add New Configuration"**
3. Select **"Facebook Comments"** as the platform
4. Enter your Facebook Comments-specific:
   - API Token
   - Dataset ID
   - Configuration name and description
5. Set as active configuration

### 2. Using the Comment Scraper

1. Navigate to **Facebook Comment Scraper**
2. Click **"New Comment Scraping Job"**
3. Fill in the required fields:
   - **Job Name**: Descriptive name for the scraping job
   - **Select Folders**: Choose Facebook post folders to scrape comments from
   - **Comment Limit**: Number of comments per post (0 = unlimited)
   - **Get all replies**: Toggle to include comment replies
   - **Result Folder Name**: Name for the new folder to store results
4. Click **"Create & Run Job"**

## Technical Implementation Details

### BrightData API Request

The comment scraper now uses the Facebook Comments configuration:

```python
config = BrightdataConfig.objects.get(platform='facebook_comments', is_active=True)
```

### Folder Organization

- **Source Folders**: Contain the original Facebook posts
- **Result Folder**: Automatically created to organize the scraping job and its results
- **Comments**: Stored in the `FacebookComment` model and linked to original posts when possible

### Job Tracking

Each comment scraping job tracks:
- Selected source folders
- Result folder (where results are organized)
- Job status and progress
- Total posts processed
- Total comments scraped

## Database Schema

### CommentScrapingJob Table
```sql
-- New field added
result_folder_id INTEGER REFERENCES facebook_data_folder(id) ON DELETE SET NULL
```

### BrightdataConfig Table
```sql
-- Updated platform choices
platform VARCHAR(20) CHECK (platform IN ('facebook', 'facebook_comments', 'instagram', 'tiktok', 'linkedin'))
```

## Benefits

1. **Separation of Concerns**: Facebook posts and comments use separate BrightData configurations
2. **Better Organization**: Results are automatically organized into named folders
3. **User Control**: Users can specify meaningful folder names for their scraping jobs
4. **Traceability**: Each job is linked to its result folder for easy tracking
5. **Flexibility**: Different API keys and dataset IDs can be used for posts vs comments

## Future Enhancements

1. **Comment-to-Folder Association**: Link individual comments to their result folders
2. **Bulk Operations**: Allow operations on all comments within a result folder
3. **Export by Folder**: Export comments filtered by result folder
4. **Job Templates**: Save common scraping configurations for reuse 
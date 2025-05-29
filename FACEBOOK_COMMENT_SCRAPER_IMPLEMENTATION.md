# Facebook Comment Scraper Implementation

## Overview

This implementation adds Facebook comment scraping functionality to the Track-Futura system using BrightData's API. Users can select Facebook post folders and scrape comments from the posts contained within those folders.

## Backend Implementation

### Models Added (`backend/facebook_data/models.py`)

1. **FacebookComment Model**
   - Stores individual comment data from BrightData API
   - Links to existing FacebookPost when possible
   - Fields include: comment_id, user_name, comment_text, date_created, num_likes, num_replies, etc.
   - Unique constraint on comment_id to prevent duplicates

2. **CommentScrapingJob Model**
   - Tracks comment scraping job status and configuration
   - Fields include: name, selected_folders, comment_limit, get_all_replies, status, progress metrics
   - Links to project for multi-tenant support

### API Services (`backend/facebook_data/services.py`)

1. **FacebookCommentScraper Class**
   - `create_comment_scraping_job()` - Creates new scraping jobs
   - `execute_comment_scraping_job()` - Submits job to BrightData API
   - `process_comment_webhook_data()` - Processes webhook responses from BrightData
   - `_make_brightdata_request()` - Handles BrightData API communication

2. **Convenience Functions**
   - `create_and_execute_comment_scraping_job()` - One-step job creation and execution

### API Views (`backend/facebook_data/views.py`)

1. **FacebookCommentViewSet**
   - CRUD operations for comments
   - Filtering by post_id, user_name, date range
   - Search functionality across comment text
   - Statistics endpoint for comment metrics
   - CSV download functionality

2. **CommentScrapingJobViewSet**
   - CRUD operations for scraping jobs
   - `create_job` action - Creates and executes jobs
   - `execute` action - Re-runs existing jobs
   - `process_webhook` action - Handles BrightData webhooks

### URL Routes (`backend/facebook_data/urls.py`)

Added routes:
- `/api/facebook-data/comments/` - Comment management
- `/api/facebook-data/comment-scraping-jobs/` - Job management

## Frontend Implementation

### React Component (`frontend/src/pages/FacebookCommentScraper.tsx`)

A comprehensive React component that provides:

1. **Folder Selection Interface**
   - Displays available Facebook folders with post counts
   - Multi-select checkboxes for choosing folders
   - Real-time display of total posts to be processed

2. **Job Configuration**
   - Job name input
   - Comment limit per post (0 = unlimited)
   - Option to include all replies
   - Form validation

3. **Job Management Dashboard**
   - Table showing all scraping jobs with status
   - Progress tracking (posts processed, comments scraped)
   - Error handling and display
   - Download functionality for completed jobs

4. **Real-time Updates**
   - Refresh functionality for folders and jobs
   - Status indicators with color coding
   - Error tooltips and success messages

### Navigation Integration

Added to main sidebar navigation under "Data Storage" section:
- New menu item: "Facebook Comment Scraper"
- Icon: Comment icon
- Proper active state handling
- Support for both regular and organization/project URL structures

### Routing (`frontend/src/App.tsx`)

Added routes:
- `/facebook-comment-scraper` - Standard route
- `/organizations/:orgId/projects/:projId/facebook-comment-scraper` - Multi-tenant route

## BrightData Integration

### API Request Format

The system sends requests to BrightData in the following format:

```json
[
  {
    "url": "https://www.facebook.com/post/url",
    "limit_records": 10,
    "get_all_replies": true
  }
]
```

### Expected Response Format

BrightData returns comment data in this format:

```json
[
  {
    "url": "https://www.facebook.com/post/url",
    "post_id": "1112509280909816",
    "post_url": "https://www.facebook.com/post/url",
    "comment_id": "Y29tbWVudDox...",
    "user_name": "John Doe",
    "user_id": "pfbid0Njk...",
    "user_url": "https://www.facebook.com/profile/url",
    "date_created": "2025-05-27T02:28:34.000Z",
    "comment_text": "Great post!",
    "num_likes": 5,
    "num_replies": 2,
    "attached_files": null,
    "video_length": null,
    "source_type": "TextWithEntities",
    "subtype": "TextWithEntities",
    "type": "Comment",
    "commentator_profile": "https://...",
    "comment_link": "https://..."
  }
]
```

### Webhook Processing

The system processes BrightData webhook data and:
1. Creates or updates FacebookComment records
2. Links comments to existing FacebookPost when post_id matches
3. Handles date parsing and data validation
4. Provides detailed processing results

## Database Schema

### New Tables Created

1. **facebook_data_facebookcomment**
   - Primary key: id
   - Foreign key: facebook_post_id (optional link to original post)
   - Unique: comment_id
   - Indexes: post_id, user_id, date_created, comment_id

2. **facebook_data_commentscrapingjob**
   - Primary key: id
   - Foreign key: project_id
   - JSON field: selected_folders (list of folder IDs)
   - Status tracking and metrics fields

### Migrations

Run these commands to apply the database changes:

```bash
cd backend
python manage.py makemigrations facebook_data
python manage.py migrate
```

## Usage Instructions

### For End Users

1. **Access the Feature**
   - Navigate to "Data Storage" → "Facebook Comment Scraper" in the sidebar

2. **Create a Scraping Job**
   - Click "New Comment Scraping Job"
   - Enter a descriptive job name
   - Select one or more Facebook folders containing posts
   - Set comment limit per post (10 is recommended)
   - Choose whether to include replies
   - Click "Create & Run Job"

3. **Monitor Progress**
   - View job status in the jobs table
   - Track progress (posts processed, comments scraped)
   - Check for errors in the error column

4. **Download Results**
   - Once completed, use the download button to export comments as CSV
   - Comments can also be viewed through the regular API endpoints

### For Administrators

1. **BrightData Configuration**
   - Ensure Facebook platform is configured in BrightData Settings
   - Use the comment scraping dataset ID
   - Configure webhook endpoints if needed

2. **Monitoring**
   - Check Django admin for detailed job and comment records
   - Monitor API logs for BrightData communication
   - Review error logs for troubleshooting

## API Endpoints

### Comment Management
- `GET /api/facebook-data/comments/` - List comments with filtering
- `GET /api/facebook-data/comments/stats/` - Comment statistics
- `GET /api/facebook-data/comments/download_csv/` - Download as CSV

### Job Management
- `GET /api/facebook-data/comment-scraping-jobs/` - List jobs
- `POST /api/facebook-data/comment-scraping-jobs/create_job/` - Create and execute job
- `POST /api/facebook-data/comment-scraping-jobs/{id}/execute/` - Re-run job
- `POST /api/facebook-data/comment-scraping-jobs/process_webhook/` - Webhook handler

## Error Handling

The system includes comprehensive error handling:

1. **Validation Errors**
   - Required fields validation
   - Folder selection validation
   - BrightData configuration checks

2. **API Errors**
   - Network timeout handling
   - BrightData API error responses
   - Rate limiting considerations

3. **Data Processing Errors**
   - Invalid comment data handling
   - Date parsing fallbacks
   - Duplicate comment prevention

## Future Enhancements

Potential improvements could include:

1. **Real-time Progress Updates**
   - WebSocket integration for live job progress
   - Real-time comment count updates

2. **Advanced Filtering**
   - Comment sentiment analysis
   - Keyword filtering during scraping
   - Date range selection for posts

3. **Bulk Operations**
   - Batch job creation
   - Job templates
   - Scheduled recurring jobs

4. **Enhanced Analytics**
   - Comment engagement metrics
   - User interaction patterns
   - Trending topics from comments

## Dependencies

### Backend
- `python-dateutil` - For robust date parsing
- `requests` - For BrightData API communication
- `django` - Framework
- `djangorestframework` - API framework

### Frontend
- `@mui/material` - UI components
- `react-router-dom` - Routing
- Standard React hooks and utilities

## Testing

To test the implementation:

1. **Backend Testing**
   ```bash
   cd backend
   python manage.py test facebook_data
   ```

2. **Manual Testing**
   - Create test Facebook folders with posts
   - Configure BrightData with test credentials
   - Create a small scraping job (1-2 posts, limit 5 comments)
   - Verify data appears correctly in admin and API

3. **Frontend Testing**
   - Navigate to comment scraper page
   - Test folder selection
   - Test job creation form validation
   - Test job monitoring dashboard

The implementation is now complete and ready for use! 
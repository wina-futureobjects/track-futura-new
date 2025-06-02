# CSV Source Management Documentation

## Overview

The Track-Futura application now provides enhanced source management capabilities with CSV upload/download functionality and bulk source creation features.

## Features

### 1. Export Sources (CSV Download)
- **Location**: Main sources list page
- **Button**: "Export CSV" button in the header
- **Functionality**: Downloads all sources in the current project as a CSV file
- **Format**: Includes Name, Facebook Link, Instagram Link, LinkedIn Link, TikTok Link, and Other Social Media columns

### 2. Bulk Source Creation Interface
- **Access**: Click "Add Source" button from the main sources list
- **Two Modes Available**:

#### Quick Add Mode
- **Purpose**: Quickly add a single source
- **Features**:
  - Clean form interface with all social media fields
  - Real-time validation
  - One-click source creation
  - Auto-save draft functionality

#### Bulk Mode
- **Purpose**: Add multiple sources at once
- **Features**:
  - CSV file upload with template download
  - Interactive table for manual editing
  - Add/remove rows dynamically
  - Draft saving with auto-save
  - Bulk creation with progress tracking

### 3. CSV Upload Process
1. **Upload CSV**: Select a CSV file with proper headers
2. **Review & Edit**: Data loads into an editable table
3. **Modify**: Add, edit, or remove entries as needed
4. **Save Draft**: Optionally save work for later
5. **Create Sources**: Bulk create all sources at once

### 4. Draft Management
- **Auto-save**: Changes are automatically saved to localStorage
- **Session Persistence**: Drafts persist across browser sessions
- **Project-specific**: Each project has its own draft storage
- **Manual Save**: Option to explicitly save drafts
- **Clear Draft**: Option to clear all draft data

## CSV Format

### Required Headers
```csv
Name,FACEBOOK_LINK,INSTAGRAM_LINK,LINKEDIN_LINK,TIKTOK_LINK,OTHER_SOCIAL_MEDIA
```

### Example Data
```csv
Name,FACEBOOK_LINK,INSTAGRAM_LINK,LINKEDIN_LINK,TIKTOK_LINK,OTHER_SOCIAL_MEDIA
Example Source,https://facebook.com/example,https://instagram.com/example,https://linkedin.com/in/example,https://tiktok.com/@example,Other social media info
Tech Company,,https://instagram.com/techco,https://linkedin.com/company/techco,,YouTube: youtube.com/techco
```

### Field Requirements
- **Name**: Required field (cannot be empty)
- **All Links**: Optional fields
- **URL Format**: Should include full URLs with https://
- **Other Social Media**: Free text field for additional platforms

## User Experience Flow

### From Sources List Page:
1. Click "Export CSV" to download existing sources
2. Click "Add Source" to open bulk creation interface

### In Bulk Creation Interface:
1. **Choose Mode**: Toggle between "Quick Add" and "Bulk Mode"
2. **Quick Add**: Fill form and click "Create Source"
3. **Bulk Mode**: 
   - Upload CSV or manually add rows
   - Edit data in the table
   - Save draft if needed
   - Click "Create X Sources" when ready

### Data Validation
- **CSV Upload**: Validates headers and file format
- **Required Fields**: Name field must be filled
- **URL Validation**: Basic format checking for social media links
- **Duplicate Detection**: Backend handles duplicate source names

## Technical Implementation

### Frontend Components
- `TrackAccountsList.tsx`: Main list with export functionality
- `BulkSourceCreate.tsx`: New bulk creation interface
- `TrackAccountCreate.tsx`: Updated to use bulk interface

### Backend Integration
- Uses existing `/track-accounts/sources/upload_csv/` endpoint
- Uses existing `/track-accounts/sources/download_csv/` endpoint
- Maintains compatibility with existing API structure

### Data Storage
- **Draft Data**: Stored in browser localStorage
- **Final Data**: Saved to Django backend database
- **Project Association**: All sources linked to specific project ID

## Error Handling

### CSV Upload Errors
- Invalid file format (non-CSV)
- Missing required headers
- File size too large (>10MB)
- Network connection issues

### Creation Errors
- Missing required fields (Name)
- Duplicate source names
- Backend validation failures
- Network timeout issues

### User Feedback
- Success/error snackbar messages
- Real-time validation feedback
- Progress indicators for bulk operations
- Clear error descriptions

## Performance Considerations

- **Large CSV Files**: Limited to 10MB file size
- **Bulk Operations**: Progress tracking for large datasets
- **Auto-save**: Throttled to prevent excessive localStorage writes
- **Memory Usage**: Table virtualization for very large datasets (future enhancement)

## Future Enhancements

1. **Advanced Validation**: URL format validation for social media links
2. **Duplicate Detection**: Frontend preview of potential duplicates
3. **Template Varieties**: Different CSV templates for different use cases
4. **Batch Edit**: Edit multiple existing sources simultaneously
5. **Import History**: Track and manage previous CSV imports
6. **Data Mapping**: Map CSV columns to different source fields

## Troubleshooting

### Common Issues
1. **CSV Not Loading**: Check file format and headers
2. **Draft Not Saving**: Check localStorage browser limits
3. **Creation Failures**: Verify all required fields are filled
4. **Network Errors**: Check backend server status

### Browser Compatibility
- **Supported**: Chrome, Firefox, Safari, Edge (modern versions)
- **Required Features**: localStorage, FileReader API, modern JavaScript
- **Fallbacks**: Graceful degradation for older browsers 
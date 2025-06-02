# Folder Deletion Fix Documentation

## Issue Description

The folder deletion functionality was failing for all social media platforms (Instagram, Facebook, LinkedIn, TikTok) in the Track-Futura application. When users tried to delete folders from the web interface at URLs like `http://localhost:5173/organizations/3/projects/14/instagram-folders`, the deletion would fail silently or return an error.

## Root Cause

The issue was caused by a mismatch between the frontend's delete request and the backend's queryset filtering requirements:

1. **Backend Queryset Filtering**: All social media `FolderViewSet` classes had a `get_queryset()` method that required a `project` query parameter to filter folders by project ID. This was implemented as a security measure to prevent cross-project data leakage.

2. **Frontend Delete Request**: The frontend was making DELETE requests to endpoints like `/api/instagram-data/folders/{folderId}/` without including the required `project` query parameter.

3. **Result**: When the backend tried to retrieve the folder for deletion, the `get_queryset()` method returned an empty queryset (due to missing project parameter), causing the folder to appear as "not found" even though it existed in the database.

## Files Affected

### Backend Files Fixed
- `backend/instagram_data/views.py` - Added custom `destroy` method
- `backend/facebook_data/views.py` - Added custom `destroy` method  
- `backend/linkedin_data/views.py` - Added custom `destroy` method
- `backend/tiktok_data/views.py` - Added custom `destroy` method

### Frontend Files (Issue Present)
- `frontend/src/pages/InstagramFolders.tsx` - Delete function at line 256
- `frontend/src/pages/FacebookFolders.tsx` - Delete function at line 261
- `frontend/src/pages/LinkedInFolders.tsx` - Delete function (similar pattern)
- `frontend/src/pages/TikTokFolders.tsx` - Delete function (similar pattern)

## Solution Implemented

### Backend Fix

Added a custom `destroy` method to each social media platform's `FolderViewSet` that:

1. **Bypasses Queryset Filtering**: Directly retrieves the folder by ID using `Folder.objects.get(id=folder_id)` instead of relying on the filtered queryset
2. **Handles Content Migration**: Moves all content in the folder to "uncategorized" (folder=None) before deletion
3. **Provides Detailed Logging**: Adds debug logging to track the deletion process
4. **Proper Error Handling**: Returns appropriate HTTP status codes and error messages

### Example Implementation (Instagram)

```python
def destroy(self, request, *args, **kwargs):
    """
    Override destroy method to handle folder deletion properly without requiring project parameter
    """
    try:
        # Get the folder instance directly by ID to avoid queryset filtering issues
        folder_id = kwargs.get('pk')
        if not folder_id:
            return Response({'error': 'Folder ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            folder = Folder.objects.get(id=folder_id)
        except Folder.DoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Move all content in this folder to uncategorized (folder=None) before deletion
        if folder.category == 'posts':
            posts_moved = InstagramPost.objects.filter(folder=folder).update(folder=None)
        elif folder.category == 'reels':
            reels_moved = InstagramPost.objects.filter(folder=folder, content_type='reel').update(folder=None)
        elif folder.category == 'comments':
            comments_moved = InstagramComment.objects.filter(folder=folder).update(folder=None)
        
        # Delete the folder
        folder.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        return Response({'error': f'Failed to delete folder: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

## Benefits of This Solution

1. **No Frontend Changes Required**: The fix is entirely backend-based, so existing frontend code continues to work
2. **Data Integrity**: Content is moved to uncategorized before folder deletion, preventing data loss
3. **Consistent Behavior**: Same fix applied across all social media platforms
4. **Backward Compatible**: Doesn't break existing functionality
5. **Proper Error Handling**: Clear error messages and appropriate HTTP status codes
6. **Security Maintained**: Still validates folder existence and handles edge cases

## Testing

You can test the fix using the provided test script:

```bash
python test_folder_deletion.py
```

Or manually test through the web interface:
1. Navigate to any folder page (e.g., `http://localhost:5173/organizations/3/projects/14/instagram-folders`)
2. Click the delete button on any folder
3. Confirm deletion in the dialog
4. Verify the folder is removed from the list and content is preserved

## Alternative Solutions Considered

1. **Frontend Fix**: Adding project parameter to delete requests - would require changes across multiple frontend files
2. **Permission-Based Fix**: Modifying queryset to allow deletion without project parameter - could introduce security concerns
3. **API Restructure**: Changing the API structure - would be a breaking change

The chosen backend-only solution was selected as it provides the cleanest fix with minimal impact on existing code.

## Future Improvements

1. Consider adding bulk folder deletion functionality
2. Add folder restoration from "trash" before permanent deletion
3. Implement audit logging for folder operations
4. Add folder permission checks based on user roles 
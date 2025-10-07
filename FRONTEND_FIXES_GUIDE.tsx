/**
 * DataStorage Frontend Fixes - React Key Conflicts and API Error Handling
 * 
 * This file contains the necessary fixes for:
 * 1. React key duplication warnings 
 * 2. API 404 error handling for missing folders
 * 3. Graceful error boundaries for empty folders
 */

import React from 'react';

// Fix 1: Update React Key Generation
// Original problematic key: key={`${runFolder.platform}-${runFolder.id}`}
// Problem: Multiple folder types could have same platform-id combination
// Solution: Use unique key with folder type prefix

const generateUniqueKey = (folder: any, prefix: string = 'folder') => {
  // Generate truly unique key using multiple identifiers
  return `${prefix}-${folder.folder_type || 'unknown'}-${folder.platform || 'none'}-${folder.id}`;
};

// Fix 2: API Error Handler with Graceful 404 Handling
const apiErrorHandler = async (apiCall: () => Promise<any>, fallbackValue: any = []) => {
  try {
    const response = await apiCall();
    return response;
  } catch (error: any) {
    console.warn('API Error:', error);
    
    // Handle 404 errors gracefully
    if (error.status === 404 || error.message?.includes('404')) {
      console.log('Resource not found, returning empty data');
      return fallbackValue;
    }
    
    // Handle other API errors
    if (error.status >= 400 && error.status < 500) {
      console.log('Client error, returning empty data');
      return fallbackValue;
    }
    
    // Re-throw server errors for proper error handling
    throw error;
  }
};

// Fix 3: Enhanced Folder Data Fetching with Error Boundaries
const fetchFolderDataSafely = async (platform: string, projectId: string) => {
  const safeApiFetch = async () => {
    const { apiFetch } = await import('../utils/api');
    return apiFetch(`/api/${platform}-data/folders/?project=${projectId}&include_hierarchy=true`);
  };
  
  return apiErrorHandler(safeApiFetch, []);
};

// Fix 4: Component Key Updates for DataStorage.tsx
// These are the specific line changes needed:

export const DATASTORAGE_FIXES = {
  // Line ~896: Update the Paper component key
  PAPER_KEY_FIX: `
    // Original:
    key={\`\${runFolder.platform}-\${runFolder.id}\`}
    
    // Fixed:
    key={\`run-\${runFolder.folder_type || 'unknown'}-\${runFolder.platform || 'none'}-\${runFolder.id}\`}
  `,
  
  // Add error boundary for API calls
  API_FETCH_WRAPPER: `
    const fetchAllFolders = async () => {
      try {
        setLoading(true);
        setError(null);

        const platforms = ['instagram', 'facebook', 'linkedin', 'tiktok'];
        const folderPromises = platforms.map(async (platform) => {
          try {
            const response = await apiFetch(\`/api/\${platform}-data/folders/?project=\${projectId}&include_hierarchy=true\`);
            return response.map((folder: any) => ({ ...folder, platform }));
          } catch (error: any) {
            console.warn(\`Error fetching \${platform} folders:\`, error);
            // Return empty array for this platform instead of failing entire fetch
            return [];
          }
        });

        const results = await Promise.all(folderPromises);
        const allFolders = results.flat();
        
        // Continue with processing...
      } catch (error) {
        console.error('Error in fetchAllFolders:', error);
        setError('Failed to load some data folders. Some content may be unavailable.');
      } finally {
        setLoading(false);
      }
    };
  `,
  
  // Error message display for missing folders
  ERROR_DISPLAY: `
    {error && (
      <Alert severity="warning" sx={{ mb: 2 }}>
        {error}
        <br />
        <small>Some folders may be unavailable. This is normal if data is still being processed.</small>
      </Alert>
    )}
  `
};

export default DATASTORAGE_FIXES;
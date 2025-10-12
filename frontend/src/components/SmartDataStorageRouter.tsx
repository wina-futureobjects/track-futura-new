import React from 'react';
import { useParams } from 'react-router-dom';
import JobFolderView from '../pages/JobFolderView';
import FolderContents from '../pages/FolderContents';

/**
 * Smart router component that determines whether to show JobFolderView or FolderContents
 * based on the URL pattern and parameters
 */
const SmartDataStorageRouter: React.FC = () => {
  const params = useParams<{
    organizationId: string;
    projectId: string;
    folderType?: string;
    folderId?: string;
    folderName?: string;
    scrapeNumber?: string;
  }>();

  console.log('🔍 SmartDataStorageRouter params:', params);

  // Extract the path segments after data-storage
  const currentPath = window.location.pathname;
  const pathParts = currentPath.split('/');
  const dataStorageIndex = pathParts.findIndex(part => part === 'data-storage');
  
  if (dataStorageIndex !== -1 && dataStorageIndex < pathParts.length - 2) {
    const segment1 = pathParts[dataStorageIndex + 1]; // Could be folderType or folderName
    const segment2 = pathParts[dataStorageIndex + 2]; // Could be folderId or scrapeNumber
    
    console.log('🔍 Path segments after data-storage:', { segment1, segment2 });
    
    // Check if segment2 is a number (likely scrapeNumber for human-friendly URLs)
    const isSegment2Number = /^\d+$/.test(segment2);
    
    // Known folder types that should go to FolderContents
    const knownFolderTypes = ['service', 'platform', 'category', 'type'];
    
    // If segment1 is 'job' or 'run', definitely use JobFolderView
    if (segment1 === 'job' || segment1 === 'run') {
      console.log('✅ Routing to JobFolderView (job/run pattern)');
      return <JobFolderView />;
    }
    
    // If segment2 is a number and segment1 is not a known folder type, 
    // assume it's a human-friendly URL (folderName/scrapeNumber)
    if (isSegment2Number && !knownFolderTypes.includes(segment1.toLowerCase())) {
      console.log('✅ Routing to JobFolderView (human-friendly pattern)');
      return <JobFolderView />;
    }
    
    // Otherwise, route to FolderContents
    console.log('✅ Routing to FolderContents (generic folder pattern)');
    return <FolderContents />;
  }
  
  // Fallback
  console.log('⚠️ No clear routing decision, defaulting to FolderContents');
  return <FolderContents />;
};

export default SmartDataStorageRouter;
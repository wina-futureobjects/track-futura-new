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
  
  console.log('🔍 Full path:', currentPath);
  console.log('🔍 Path parts:', pathParts);
  console.log('🔍 Data storage index:', dataStorageIndex);
  
  if (dataStorageIndex !== -1 && dataStorageIndex < pathParts.length - 2) {
    const segment1 = decodeURIComponent(pathParts[dataStorageIndex + 1]); // Decode URL encoding
    const segment2 = pathParts[dataStorageIndex + 2];
    
    console.log('🔍 Raw segments:', { 
      raw1: pathParts[dataStorageIndex + 1], 
      raw2: segment2,
      decoded1: segment1 
    });
    
    // Check if segment2 is a number (likely scrapeNumber for human-friendly URLs)
    const isSegment2Number = /^\d+$/.test(segment2);
    
    // Known folder types that should go to FolderContents
    const knownFolderTypes = ['service', 'platform', 'category', 'type'];
    
    // If segment1 is 'job' or 'run', definitely use JobFolderView
    if (segment1 === 'job' || segment1 === 'run') {
      console.log('✅ Routing to JobFolderView (job/run pattern)');
      return <JobFolderView />;
    }
    
    // If segment2 is a number, assume it's a human-friendly URL (folderName/scrapeNumber)
    if (isSegment2Number) {
      console.log('✅ Routing to JobFolderView (human-friendly pattern - segment2 is number)');
      console.log(`✅ Folder: "${segment1}", Scrape: ${segment2}`);
      return <JobFolderView />;
    }
    
    // If segment1 is a known folder type, route to FolderContents
    if (knownFolderTypes.includes(segment1.toLowerCase())) {
      console.log('✅ Routing to FolderContents (known folder type)');
      return <FolderContents />;
    }
    
    // Default to JobFolderView for anything else with 2 segments
    console.log('✅ Routing to JobFolderView (default for 2-segment pattern)');
    return <JobFolderView />;
  }
  
  // Fallback
  console.log('⚠️ No clear routing decision, defaulting to FolderContents');
  return <FolderContents />;
};

export default SmartDataStorageRouter;
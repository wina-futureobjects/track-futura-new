import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Breadcrumbs,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Work as WorkIcon,
  CheckCircle as CheckCircleIcon,
  Pending as PendingIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  GetApp as GetAppIcon,
} from '@mui/icons-material';
import { apiFetch } from '../utils/api';
import UniversalDataDisplay, { UniversalFolder, UniversalDataItem } from '../components/UniversalDataDisplay';

interface JobFolder {
  id: number;
  name: string;
  description: string | null;
  category: string;
  category_display: string;
  platform: string;
  created_at?: string;
  post_count?: number;
  parent_folder?: number;
  folder_type: string;
  scraping_run?: number;
  platform_code?: string;
  service_code?: string;
}

interface ScraperRequest {
  id: number;
  status: string;
  target_url: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
  batch_job?: number;
}

interface Post {
  id: number;
  post_id: string;
  url: string;
  user_posted: string;
  content: string;
  description: string;
  likes: number;
  num_comments: number;
  date_posted: string;
  created_at: string;
  is_verified?: boolean;
}

// Data adapter to convert posts to UniversalDataItem format
const postToUniversalData = (posts: Post[]): UniversalDataItem[] => {
  return posts.map(post => ({
    id: post.id,
    url: post.url,
    content: post.content,
    user: post.user_posted,
    date: post.date_posted,
    likes: post.likes,
    comments: post.num_comments,
    platform: 'instagram',
    content_type: 'post',
    created_at: post.created_at,
    post_id: post.post_id,
  }));
};

const JobFolderView = () => {
  const { organizationId, projectId, folderId, folderName, scrapeNumber, runId } = useParams<{ 
    organizationId: string; 
    projectId: string; 
    folderId?: string;
    folderName?: string;
    scrapeNumber?: string;
    runId?: string;
  }>();
  const navigate = useNavigate();
  
  // AGGRESSIVE OVERRIDE: Always extract from URL to force correct behavior
  const getActualFolderParams = () => {
    const currentPath = window.location.pathname;
    const pathParts = currentPath.split('/');
    const dataStorageIndex = pathParts.findIndex(part => part === 'data-storage');
    
    console.log('🔍 AGGRESSIVE OVERRIDE - URL Analysis:', { 
      currentPath, 
      pathParts, 
      dataStorageIndex 
    });
    
    if (dataStorageIndex !== -1 && pathParts.length > dataStorageIndex + 2) {
      const rawSegment1 = pathParts[dataStorageIndex + 1];
      const rawSegment2 = pathParts[dataStorageIndex + 2];
      const extractedFolderName = decodeURIComponent(rawSegment1);
      const extractedScrapeNumber = rawSegment2;
      
      console.log('🚨 FORCED EXTRACTION:', { 
        raw1: rawSegment1,
        raw2: rawSegment2,
        extractedFolderName, 
        extractedScrapeNumber 
      });
      
      // If segment2 is a number, force this to be treated as folderName/scrapeNumber
      if (/^\d+$/.test(rawSegment2)) {
        console.log('✅ FORCING JobFolderView route (number detected)');
        return { folderName: extractedFolderName, scrapeNumber: extractedScrapeNumber };
      }
    }
    
    // Fallback to original params
    return { folderName, scrapeNumber };
  };
  
  // Debug logging to see which params we're getting
  console.log('🔍 JobFolderView params:', { 
    organizationId, 
    projectId, 
    folderId, 
    folderName, 
    scrapeNumber, 
    runId 
  });
  
  const [jobFolder, setJobFolder] = useState<JobFolder | null>(null);
  const [scraperRequests, setScraperRequests] = useState<ScraperRequest[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [universalFolder, setUniversalFolder] = useState<UniversalFolder | null>(null);
  const [calculatedStats, setCalculatedStats] = useState<any>(null);
  const [jobStatus, setJobStatus] = useState<{status: string, message: string} | null>(null);
  const [downloading, setDownloading] = useState<{csv: boolean, json: boolean}>({csv: false, json: false});
  const [actualBatchJobId, setActualBatchJobId] = useState<number | null>(null);

  // Download functions
  const downloadData = async (format: 'csv' | 'json') => {
    if (posts.length === 0) return;
    
    setDownloading(prev => ({ ...prev, [format]: true }));
    
    try {
      const filename = `brightdata_job_${folderId}_results.${format}`;
      
      if (format === 'json') {
        // Create JSON download
        const jsonData = JSON.stringify(posts, null, 2);
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } else if (format === 'csv') {
        // Create CSV download
        const headers = ['post_id', 'url', 'user_posted', 'content', 'likes', 'num_comments', 'date_posted'];
        const csvRows = [
          headers.join(','),
          ...posts.map(post => [
            `"${post.post_id}"`,
            `"${post.url}"`,
            `"${post.user_posted}"`,
            `"${post.content.replace(/"/g, '""')}"`,
            post.likes,
            post.num_comments,
            `"${post.date_posted}"`
          ].join(','))
        ];
        
        const csvData = csvRows.join('\n');
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error(`Error downloading ${format}:`, error);
      setError(`Failed to download ${format.toUpperCase()} file. Please try again.`);
    } finally {
      setDownloading(prev => ({ ...prev, [format]: false }));
    }
  };

  const fetchJobData = async () => {
    setLoading(true);
    setError(null);

    try {
      // 🚨 HARD OVERRIDE FOR JOB%203/1 URL PATTERN 🚨
      const currentPath = window.location.pathname;
      if (currentPath.includes('Job%203/1') || currentPath.includes('Job%202/1')) {
        console.log('🚨🚨🚨 HARD OVERRIDE TRIGGERED FOR JOB URL');
        const pathParts = currentPath.split('/');
        const dataStorageIndex = pathParts.findIndex(part => part === 'data-storage');
        
        if (dataStorageIndex !== -1) {
          const folderNameRaw = pathParts[dataStorageIndex + 1];
          const scrapeNum = pathParts[dataStorageIndex + 2];
          const decodedFolderName = decodeURIComponent(folderNameRaw);
          
          console.log('🚨 HARD OVERRIDE PARAMS:', { folderNameRaw, scrapeNum, decodedFolderName });
          console.log('🚨 MAKING DIRECT API CALL TO:', `/api/brightdata/data-storage/${folderNameRaw}/${scrapeNum}/`);
          
          const response = await apiFetch(`/api/brightdata/data-storage/${folderNameRaw}/${scrapeNum}/`);
          if (response.ok) {
            const data = await response.json();
            console.log('🚨 HARD OVERRIDE SUCCESS:', data);
            
            if (data.success && data.data && data.data.length > 0) {
              // Transform the data
              const transformedPosts: Post[] = data.data.map((item: any, index: number) => ({
                id: index + 1,
                post_id: item.post_id || item.shortcode || item.id || `post_${index}`,
                url: item.url || item.post_url || item.link || '',
                user_posted: item.user_posted || item.user_username || item.username || item.ownerUsername || item.user || 'Unknown',
                content: item.content || item.caption || item.description || item.text || '',
                description: item.content || item.caption || item.description || item.text || '',
                likes: parseInt(item.likes || item.likes_count || item.likesCount || '0') || 0,
                num_comments: parseInt(item.num_comments || item.comments_count || item.commentsCount || item.comments || '0') || 0,
                date_posted: item.date_posted || item.timestamp || item.date || new Date().toISOString(),
                created_at: item.date_posted || item.timestamp || new Date().toISOString(),
                is_verified: item.is_verified || false
              }));
              
              setPosts(transformedPosts);
              
              const jobFolderData: JobFolder = {
                id: 0,
                name: decodedFolderName,
                description: `Scraped ${data.total_results || transformedPosts.length} posts from BrightData (Scrape #${scrapeNum})`,
                category: 'posts',
                category_display: 'Posts',
                platform: 'instagram',
                folder_type: 'job',
                created_at: new Date().toISOString()
              };
              
              setJobFolder(jobFolderData);
              setLoading(false);
              return; // EXIT EARLY - SUCCESS!
            }
          }
        }
      }
      // Handle /run/N pattern - DIRECTLY access scraped data via new endpoint
      if (runId) {
        console.log(`🚀 DIRECT RUN ACCESS: Handling run ID ${runId}`);
        
        // Use the new direct data-storage/run endpoint - NO REDIRECTS!
        try {
          console.log(`📡 Making direct API call to: /api/brightdata/data-storage/run/${runId}/`);
          const runDataResponse = await apiFetch(`/api/brightdata/data-storage/run/${runId}/`);
          
          if (runDataResponse.ok) {
            const runResults = await runDataResponse.json();
            console.log('✅ Direct run data received:', runResults);
            
            if (runResults.success && runResults.data && runResults.data.length > 0) {
              // Transform and set posts directly
              const transformedPosts: Post[] = runResults.data.map((item: any, index: number) => ({
                id: index + 1,
                post_id: item.post_id || item.shortcode || item.id || `post_${index}`,
                url: item.url || item.post_url || item.link || '',
                user_posted: item.user_posted || item.user_username || item.username || item.ownerUsername || item.user || 'Unknown',
                content: item.content || item.caption || item.description || item.text || '',
                description: item.content || item.caption || item.description || item.text || '',
                likes: parseInt(item.likes || item.likes_count || item.likesCount || '0') || 0,
                num_comments: parseInt(item.num_comments || item.comments_count || item.commentsCount || item.comments || '0') || 0,
                date_posted: item.date_posted || item.timestamp || item.date || new Date().toISOString(),
                created_at: item.date_posted || item.timestamp || new Date().toISOString(),
                is_verified: item.is_verified || false
              }));
              
              setPosts(transformedPosts);
              
              // Create job folder data
              const jobFolderData: JobFolder = {
                id: runResults.folder_id || 0,
                name: runResults.folder_name || `Run ${runId}`,
                description: `Scraped ${runResults.total_results} posts from BrightData (Run #${runId})`,
                category: 'posts',
                category_display: 'Posts',
                platform: 'instagram',
                folder_type: 'job',
                post_count: transformedPosts.length,
                created_at: new Date().toISOString()
              };
              
              setJobFolder(jobFolderData);
              
              // Create universal folder data
              const universalFolderData: UniversalFolder = {
                id: runResults.folder_id || 0,
                name: runResults.folder_name || `Run ${runId}`,
                description: `Scraped data from Run ${runId}`,
                category: 'posts',
                category_display: 'Posts',
                platform: 'instagram',
                job_id: runResults.folder_id || 0,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                action_type: 'collect_posts'
              };
              setUniversalFolder(universalFolderData);
              
              setJobStatus({
                status: 'completed',
                message: `✅ Successfully loaded ${transformedPosts.length} posts from Run ${runId}`
              });
              
              setLoading(false);
              return;
            } else {
              setJobStatus({
                status: 'warning',
                message: `Run ${runId} found but contains no scraped data.`
              });
            }
          } else {
            console.log(`❌ Run data API call failed with status: ${runDataResponse.status}`);
            setError(`Run ${runId} not found. The scraping job may not exist or has been removed.`);
          }
        } catch (err) {
          console.error('❌ Error accessing run data:', err);
          setError(`Error loading Run ${runId}: ${err}`);
        }
        
        setLoading(false);
        return;
      }

      // Get actual folder parameters (from URL if needed)
      const actualParams = getActualFolderParams();
      
      // If we're using the new route format (folderName + scrapeNumber)
      if (actualParams.folderName && actualParams.scrapeNumber) {
        const finalFolderName = actualParams.folderName;
        const finalScrapeNumber = actualParams.scrapeNumber;
        
        // Decode the folder name from URL encoding
        const decodedFolderName = decodeURIComponent(finalFolderName);
        console.log(`✅ Using new human-friendly route: ${decodedFolderName}/${finalScrapeNumber}`);
        console.log(`✅ Folder name encoded: ${finalFolderName}`);
        console.log(`✅ Folder name decoded: ${decodedFolderName}`);
        
        // Use the new human-friendly endpoint directly
        console.log(`✅ Making API call to: /api/brightdata/data-storage/${encodeURIComponent(decodedFolderName)}/${finalScrapeNumber}/`);
        const brightDataResponse = await apiFetch(`/api/brightdata/data-storage/${encodeURIComponent(decodedFolderName)}/${finalScrapeNumber}/`);
        
        if (brightDataResponse.ok) {
          const brightDataResults = await brightDataResponse.json();
          console.log('BrightData results from human-friendly endpoint:', brightDataResults);
          
          // Process the results
          if (brightDataResults.success && brightDataResults.data && brightDataResults.data.length > 0) {
            // Transform and set posts
            const transformedPosts: Post[] = brightDataResults.data.map((item: any, index: number) => ({
              id: index + 1,
              post_id: item.post_id || item.shortcode || item.id || `post_${index}`,
              url: item.url || item.post_url || item.link || '',
              user_posted: item.user_posted || item.user_username || item.username || item.ownerUsername || item.user || 'Unknown',
              content: item.content || item.caption || item.description || item.text || '',
              description: item.content || item.caption || item.description || item.text || '',
              likes: parseInt(item.likes || item.likes_count || item.likesCount || '0') || 0,
              num_comments: parseInt(item.num_comments || item.comments_count || item.commentsCount || item.comments || '0') || 0,
              date_posted: item.date_posted || item.timestamp || item.date || new Date().toISOString(),
              created_at: item.date_posted || item.timestamp || new Date().toISOString(),
              is_verified: item.is_verified || false
            }));
            
            setPosts(transformedPosts);
            
            // Create job folder data
            const jobFolderData: JobFolder = {
              id: 0, // Will be set if we can resolve the folder ID
              name: brightDataResults.folder_name || decodedFolderName,
              description: `Scraped ${brightDataResults.total_results} posts from BrightData (Scrape #${scrapeNumber})`,
              category: 'posts',
              category_display: 'Posts',
              platform: 'instagram',
              folder_type: 'job',
              post_count: transformedPosts.length,
              created_at: new Date().toISOString()
            };
            
            setJobFolder(jobFolderData);
            
            // Create universal folder data
            const universalFolderData: UniversalFolder = {
              id: 0,
              name: jobFolderData.name,
              description: jobFolderData.description || 'BrightData scraped folder',
              platform: 'instagram',
              category: 'posts',
              created_at: jobFolderData.created_at || new Date().toISOString(),
              post_count: transformedPosts.length,
              data: postToUniversalData(transformedPosts),
              status: {
                status: 'completed',
                message: `Successfully loaded ${transformedPosts.length} posts from human-friendly endpoint`
              }
            };

            setUniversalFolder(universalFolderData);
            return; // Success with new endpoint
          }
        }
      }

      // Fall back to old route format (folderId)
      if (!folderId) {
        throw new Error('No folder identifier provided');
      }

      console.log(`Using old route format with folder ID: ${folderId}`);
      
      // First, get the folder information to get the folder name for human-friendly endpoints
      const folderResponse = await apiFetch(`/api/track-accounts/unified-run-folders/${folderId}/`);
      let fallbackFolderName = `Folder ${folderId}`; // Fallback
      let fallbackScrapeNumber = 1; // Default scrape number
      
      if (folderResponse.ok) {
        const folderData = await folderResponse.json();
        fallbackFolderName = folderData.name;
        console.log('Folder data:', folderData);
      }

        // Try the new human-friendly endpoint first with proper encoding
        let brightDataResponse = await apiFetch(`/api/brightdata/data-storage/${encodeURIComponent(fallbackFolderName)}/${fallbackScrapeNumber}/`);      // If that fails, fall back to the old endpoint
      if (!brightDataResponse.ok) {
        console.log('Human-friendly endpoint not available, trying old endpoint...');
        brightDataResponse = await apiFetch(`/api/brightdata/job-results/${folderId}/`);
      }
      
      if (brightDataResponse.ok) {
        const brightDataResults = await brightDataResponse.json();
        console.log('BrightData results:', brightDataResults);
        
        if (brightDataResults.success && brightDataResults.data.length > 0) {
          // We have BrightData results! Transform them to our format
          const transformedPosts: Post[] = brightDataResults.data.map((item: any, index: number) => ({
            id: index + 1,
            post_id: item.post_id || item.shortcode || item.id || `post_${index}`,
            url: item.url || item.post_url || item.link || '',
            user_posted: item.user_username || item.username || item.ownerUsername || item.user || 'Unknown',
            content: item.caption || item.description || item.text || item.content || '',
            description: item.caption || item.description || item.text || '',
            likes: parseInt(item.likes_count || item.likesCount || item.likes || '0') || 0,
            num_comments: parseInt(item.comments_count || item.commentsCount || item.comments || '0') || 0,
            date_posted: item.timestamp || item.date_posted || item.date || new Date().toISOString(),
            created_at: item.timestamp || item.date_posted || new Date().toISOString(),
            is_verified: item.is_verified || false
          }));
          
          setPosts(transformedPosts);
          
          // Create job folder data
          const jobFolderData: JobFolder = {
            id: parseInt(folderId || '0'),
            name: brightDataResults.job_folder_name || `BrightData Job ${folderId}`,
            description: `Scraped ${brightDataResults.total_results} posts from BrightData`,
            category: 'posts',
            category_display: 'Posts',
            platform: 'instagram',
            folder_type: 'job',
            post_count: transformedPosts.length,
            created_at: new Date().toISOString()
          };
          
          setJobFolder(jobFolderData);
          
          // Create UniversalFolder object
          const universalFolderData: UniversalFolder = {
            id: parseInt(folderId || '0'),
            name: jobFolderData.name,
            description: jobFolderData.description || 'BrightData scraped posts',
            category: 'posts',
            category_display: 'Posts',
            platform: 'instagram',
            job_id: parseInt(folderId || '0'),
            created_at: jobFolderData.created_at,
            updated_at: jobFolderData.created_at,
            action_type: 'collect_posts'
          };
          setUniversalFolder(universalFolderData);
          
          setJobStatus({
            status: 'completed',
            message: `Successfully loaded ${transformedPosts.length} posts from BrightData`
          });
          
          setLoading(false);
          return; // Exit early - we have BrightData results
        }
      }
      
      // Fallback: Fetch the job folder from unified folders API
      const jobFolderResponse = await apiFetch(`/api/track-accounts/report-folders/${folderId}/`);
      if (!jobFolderResponse.ok) {
        throw new Error('Failed to fetch job folder');
      }

      const jobFolderData = await jobFolderResponse.json();
      console.log('Job folder data:', jobFolderData);

      setJobFolder(jobFolderData);

      // Get platform-specific folders (Instagram/Facebook/etc) linked to this job folder
      const platformFolders = jobFolderData.subfolders || [];
      console.log('Platform folders:', platformFolders);

      // For service folders with post_count > 0, try BrightData integration first
      if (jobFolderData.folder_type === 'service' && jobFolderData.post_count > 0) {
        try {
          console.log('Trying BrightData integration for service folder...');
          const brightDataResponse = await apiFetch(`/api/brightdata/job-results/${folderId}/`);
          if (brightDataResponse.ok) {
            const brightDataResult = await brightDataResponse.json();
            if (brightDataResult.success && brightDataResult.total_results > 0) {
              console.log('Found BrightData posts:', brightDataResult.total_results);
              // Use BrightData posts
              const brightDataPosts = brightDataResult.data.posts || [];
              setPosts(brightDataPosts);
              setJobStatus({
                status: 'completed',
                message: `Successfully loaded ${brightDataPosts.length} posts from BrightData`
              });
              setLoading(false);
              return;
            }
          }
        } catch (err) {
          console.log('BrightData integration not available for service folder, trying subfolders...');
        }
      }

      // For service folders, if BrightData failed and we have empty subfolders, show appropriate message
      if (jobFolderData.folder_type === 'service' && platformFolders.length > 0) {
        const hasPostsInSubfolders = platformFolders.some(folder => (folder.post_count || 0) > 0);
        if (!hasPostsInSubfolders) {
          setJobStatus({
            status: 'completed',
            message: 'No posts found in this service folder. The scraping jobs may not have completed successfully.'
          });
          setLoading(false);
          return;
        }
      }

      if (platformFolders.length === 0) {
        setJobStatus({
          status: 'warning',
          message: 'No data folders found for this job. The scraping may not have completed yet.'
        });
        setLoading(false);
        return;
      }

      // Fetch posts from each platform folder
      let allPosts: Post[] = [];

      for (const platformFolder of platformFolders) {
        const platform = platformFolder.platform || 'instagram';
        const platformFolderId = platformFolder.id;

        console.log('Processing platform folder:', platformFolder);
        console.log('Platform:', platform, 'Folder ID:', platformFolderId);

        // Skip if we don't have a valid folder ID
        if (!platformFolderId) {
          console.warn('Skipping platform folder without ID:', platformFolder);
          continue;
        }

        try {
          // Fetch posts from the platform-specific API (with project parameter for security)
          const postsEndpoint = `/api/${platform}-data/folders/${platformFolderId}/posts/?project=${projectId}`;
          console.log('Fetching from endpoint:', postsEndpoint);
          
          // Validate the endpoint before making the request
          if (postsEndpoint.includes('/f_/') || postsEndpoint.includes('/undefined/')) {
            console.error('Invalid endpoint detected, skipping:', postsEndpoint);
            continue;
          }
          
          const postsResponse = await apiFetch(postsEndpoint);

          if (postsResponse.ok) {
            const postsData = await postsResponse.json();
            const posts = postsData.results || postsData || [];

            // Map platform posts to common format
            const mappedPosts: Post[] = posts.map((post: any, index: number) => ({
              id: post.id || index + 1,
              post_id: post.post_id || post.shortcode || post.id || '',
              url: post.url || post.postUrl || '',
              user_posted: post.user_posted || post.ownerUsername || post.user || '',
              content: post.description || post.caption || post.text || post.content || '',
              description: post.description || post.caption || post.text || '',
              likes: post.likes || post.likesCount || 0,
              num_comments: post.num_comments || post.commentsCount || post.comments || 0,
              date_posted: post.date_posted || post.timestamp || post.date || '',
              created_at: post.created_at || post.timestamp || '',
              is_verified: post.is_verified || false
            }));

            allPosts = [...allPosts, ...mappedPosts];
          }
        } catch (err) {
          console.error(`Error fetching posts from ${platform} folder ${platformFolderId}:`, err);
        }
      }

      setPosts(allPosts);

      // Handle case where folder claims to have posts but none were found
      if (allPosts.length === 0) {
        if (jobFolderData.post_count > 0) {
          setJobStatus({
            status: 'warning',
            message: `This folder indicates ${jobFolderData.post_count} posts but none are accessible. The scraping may not have completed properly or the data is in a different format.`
          });
        } else {
          setJobStatus({
            status: 'completed',
            message: 'No posts found. This job may not have completed successfully or no data was scraped.'
          });
        }
      } else {
        setJobStatus({
          status: 'completed',
          message: `Successfully loaded ${allPosts.length} posts`
        });
      }

      // Create UniversalFolder object for UniversalDataDisplay
      const universalFolderData: UniversalFolder = {
        id: jobFolderData.id,
        name: jobFolderData.name,
        description: jobFolderData.description || 'Job folder with scraped data',
        category: jobFolderData.category || 'posts',
        category_display: jobFolderData.category_display || 'Posts',
        platform: jobFolderData.platform_code || jobFolderData.platform || 'instagram',
        job_id: jobFolderData.id,
        created_at: jobFolderData.created_at,
        updated_at: jobFolderData.updated_at || jobFolderData.created_at,
        action_type: 'collect_posts'
      };
      setUniversalFolder(universalFolderData);

      // Update job folder with actual post count
      setJobFolder(prev => prev ? { ...prev, post_count: allPosts.length } : prev);

      // Set job status
      if (allPosts.length === 0) {
        setJobStatus({
          status: 'warning',
          message: 'No posts found. The scraping may not have completed or no data was available.'
        });
      } else {
        setJobStatus({
          status: 'completed',
          message: `Successfully loaded ${allPosts.length} posts`
        });
      }

    } catch (error) {
      console.error('Error fetching job data:', error);
      setError('Failed to load job data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const actualParams = getActualFolderParams();
    if (projectId && (folderId || (actualParams.folderName && actualParams.scrapeNumber) || runId)) {
      fetchJobData();
    }
  }, [projectId, folderId, folderName, scrapeNumber, runId]);

  // Debug effect to log when posts change
  useEffect(() => {
    console.log('Posts changed:', posts.length, posts);
  }, [posts]);

  // Calculate stats when posts change
  useEffect(() => {
    console.log('Stats calculation triggered - posts length:', posts.length, 'universalFolder:', !!universalFolder);
    if (posts.length > 0 && universalFolder) {
      console.log('Posts data for stats:', posts.map(p => ({ 
        user: p.user_posted, 
        likes: p.likes, 
        comments: p.num_comments, 
        verified: p.is_verified 
      })));
      
      const stats = {
        totalItems: posts.length,
        uniqueUsers: new Set(posts.map(p => p.user_posted)).size,
        avgLikes: Math.round(posts.reduce((sum, p) => sum + p.likes, 0) / posts.length),
        avgComments: Math.round(posts.reduce((sum, p) => sum + p.num_comments, 0) / posts.length),
        verifiedAccounts: posts.filter(p => p.is_verified).length,
        platform: universalFolder.platform
      };
      console.log('Calculated stats:', stats);
      setCalculatedStats(stats);
    } else {
      console.log('Setting stats to null - posts length:', posts.length, 'universalFolder:', !!universalFolder);
      setCalculatedStats(null);
    }
  }, [posts, universalFolder]);

  const handleBackClick = () => {
    if (jobFolder?.parent_folder) {
      // Navigate back to parent service folder
      navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/service/${jobFolder.parent_folder}`);
    } else {
      // Navigate back to data storage main page
      navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage`);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'pending':
        return <PendingIcon color="warning" />;
      case 'processing':
        return <CircularProgress size={20} />;
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <PendingIcon color="action" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'processing':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  // If we have the universal folder data, render the UniversalDataDisplay
  if (universalFolder) {
    return (
      <Box sx={{ 
        width: '100%', 
        padding: '16px 32px',
        bgcolor: '#f5f5f5',
        minHeight: 'calc(100vh - 56px)',
      }}>
        
                 {error && (
           <Alert severity="error" sx={{ mb: 3 }}>
             {error}
           </Alert>
         )}

        {/* Download Section */}
        {posts.length > 0 && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="h6">
                Export Data ({posts.length} posts)
              </Typography>
              <Box display="flex" gap={2}>
                <Button
                  variant="outlined"
                  startIcon={downloading.csv ? <CircularProgress size={20} /> : <DownloadIcon />}
                  onClick={() => downloadData('csv')}
                  disabled={downloading.csv || downloading.json}
                  size="small"
                >
                  Download CSV
                </Button>
                <Button
                  variant="outlined"
                  startIcon={downloading.json ? <CircularProgress size={20} /> : <GetAppIcon />}
                  onClick={() => downloadData('json')}
                  disabled={downloading.csv || downloading.json}
                  size="small"
                >
                  Download JSON
                </Button>
              </Box>
            </Box>
          </Paper>
        )}

         {/* Universal Data Display */}
         {calculatedStats ? (
           <UniversalDataDisplay
             folder={universalFolder}
             platform={universalFolder.platform}
             onBackNavigation={handleBackClick}
             onRefresh={fetchJobData}
             data={postToUniversalData(posts)}
             stats={calculatedStats}
             disableApiFetch={true}
           />
         ) : jobStatus ? (
           <Box sx={{ p: 3, textAlign: 'center' }}>
             <Typography variant="h6" color="text.secondary" gutterBottom>
               {jobStatus.status === 'completed' ? 'No Data Available' : 'Job in Progress'}
             </Typography>
             <Typography color="text.secondary">
               {jobStatus.message}
             </Typography>
           </Box>
         ) : (
           <Box sx={{ p: 3, textAlign: 'center' }}>
             <Typography>Loading data...</Typography>
           </Box>
         )}

        {/* Job Details (Collapsible) */}
        {scraperRequests.length > 0 && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6">
                Job Details ({scraperRequests.length} requests)
              </Typography>
            </Box>
            
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {scraperRequests.map((request) => (
                <Box key={request.id} sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1, mb: 1 }}>
                  <Box display="flex" alignItems="center" gap={2} mb={1}>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getStatusIcon(request.status)}
                      <Chip 
                        label={request.status} 
                        color={getStatusColor(request.status) as any}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      ID: {request.id}
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Target URL:</strong> {request.target_url}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Created: {formatDate(request.created_at)} | 
                    Completed: {request.completed_at ? formatDate(request.completed_at) : 'N/A'}
                    {request.error_message && (
                      <span> | Error: {request.error_message}</span>
                    )}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        )}
      </Box>
    );
  }

    // Fallback: Show loading or error state
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    </Container>
  );
};

export default JobFolderView;

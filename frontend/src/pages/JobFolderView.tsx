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
  const { organizationId, projectId, folderId } = useParams<{ 
    organizationId: string; 
    projectId: string; 
    folderId: string;
  }>();
  const navigate = useNavigate();
  
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
    const jobId = actualBatchJobId || folderId;
    if (!jobId) return;
    
    setDownloading(prev => ({ ...prev, [format]: true }));
    
    try {
      const response = await apiFetch(`/api/apify/batch-jobs/${jobId}/export/?format=${format}`);
      if (!response.ok) {
        throw new Error(`Failed to download ${format.toUpperCase()} data`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `batch_job_${jobId}_results.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
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
      // Fetch the job folder from unified folders API
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

        try {
          // Fetch posts from the platform-specific API (with project parameter for security)
          const postsEndpoint = `/api/${platform}-data/folders/${platformFolderId}/posts/?project=${projectId}`;
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
    if (projectId && folderId) {
      fetchJobData();
    }
  }, [projectId, folderId]);

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

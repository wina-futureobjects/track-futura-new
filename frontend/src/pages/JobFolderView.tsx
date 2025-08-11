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
  description: string;
  likes: number;
  num_comments: number;
  date_posted: string;
  created_at: string;
}

// Data adapter to convert posts to UniversalDataItem format
const postToUniversalData = (posts: Post[]): UniversalDataItem[] => {
  return posts.map(post => ({
    id: post.id,
    url: post.url,
    content: post.description,
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

  const fetchJobData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch job folder details
      const folderResponse = await apiFetch(`/api/track-accounts/report-folders/${folderId}/?project=${projectId}`);
      if (!folderResponse.ok) {
        throw new Error('Failed to fetch job folder details');
      }
             const folderData = await folderResponse.json();
       setJobFolder(folderData);

       // Create UniversalFolder object for UniversalDataDisplay
       const universalFolderData: UniversalFolder = {
         id: folderData.id,
         name: folderData.name,
         description: folderData.description,
         category: 'posts', // Job folders are always posts
         category_display: 'Posts',
         platform: folderData.platform_code || folderData.platform || 'instagram',
         job_id: folderData.id,
         created_at: folderData.created_at,
         updated_at: folderData.created_at,
         action_type: 'collect_posts'
       };
       setUniversalFolder(universalFolderData);

       // Fetch associated scraper requests - we'll get all requests and filter by track_source_id
      const requestsResponse = await apiFetch(`/api/brightdata/requests/`);
      if (requestsResponse.ok) {
        const requestsData = await requestsResponse.json();
        const allRequests = requestsData.results || requestsData || [];
        
        // Filter requests that are associated with this job folder
        // Since we know the job folder is for track_source_id 49, we'll filter by that
        const filteredRequests = allRequests.filter((req: any) => {
          if (req.batch_job && req.batch_job.platform_params) {
            try {
              const params = typeof req.batch_job.platform_params === 'string' 
                ? JSON.parse(req.batch_job.platform_params) 
                : req.batch_job.platform_params;
              return params.track_source_id === 49; // The track source for this job
            } catch {
              return false;
            }
          }
          return false;
        });
        
        setScraperRequests(filteredRequests);
      }

             // Fetch platform-specific data (posts) for this job folder
       const platformDataResponse = await apiFetch(`/api/track-accounts/report-folders/${folderId}/platform_data/`);
       if (platformDataResponse.ok) {
         const platformData = await platformDataResponse.json();
         const fetchedPosts = platformData.posts || [];
         setPosts(fetchedPosts);
         
         // Update universal folder with platform info
         if (universalFolder) {
           setUniversalFolder({
             ...universalFolder,
             platform: platformData.platform || universalFolder.platform
           });
         }
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
        
        {/* Header with breadcrumbs */}
        <Box display="flex" alignItems="center" mb={3}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBackClick}
            sx={{ mr: 2 }}
          >
            Back
          </Button>
          <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
            <Button
              startIcon={<HomeIcon />}
              onClick={() => navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage`)}
              sx={{ textTransform: 'none' }}
            >
              Data Storage
            </Button>
            {jobFolder && (
              <Typography color="text.primary">{jobFolder.name}</Typography>
            )}
          </Breadcrumbs>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Job Folder Header */}
        {jobFolder && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Box display="flex" alignItems="center">
                <WorkIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h5" sx={{ fontWeight: 500 }}>
                  {jobFolder.name}
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <Chip 
                  label={jobFolder.platform_code || jobFolder.platform} 
                  color="primary" 
                  variant="outlined"
                />
                <Chip 
                  label={jobFolder.service_code || jobFolder.category} 
                  color="secondary" 
                  variant="outlined"
                />
              </Box>
            </Box>
            {jobFolder.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {jobFolder.description}
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary">
              Created: {formatDate(jobFolder.created_at || '')}
            </Typography>
          </Paper>
        )}

        {/* Job Statistics */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Posts
                </Typography>
                <Typography variant="h4" color="primary.main">
                  {posts.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Requests
                </Typography>
                <Typography variant="h4">
                  {scraperRequests.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Completed
                </Typography>
                <Typography variant="h4" color="success.main">
                  {scraperRequests.filter(req => req.status === 'completed').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Failed
                </Typography>
                <Typography variant="h4" color="error.main">
                  {scraperRequests.filter(req => req.status === 'failed').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Universal Data Display */}
        <UniversalDataDisplay
          folder={universalFolder}
          platform={universalFolder.platform}
          onBackNavigation={handleBackClick}
          onRefresh={fetchJobData}
          data={postToUniversalData(posts)}
          stats={{
            totalItems: posts.length,
            uniqueUsers: new Set(posts.map(p => p.user_posted)).size,
            avgLikes: posts.length > 0 ? Math.round(posts.reduce((sum, p) => sum + p.likes, 0) / posts.length) : 0,
            avgComments: posts.length > 0 ? Math.round(posts.reduce((sum, p) => sum + p.num_comments, 0) / posts.length) : 0,
            verifiedAccounts: 0, // We don't have this data in posts
            platform: universalFolder.platform
          }}
          disableApiFetch={true}
        />

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

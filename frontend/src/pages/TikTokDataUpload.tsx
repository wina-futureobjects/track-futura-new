import { useState, useEffect, ChangeEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Link,
  Chip,
  Divider,
  Card,
  CardContent,
  IconButton,
  TextField,
  Stack,
  Breadcrumbs,
  Tooltip,
  Snackbar,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  InputAdornment,
  Grid,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import EditIcon from '@mui/icons-material/Edit';

interface TikTokPost {
  id: number;
  url: string;
  user_posted: string;
  description: string | null;
  hashtags: string | null;
  num_comments: number;
  date_posted: string;
  likes: number;
  post_id: string;
  content_type: string | null;
  thumbnail: string | null;
  followers: number | null;
  posts_count: number | null;
  is_verified: boolean;
  is_paid_partnership: boolean;
}

interface Folder {
  id: number;
  name: string;
  description: string | null;
}

// Add an interface for folder statistics
interface FolderStats {
  totalPosts: number;
  uniqueUsers: number;
  avgLikes: number;
  verifiedAccounts: number;
}

const TikTokDataUpload = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  
  // Update state to handle two separate files
  const [postFile, setPostFile] = useState<File | null>(null);
  const [reelFile, setReelFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [posts, setPosts] = useState<TikTokPost[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredPosts, setFilteredPosts] = useState<TikTokPost[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentFolder, setCurrentFolder] = useState<Folder | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [folderStats, setFolderStats] = useState<FolderStats>({
    totalPosts: 0,
    uniqueUsers: 0,
    avgLikes: 0,
    verifiedAccounts: 0
  });
  // Add tab state for upload section
  const [uploadTabValue, setUploadTabValue] = useState(0);
  // Add content type filter state
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('all');
  // Add a state for server status
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Fetch TikTok posts with pagination
  const fetchPosts = async (pageNumber = 0, pageSize = 10, searchTerm = '', contentType = '') => {
    try {
      setIsLoading(true);
      // Add folder filtering if folderId is present
      const folderParam = folderId ? `&folder_id=${folderId}` : '';
      // Add search param if search term exists
      const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
      // Add content type filter if not 'all'
      const contentTypeParam = contentType && contentType !== 'all' 
        ? `&content_type=${contentType}` 
        : '';
      
      const response = await fetch(`/api/tiktok-data/posts/?page=${pageNumber + 1}&page_size=${pageSize}${folderParam}${searchParam}${contentTypeParam}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch posts');
      }
      const data = await response.json();
      
      // Check if the response has the expected pagination structure
      if (data && typeof data === 'object' && 'results' in data) {
        setPosts(data.results || []);
        setFilteredPosts(data.results || []);
        setTotalCount(data.count || 0);
      } else if (Array.isArray(data)) {
        // Handle case where API might return a direct array
        setPosts(data);
        setFilteredPosts(data);
        setTotalCount(data.length);
        console.warn('API returned an array instead of paginated results');
      } else {
        console.error('API returned unexpected data format:', data);
        setPosts([]);
        setFilteredPosts([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      setPosts([]);
      setFilteredPosts([]);
      setTotalCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch folder details if folderId is present
  const fetchFolderDetails = async () => {
    if (folderId) {
      try {
        const response = await fetch(`/api/tiktok-data/folders/${folderId}/`);
        if (response.ok) {
          const data = await response.json();
          setCurrentFolder(data);
        }
      } catch (error) {
        console.error('Error fetching folder details:', error);
      }
    }
  };

  // Add function to fetch folder statistics
  const fetchFolderStats = async () => {
    if (!folderId) return;
    
    try {
      const folderParam = `folder_id=${folderId}`;
      // Get stats for all posts in the folder (no pagination)
      const response = await fetch(`/api/tiktok-data/posts/?${folderParam}&page_size=1000`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch folder statistics');
      }
      
      const data = await response.json();
      
      if (data && typeof data === 'object' && 'results' in data) {
        const allPosts = data.results || [];
        const uniqueUsers = [...new Set(allPosts.map((post: TikTokPost) => post.user_posted))].length;
        const totalLikes = allPosts.reduce((acc: number, post: TikTokPost) => acc + post.likes, 0);
        const avgLikes = allPosts.length > 0 ? Math.round(totalLikes / allPosts.length) : 0;
        const verifiedAccounts = allPosts.filter((post: TikTokPost) => post.is_verified).length;
        
        setFolderStats({
          totalPosts: data.count || 0,
          uniqueUsers,
          avgLikes,
          verifiedAccounts
        });
      }
    } catch (error) {
      console.error('Error fetching folder statistics:', error);
    }
  };

  // Check server status
  const checkServerStatus = async () => {
    try {
      // Use a simple endpoint to check if server is running
      const response = await fetch('/api/tiktok-data/folders/', { 
        method: 'HEAD',
        headers: { 'Accept': 'application/json' }
      });
      
      setServerStatus(response.ok ? 'online' : 'offline');
    } catch (error) {
      console.error('Server connection error:', error);
      setServerStatus('offline');
    }
  };

  // Check server status on component mount
  useEffect(() => {
    checkServerStatus();
  }, []);

  // Initial data load
  useEffect(() => {
    fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
    if (folderId) {
      fetchFolderDetails();
      fetchFolderStats();
    }
  }, [folderId]); // Only re-fetch when folder ID changes
  
  // This effect handles pagination, search, and content type filter changes
  useEffect(() => {
    fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
  }, [page, rowsPerPage, searchTerm, contentTypeFilter]);

  // Handle tab change
  const handleUploadTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setUploadTabValue(newValue);
  };

  // Separate handlers for post and reel file selection
  const handlePostFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setPostFile(event.target.files[0]);
      // Reset status messages
      setUploadSuccess(null);
      setUploadError(null);
    }
  };

  const handleReelFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setReelFile(event.target.files[0]);
      // Reset status messages
      setUploadSuccess(null);
      setUploadError(null);
    }
  };

  // CSV validation function to check for common date format issues
  const validateCsvFile = async (file: File): Promise<{valid: boolean, message?: string}> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          const csvContent = event.target?.result as string;
          if (!csvContent) {
            resolve({valid: false, message: 'Could not read file content'});
            return;
          }
          
          // Split into lines and get headers
          const lines = csvContent.split('\n');
          if (lines.length < 2) {
            resolve({valid: false, message: 'CSV file appears to be empty or invalid'});
            return;
          }
          
          const headers = lines[0].split(',');
          
          // Check if date_posted column exists
          const dateColumnIndex = headers.findIndex(h => 
            h.trim().toLowerCase() === 'date_posted' || 
            h.trim().toLowerCase() === '"date_posted"'
          );
          
          if (dateColumnIndex === -1) {
            // No date column found, file is valid
            resolve({valid: true});
            return;
          }
          
          // Check a sample of rows for potential date issues
          const sampleSize = Math.min(10, lines.length - 1); // Check up to 10 rows
          for (let i = 1; i <= sampleSize; i++) {
            const row = lines[i].split(',');
            if (row.length <= dateColumnIndex) continue;
            
            const dateValue = row[dateColumnIndex].trim();
            
            // Skip empty values
            if (!dateValue || dateValue === '""' || dateValue === "''") continue;
            
            // Check for common date format issues
            if (dateValue.includes('/') || 
                (dateValue.includes('"') && dateValue.length > 2) ||
                dateValue.match(/^\d{1,2}-\d{1,2}-\d{4}$/)) {
              resolve({
                valid: false, 
                message: 'Warning: Your CSV may contain dates in non-standard formats. ' +
                         'Please ensure dates are in YYYY-MM-DD format or they might not be processed correctly.'
              });
              return;
            }
          }
          
          // If we got here, file seems valid
          resolve({valid: true});
          
        } catch (error) {
          console.error('CSV validation error:', error);
          resolve({valid: true}); // Allow upload despite validation error
        }
      };
      
      reader.onerror = () => {
        resolve({valid: false, message: 'Error reading the file'});
      };
      
      reader.readAsText(file);
    });
  };

  // Handle upload for posts
  const handlePostUpload = async () => {
    if (!postFile) {
      setUploadError('Please select a post CSV file to upload');
      return;
    }

    if (!postFile.name.endsWith('.csv')) {
      setUploadError('Please upload a CSV file');
      return;
    }
    
    // Validate CSV before uploading
    try {
      const validationResult = await validateCsvFile(postFile);
      if (!validationResult.valid) {
        setUploadError(validationResult.message || 'CSV validation failed');
        return;
      }
    } catch (error) {
      console.error('Validation error:', error);
      // Continue with upload despite validation error
    }

    const formData = new FormData();
    formData.append('file', postFile);
    formData.append('content_type', 'post');
    
    // Add folder_id to the form data if available
    if (folderId) {
      formData.append('folder_id', folderId);
    }

    try {
      setIsUploading(true);
      setUploadError(null); // Clear previous errors
      
      // Check if the backend server is running
      try {
        const response = await fetch('/api/tiktok-data/posts/upload_csv/', {
          method: 'POST',
          body: formData,
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          // Check for specific error messages
          let errorMessage = errorData.error || 'Upload failed';
          
          // Format array error messages more nicely
          if (Array.isArray(errorMessage)) {
            errorMessage = errorMessage.join('\n');
          }
          
          throw new Error(errorMessage);
        }

        const data = await response.json();
        
        if (data.success) {
          setUploadSuccess(`Successfully uploaded TikTok posts.`);
          if (data.posts_created > 0 || data.posts_updated > 0) {
            setUploadSuccess(
              `Successfully processed ${data.posts_created + data.posts_updated} posts. ` +
              `Created: ${data.posts_created}, Updated: ${data.posts_updated}, Skipped: ${data.posts_skipped}.`
            );
          }
          
          // Refresh the posts to show the newly uploaded ones
          fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
          // Also refresh the stats
          if (folderId) {
            fetchFolderStats();
          }
          
          // Clear the file input
          setPostFile(null);
          
          // Add error summary if there were some errors
          if (data.total_errors > 0) {
            setUploadSuccess(prevSuccess => 
              `${prevSuccess} However, ${data.total_errors} rows had errors. See browser console for details.`
            );
            console.error('Upload errors:', data.errors);
          }
        } else {
          throw new Error(data.error || 'Upload failed');
        }
      } catch (error: any) {
        // Network or API errors
        if (error instanceof Error) {
          setUploadError(error.message);
        } else if (typeof error === 'string') {
          setUploadError(error);
        } else {
          setUploadError('Failed to upload posts. Please check your network connection and try again.');
        }
        console.error('Upload error:', error);
      }
    } finally {
      setIsUploading(false);
    }
  };

  // Handle upload for reels
  const handleReelUpload = async () => {
    if (!reelFile) {
      setUploadError('Please select a reel CSV file to upload');
      return;
    }

    if (!reelFile.name.endsWith('.csv')) {
      setUploadError('Please upload a CSV file');
      return;
    }
    
    // Validate CSV before uploading
    try {
      const validationResult = await validateCsvFile(reelFile);
      if (!validationResult.valid) {
        setUploadError(validationResult.message || 'CSV validation failed');
        return;
      }
    } catch (error) {
      console.error('Validation error:', error);
      // Continue with upload despite validation error
    }

    const formData = new FormData();
    formData.append('file', reelFile);
    formData.append('content_type', 'reel');
    
    // Add folder_id to the form data if available
    if (folderId) {
      formData.append('folder_id', folderId);
    }

    try {
      setIsUploading(true);
      setUploadError(null); // Clear previous errors
      
      // Check if the backend server is running
      try {
        const response = await fetch('/api/tiktok-data/posts/upload_csv/', {
          method: 'POST',
          body: formData,
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          // Check for specific error messages
          let errorMessage = errorData.error || 'Upload failed';
          
          // Format array error messages more nicely
          if (Array.isArray(errorMessage)) {
            errorMessage = errorMessage.join('\n');
          }
          
          throw new Error(errorMessage);
        }

        const data = await response.json();
        
        if (data.success) {
          setUploadSuccess(`Successfully uploaded TikTok videos.`);
          if (data.posts_created > 0 || data.posts_updated > 0) {
            setUploadSuccess(
              `Successfully processed ${data.posts_created + data.posts_updated} videos. ` +
              `Created: ${data.posts_created}, Updated: ${data.posts_updated}, Skipped: ${data.posts_skipped}.`
            );
          }
          
          // Refresh the posts to show the newly uploaded ones
          fetchPosts(page, rowsPerPage, searchTerm, 'reel');
          // Also refresh the stats
          if (folderId) {
            fetchFolderStats();
          }
          
          // Clear the file input
          setReelFile(null);
          
          // Add error summary if there were some errors
          if (data.total_errors > 0) {
            setUploadSuccess(prevSuccess => 
              `${prevSuccess} However, ${data.total_errors} rows had errors. See browser console for details.`
            );
            console.error('Upload errors:', data.errors);
          }
        } else {
          throw new Error(data.error || 'Upload failed');
        }
      } catch (error: any) {
        // Network or API errors
        if (error instanceof Error) {
          setUploadError(error.message);
        } else if (typeof error === 'string') {
          setUploadError(error);
        } else {
          setUploadError('Failed to upload videos. Please check your network connection and try again.');
        }
        console.error('Upload error:', error);
      }
    } finally {
      setIsUploading(false);
    }
  };

  // Handle CSV download
  const handleDownloadCSV = async (contentType: 'post' | 'reel' | undefined) => {
    try {
      let url = `/api/tiktok-data/posts/download_csv/?`;
      
      // Add folder parameter if we have a folder ID
      if (folderId) {
        url += `folder_id=${folderId}&`;
      }
      
      // Add content type if specified
      if (contentType) {
        url += `content_type=${contentType}`;
      }
      
      // Force download using window.location to avoid CORS issues with fetch
      window.location.href = url;
      
      // Show confirmation
      setSnackbarMessage('Download started. Check your downloads folder.');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Error downloading CSV:', error);
      setSnackbarMessage('Failed to download data. Please try again.');
      setSnackbarOpen(true);
    }
  };

  // Handle pagination change
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };
  
  // Handle rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Handle search input change
  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    // Reset to first page when searching
    setPage(0);
  };
  
  // Navigate back to folders
  const handleGoToFolders = () => {
    navigate('/tiktok-folders');
  };
  
  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    setSnackbarMessage('Link copied to clipboard');
    setSnackbarOpen(true);
  };
  
  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };
  
  // Handle content type filter change
  const handleContentTypeFilterChange = (event: SelectChangeEvent) => {
    setContentTypeFilter(event.target.value as string);
    setPage(0); // Reset to first page when changing filter
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs navigation */}
      <Box mb={4}>
        <Breadcrumbs separator="›" aria-label="breadcrumb">
          <Link 
            component="button"
            underline="hover"
            sx={{ display: 'flex', alignItems: 'center' }}
            color="inherit"
            onClick={handleGoToFolders}
          >
            <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Folders
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
            <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            {currentFolder ? currentFolder.name : 'TikTok Data'}
          </Typography>
        </Breadcrumbs>
      </Box>

      {/* Page title with folder details */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          {currentFolder ? currentFolder.name : 'TikTok Data'}
        </Typography>
        {currentFolder?.description && (
          <Typography variant="body1" color="text.secondary" paragraph>
            {currentFolder.description}
          </Typography>
        )}
      </Box>

      {/* Folder statistics cards */}
      {folderId && (
        <Box mb={4}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Content
                  </Typography>
                  <Typography variant="h4">
                    {folderStats.totalPosts}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Unique Creators
                  </Typography>
                  <Typography variant="h4">
                    {folderStats.uniqueUsers}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Avg. Likes
                  </Typography>
                  <Typography variant="h4">
                    {folderStats.avgLikes}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Verified Accounts
                  </Typography>
                  <Typography variant="h4">
                    {folderStats.verifiedAccounts}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* File Upload Section */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Upload TikTok Data
        </Typography>
        
        {serverStatus === 'offline' && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Server appears to be offline or not responding. Please check your connection and try again.
          </Alert>
        )}

        <Tabs 
          value={uploadTabValue} 
          onChange={handleUploadTabChange}
          sx={{ mb: 2 }}
        >
          <Tab label="Posts" />
          <Tab label="Videos" />
        </Tabs>

        {uploadTabValue === 0 && (
          <Box>
            <Box mb={3}>
              <Typography variant="body1" gutterBottom>
                Upload a CSV file containing TikTok post data.
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                File must be in CSV format and include the following columns: Post URL, User Name, Post Caption, etc.
              </Typography>
              <Button
                component="label"
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                sx={{ my: 2 }}
                disabled={isUploading || serverStatus === 'offline'}
              >
                Select Post CSV
                <input
                  type="file"
                  hidden
                  accept=".csv"
                  onChange={handlePostFileChange}
                />
              </Button>
              {postFile && (
                <Typography variant="body2" sx={{ ml: 2, display: 'inline' }}>
                  Selected: {postFile.name}
                </Typography>
              )}
            </Box>
            <Button
              variant="contained"
              color="primary"
              onClick={handlePostUpload}
              disabled={!postFile || isUploading || serverStatus === 'offline'}
            >
              {isUploading ? <CircularProgress size={24} /> : 'Upload Posts'}
            </Button>
            <Button
              variant="outlined"
              color="primary"
              startIcon={<DownloadIcon />}
              sx={{ ml: 2 }}
              onClick={() => handleDownloadCSV('post')}
              disabled={serverStatus === 'offline'}
            >
              Download Posts CSV
            </Button>
          </Box>
        )}

        {uploadTabValue === 1 && (
          <Box>
            <Box mb={3}>
              <Typography variant="body1" gutterBottom>
                Upload a CSV file containing TikTok video data.
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                File must be in CSV format and include the following columns: Video URL, Creator Name, Video Caption, etc.
              </Typography>
              <Button
                component="label"
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                sx={{ my: 2 }}
                disabled={isUploading || serverStatus === 'offline'}
              >
                Select Video CSV
                <input
                  type="file"
                  hidden
                  accept=".csv"
                  onChange={handleReelFileChange}
                />
              </Button>
              {reelFile && (
                <Typography variant="body2" sx={{ ml: 2, display: 'inline' }}>
                  Selected: {reelFile.name}
                </Typography>
              )}
            </Box>
            <Button
              variant="contained"
              color="primary"
              onClick={handleReelUpload}
              disabled={!reelFile || isUploading || serverStatus === 'offline'}
            >
              {isUploading ? <CircularProgress size={24} /> : 'Upload Videos'}
            </Button>
            <Button
              variant="outlined"
              color="primary"
              startIcon={<DownloadIcon />}
              sx={{ ml: 2 }}
              onClick={() => handleDownloadCSV('reel')}
              disabled={serverStatus === 'offline'}
            >
              Download Videos CSV
            </Button>
          </Box>
        )}

        {uploadError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {uploadError}
          </Alert>
        )}
        
        {uploadSuccess && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {uploadSuccess}
          </Alert>
        )}
      </Paper>

      {/* Data display section */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap' }}>
          <Typography variant="h5" component="h2" gutterBottom>
            TikTok Data
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {/* Content type filter */}
            <FormControl sx={{ minWidth: 120, mt: { xs: 2, sm: 0 } }}>
              <InputLabel id="content-type-filter-label">Content Type</InputLabel>
              <Select
                labelId="content-type-filter-label"
                id="content-type-filter"
                value={contentTypeFilter}
                label="Content Type"
                onChange={handleContentTypeFilterChange}
                size="small"
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="post">Posts</MenuItem>
                <MenuItem value="reel">Videos</MenuItem>
              </Select>
            </FormControl>
            {/* Search box */}
            <TextField
              label="Search"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ mt: { xs: 2, sm: 0 } }}
            />
          </Box>
        </Box>
        
        {isLoading ? (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        ) : posts.length === 0 ? (
          <Alert severity="info">
            No TikTok data available. Upload some data to get started.
          </Alert>
        ) : (
          <>
            <TableContainer>
              <Table aria-label="TikTok posts table">
                <TableHead>
                  <TableRow>
                    <TableCell>Creator</TableCell>
                    <TableCell>Content</TableCell>
                    <TableCell>Posted Date</TableCell>
                    <TableCell>Engagement</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {posts.map((post) => (
                    <TableRow key={post.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Box>
                            <Typography variant="body2" component="div">
                              {post.user_posted}
                              {post.is_verified && (
                                <Tooltip title="Verified Account">
                                  <Chip 
                                    label="Verified" 
                                    size="small" 
                                    color="primary" 
                                    variant="outlined"
                                    sx={{ ml: 1 }}
                                  />
                                </Tooltip>
                              )}
                            </Typography>
                            {post.followers !== null && (
                              <Typography variant="caption" color="text.secondary">
                                {post.followers.toLocaleString()} followers
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 250 }} noWrap>
                          {post.description || 'No description'}
                        </Typography>
                        {post.hashtags && (
                          <Typography variant="caption" color="primary">
                            {post.hashtags.slice(0, 50)}
                            {post.hashtags.length > 50 ? '...' : ''}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {post.date_posted ? new Date(post.date_posted).toLocaleDateString() : 'Unknown'}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {post.likes} likes
                        </Typography>
                        <Typography variant="body2">
                          {post.num_comments} comments
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={post.content_type === 'reel' ? 'Video' : 'Post'} 
                          size="small" 
                          color={post.content_type === 'reel' ? 'secondary' : 'default'}
                        />
                        {post.is_paid_partnership && (
                          <Chip 
                            label="Paid" 
                            size="small" 
                            color="warning" 
                            variant="outlined"
                            sx={{ mt: 0.5 }}
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="Open in TikTok">
                            <IconButton 
                              size="small" 
                              onClick={() => window.open(post.url, '_blank')}
                              color="primary"
                            >
                              <OpenInNewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy Link">
                            <IconButton 
                              size="small"
                              onClick={() => handleCopyLink(post.url)}
                            >
                              <ContentCopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50, 100]}
              component="div"
              count={totalCount}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </>
        )}
      </Paper>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default TikTokDataUpload; 
import { useState, useEffect, ChangeEvent } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  InputAdornment,
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
import { apiFetch } from '../utils/api';

interface InstagramPost {
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

interface InstagramComment {
  id: number;
  comment_id: string;
  post_id: string;
  post_url: string;
  post_user: string;
  comment: string;
  comment_date: string;
  comment_user: string;
  comment_user_url: string;
  likes_number: number;
  replies_number: number;
  hashtag_comment: string;
  url: string;
}

interface Folder {
  id: number;
  name: string;
  description: string | null;
  category: 'posts' | 'reels' | 'comments';
  category_display: string;
}

// Add an interface for folder statistics
interface FolderStats {
  totalPosts: number;
  uniqueUsers: number;
  avgLikes: number;
  verifiedAccounts: number;
}

const InstagramDataUpload = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Update state to handle single file upload
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [posts, setPosts] = useState<InstagramPost[]>([]);
  const [comments, setComments] = useState<InstagramComment[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredPosts, setFilteredPosts] = useState<InstagramPost[]>([]);
  const [filteredComments, setFilteredComments] = useState<InstagramComment[]>([]);
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
  // Remove upload tab state as we're using single upload now
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('all');
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Fetch Instagram posts/comments with pagination
  const fetchPosts = async (pageNumber = 0, pageSize = 10, searchTerm = '', contentType = '') => {
    try {
      setIsLoading(true);
      
      if (!folderId) {
        setPosts([]);
        setComments([]);
        setFilteredPosts([]);
        setFilteredComments([]);
        setTotalCount(0);
        return;
      }
      
      // Always try the posts endpoint first (same as fetchFolderStats)
      const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
      const contentTypeParam = contentType && contentType !== 'all' ? `&content_type=${contentType}` : '';
      const folderParam = `folder_id=${folderId}`;
      
      const postsApiUrl = `/api/instagram-data/posts/?${folderParam}&page=${pageNumber + 1}&page_size=${pageSize}${searchParam}${contentTypeParam}`;
      console.log('🚀 Attempting to fetch posts from:', postsApiUrl);
      
      try {
        const response = await apiFetch(postsApiUrl);
        console.log('📥 Posts API response status:', response.status, 'OK:', response.ok);
        
        if (response.ok) {
          const data = await response.json();
          console.log('📊 Posts endpoint response data:', data);
          console.log('📊 Posts endpoint response structure:', {
            hasResults: 'results' in data,
            hasCount: 'count' in data,
            resultsLength: data.results?.length || 0,
            totalCount: data.count || 0,
            dataType: typeof data,
            dataKeys: Object.keys(data || {})
          });
          
          if (data && typeof data === 'object' && 'results' in data) {
            const results = data.results || [];
            console.log('✅ Setting posts data with', results.length, 'items');
            console.log('📋 First few posts:', results.slice(0, 2));
            
            setPosts(results);
            setFilteredPosts(results);
            setComments([]);
            setFilteredComments([]);
            setTotalCount(data.count || results.length);
            return; // Success, exit function
          } else {
            console.error('❌ Posts endpoint returned data without results structure:', data);
          }
        } else {
          console.error('❌ Posts endpoint HTTP error:', response.status, response.statusText);
        }
      } catch (postsError) {
        console.log('❌ Posts endpoint failed with error:', postsError);
      }
      
      // Fallback: try the comments/folder contents endpoint if posts endpoint fails
      if (currentFolder?.category === 'comments') {
        const response = await apiFetch(`/api/instagram-data/folders/${folderId}/contents/?page=${pageNumber + 1}&page_size=${pageSize}${searchParam}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch folder contents');
        }
        const data = await response.json();
        
        console.log('Comments folder contents response:', data);
        
        if (data && typeof data === 'object') {
          const results = data.results || [];
          console.log('Setting comments data:', results);
          setComments(results);
          setFilteredComments(results);
          setPosts([]);
          setFilteredPosts([]);
          setTotalCount(data.count || results.length);
        }
      } else {
        // If posts endpoint failed and it's not a comments folder, set empty state
        console.error('Posts endpoint failed and folder is not comments type');
        setPosts([]);
        setComments([]);
        setFilteredPosts([]);
        setFilteredComments([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      setPosts([]);
      setComments([]);
      setFilteredPosts([]);
      setFilteredComments([]);
      setTotalCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch folder details if folderId is present
  const fetchFolderDetails = async () => {
    if (folderId) {
      try {
        const response = await apiFetch(`/api/instagram-data/folders/${folderId}/`);
        if (response.ok) {
          const data = await response.json();
          console.log('Folder details response:', data);
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
      const statsApiUrl = `/api/instagram-data/posts/?${folderParam}&page_size=1000`;
      console.log('📈 Fetching folder stats from:', statsApiUrl);
      
      // Get stats for all posts in the folder (no pagination)
      const response = await apiFetch(statsApiUrl);
      console.log('📈 Stats API response status:', response.status, 'OK:', response.ok);
      
      if (!response.ok) {
        throw new Error('Failed to fetch folder statistics');
      }
      
      const data = await response.json();
      console.log('📈 Stats API response data:', data);
      console.log('📈 Stats API response structure:', {
        hasResults: 'results' in data,
        hasCount: 'count' in data,
        resultsLength: data.results?.length || 0,
        totalCount: data.count || 0,
        dataType: typeof data
      });
      
      if (data && typeof data === 'object' && 'results' in data) {
        const allPosts = data.results || [];
        const uniqueUsers = [...new Set(allPosts.map((post: InstagramPost) => post.user_posted))].length;
        const totalLikes = allPosts.reduce((acc: number, post: InstagramPost) => acc + post.likes, 0);
        const avgLikes = allPosts.length > 0 ? Math.round(totalLikes / allPosts.length) : 0;
        const verifiedAccounts = allPosts.filter((post: InstagramPost) => post.is_verified).length;
        
        console.log('📈 Calculated stats:', {
          totalPosts: data.count || 0,
          uniqueUsers,
          avgLikes,
          verifiedAccounts,
          actualPostsLength: allPosts.length
        });
        
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
      const response = await apiFetch('/api/instagram-data/folders/', { 
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

  // Handle file change
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setUploadFile(event.target.files[0]);
      // Reset status messages
      setUploadSuccess(null);
      setUploadError(null);
    }
  };

  // Validate CSV file format
  const validateCsvFile = async (file: File): Promise<{valid: boolean, message?: string}> => {
    if (!file) {
      return { valid: false, message: 'No file selected' };
    }
    
    // Check file extension
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (fileExtension !== 'csv') {
      return { valid: false, message: 'File must be a CSV' };
    }
    
    // Basic check on file size
    if (file.size === 0) {
      return { valid: false, message: 'File is empty' };
    }

    if (file.size > 50 * 1024 * 1024) { // 50MB
      return { valid: false, message: 'File is too large (max 50MB)' };
    }
    
    // Basic check for CSV content
    try {
      const sample = await file.slice(0, 1000).text();
      const lines = sample.split('\n');
      
      if (lines.length < 2) {
        return { valid: false, message: 'CSV must contain at least a header row and one data row' };
      }
      
      const header = lines[0].toLowerCase();
      
      // Check for required columns in the header
      const requiredColumns = ['url']; // Only require URL field
      for (const column of requiredColumns) {
        if (!header.includes(column)) {
          return { 
            valid: false, 
            message: `CSV is missing required column: ${column}. Please check the file format.` 
          };
        }
      }
      
      return { valid: true };
    } catch (error) {
      console.error('Error validating file:', error);
      return { valid: false, message: 'Error validating file. Please check the format.' };
    }
  };

  // Handle upload
  const handleUpload = async () => {
    if (!uploadFile) {
      setUploadError('Please select a CSV file to upload');
      return;
    }

    if (!uploadFile.name.endsWith('.csv')) {
      setUploadError('Please upload a CSV file');
      return;
    }
    
    // Validate CSV before uploading
    try {
      const validationResult = await validateCsvFile(uploadFile);
      if (!validationResult.valid) {
        setUploadError(validationResult.message || 'CSV validation failed');
        return;
      }
    } catch (error) {
      console.error('Validation error:', error);
      // Continue with upload despite validation error
    }

    const formData = new FormData();
    formData.append('file', uploadFile);
    
    // Add folder_id to the form data if available
    if (folderId) {
      formData.append('folder_id', folderId);
    }

    try {
      setIsUploading(true);
      setUploadError(null); // Clear previous errors
      
      // Determine the correct upload endpoint based on folder category
      let uploadEndpoint = '/api/instagram-data/posts/upload_csv/';
      if (currentFolder?.category === 'comments') {
        uploadEndpoint = '/api/instagram-data/comments/upload_csv/';
      }
      
      console.log('🔧 Upload Debug Info:');
      console.log('🔧 Current folder:', currentFolder);
      console.log('🔧 Folder category:', currentFolder?.category);
      console.log('🔧 Selected upload endpoint:', uploadEndpoint);
      console.log('🔧 File being uploaded:', uploadFile?.name);
      
      // Check if the backend server is running
      try {
        const response = await apiFetch(uploadEndpoint, {
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
          
          // Show a more user-friendly message for date format errors
          if ((typeof errorMessage === 'string') && 
              (errorMessage.includes('invalid format') || errorMessage.includes('YYYY-MM-DD'))) {
            throw new Error('Your CSV file contains dates in an invalid format. Please check that dates use a standard format like YYYY-MM-DD.');
          }
          
          throw new Error(errorMessage);
        }

        const data = await response.json();
        let successMessage = `${data.message}`;
        
        if (data.detected_content_type) {
          successMessage += ` Content type detected: ${data.detected_content_type}`;
        }
        
        setUploadSuccess(successMessage);
        
        // Refresh the post list and folder details
        await fetchFolderDetails(); // Refresh folder details first
        fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
        fetchFolderStats();
        
        // Reset file input
        setUploadFile(null);
        
        // Reset file input element
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
      } catch (networkError) {
        console.error('Network error:', networkError);
        // Show more helpful error message
        if (networkError instanceof TypeError && networkError.message.includes('Failed to fetch')) {
          throw new Error('Failed to connect to the server. Please check if the backend server is running and try again.');
        } else {
          throw networkError;
        }
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error instanceof Error ? error.message : 'An error occurred during upload');
    } finally {
      setIsUploading(false);
    }
  };

  // Update download function to handle content type
  const handleDownloadCSV = async (contentType: 'post' | 'reel' | undefined) => {
    try {
      // Add folder filtering if folderId is present
      const folderParam = folderId ? `folder_id=${folderId}` : '';
      // Add content type parameter
      const contentTypeParam = contentType ? `&content_type=${contentType}` : '';
      
      const response = await apiFetch(
        `/api/instagram-data/posts/download_csv/?${folderParam}${contentTypeParam}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to download CSV');
      }
      
      // Get the filename from the Content-Disposition header if possible
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'instagram_data.csv';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      } else {
        // Fallback filename based on content type
        filename = contentType ? `instagram_${contentType}s.csv` : 'instagram_data.csv';
      }
      
      // Convert the response to a blob
      const blob = await response.blob();
      
      // Create a download link and trigger download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      
      // Show success message
      setSnackbarMessage('CSV downloaded successfully!');
      setSnackbarOpen(true);
      
    } catch (error) {
      console.error('Download error:', error);
      setSnackbarMessage('Failed to download CSV. Please try again.');
      setSnackbarOpen(true);
    }
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    // No need to call fetchPosts here, it will be triggered by the useEffect
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0); // Reset to first page
    // No need to call fetchPosts here, it will be triggered by the useEffect
  };

  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchTerm(value);
    setPage(0); // Reset to first page when searching
    
    // Search will be triggered by the useEffect hook
  };

  // Redirect to folders view
  const handleGoToFolders = () => {
    // Extract organization and project IDs from URL
    const match = location.pathname.match(/\/organizations\/(\d+)\/projects\/(\d+)/);
    
    if (match) {
      const [, orgId, projId] = match;
      navigate(`/organizations/${orgId}/projects/${projId}/instagram-folders`);
    } else {
      // Get project ID from URL query parameter
      const queryParams = new URLSearchParams(location.search);
      const projectId = queryParams.get('project');
      
      if (projectId) {
        navigate(`/instagram-folders?project=${projectId}`);
      } else {
        navigate('/instagram-folders');
      }
    }
  };

  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    setSnackbarMessage('Link copied to clipboard!');
    setSnackbarOpen(true);
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  // Add handler for content type filter change
  const handleContentTypeFilterChange = (event: SelectChangeEvent) => {
    setContentTypeFilter(event.target.value);
    setPage(0); // Reset to first page when changing filter
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Server status indicator */}
      {serverStatus !== 'online' && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: serverStatus === 'checking' ? 'info.light' : 'error.light' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {serverStatus === 'checking' ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography>Checking server status...</Typography>
              </>
            ) : (
              <Typography color="error" fontWeight="bold">
                Server connection issue detected. File uploads may fail. 
                Please check if the backend server is running.
                <Button 
                  variant="outlined" 
                  size="small" 
                  sx={{ ml: 2 }}
                  onClick={checkServerStatus}
                >
                  Retry Connection
                </Button>
              </Typography>
            )}
          </Box>
        </Paper>
      )}
      
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {currentFolder ? `Instagram Data: ${currentFolder.name}` : 'Instagram Data Management'}
          </Typography>
          <Button
            variant="outlined"
            onClick={handleGoToFolders}
          >
            View All Folders
          </Button>
        </Box>
        <Divider sx={{ mb: 4 }} />

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Upload CSV Data
          </Typography>
          
          {currentFolder && currentFolder.category && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <strong>Current folder category: {currentFolder.category_display || currentFolder.category}</strong>
              <br />
              {currentFolder.category === 'comments' 
                ? 'This folder is configured for comments. Upload comment CSV files here.'
                : currentFolder.category === 'posts'
                ? 'This folder is configured for posts. To upload comments, please create or select a folder with "Comments" category.'
                : 'This folder is configured for reels. To upload comments, please create or select a folder with "Comments" category.'
              }
            </Alert>
          )}
          
          {uploadError && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setUploadError(null)}>
              {uploadError}
            </Alert>
          )}
          
          {uploadSuccess && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setUploadSuccess(null)}>
              {uploadSuccess}
            </Alert>
          )}
          
          <Typography variant="body1" gutterBottom>
            Upload CSV file containing Instagram posts/reels data.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            The system will automatically detect whether your CSV contains posts or reels based on the column headers.
            Ensure date columns are in a standard format (YYYY-MM-DD). Empty date fields are allowed.
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              variant="contained"
              component="label"
              startIcon={<CloudUploadIcon />}
              disabled={isUploading}
            >
              Select CSV
              <input
                id="file-upload"
                type="file"
                hidden
                accept=".csv"
                onChange={handleFileChange}
              />
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={!uploadFile || isUploading}
            >
              {isUploading ? <CircularProgress size={24} /> : 'Upload'}
            </Button>
            {uploadFile && <Typography variant="body2">{uploadFile.name}</Typography>}
          </Box>
          
          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleDownloadCSV(undefined)}
            >
              Download CSV
            </Button>
          </Box>
        </Paper>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
          {/* Statistics Card */}
          <Box sx={{ width: { xs: '100%', md: '50%' } }}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2">
                  Data Statistics
                </Typography>
                <Stack direction="row" flexWrap="wrap" spacing={2} sx={{ mt: 1 }}>
                  <Box sx={{ width: { xs: '100%', sm: '45%' } }}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4">{folderStats.totalPosts}</Typography>
                      <Typography variant="body2">Total Posts</Typography>
                    </Paper>
                  </Box>
                  <Box sx={{ width: { xs: '100%', sm: '45%' } }}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4">
                        {folderStats.uniqueUsers}
                      </Typography>
                      <Typography variant="body2">Unique Users</Typography>
                    </Paper>
                  </Box>
                  <Box sx={{ width: { xs: '100%', sm: '45%' } }}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4">
                        {folderStats.avgLikes}
                      </Typography>
                      <Typography variant="body2">Avg. Likes Per Post</Typography>
                    </Paper>
                  </Box>
                  <Box sx={{ width: { xs: '100%', sm: '45%' } }}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4">
                        {folderStats.verifiedAccounts}
                      </Typography>
                      <Typography variant="body2">Verified Accounts</Typography>
                    </Paper>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Box>
        </Stack>

        {/* Data display section - conditional based on folder category */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {currentFolder?.category === 'comments' ? 'Instagram Comments' : 'Instagram Posts'}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            {/* Search field */}
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
              sx={{ width: '300px' }}
            />
            
            {/* Content type filter - only show for posts/reels folders */}
            {currentFolder?.category !== 'comments' && (
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel id="content-type-filter-label">Content Type</InputLabel>
                <Select
                  labelId="content-type-filter-label"
                  id="content-type-filter"
                  value={contentTypeFilter}
                  label="Content Type"
                  onChange={handleContentTypeFilterChange}
                  disabled={isLoading}
                >
                  <MenuItem value="all">All Content Types</MenuItem>
                  <MenuItem value="post">Instagram Posts Only</MenuItem>
                  <MenuItem value="reel">Instagram Reels Only</MenuItem>
                </Select>
                {isLoading && (
                  <CircularProgress
                    size={24}
                    sx={{
                      position: 'absolute',
                      right: 30,
                      top: '50%',
                      marginTop: '-12px',
                    }}
                  />
                )}
              </FormControl>
            )}
          </Box>
          
          {/* Conditional table rendering */}
          <TableContainer>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  {currentFolder?.category === 'comments' ? (
                    /* Comments table headers */
                    <>
                      <TableCell>Comment User</TableCell>
                      <TableCell>Comment</TableCell>
                      <TableCell>Post User</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell align="right">Likes</TableCell>
                      <TableCell align="right">Replies</TableCell>
                      <TableCell>Actions</TableCell>
                    </>
                  ) : (
                    /* Posts table headers */
                    <>
                      <TableCell>User</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Date Posted</TableCell>
                      <TableCell align="right">Likes</TableCell>
                      <TableCell align="right">Comments</TableCell>
                      <TableCell>Actions</TableCell>
                    </>
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <CircularProgress size={40} />
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Loading data...
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : currentFolder?.category === 'comments' ? (
                  /* Comments table body */
                  comments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography>No comments found</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    comments.map((comment) => (
                      <TableRow key={comment.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {comment.comment_user}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                            {comment.comment || 'No comment text'}
                          </Typography>
                        </TableCell>
                        <TableCell>{comment.post_user || 'Unknown'}</TableCell>
                        <TableCell>
                          {comment.comment_date 
                            ? new Date(comment.comment_date).toLocaleDateString() 
                            : 'Unknown'}
                        </TableCell>
                        <TableCell align="right">{comment.likes_number.toLocaleString()}</TableCell>
                        <TableCell align="right">{comment.replies_number.toLocaleString()}</TableCell>
                        <TableCell>
                          <Tooltip title="Open Post">
                            <IconButton 
                              size="small" 
                              onClick={() => window.open(comment.post_url, '_blank')}
                            >
                              <OpenInNewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy link">
                            <IconButton 
                              size="small" 
                              onClick={() => handleCopyLink(comment.post_url)}
                            >
                              <ContentCopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )
                ) : (
                  /* Posts table body */
                  posts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography>No posts found</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    posts.map((post) => (
                      <TableRow key={post.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {post.is_verified && (
                              <Tooltip title="Verified Account">
                                <Chip 
                                  size="small" 
                                  color="primary" 
                                  label="Verified" 
                                  sx={{ mr: 1 }} 
                                />
                              </Tooltip>
                            )}
                            {post.user_posted}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            size="small" 
                            color={post.content_type === 'reel' ? 'secondary' : 'primary'}
                            variant={post.content_type === 'reel' ? 'filled' : 'outlined'}
                            label={post.content_type === 'reel' ? 'Reel' : 'Post'} 
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                            {post.description || 'No description'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {post.date_posted 
                            ? new Date(post.date_posted).toLocaleDateString() 
                            : 'Unknown'}
                        </TableCell>
                        <TableCell align="right">{post.likes.toLocaleString()}</TableCell>
                        <TableCell align="right">{post.num_comments.toLocaleString()}</TableCell>
                        <TableCell>
                          <Tooltip title="Open in Instagram">
                            <IconButton 
                              size="small" 
                              onClick={() => window.open(post.url, '_blank')}
                            >
                              <OpenInNewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy link">
                            <IconButton 
                              size="small" 
                              onClick={() => handleCopyLink(post.url)}
                            >
                              <ContentCopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          {/* Pagination */}
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50, 100]}
            component="div"
            count={totalCount}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      />
    </Container>
  );
};

export default InstagramDataUpload; 
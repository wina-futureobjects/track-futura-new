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
  Tabs,
  Tab,
  Grid,
  Avatar,
  LinearProgress,
  Menu,
  ListItemIcon,
  ListItemText,
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
import AnalyticsIcon from '@mui/icons-material/Analytics';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import GroupIcon from '@mui/icons-material/Group';
import VerifiedIcon from '@mui/icons-material/Verified';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import RefreshIcon from '@mui/icons-material/Refresh';
import GetAppIcon from '@mui/icons-material/GetApp';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import SortIcon from '@mui/icons-material/Sort';
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

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
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
  const [folderLoading, setFolderLoading] = useState(false);
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
  const [tabValue, setTabValue] = useState(0);
  const [sortMenuAnchor, setSortMenuAnchor] = useState<null | HTMLElement>(null);
  const [sortBy, setSortBy] = useState<string>('date_posted');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

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
        setFolderLoading(true);
        // Get project ID from URL params
        const queryParams = new URLSearchParams(location.search);
        const projectId = queryParams.get('project');
        if (!projectId) {
          console.error('Project ID is required but not found in URL params');
          setUploadError('Project ID is missing. Please navigate from the projects page.');
          return;
        }
        
        // Include project parameter in the API request
        const response = await apiFetch(`/api/instagram-data/folders/${folderId}/?project=${projectId}`);
        if (response.ok) {
          const data = await response.json();
          console.log('Folder details response:', data);
          setCurrentFolder(data);
        } else {
          console.error('Failed to fetch folder details:', response.status, response.statusText);
          setUploadError(`Failed to load folder details. Please refresh the page.`);
        }
      } catch (error) {
        console.error('Error fetching folder details:', error);
        setUploadError(`Error loading folder details: ${error instanceof Error ? error.message : 'Unknown error'}`);
      } finally {
        setFolderLoading(false);
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
      // Get project ID from URL params for the server status check
      const queryParams = new URLSearchParams(location.search);
      const projectId = queryParams.get('project');
      
      // Use a simple endpoint to check if server is running
      // Include project parameter if available to avoid 404 from security filtering
      const endpoint = projectId ? `/api/instagram-data/folders/?project=${projectId}` : '/api/instagram-data/folders/';
      const response = await apiFetch(endpoint, { 
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
    
    // Ensure folder details are loaded before upload
    if (folderId && !currentFolder) {
      setUploadError('Folder details are still loading. Please wait a moment and try again.');
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
      
      // Enhanced debugging and validation
      console.log('🔧 Upload Debug Info:');
      console.log('🔧 Folder ID:', folderId);
      console.log('🔧 Current folder object:', currentFolder);
      console.log('🔧 Folder category:', currentFolder?.category);
      console.log('🔧 File being uploaded:', uploadFile?.name);
      
      if (currentFolder?.category === 'comments') {
        uploadEndpoint = '/api/instagram-data/comments/upload_csv/';
        console.log('🔧 DETECTED COMMENTS FOLDER - Using comments endpoint');
      } else {
        console.log('🔧 Using posts endpoint (folder category is not "comments")');
      }
      
      console.log('🔧 Final upload endpoint:', uploadEndpoint);
      
      // Additional safety check
      if (folderId && currentFolder && currentFolder.category === 'comments' && !uploadEndpoint.includes('comments')) {
        throw new Error('ERROR: Comments folder detected but posts endpoint selected. This is a bug!');
      }
      
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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSortMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setSortMenuAnchor(event.currentTarget);
  };

  const handleSortMenuClose = () => {
    setSortMenuAnchor(null);
  };

  const handleSort = (field: string) => {
    const newOrder = sortBy === field && sortOrder === 'desc' ? 'asc' : 'desc';
    setSortBy(field);
    setSortOrder(newOrder);
    handleSortMenuClose();
    // Trigger data refresh with new sorting
    fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      {/* Server status indicator */}
      {serverStatus !== 'online' && (
        <Alert 
          severity={serverStatus === 'checking' ? 'info' : 'error'} 
          sx={{ mb: 2 }}
          icon={serverStatus === 'checking' ? <CircularProgress size={20} /> : undefined}
        >
          {serverStatus === 'checking' 
            ? 'Checking server status...'
            : 'Server connection issue detected. File uploads may fail.'
          }
          {serverStatus === 'offline' && (
            <Button 
              variant="outlined" 
              size="small" 
              sx={{ ml: 2 }}
              onClick={checkServerStatus}
            >
              Retry Connection
            </Button>
          )}
        </Alert>
      )}
      
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h4" component="h1" fontWeight={600} sx={{ mb: 1 }}>
              {currentFolder ? currentFolder.name : 'Instagram Data Management'}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {currentFolder ? currentFolder.description || `${currentFolder.category_display || currentFolder.category} data analysis` : 'Manage and analyze your Instagram data'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={() => {
                fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
                fetchFolderStats();
              }}
            >
              Refresh
            </Button>
            <Button
              variant="outlined"
              startIcon={<GetAppIcon />}
              onClick={() => handleDownloadCSV(undefined)}
            >
              Export
            </Button>
            <Button
              variant="outlined"
              onClick={handleGoToFolders}
            >
              All Folders
            </Button>
          </Box>
        </Box>

        {/* Status Chip */}
        {currentFolder && (
          <Box sx={{ mb: 3 }}>
            <Chip 
              label={`${currentFolder.category_display || currentFolder.category} • Dynamic`} 
              color="success" 
              variant="outlined"
              size="small"
            />
          </Box>
        )}

        {/* Single Summary Box */}
        <Paper sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Data Overview
            </Typography>
            <IconButton
              onClick={handleSortMenuOpen}
              size="small"
              sx={{ color: 'text.secondary' }}
            >
              <MoreVertIcon />
            </IconButton>
            <Menu
              anchorEl={sortMenuAnchor}
              open={Boolean(sortMenuAnchor)}
              onClose={handleSortMenuClose}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
            >
              <MenuItem onClick={() => handleSort('date_posted')}>
                <ListItemIcon>
                  <SortIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Sort by Date</ListItemText>
              </MenuItem>
              <MenuItem onClick={() => handleSort('likes')}>
                <ListItemIcon>
                  <ThumbUpIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Sort by Likes</ListItemText>
              </MenuItem>
              <MenuItem onClick={() => handleSort('user_posted')}>
                <ListItemIcon>
                  <GroupIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Sort by User</ListItemText>
              </MenuItem>
              <MenuItem onClick={() => handleSort('num_comments')}>
                <ListItemIcon>
                  <AnalyticsIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Sort by Comments</ListItemText>
              </MenuItem>
            </Menu>
          </Box>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 4 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <AnalyticsIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h4" fontWeight={600}>
                  {folderStats.totalPosts.toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total {currentFolder?.category === 'comments' ? 'Comments' : 'Posts'}
              </Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <GroupIcon sx={{ color: 'secondary.main', mr: 1 }} />
                <Typography variant="h4" fontWeight={600}>
                  {folderStats.uniqueUsers.toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Unique Users
              </Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <ThumbUpIcon sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h4" fontWeight={600}>
                  {folderStats.avgLikes.toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Avg. Engagement
              </Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <VerifiedIcon sx={{ color: 'warning.main', mr: 1 }} />
                <Typography variant="h4" fontWeight={600}>
                  {folderStats.verifiedAccounts.toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Verified Accounts
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>

      {/* Tabs Section */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="data management tabs">
            <Tab label="Data Overview" {...a11yProps(0)} />
            <Tab label="Upload & Management" {...a11yProps(1)} />
            <Tab label="Analytics" {...a11yProps(2)} />
          </Tabs>
        </Box>
        
        {/* Tab Panel 0: Data Overview */}
        <TabPanel value={tabValue} index={0}>
          {/* Search and Filter Controls */}
          <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
            <TextField
              placeholder="Search users, content, or hashtags..."
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
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      edge="end"
                      onClick={handleSortMenuOpen}
                      size="small"
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ flexGrow: 1, maxWidth: 400 }}
            />
            
            {currentFolder?.category !== 'comments' && (
              <FormControl size="small" sx={{ minWidth: 180 }}>
                <InputLabel>Content Type</InputLabel>
                <Select
                  value={contentTypeFilter}
                  label="Content Type"
                  onChange={handleContentTypeFilterChange}
                  disabled={isLoading}
                >
                  <MenuItem value="all">All Content</MenuItem>
                  <MenuItem value="post">Posts Only</MenuItem>
                  <MenuItem value="reel">Reels Only</MenuItem>
                </Select>
              </FormControl>
            )}
            
            <IconButton onClick={() => fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter)}>
              <FilterListIcon />
            </IconButton>
          </Box>

          {/* Data Table */}
          <TableContainer sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow sx={{ backgroundColor: 'grey.50' }}>
                  {currentFolder?.category === 'comments' ? (
                    <>
                      <TableCell sx={{ fontWeight: 600 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          Comment User
                          <IconButton size="small" onClick={handleSortMenuOpen}>
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Comment</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Post User</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          Date
                          <IconButton size="small" onClick={handleSortMenuOpen}>
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          Likes
                          <IconButton size="small" onClick={handleSortMenuOpen}>
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Replies</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                    </>
                  ) : (
                    <>
                      <TableCell sx={{ fontWeight: 600 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          User
                          <IconButton size="small" onClick={handleSortMenuOpen}>
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Content</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          Date Posted
                          <IconButton size="small" onClick={handleSortMenuOpen}>
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          Likes
                          <IconButton size="small" onClick={handleSortMenuOpen}>
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          Comments
                          <IconButton size="small" onClick={handleSortMenuOpen}>
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                    </>
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <CircularProgress size={40} />
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Loading data...
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : currentFolder?.category === 'comments' ? (
                  comments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                        <Typography color="text.secondary">No comments found</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    comments.map((comment) => (
                      <TableRow key={comment.id} hover sx={{ '&:hover': { backgroundColor: 'grey.50' } }}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ width: 32, height: 32, mr: 2, fontSize: '0.875rem' }}>
                              {comment.comment_user.charAt(0).toUpperCase()}
                            </Avatar>
                            <Typography variant="body2" fontWeight={500}>
                              {comment.comment_user}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 300 }} noWrap>
                            {comment.comment || 'No comment text'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{comment.post_user || 'Unknown'}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {comment.comment_date 
                              ? new Date(comment.comment_date).toLocaleDateString() 
                              : 'Unknown'}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">{comment.likes_number.toLocaleString()}</Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">{comment.replies_number.toLocaleString()}</Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <Tooltip title="Open Post">
                              <IconButton 
                                size="small" 
                                onClick={() => window.open(comment.post_url, '_blank')}
                              >
                                <OpenInNewIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Copy Link">
                              <IconButton 
                                size="small" 
                                onClick={() => handleCopyLink(comment.post_url)}
                              >
                                <ContentCopyIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                  )
                ) : (
                  posts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                        <Typography color="text.secondary">No posts found</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    posts.map((post) => (
                      <TableRow key={post.id} hover sx={{ '&:hover': { backgroundColor: 'grey.50' } }}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ width: 32, height: 32, mr: 2, fontSize: '0.875rem' }}>
                              {post.user_posted.charAt(0).toUpperCase()}
                            </Avatar>
                            <Box>
                              <Typography variant="body2" fontWeight={500}>
                                {post.user_posted}
                              </Typography>
                              {post.is_verified && (
                                <Chip 
                                  size="small" 
                                  color="primary" 
                                  label="Verified" 
                                  sx={{ mt: 0.5, height: 16, fontSize: '0.75rem' }}
                                />
                              )}
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            size="small" 
                            color={post.content_type === 'reel' ? 'secondary' : 'primary'}
                            variant="outlined"
                            label={post.content_type === 'reel' ? 'Reel' : 'Post'} 
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 300 }} noWrap>
                            {post.description || 'No description'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {post.date_posted 
                              ? new Date(post.date_posted).toLocaleDateString() 
                              : 'Unknown'}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight={500}>
                            {post.likes.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {post.num_comments.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <Tooltip title="Open in Instagram">
                              <IconButton 
                                size="small" 
                                onClick={() => window.open(post.url, '_blank')}
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
                          </Box>
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
            sx={{ borderTop: '1px solid', borderColor: 'divider' }}
          />
        </TabPanel>

        {/* Tab Panel 1: Upload & Management */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
            <Box sx={{ flex: 2 }}>
              <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <CloudUploadIcon sx={{ mr: 1 }} />
                    Upload CSV Data
                  </Typography>
                  
                  {currentFolder && currentFolder.category && (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      <strong>Current folder: {currentFolder.category_display || currentFolder.category}</strong>
                      <br />
                      {currentFolder.category === 'comments' 
                        ? 'Upload comment CSV files here.'
                        : 'Upload posts/reels CSV files here.'
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
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Upload CSV files containing Instagram data. The system automatically detects content type 
                    based on column headers. Ensure dates are in standard format (YYYY-MM-DD).
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<CloudUploadIcon />}
                      disabled={isUploading}
                    >
                      Select CSV File
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
                      onClick={handleUpload}
                      disabled={!uploadFile || isUploading || folderLoading || (folderId ? !currentFolder : false)}
                      startIcon={isUploading ? <CircularProgress size={20} /> : undefined}
                    >
                      {isUploading ? 'Uploading...' : folderLoading ? 'Loading folder...' : 'Upload'}
                    </Button>
                    {uploadFile && (
                      <Typography variant="body2" color="text.secondary">
                        {uploadFile.name}
                      </Typography>
                    )}
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownloadCSV(undefined)}
                  >
                    Download Current Data as CSV
                  </Button>
                </CardContent>
              </Card>
            </Box>
            
            <Box sx={{ flex: 1 }}>
              <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Stack spacing={2}>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleDownloadCSV('post')}
                      disabled={currentFolder?.category === 'comments'}
                    >
                      Download Posts Only
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleDownloadCSV('reel')}
                      disabled={currentFolder?.category === 'comments'}
                    >
                      Download Reels Only
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<RefreshIcon />}
                      onClick={() => {
                        fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
                        fetchFolderStats();
                      }}
                    >
                      Refresh Data
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Box>
          </Box>
        </TabPanel>

        {/* Tab Panel 2: Analytics */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Analytics Overview
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Advanced analytics features coming soon. Current data insights are available in the overview cards above.
          </Typography>
          
          {/* Progress bars for different metrics */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Engagement Distribution
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    High Engagement Posts
                  </Typography>
                  <LinearProgress variant="determinate" value={75} sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Medium Engagement Posts
                  </Typography>
                  <LinearProgress variant="determinate" value={45} sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Low Engagement Posts
                  </Typography>
                  <LinearProgress variant="determinate" value={20} sx={{ height: 8, borderRadius: 4 }} />
                </Box>
              </CardContent>
            </Card>
            
            <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Content Performance
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Posts vs Reels Ratio
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={60} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color="secondary" 
                  />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Verified Account Content
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={30} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color="success" 
                  />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Average Response Time
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={85} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color="warning" 
                  />
                </Box>
              </CardContent>
            </Card>
          </Box>
        </TabPanel>
      </Paper>

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
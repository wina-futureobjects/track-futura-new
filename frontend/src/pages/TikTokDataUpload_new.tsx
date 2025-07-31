import { useState, useEffect, ChangeEvent, useCallback } from 'react';
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
  Avatar,
  LinearProgress,
  Menu,
  ListItemIcon,
  ListItemText,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemButton,
  ListItemAvatar,
  Badge,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
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
import DateRangeIcon from '@mui/icons-material/DateRange';
import ChatIcon from '@mui/icons-material/Chat';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import WebhookIcon from '@mui/icons-material/Webhook';
import SettingsIcon from '@mui/icons-material/Settings';
import NotificationsIcon from '@mui/icons-material/Notifications';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { apiFetch } from '../utils/api';

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

interface TikTokComment {
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
  avgComments: number;
  verifiedAccounts: number;
}

// BrightData Webhook Integration Interfaces - Simplified for receiving data only
interface WebhookStatus {
  isActive: boolean;
  lastUpdate: string | null;
  totalRequests: number;
  successRate: number;
  averageResponseTime: number;
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

const TikTokDataUpload = () => {
  const { folderId, organizationId, projectId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Update state to handle single file upload
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [folderLoading, setFolderLoading] = useState(false);
  const [posts, setPosts] = useState<TikTokPost[]>([]);
  const [comments, setComments] = useState<TikTokComment[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredPosts, setFilteredPosts] = useState<TikTokPost[]>([]);
  const [filteredComments, setFilteredComments] = useState<TikTokComment[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentFolder, setCurrentFolder] = useState<Folder | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [folderStats, setFolderStats] = useState<FolderStats>({
    totalPosts: 0,
    uniqueUsers: 0,
    avgLikes: 0,
    avgComments: 0,
    verifiedAccounts: 0
  });
  // Remove upload tab state as we're using single upload now
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('all');
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [tabValue, setTabValue] = useState(0);
  const [sortMenuAnchor, setSortMenuAnchor] = useState<null | HTMLElement>(null);
  const [sortBy, setSortBy] = useState<string>('date_posted');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // Filter state
  const [showFilters, setShowFilters] = useState(false);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [minLikes, setMinLikes] = useState<string>('');
  const [maxLikes, setMaxLikes] = useState<string>('');

  // BrightData Webhook Integration State - Simplified for receiving data only
  const [webhookStatus, setWebhookStatus] = useState<WebhookStatus>({
    isActive: false,
    lastUpdate: null,
    totalRequests: 0,
    successRate: 0,
    averageResponseTime: 0
  });
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  const [webhookLoading, setWebhookLoading] = useState(false);

  // Fetch Instagram posts/comments with pagination
  const fetchPosts = async (pageNumber = 0, pageSize = 10, searchTerm = '', contentType = '', useFilters = false) => {
    try {
      setIsLoading(true);
      
      // Clear existing data immediately to show loading state
      setPosts([]);
      setComments([]);
      setFilteredPosts([]);
      setFilteredComments([]);
      setTotalCount(0);
      
      if (!folderId) {
        console.log('No folder ID provided, skipping data fetch');
        return;
      }
      
      console.log(`📡 Fetching data for folder ${folderId}, page ${pageNumber + 1}, search: "${searchTerm}", content type: "${contentType}"`);
      console.log(`📁 Current folder category: ${currentFolder?.category}`);
      
      const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
      const projectParam = projectId ? `&project=${projectId}` : '';
      
      // Add sorting parameters
      const sortParams = `&sort_by=${sortBy}&sort_order=${sortOrder}`;
      
      // Add filter parameters if useFilters is true
      const filterParams = useFilters ? [
        startDate ? `&start_date=${startDate}` : '',
        endDate ? `&end_date=${endDate}` : '',
        minLikes ? `&min_likes=${minLikes}` : '',
        maxLikes ? `&max_likes=${maxLikes}` : ''
      ].join('') : '';
      
      // Check folder category first and call appropriate endpoint
      if (currentFolder?.category === 'comments') {
        console.log('🔄 Comments folder detected - using comments endpoint directly');
        
        // For comments folders, use the folder contents endpoint or direct comments API
        const commentsApiUrl = `/api/tiktok-data/folders/${folderId}/contents/?page=${pageNumber + 1}&page_size=${pageSize}${searchParam}${projectParam}${filterParams}${sortParams}`;
        console.log('🔄 Fetching comments from:', commentsApiUrl);
        
        const response = await apiFetch(commentsApiUrl);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ Comments endpoint error:', response.status, errorText);
          throw new Error(`Failed to fetch comments: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📝 Comments endpoint response:', data);
        console.log('📝 Comments response structure:', {
          hasResults: 'results' in data,
          hasCount: 'count' in data,
          resultsLength: data.results?.length || 0,
          totalCount: data.count || 0,
          category: data.category
        });
        
        if (data && typeof data === 'object') {
          const results = data.results || [];
          console.log('✅ Setting comments data with', results.length, 'items');
          console.log('📋 First few comments:', results.slice(0, 2));
          
          setComments(results);
          setFilteredComments(results);
          setPosts([]);
          setFilteredPosts([]);
          setTotalCount(data.count || results.length);
          
          console.log(`✅ Successfully loaded ${results.length} comments, total count: ${data.count || results.length}`);
        } else {
          console.error('❌ Comments endpoint returned unexpected data structure:', data);
          throw new Error('Comments endpoint returned unexpected data format');
        }
        
      } else {
        // For posts/reels folders, use the posts endpoint
        console.log('📊 Posts/reels folder detected - using posts endpoint');
        
        const contentTypeParam = contentType && contentType !== 'all' ? `&content_type=${contentType}` : '';
        const folderParam = `folder_id=${folderId}`;
        
        const postsApiUrl = `/api/tiktok-data/posts/?${folderParam}&page=${pageNumber + 1}&page_size=${pageSize}${searchParam}${contentTypeParam}${projectParam}${filterParams}${sortParams}`;
        console.log('🚀 Fetching posts from:', postsApiUrl);
        
        const response = await apiFetch(postsApiUrl);
        console.log('📥 Posts API response status:', response.status, 'OK:', response.ok);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ Posts endpoint error:', response.status, errorText);
          throw new Error(`Failed to fetch posts: ${response.status}`);
        }
        
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
          
          console.log(`✅ Successfully loaded ${results.length} posts, total count: ${data.count || results.length}`);
        } else {
          console.error('❌ Posts endpoint returned data without results structure:', data);
          throw new Error('Posts endpoint returned unexpected data format');
        }
      }
      
    } catch (error) {
      console.error('❌ Error fetching data:', error);
      // Keep the empty state but show an error to the user
      setPosts([]);
      setComments([]);
      setFilteredPosts([]);
      setFilteredComments([]);
      setTotalCount(0);
      
      // Set error state for user feedback
      setUploadError(error instanceof Error ? error.message : 'Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch folder details if folderId is present
  const fetchFolderDetails = async () => {
    if (folderId) {
      try {
        setFolderLoading(true);
        // Get project ID from URL path params instead of query params
        if (!projectId) {
          console.error('Project ID is required but not found in URL params');
          setUploadError('Project ID is missing. Please navigate from the projects page.');
          return;
        }
        
        // Include project parameter in the API request
        const response = await apiFetch(`/api/tiktok-data/folders/${folderId}/?project=${projectId}`);
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
      const projectParam = projectId ? `&project=${projectId}` : '';
      
      // Use different endpoint based on folder category
      if (currentFolder?.category === 'comments') {
        console.log('📈 Fetching comments folder stats...');
        const statsApiUrl = `/api/tiktok-data/comments/stats/?${folderParam}${projectParam}`;
        console.log('📈 Fetching comments stats from:', statsApiUrl);
        
        const response = await apiFetch(statsApiUrl);
        console.log('📈 Comments stats API response status:', response.status, 'OK:', response.ok);
        
        if (!response.ok) {
          throw new Error('Failed to fetch comments folder statistics');
        }
        
        const data = await response.json();
        console.log('📈 Comments stats API response data:', data);
        
        setFolderStats({
          totalPosts: data.totalComments || 0, // This represents total comments for comments folders
          uniqueUsers: data.uniqueCommenters || 0,
          avgLikes: Math.round(data.avgLikes || 0),
          avgComments: Math.round(data.avgReplies || 0), // For comments, use avgReplies as avgComments
          verifiedAccounts: 0 // Comments don't have verified account info
        });
        
        console.log('📈 Set comments stats:', {
          totalComments: data.totalComments || 0,
          uniqueCommenters: data.uniqueCommenters || 0,
          avgLikes: data.avgLikes || 0
        });
        
      } else {
        // For posts/reels folders, use the posts stats endpoint
        console.log('📈 Fetching posts folder stats...');
        const statsApiUrl = `/api/tiktok-data/posts/stats/?${folderParam}${projectParam}`;
        console.log('📈 Fetching posts stats from:', statsApiUrl);
        
        const response = await apiFetch(statsApiUrl);
        console.log('📈 Posts stats API response status:', response.status, 'OK:', response.ok);
        
        if (!response.ok) {
          throw new Error('Failed to fetch posts folder statistics');
        }
        
        const data = await response.json();
        console.log('📈 Posts stats API response data:', data);
        
        setFolderStats({
          totalPosts: data.totalPosts || 0,
          uniqueUsers: data.uniqueUsers || 0,
          avgLikes: Math.round(data.avgLikes || 0),
          avgComments: Math.round(data.avgComments || 0), // For posts, use avgComments
          verifiedAccounts: data.verifiedAccounts || 0
        });
        
        console.log('📈 Set posts stats:', {
          totalPosts: data.totalPosts || 0,
          uniqueUsers: data.uniqueUsers || 0,
          avgLikes: data.avgLikes || 0,
          verifiedAccounts: data.verifiedAccounts || 0
        });
      }
    } catch (error) {
      console.error('Error fetching folder statistics:', error);
    }
  };

  // Check server status
  const checkServerStatus = async () => {
    try {
      // Use project ID from URL path params for the server status check
      // Include project parameter if available to avoid 404 from security filtering
      const endpoint = projectId ? `/api/tiktok-data/folders/?project=${projectId}` : '/api/tiktok-data/folders/';
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

  // BrightData Webhook Integration Functions
  const fetchWebhookStatus = async () => {
    try {
      setWebhookLoading(true);
      const response = await apiFetch('/api/brightdata/webhook-metrics/');
      
      if (response.ok) {
        const data = await response.json();
        setWebhookStatus({
          isActive: data.is_active || false,
          lastUpdate: data.last_update,
          totalRequests: data.total_requests || 0,
          successRate: data.success_rate || 0,
          averageResponseTime: data.average_response_time || 0
        });
      }
    } catch (error) {
      console.error('Error fetching webhook status:', error);
    } finally {
      setWebhookLoading(false);
    }
  };

  const startAutoRefresh = useCallback(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
    
    const interval = setInterval(() => {
      fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter, Boolean(startDate || endDate || minLikes || maxLikes));
      fetchFolderStats();
      fetchWebhookStatus();
    }, 30000); // Refresh every 30 seconds
    
    setRefreshInterval(interval);
  }, [page, rowsPerPage, searchTerm, contentTypeFilter, startDate, endDate, minLikes, maxLikes]);

  const stopAutoRefresh = useCallback(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }
  }, [refreshInterval]);

  // Effect to handle auto-refresh
  useEffect(() => {
    if (autoRefresh) {
      startAutoRefresh();
    } else {
      stopAutoRefresh();
    }

    return () => {
      stopAutoRefresh();
    };
  }, [autoRefresh, startAutoRefresh, stopAutoRefresh]);

  // Effect to fetch webhook data on component mount
  useEffect(() => {
    if (folderId) {
      fetchWebhookStatus();
    }
  }, [folderId]);

  // Check server status on component mount
  useEffect(() => {
    checkServerStatus();
  }, []);

  // Initial folder details load
  useEffect(() => {
    if (folderId) {
      fetchFolderDetails();
    }
  }, [folderId]); // Only re-fetch when folder ID changes
  
  // Fetch data after folder details are loaded
  useEffect(() => {
    if (folderId && currentFolder) {
      console.log('📁 Folder details loaded, now fetching data...');
      const hasFilterValues = Boolean(startDate || endDate || minLikes || maxLikes);
      fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter, hasFilterValues);
      fetchFolderStats();
    }
  }, [folderId, currentFolder]); // Re-fetch when folder ID or folder details change
  
  // This effect handles pagination, search, content type filter, sorting, and filtering changes
  useEffect(() => {
    // Only fetch if we have both folderId and currentFolder loaded
    if (folderId && currentFolder) {
      // Check if there are actual filter values to apply
      const hasFilterValues = Boolean(startDate || endDate || minLikes || maxLikes);
      fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter, hasFilterValues);
    }
  }, [page, rowsPerPage, searchTerm, contentTypeFilter, sortBy, sortOrder, showFilters, startDate, endDate, minLikes, maxLikes, currentFolder]);

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
      let uploadEndpoint = '/api/tiktok-data/posts/upload_csv/';
      
      // Enhanced debugging and validation
      console.log('🔧 Upload Debug Info:');
      console.log('🔧 Organization ID:', organizationId);
      console.log('🔧 Project ID:', projectId);
      console.log('🔧 Folder ID:', folderId);
      console.log('🔧 Current folder object:', currentFolder);
      console.log('🔧 Folder category:', currentFolder?.category);
      console.log('🔧 File being uploaded:', uploadFile?.name);
      console.log('🔧 File size:', uploadFile?.size);
      
      if (currentFolder?.category === 'comments') {
        uploadEndpoint = '/api/tiktok-data/comments/upload_csv/';
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

        console.log('🔧 Upload response status:', response.status);
        console.log('🔧 Upload response headers:', Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
          const errorText = await response.text();
          console.log('🔧 Upload error response text:', errorText);
          
          let errorData;
          try {
            errorData = JSON.parse(errorText);
          } catch {
            errorData = { error: errorText };
          }
          
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
        console.log('🔧 Upload success response:', data);
        
        let successMessage = `${data.message}`;
        
        if (data.detected_content_type) {
          successMessage += ` Content type detected: ${data.detected_content_type}`;
        }
        
        setUploadSuccess(successMessage);
        
        // Reset pagination to first page to see new data
        setPage(0);
        
        // Clear any existing search/filters to show all new data
        setSearchTerm('');
        setContentTypeFilter('all');
        
        // Add a small delay to ensure backend has finished processing
        setTimeout(async () => {
          // Clear any previous error states
          setUploadError(null);
          
          // Refresh the data in the proper order
          await fetchFolderDetails(); // Refresh folder details first
          await fetchPosts(0, rowsPerPage, '', 'all', false); // Reset to page 0 with no filters
          fetchFolderStats(); // Update statistics
          
          // Clear success message after 5 seconds
          setTimeout(() => {
            setUploadSuccess(null);
          }, 5000);
        }, 500); // 500ms delay to ensure backend processing is complete
        
        // Reset file input
        setUploadFile(null);
        
        // Reset file input element
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
      } catch (networkError) {
        console.error('Network error:', networkError);
        console.log('🔧 Network error details:', {
          name: networkError instanceof Error ? networkError.name : 'Unknown',
          message: networkError instanceof Error ? networkError.message : String(networkError),
          stack: networkError instanceof Error ? networkError.stack : undefined
        });
        
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
      // Add project parameter if available for consistency
      const projectParam = projectId ? `&project=${projectId}` : '';
      
      const response = await apiFetch(
        `/api/tiktok-data/posts/download_csv/?${folderParam}${contentTypeParam}${projectParam}`,
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
      let filename = 'tiktok_data.csv';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      } else {
        // Fallback filename based on content type
        filename = contentType ? `tiktok_${contentType}s.csv` : 'tiktok_data.csv';
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
    // Check if we're on the new organized URL structure (with org and project IDs)
    if (organizationId && projectId) {
      navigate(`/organizations/${organizationId}/projects/${projectId}/instagram-folders`);
    } else {
      // Fallback to check if we're on the legacy URL structure with path params
      const match = location.pathname.match(/\/organizations\/(\d+)\/projects\/(\d+)\//);
      
      if (match) {
        const [, orgId, projId] = match;
        navigate(`/organizations/${orgId}/projects/${projId}/instagram-folders`);
      } else {
        // Legacy fallback - try query parameters
        const queryParams = new URLSearchParams(location.search);
        const projectIdFromQuery = queryParams.get('project');
        
        if (projectIdFromQuery) {
          navigate(`/instagram-folders?project=${projectIdFromQuery}`);
        } else {
          navigate('/instagram-folders');
        }
      }
    }
  };

  const handleBackNavigation = () => {
    // Use the same logic as handleGoToFolders for back navigation
    handleGoToFolders();
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
    
    // Map frontend field names to backend field names based on folder category
    let backendField = field;
    if (currentFolder?.category === 'comments') {
      // Map comment-specific field names
      const fieldMapping: { [key: string]: string } = {
        'likes': 'likes_number',
        'num_comments': 'replies_number',
        'user_posted': 'comment_user',
        'date_posted': 'comment_date'
      };
      backendField = fieldMapping[field] || field;
    }
    
    setSortBy(backendField);
    setSortOrder(newOrder);
    handleSortMenuClose();
    // Trigger data refresh with new sorting and current filters
    const hasFilterValues = Boolean(startDate || endDate || minLikes || maxLikes);
    fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter, hasFilterValues);
  };

  // Filter handlers
  const handleFilterToggle = () => {
    setShowFilters(!showFilters);
  };

  const handleApplyFilters = () => {
    // Check if there are actual filter values to apply
    const hasFilterValues = Boolean(startDate || endDate || minLikes || maxLikes);
    fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter, hasFilterValues);
  };

  const handleClearFilters = () => {
    setStartDate('');
    setEndDate('');
    setMinLikes('');
    setMaxLikes('');
    // Trigger data refresh with cleared filters
    const hasFilterValues = Boolean(startDate || endDate || minLikes || maxLikes);
    fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter, hasFilterValues);
  };

  // Webhook Integration Event Handlers
  const handleRefreshWebhookData = () => {
    fetchWebhookStatus();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {currentFolder && (
              <IconButton
                onClick={handleBackNavigation}
                sx={{ 
                  color: 'primary.main',
                  '&:hover': { 
                    backgroundColor: 'primary.light',
                    color: 'white'
                  }
                }}
                size="small"
              >
                <ArrowBackIcon />
              </IconButton>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box>
                <Typography variant="h4" component="h1" fontWeight={600} sx={{ mb: 1 }}>
                  {currentFolder ? currentFolder.name : 'TikTok Data Management'}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {currentFolder ? currentFolder.description || `${currentFolder.category_display || currentFolder.category} data analysis` : 'Manage and analyze your TikTok data'}
                </Typography>
              </Box>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {/* Auto-refresh Toggle */}
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={() => setAutoRefresh(!autoRefresh)}
                  size="small"
                />
              }
              label="Auto-refresh"
              sx={{ ml: 1 }}
            />
            
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={() => {
                // Clear any error states
                setUploadError(null);
                setUploadSuccess(null);
                
                // Reset page to 0 to ensure we see all data
                setPage(0);
                
                // Refresh all data
                const hasFilterValues = Boolean(startDate || endDate || minLikes || maxLikes);
                fetchPosts(0, rowsPerPage, searchTerm, contentTypeFilter, hasFilterValues);
                fetchFolderStats();
                fetchFolderDetails();
              }}
              disabled={isLoading}
            >
              {isLoading ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<GetAppIcon />}
              onClick={() => handleDownloadCSV(undefined)}
            >
              Export CSV
            </Button>
          </Box>
        </Box>

        {/* Status Chips */}
        {currentFolder && (
          <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
            <Chip 
              label={`${currentFolder.category_display || currentFolder.category} • Dynamic`} 
              color="success" 
              variant="outlined"
              size="small"
            />
            {/* Webhook Status Label */}
            <Chip
              icon={<WebhookIcon />}
              label={webhookStatus.isActive ? 'Webhook Active' : 'Webhook Inactive'}
              color={webhookStatus.isActive ? 'success' : 'default'}
              variant="outlined"
              size="small"
            />
          </Box>
        )}

        {/* Single Summary Box */}
        <Paper sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h6" fontWeight={600}>
                Data Overview
              </Typography>
              <Chip 
                label={`Sorted by ${sortBy} (${sortOrder})`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>
        

          </Box>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr 1fr' }, gap: 4 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <AnalyticsIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h4" fontWeight={600}>
                  {folderStats.totalPosts.toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total                   {currentFolder?.category === 'comments'
                  ? 'Comments'
                  : currentFolder?.category === 'videos'
                  ? 'Videos'
                  : 'Posts'}
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
                <ChatIcon sx={{ color: 'info.main', mr: 1 }} />
                <Typography variant="h4" fontWeight={600}>
                  {folderStats.avgComments.toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Avg. {currentFolder?.category === 'comments' ? 'Replies' : 'Comments'}
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="data management tabs">
              <Tab label="Data Overview" {...a11yProps(0)} />
              <Tab label="Upload & Management" {...a11yProps(1)} />
              <Tab label="Webhook Status" {...a11yProps(2)} />
            </Tabs>
          </Box>
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
              }}
              sx={{ flexGrow: 1, maxWidth: 400 }}
            />
            
            {/* Sort Button */}
            <Button
              variant="outlined"
              startIcon={<SortIcon />}
              onClick={handleSortMenuOpen}
              size="small"
              sx={{ minWidth: 140 }}
            >
              {sortBy === (currentFolder?.category === 'comments' ? 'comment_date' : 'date_posted') 
                ? `Date (${sortOrder === 'asc' ? 'Asc' : 'Desc'})`
                : sortBy === (currentFolder?.category === 'comments' ? 'likes_number' : 'likes')
                ? `Likes (${sortOrder === 'asc' ? 'Asc' : 'Desc'})`
                : sortBy === (currentFolder?.category === 'comments' ? 'comment_user' : 'user_posted')
                ? `${currentFolder?.category === 'comments' ? 'Commenter' : 'User'} (${sortOrder === 'asc' ? 'Asc' : 'Desc'})`
                : sortBy === (currentFolder?.category === 'comments' ? 'replies_number' : 'num_comments')
                ? `${currentFolder?.category === 'comments' ? 'Replies' : 'Comments'} (${sortOrder === 'asc' ? 'Asc' : 'Desc'})`
                : `Sort (${sortOrder === 'asc' ? 'Asc' : 'Desc'})`
              }
            </Button>
            
            <Tooltip title="Filter data">
              <IconButton onClick={handleFilterToggle}>
                <FilterListIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Sort Menu */}
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
            <MenuItem onClick={() => handleSort('date_posted')} selected={sortBy === (currentFolder?.category === 'comments' ? 'comment_date' : 'date_posted')}>
              <ListItemIcon>
                <SortIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>
                Sort by {currentFolder?.category === 'comments' ? 'Comment Date' : 'Date'}
                {sortBy === (currentFolder?.category === 'comments' ? 'comment_date' : 'date_posted') && (
                  <Typography variant="caption" color="primary" sx={{ ml: 1 }}>
                    ({sortOrder})
                  </Typography>
                )}
              </ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleSort('likes')} selected={sortBy === (currentFolder?.category === 'comments' ? 'likes_number' : 'likes')}>
              <ListItemIcon>
                <ThumbUpIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>
                Sort by Likes
                {sortBy === (currentFolder?.category === 'comments' ? 'likes_number' : 'likes') && (
                  <Typography variant="caption" color="primary" sx={{ ml: 1 }}>
                    ({sortOrder})
                  </Typography>
                )}
              </ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleSort('user_posted')} selected={sortBy === (currentFolder?.category === 'comments' ? 'comment_user' : 'user_posted')}>
              <ListItemIcon>
                <GroupIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>
                Sort by {currentFolder?.category === 'comments' ? 'Commenter' : 'User'}
                {sortBy === (currentFolder?.category === 'comments' ? 'comment_user' : 'user_posted') && (
                  <Typography variant="caption" color="primary" sx={{ ml: 1 }}>
                    ({sortOrder})
                  </Typography>
                )}
              </ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleSort('num_comments')} selected={sortBy === (currentFolder?.category === 'comments' ? 'replies_number' : 'num_comments')}>
              <ListItemIcon>
                <AnalyticsIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>
                Sort by {currentFolder?.category === 'comments' ? 'Replies' : 'Comments'}
                {sortBy === (currentFolder?.category === 'comments' ? 'replies_number' : 'num_comments') && (
                  <Typography variant="caption" color="primary" sx={{ ml: 1 }}>
                    ({sortOrder})
                  </Typography>
                )}
              </ListItemText>
            </MenuItem>
          </Menu>

          {/* Filter Controls */}
          <Collapse in={showFilters}>
            <Paper sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <FilterListIcon sx={{ mr: 1 }} />
                Filter Options
              </Typography>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 2 }}>
                {/* Date Range Filters */}
                <TextField
                  label="Start Date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  size="small"
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <DateRangeIcon />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  label="End Date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  size="small"
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <DateRangeIcon />
                      </InputAdornment>
                    ),
                  }}
                />
                
                {/* Likes Range Filters */}
                <TextField
                  label="Min Likes"
                  type="number"
                  value={minLikes}
                  onChange={(e) => setMinLikes(e.target.value)}
                  size="small"
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <ThumbUpIcon />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  label="Max Likes"
                  type="number"
                  value={maxLikes}
                  onChange={(e) => setMaxLikes(e.target.value)}
                  size="small"
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <ThumbUpIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <Button
                  variant="contained"
                  onClick={handleApplyFilters}
                  disabled={isLoading}
                  startIcon={<FilterListIcon />}
                >
                  Apply Filters
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleClearFilters}
                  disabled={isLoading}
                >
                  Clear Filters
                </Button>
              </Box>
            </Paper>
          </Collapse>

          {/* Data Table */}
          <TableContainer sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow sx={{ backgroundColor: 'grey.50' }}>
                  {currentFolder?.category === 'comments' ? (
                    <>
                      <TableCell sx={{ fontWeight: 600 }}>Comment User</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Comment</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Post User</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Likes</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Replies</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                    </>
                  ) : (
                    <>
                      <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Content</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Date Posted</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Likes</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Comments</TableCell>
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
                            color={post.content_type === 'video' ? 'secondary' : 'primary'}
                            variant="outlined"
                            label={post.content_type === 'video' ? 'Video' : 'Post'} 
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
                            <Tooltip title="Open in TikTok">
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
                        : 'Upload posts/videos CSV files here.'
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
                    Upload CSV files containing TikTok data. The system automatically detects content type 
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
                      onClick={() => handleDownloadCSV('video')}
                      disabled={currentFolder?.category === 'comments'}
                    >
                      Download Videos Only
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<RefreshIcon />}
                      onClick={() => {
                        // Clear any error states
                        setUploadError(null);
                        setUploadSuccess(null);
                        
                        // Reset page to 0 to ensure we see all data
                        setPage(0);
                        
                        // Refresh all data
                        const hasFilterValues = Boolean(startDate || endDate || minLikes || maxLikes);
                        fetchPosts(0, rowsPerPage, searchTerm, contentTypeFilter, hasFilterValues);
                        fetchFolderStats();
                        fetchFolderDetails();
                      }}
                      disabled={isLoading}
                    >
                      {isLoading ? 'Refreshing...' : 'Refresh'}
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Box>
          </Box>
        </TabPanel>

        {/* Tab Panel 2: Webhook Status */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Webhook Status & Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Monitor the status of your BrightData webhook integration and view detailed metrics. Data is automatically received and stored in this folder.
          </Typography>
          
          {/* Webhook Status Overview */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 3, mb: 4 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <WebhookIcon color={webhookStatus.isActive ? 'success' : 'disabled'} sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Webhook Status</Typography>
                </Box>
                <Typography variant="h4" color={webhookStatus.isActive ? 'success.main' : 'text.secondary'}>
                  {webhookStatus.isActive ? 'Active' : 'Inactive'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Last Update: {webhookStatus.lastUpdate ? formatDate(webhookStatus.lastUpdate) : 'Never'}
                </Typography>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <NotificationsIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Total Requests</Typography>
                </Box>
                <Typography variant="h4">{webhookStatus.totalRequests}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Success Rate: {webhookStatus.successRate.toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Response Time</Typography>
                </Box>
                <Typography variant="h4">{webhookStatus.averageResponseTime.toFixed(2)}s</Typography>
                <Typography variant="body2" color="text.secondary">
                  Average processing time
                </Typography>
              </CardContent>
            </Card>
          </Box>

          {/* Detailed Webhook Information */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Webhook Endpoint</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                  /api/brightdata/webhook/
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Status: {webhookStatus.isActive ? 'Active' : 'Inactive'}
                </Typography>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Total Requests:</Typography>
                  <Typography variant="body2" fontWeight="bold">{webhookStatus.totalRequests}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Success Rate:</Typography>
                  <Typography variant="body2" fontWeight="bold">{webhookStatus.successRate.toFixed(1)}%</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Avg Response Time:</Typography>
                  <Typography variant="body2" fontWeight="bold">{webhookStatus.averageResponseTime.toFixed(2)}s</Typography>
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={handleRefreshWebhookData}
              disabled={webhookLoading}
            >
              {webhookLoading ? 'Refreshing...' : 'Refresh Data'}
            </Button>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={() => setAutoRefresh(!autoRefresh)}
                />
              }
              label="Auto-refresh (30s)"
            />
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

export default TikTokDataUpload; 
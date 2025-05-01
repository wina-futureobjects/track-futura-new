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

const InstagramDataUpload = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  
  // Update state to handle two separate files
  const [postFile, setPostFile] = useState<File | null>(null);
  const [reelFile, setReelFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [posts, setPosts] = useState<InstagramPost[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredPosts, setFilteredPosts] = useState<InstagramPost[]>([]);
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

  // Fetch Instagram posts with pagination
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
      
      const response = await fetch(`/api/instagram-data/posts/?page=${pageNumber + 1}&page_size=${pageSize}${folderParam}${searchParam}${contentTypeParam}`);
      
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
        const response = await fetch(`/api/instagram-data/folders/${folderId}/`);
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
      const response = await fetch(`/api/instagram-data/posts/?${folderParam}&page_size=1000`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch folder statistics');
      }
      
      const data = await response.json();
      
      if (data && typeof data === 'object' && 'results' in data) {
        const allPosts = data.results || [];
        const uniqueUsers = [...new Set(allPosts.map((post: InstagramPost) => post.user_posted))].length;
        const totalLikes = allPosts.reduce((acc: number, post: InstagramPost) => acc + post.likes, 0);
        const avgLikes = allPosts.length > 0 ? Math.round(totalLikes / allPosts.length) : 0;
        const verifiedAccounts = allPosts.filter((post: InstagramPost) => post.is_verified).length;
        
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
      const response = await fetch('/api/instagram-data/folders/', { 
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
        const response = await fetch('/api/instagram-data/posts/upload_csv/', {
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
        setUploadSuccess(`${data.message}`);
        
        // Refresh the post list
        fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
        fetchFolderStats();
        
        // Reset file input
        setPostFile(null);
        
        // Reset file input element
        const fileInput = document.getElementById('post-file-upload') as HTMLInputElement;
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
        const response = await fetch('/api/instagram-data/posts/upload_csv/', {
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
        setUploadSuccess(`${data.message}`);
        
        // Refresh the post list
        fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
        fetchFolderStats();
        
        // Reset file input
        setReelFile(null);
        
        // Reset file input element
        const fileInput = document.getElementById('reel-file-upload') as HTMLInputElement;
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
      
      const response = await fetch(
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
    navigate('/instagram-folders');
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
    <Container maxWidth="xl">
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
        {/* Breadcrumbs */}
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link 
            underline="hover" 
            sx={{ display: 'flex', alignItems: 'center' }}
            color="inherit" 
            href="/"
          >
            <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Home
          </Link>
          <Link 
            underline="hover" 
            sx={{ display: 'flex', alignItems: 'center' }}
            color="inherit" 
            onClick={() => navigate('/instagram-folders')}
          >
            <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Instagram Data
          </Link>
          {currentFolder && (
            <Typography color="text.primary">
              {currentFolder.name}
            </Typography>
          )}
        </Breadcrumbs>

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

        {/* Upload section with tabs */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Upload Instagram Data
          </Typography>
          
          <Tabs value={uploadTabValue} onChange={handleUploadTabChange} aria-label="instagram data upload tabs">
            <Tab label="Posts" />
            <Tab label="Reels" />
          </Tabs>
          
          {uploadTabValue === 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                Upload Instagram Posts CSV file
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Ensure date columns are in a standard format (YYYY-MM-DD). Empty date fields are allowed.
                <br />
                Common date issues include quoted dates, inconsistent formats, or regional formats (like DD/MM/YYYY).
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  variant="contained"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  disabled={isUploading}
                >
                  Select Post CSV
                  <input
                    id="post-file-upload"
                    type="file"
                    hidden
                    accept=".csv"
                    onChange={handlePostFileChange}
                  />
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handlePostUpload}
                  disabled={!postFile || isUploading}
                >
                  {isUploading ? <CircularProgress size={24} /> : 'Upload'}
                </Button>
                {postFile && <Typography variant="body2">{postFile.name}</Typography>}
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownloadCSV('post')}
                >
                  Download Posts CSV
                </Button>
              </Box>
            </Box>
          )}
          
          {uploadTabValue === 1 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                Upload Instagram Reels CSV file
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Ensure date columns are in a standard format (YYYY-MM-DD). Empty date fields are allowed.
                <br />
                Common date issues include quoted dates, inconsistent formats, or regional formats (like DD/MM/YYYY).
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  variant="contained"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  disabled={isUploading}
                >
                  Select Reel CSV
                  <input
                    id="reel-file-upload"
                    type="file"
                    hidden
                    accept=".csv"
                    onChange={handleReelFileChange}
                  />
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleReelUpload}
                  disabled={!reelFile || isUploading}
                >
                  {isUploading ? <CircularProgress size={24} /> : 'Upload'}
                </Button>
                {reelFile && <Typography variant="body2">{reelFile.name}</Typography>}
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownloadCSV('reel')}
                >
                  Download Reels CSV
                </Button>
              </Box>
            </Box>
          )}
          
          {uploadSuccess && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {uploadSuccess}
            </Alert>
          )}
          
          {uploadError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography component="div">
                {uploadError.split('\n').map((line, index) => (
                  <div key={index}>{line}</div>
                ))}
              </Typography>
            </Alert>
          )}
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

        {/* Add filters section above the data table */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Instagram Posts
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            {/* Existing search field */}
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
            
            {/* Add content type filter */}
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
          </Box>
          
          {/* Existing data table */}
          <TableContainer>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Date Posted</TableCell>
                  <TableCell align="right">Likes</TableCell>
                  <TableCell align="right">Comments</TableCell>
                  <TableCell>Actions</TableCell>
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
                ) : posts.length === 0 ? (
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
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          {/* Existing pagination */}
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
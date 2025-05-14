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
import { apiFetch } from '../utils/api';

interface FacebookPost {
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

interface FolderStats {
  totalPosts: number;
  uniqueUsers: number;
  avgLikes: number;
  verifiedAccounts: number;
}

const FacebookDataUpload = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  
  const [postFile, setPostFile] = useState<File | null>(null);
  const [reelFile, setReelFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [posts, setPosts] = useState<FacebookPost[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredPosts, setFilteredPosts] = useState<FacebookPost[]>([]);
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
  const [uploadTabValue, setUploadTabValue] = useState(0);
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('all');
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Fetch Facebook posts with pagination
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
      
      const response = await apiFetch(`/api/facebook-data/posts/?page=${pageNumber + 1}&page_size=${pageSize}${folderParam}${searchParam}${contentTypeParam}`);
      
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
        const response = await apiFetch(`/api/facebook-data/folders/${folderId}/`);
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
      const response = await apiFetch(`/api/facebook-data/posts/stats/?folder_id=${folderId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch folder statistics');
      }
      
      const stats = await response.json();
      setFolderStats(stats);
    } catch (error) {
      console.error('Error fetching folder statistics:', error);
    }
  };

  // Check if server is online
  const checkServerStatus = async () => {
    try {
      const response = await apiFetch('/api/facebook-data/posts/?page=1&page_size=1');
      setServerStatus(response.ok ? 'online' : 'offline');
    } catch {
      setServerStatus('offline');
    }
  };

  // Initial data loading
  useEffect(() => {
    fetchFolderDetails();
    fetchFolderStats();
    fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
    checkServerStatus();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [folderId]);

  // Handle tab change for upload section
  const handleUploadTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setUploadTabValue(newValue);
  };

  // Handle file input changes
  const handlePostFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setPostFile(event.target.files[0]);
      setUploadError(null);
    }
  };

  const handleReelFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setReelFile(event.target.files[0]);
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

  // Handle post upload
  const handlePostUpload = async () => {
    if (!postFile || !folderId) {
      setUploadError('Please select a file and ensure you are in a folder');
      return;
    }
    
    // Validate file
    const validation = await validateCsvFile(postFile);
    if (!validation.valid) {
      setUploadError(validation.message);
      return;
    }
    
    setIsUploading(true);
    setUploadSuccess(null);
    setUploadError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', postFile);
      formData.append('folder_id', folderId);
      formData.append('content_type', 'post');
      
      const response = await apiFetch('/api/facebook-data/posts/upload_csv/', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }
      
      const result = await response.json();
      setUploadSuccess(`Upload successful. ${result.rows_processed} rows processed, ${result.rows_added} added, ${result.rows_updated} updated.`);
      setPostFile(null);
      
      // Refresh data
      fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
      fetchFolderStats();
      
      // Reset file input
      const input = document.getElementById('post-file-input') as HTMLInputElement;
      if (input) input.value = '';
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle reel upload
  const handleReelUpload = async () => {
    if (!reelFile || !folderId) {
      setUploadError('Please select a file and ensure you are in a folder');
      return;
    }
    
    // Validate file
    const validation = await validateCsvFile(reelFile);
    if (!validation.valid) {
      setUploadError(validation.message);
      return;
    }
    
    setIsUploading(true);
    setUploadSuccess(null);
    setUploadError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', reelFile);
      formData.append('folder_id', folderId);
      formData.append('content_type', 'reel');
      
      const response = await apiFetch('/api/facebook-data/posts/upload_csv/', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }
      
      const result = await response.json();
      setUploadSuccess(`Upload successful. ${result.rows_processed} rows processed, ${result.rows_added} added, ${result.rows_updated} updated.`);
      setReelFile(null);
      
      // Refresh data
      fetchPosts(page, rowsPerPage, searchTerm, contentTypeFilter);
      fetchFolderStats();
      
      // Reset file input
      const input = document.getElementById('reel-file-input') as HTMLInputElement;
      if (input) input.value = '';
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle download CSV
  const handleDownloadCSV = async (contentType: 'post' | 'reel' | undefined) => {
    try {
      let url = `/api/facebook-data/posts/download_csv/?folder_id=${folderId}`;
      if (contentType) {
        url += `&content_type=${contentType}`;
      }
      
      window.open(url, '_blank');
    } catch (error) {
      console.error('Error downloading CSV:', error);
      setSnackbarMessage('Failed to download CSV');
      setSnackbarOpen(true);
    }
  };

  // Pagination handlers
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    fetchPosts(newPage, rowsPerPage, searchTerm, contentTypeFilter);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    fetchPosts(0, newRowsPerPage, searchTerm, contentTypeFilter);
  };

  // Search handler
  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchTerm(value);
    if (value.length === 0 || value.length > 2) {
      fetchPosts(0, rowsPerPage, value, contentTypeFilter);
      setPage(0);
    }
  };

  // Navigation handler
  const handleGoToFolders = () => {
    navigate('/facebook-folders');
  };

  // Copy link handler
  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    setSnackbarMessage('Link copied to clipboard');
    setSnackbarOpen(true);
  };

  // Snackbar close handler
  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  // Content type filter handler
  const handleContentTypeFilterChange = (event: SelectChangeEvent) => {
    const value = event.target.value;
    setContentTypeFilter(value);
    setPage(0);
    fetchPosts(0, rowsPerPage, searchTerm, value);
  };

  return (
    <Container maxWidth="xl" style={{ marginTop: '2rem' }}>
      {/* Page title with folder details */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          {currentFolder ? currentFolder.name : 'Facebook Data'}
        </Typography>
        {currentFolder?.description && (
          <Typography variant="body1" color="text.secondary" paragraph>
            {currentFolder.description}
          </Typography>
        )}
      </Box>
      
      <Paper elevation={3} style={{ padding: '2rem' }}>
        {!currentFolder && (
          <Alert severity="warning" style={{ marginBottom: '1rem' }}>
            Please select a folder first.
          </Alert>
        )}
        
        <Alert severity="info" style={{ marginBottom: '1rem' }}>
          Only the 'url' field is required in the CSV file. The 'user_posted' field is optional and can be derived from 'page_name' or 'user_username_raw' fields if available.
        </Alert>
        
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Breadcrumbs aria-label="breadcrumb" style={{ marginBottom: '1rem' }}>
              <Link 
                style={{cursor: 'pointer', textDecoration: 'underline'}} 
                onClick={handleGoToFolders}
              >
                Folders
              </Link>
              {currentFolder && (
                <Typography color="textPrimary">{currentFolder.name}</Typography>
              )}
            </Breadcrumbs>
          </Grid>
        </Grid>

        <Typography variant="h4" component="h1" gutterBottom>
          Facebook Data {currentFolder && `- ${currentFolder.name}`}
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" component="h2">
              Statistics
            </Typography>
            <Button
              variant="outlined"
              startIcon={<FolderIcon />}
              onClick={handleGoToFolders}
            >
              Back to Folders
            </Button>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Posts
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
                    Unique Users
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
                    Average Likes
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
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Upload Data
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Tabs
              value={uploadTabValue}
              onChange={handleUploadTabChange}
              aria-label="upload tabs"
            >
              <Tab label="Upload Posts" />
              <Tab label="Upload Reels" />
            </Tabs>
          </Box>
          
          {uploadTabValue === 0 && (
            <Box>
              <Typography variant="body1" gutterBottom>
                Upload CSV file containing Facebook posts data.
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Button
                  variant="contained"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  sx={{ mr: 2 }}
                >
                  Select File
                  <input
                    id="post-file-input"
                    type="file"
                    accept=".csv"
                    hidden
                    onChange={handlePostFileChange}
                  />
                </Button>
                <Typography>
                  {postFile ? postFile.name : 'No file selected'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Button
                  variant="contained"
                  onClick={handlePostUpload}
                  disabled={!postFile || isUploading || serverStatus !== 'online'}
                  sx={{ mr: 2 }}
                >
                  {isUploading ? <CircularProgress size={24} /> : 'Upload Posts'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownloadCSV('post')}
                  disabled={folderStats.totalPosts === 0}
                >
                  Download Posts
                </Button>
              </Box>
            </Box>
          )}
          
          {uploadTabValue === 1 && (
            <Box>
              <Typography variant="body1" gutterBottom>
                Upload CSV file containing Facebook reels data.
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Button
                  variant="contained"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  sx={{ mr: 2 }}
                >
                  Select File
                  <input
                    id="reel-file-input"
                    type="file"
                    accept=".csv"
                    hidden
                    onChange={handleReelFileChange}
                  />
                </Button>
                <Typography>
                  {reelFile ? reelFile.name : 'No file selected'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Button
                  variant="contained"
                  onClick={handleReelUpload}
                  disabled={!reelFile || isUploading || serverStatus !== 'online'}
                  sx={{ mr: 2 }}
                >
                  {isUploading ? <CircularProgress size={24} /> : 'Upload Reels'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownloadCSV('reel')}
                  disabled={folderStats.totalPosts === 0}
                >
                  Download Reels
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
              {uploadError}
            </Alert>
          )}
          
          {serverStatus === 'offline' && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              The server appears to be offline. Uploads may fail.
            </Alert>
          )}
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" component="h2">
              Facebook Posts ({totalCount})
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <FormControl sx={{ minWidth: 120, mr: 2 }}>
                <InputLabel id="content-type-filter-label">Content Type</InputLabel>
                <Select
                  labelId="content-type-filter-label"
                  value={contentTypeFilter}
                  label="Content Type"
                  onChange={handleContentTypeFilterChange}
                  size="small"
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="post">Posts</MenuItem>
                  <MenuItem value="reel">Reels</MenuItem>
                </Select>
              </FormControl>
              <TextField
                placeholder="Search..."
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
              />
            </Box>
          </Box>
          
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : posts.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <Typography variant="h6" gutterBottom>
                No posts found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload some data or adjust your search filters.
              </Typography>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell>Content</TableCell>
                      <TableCell>Posted Date</TableCell>
                      <TableCell align="right">Likes</TableCell>
                      <TableCell align="right">Comments</TableCell>
                      <TableCell align="right">Type</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {posts.map((post) => (
                      <TableRow key={post.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography>{post.user_posted}</Typography>
                            {post.is_verified && (
                              <Tooltip title="Verified Account">
                                <Chip
                                  label="Verified"
                                  size="small"
                                  color="primary"
                                  sx={{ ml: 1 }}
                                />
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography noWrap sx={{ maxWidth: 300 }}>
                            {post.description || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {post.date_posted 
                            ? new Date(post.date_posted).toLocaleDateString() 
                            : '-'}
                        </TableCell>
                        <TableCell align="right">{post.likes.toLocaleString()}</TableCell>
                        <TableCell align="right">{post.num_comments.toLocaleString()}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={post.content_type === 'post' ? 'Post' : 'Reel'}
                            size="small"
                            color={post.content_type === 'post' ? 'default' : 'secondary'}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Open URL">
                            <IconButton
                              size="small"
                              href={post.url}
                              target="_blank"
                              rel="noopener noreferrer"
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
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <TablePagination
                rowsPerPageOptions={[10, 25, 50, 100]}
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
      </Paper>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default FacebookDataUpload; 
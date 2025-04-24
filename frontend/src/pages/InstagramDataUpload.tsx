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
  const [file, setFile] = useState<File | null>(null);
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

  // Fetch Instagram posts with pagination
  const fetchPosts = async (pageNumber = 0, pageSize = 10, searchTerm = '') => {
    try {
      setIsLoading(true);
      // Add folder filtering if folderId is present
      const folderParam = folderId ? `&folder_id=${folderId}` : '';
      // Add search param if search term exists
      const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
      
      const response = await fetch(`/api/instagram/posts/?page=${pageNumber + 1}&page_size=${pageSize}${folderParam}${searchParam}`);
      
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
        const response = await fetch(`/api/instagram/folders/${folderId}/`);
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
      const response = await fetch(`/api/instagram/posts/?${folderParam}&page_size=1000`);
      
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

  // Initial data load
  useEffect(() => {
    fetchPosts(page, rowsPerPage, searchTerm);
    if (folderId) {
      fetchFolderDetails();
      fetchFolderStats();
    }
  }, [folderId]); // Only re-fetch when folder ID changes
  
  // This effect handles pagination and search changes
  useEffect(() => {
    fetchPosts(page, rowsPerPage, searchTerm);
  }, [page, rowsPerPage, searchTerm]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
      // Reset status messages
      setUploadSuccess(null);
      setUploadError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadError('Please select a file to upload');
      return;
    }

    if (!file.name.endsWith('.csv')) {
      setUploadError('Please upload a CSV file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    
    // Add folder_id to the form data if available
    if (folderId) {
      formData.append('folder_id', folderId);
    }

    try {
      setIsUploading(true);
      
      const response = await fetch('/api/instagram/posts/upload_csv/', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const data = await response.json();
      setUploadSuccess(`${data.message}`);
      
      // Refresh the post list
      setPage(0); // Reset to first page after upload
      fetchPosts(0, rowsPerPage, searchTerm); // Use the fetchPosts function
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadCSV = async () => {
    try {
      const response = await fetch('/api/instagram/posts/download_csv/');
      
      if (response.ok) {
        // Create a blob from the response
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Create a temporary link and trigger download
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'instagram_data.csv';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setUploadError('Failed to download CSV');
      }
    } catch (error) {
      console.error('Download error:', error);
      setUploadError('Error downloading CSV file');
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

  return (
    <Container maxWidth="xl">
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

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
          {/* CSV Upload Card */}
          <Box sx={{ width: { xs: '100%', md: '50%' } }}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2">
                  Upload CSV Data
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Upload your Instagram tracker CSV file. The system will process and store the data.
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Button
                    component="label"
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                    sx={{ mr: 2 }}
                  >
                    Select CSV File
                    <input
                      type="file"
                      hidden
                      accept=".csv"
                      onChange={handleFileChange}
                    />
                  </Button>
                  <Typography variant="body2">
                    {file ? file.name : 'No file selected'}
                  </Typography>
                </Box>

                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleUpload}
                  disabled={!file || isUploading}
                  sx={{ mr: 2 }}
                >
                  {isUploading ? (
                    <>
                      <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
                      Uploading...
                    </>
                  ) : (
                    'Upload File'
                  )}
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownloadCSV}
                  disabled={posts.length === 0}
                >
                  Download Data as CSV
                </Button>

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
              </CardContent>
            </Card>
          </Box>

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

        {/* Data Table */}
        <Box sx={{ mt: 4 }}>
          <Paper sx={{ width: '100%', mb: 2 }}>
            <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Instagram Posts
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TextField
                  placeholder="Search posts..."
                  variant="outlined"
                  size="small"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  InputProps={{
                    startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                  sx={{ mr: 2, width: 250 }}
                />
                <IconButton>
                  <FilterListIcon />
                </IconButton>
              </Box>
            </Box>
            <Divider />
            <TableContainer sx={{ maxHeight: 600 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>User</TableCell>
                    <TableCell>Post</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Likes</TableCell>
                    <TableCell align="right">Comments</TableCell>
                    <TableCell>Date Posted</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <CircularProgress size={30} sx={{ my: 3 }} />
                        <Typography>Loading data...</Typography>
                      </TableCell>
                    </TableRow>
                  ) : filteredPosts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography sx={{ py: 3 }}>No data found</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredPosts.map((post) => (
                      <TableRow key={post.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {post.is_verified && (
                              <Chip 
                                size="small" 
                                label="Verified" 
                                color="primary" 
                                variant="outlined" 
                                sx={{ mr: 1 }}
                              />
                            )}
                            {post.user_posted}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Link href={post.url} target="_blank" rel="noopener">
                            {post.description ? 
                              (post.description.length > 60 ? 
                                `${post.description.substring(0, 60)}...` : 
                                post.description) : 
                              'No description'}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            size="small" 
                            label={post.content_type || 'Unknown'} 
                            color="secondary" 
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="right">{post.likes.toLocaleString()}</TableCell>
                        <TableCell align="right">{post.num_comments.toLocaleString()}</TableCell>
                        <TableCell>
                          {new Date(post.date_posted).toLocaleDateString()}
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="View Post">
                            <IconButton 
                              size="small" 
                              href={post.url} 
                              target="_blank" 
                              rel="noopener"
                              sx={{ mx: 0.5 }}
                            >
                              <OpenInNewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy Link">
                            <IconButton 
                              size="small" 
                              onClick={() => handleCopyLink(post.url)}
                              sx={{ mx: 0.5 }}
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
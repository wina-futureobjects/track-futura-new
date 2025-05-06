import { useState, useEffect, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Breadcrumbs,
  Link,
  IconButton,
  InputAdornment,
  CircularProgress,
  Snackbar,
  Alert,
  Tooltip,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicNoteIcon from '@mui/icons-material/MusicNote'; // For TikTok

interface TrackAccount {
  id: number;
  name: string;
  iac_no: string;
  facebook_username: string | null;
  instagram_username: string | null;
  linkedin_username: string | null;
  tiktok_username: string | null;
  facebook_id: string | null;
  instagram_id: string | null;
  linkedin_id: string | null;
  tiktok_id: string | null;
  other_social_media: string | null;
  risk_classification: string | null;
  close_monitoring: boolean;
  posting_frequency: string | null;
  folder: number | null;
  created_at: string;
  updated_at: string;
}

const TrackAccountsList = () => {
  const navigate = useNavigate();
  const [accounts, setAccounts] = useState<TrackAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  // Fetch accounts
  const fetchAccounts = async (pageNumber = 0, pageSize = 10, searchQuery = '') => {
    try {
      setLoading(true);
      
      // Prepare query parameters
      const searchParam = searchQuery ? `&search=${encodeURIComponent(searchQuery)}` : '';
      
      // Make the API request
      const response = await fetch(`/api/track-accounts/accounts/?page=${pageNumber + 1}&page_size=${pageSize}${searchParam}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch accounts');
      }
      
      const data = await response.json();
      
      if (data && typeof data === 'object' && 'results' in data) {
        setAccounts(data.results || []);
        setTotalCount(data.count || 0);
      } else {
        console.error('Unexpected data format from API:', data);
        setAccounts([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
      showSnackbar('Failed to load accounts', 'error');
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchAccounts(page, rowsPerPage, searchTerm);
  }, []);

  // Handle pagination change
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    fetchAccounts(newPage, rowsPerPage, searchTerm);
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    fetchAccounts(0, newRowsPerPage, searchTerm);
  };

  // Handle search
  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSearch = () => {
    setPage(0);
    fetchAccounts(0, rowsPerPage, searchTerm);
  };

  // Handle search on Enter key
  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  // Show snackbar message
  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  // Handle snackbar close
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs navigation */}
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center' }}
          color="inherit"
          onClick={() => navigate('/')}
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Home
        </Link>
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center' }}
          color="inherit"
          onClick={() => navigate('/track-accounts/folders')}
        >
          <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Track Account Folders
        </Link>
        <Typography
          sx={{ display: 'flex', alignItems: 'center' }}
          color="text.primary"
        >
          All Track Accounts
        </Typography>
      </Breadcrumbs>

      {/* Page title and actions */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" gutterBottom>
          All Track Accounts
        </Typography>
        <Button
          variant="contained"
          startIcon={<PersonAddIcon />}
          onClick={() => navigate('/track-accounts/create')}
        >
          Create Account
        </Button>
      </Box>

      {/* Search and filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            label="Search accounts"
            variant="outlined"
            size="small"
            fullWidth
            value={searchTerm}
            onChange={handleSearchChange}
            onKeyPress={handleKeyPress}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={handleSearch} edge="end">
                    <SearchIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{ mr: 2 }}
          />
          <Button 
            variant="contained" 
            onClick={handleSearch}
          >
            Search
          </Button>
        </Box>
      </Paper>

      {/* Accounts table */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : accounts.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" gutterBottom>
                No accounts found.
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/track-accounts/create')}
                sx={{ mt: 1 }}
              >
                Create Account
              </Button>
            </Box>
          ) : (
            <>
              <Table sx={{ minWidth: 650 }} aria-label="accounts table">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>IAC No.</TableCell>
                    <TableCell align="center">Social Media</TableCell>
                    <TableCell>Risk Classification</TableCell>
                    <TableCell>Close Monitoring</TableCell>
                    <TableCell>Folder</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {accounts.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell>{account.name}</TableCell>
                      <TableCell>{account.iac_no}</TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                          {account.instagram_username && (
                            <Tooltip title={`Instagram: ${account.instagram_username}`}>
                              <IconButton 
                                size="small" 
                                color="primary"
                                onClick={() => {
                                  if (account.instagram_id) {
                                    // Ensure URL has proper protocol
                                    const url = account.instagram_id.startsWith('http') 
                                      ? account.instagram_id 
                                      : `https://${account.instagram_id.replace(/^\/\//, '')}`;
                                    window.open(url, '_blank');
                                  } else {
                                    window.open(`https://www.instagram.com/${account.instagram_username}`, '_blank');
                                  }
                                }}
                              >
                                <InstagramIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          
                          {account.facebook_username && (
                            <Tooltip title={`Facebook: ${account.facebook_username}`}>
                              <IconButton 
                                size="small" 
                                color="primary"
                                onClick={() => {
                                  if (account.facebook_id) {
                                    // Ensure URL has proper protocol
                                    const url = account.facebook_id.startsWith('http') 
                                      ? account.facebook_id 
                                      : `https://${account.facebook_id.replace(/^\/\//, '')}`;
                                    window.open(url, '_blank');
                                  } else {
                                    window.open(`https://www.facebook.com/${account.facebook_username}`, '_blank');
                                  }
                                }}
                              >
                                <FacebookIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          
                          {account.linkedin_username && (
                            <Tooltip title={`LinkedIn: ${account.linkedin_username}`}>
                              <IconButton 
                                size="small" 
                                color="primary"
                                onClick={() => {
                                  if (account.linkedin_id) {
                                    // Ensure URL has proper protocol
                                    const url = account.linkedin_id.startsWith('http') 
                                      ? account.linkedin_id 
                                      : `https://${account.linkedin_id.replace(/^\/\//, '')}`;
                                    window.open(url, '_blank');
                                  } else {
                                    window.open(`https://www.linkedin.com/in/${account.linkedin_username}`, '_blank');
                                  }
                                }}
                              >
                                <LinkedInIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          
                          {account.tiktok_username && (
                            <Tooltip title={`TikTok: ${account.tiktok_username}`}>
                              <IconButton 
                                size="small" 
                                color="primary"
                                onClick={() => {
                                  if (account.tiktok_id) {
                                    // Ensure URL has proper protocol
                                    const url = account.tiktok_id.startsWith('http') 
                                      ? account.tiktok_id 
                                      : `https://${account.tiktok_id.replace(/^\/\//, '')}`;
                                    window.open(url, '_blank');
                                  } else {
                                    window.open(`https://www.tiktok.com/@${account.tiktok_username}`, '_blank');
                                  }
                                }}
                              >
                                <MusicNoteIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          
                          {!account.instagram_username && !account.facebook_username && 
                           !account.linkedin_username && !account.tiktok_username && '-'}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {account.risk_classification ? (
                          <Chip 
                            label={account.risk_classification} 
                            size="small" 
                            color={
                              account.risk_classification.toLowerCase() === 'high' ? 'error' :
                              account.risk_classification.toLowerCase() === 'medium' ? 'warning' : 
                              'success'
                            }
                          />
                        ) : (
                          '-'
                        )}
                      </TableCell>
                      <TableCell>
                        {account.close_monitoring ? (
                          <Chip label="Yes" size="small" color="primary" />
                        ) : (
                          <Chip label="No" size="small" color="default" variant="outlined" />
                        )}
                      </TableCell>
                      <TableCell>
                        {account.folder ? (
                          <Button 
                            size="small" 
                            variant="text"
                            startIcon={<FolderIcon />}
                            onClick={() => navigate(`/track-accounts/folders/${account.folder}`)}
                          >
                            View Folder
                          </Button>
                        ) : (
                          '-'
                        )}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<EditIcon />}
                          onClick={() => navigate(`/track-accounts/edit/${account.id}`)}
                        >
                          Edit
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={totalCount}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </>
          )}
        </TableContainer>
      </Paper>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default TrackAccountsList; 
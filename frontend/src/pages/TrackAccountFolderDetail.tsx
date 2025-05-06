import { useState, useEffect, ChangeEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
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
  Snackbar,
  Alert,
  Tooltip,
  IconButton,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  SelectChangeEvent,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Card,
  CardContent,
  Stack,
  LinearProgress,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import AssessmentIcon from '@mui/icons-material/Assessment';
import AddIcon from '@mui/icons-material/Add';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicNoteIcon from '@mui/icons-material/MusicNote'; // For TikTok
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

interface Folder {
  id: number;
  name: string;
  description: string | null;
  account_count: number;
  created_at: string;
  updated_at: string;
}

interface Account {
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
  risk_classification: string | null;
  close_monitoring: boolean;
  created_at: string;
}

const TrackAccountFolderDetail = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  const [folder, setFolder] = useState<Folder | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [monitoringFilter, setMonitoringFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Social media filters
  const [socialMediaFilters, setSocialMediaFilters] = useState({
    hasFacebook: false,
    hasInstagram: false,
    hasLinkedIn: false,
    hasTikTok: false,
  });
  
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  useEffect(() => {
    if (folderId) {
      fetchFolderDetails();
      fetchAccounts(page, rowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
    }
  }, [folderId]);

  const fetchFolderDetails = async () => {
    try {
      setLoading(true);
      
      // Fetch folder details
      const folderResponse = await api.get(`/api/track-accounts/folders/${folderId}/`);
      if (folderResponse.status === 200) {
        setFolder(folderResponse.data);
      }
    } catch (error) {
      console.error('Error fetching folder details:', error);
      showSnackbar('Failed to load folder details', 'error');
    } finally {
      setLoading(false);
      setInitialLoad(false);
    }
  };
  
  const fetchAccounts = async (
    pageNumber = 0, 
    pageSize = 10, 
    search = '',
    risk = '',
    monitoring = '',
    socialMedia = socialMediaFilters
  ) => {
    try {
      // Only set full loading on initial load, use tableLoading for subsequent fetches
      if (initialLoad) {
        setLoading(true);
      } else {
        setTableLoading(true);
      }
      
      // Build query parameters
      let queryParams = `folder_id=${folderId}&page=${pageNumber + 1}&page_size=${pageSize}`;
      
      // Add search parameter if provided
      if (search) {
        queryParams += `&search=${encodeURIComponent(search)}`;
      }
      
      // Add risk classification filter if selected
      if (risk) {
        queryParams += `&risk_classification=${encodeURIComponent(risk)}`;
      }
      
      // Add monitoring filter if selected
      if (monitoring !== '') {
        queryParams += `&close_monitoring=${monitoring === 'yes' ? 'true' : 'false'}`;
      }
      
      // Add social media filters
      if (socialMedia.hasFacebook) {
        queryParams += '&has_facebook=true';
      }
      
      if (socialMedia.hasInstagram) {
        queryParams += '&has_instagram=true';
      }
      
      if (socialMedia.hasLinkedIn) {
        queryParams += '&has_linkedin=true';
      }
      
      if (socialMedia.hasTikTok) {
        queryParams += '&has_tiktok=true';
      }
      
      // Fetch accounts in the folder with pagination and filters
      const accountsResponse = await api.get(`/api/track-accounts/accounts/?${queryParams}`);
      
      if (accountsResponse.status === 200) {
        if (accountsResponse.data && 'results' in accountsResponse.data) {
          setAccounts(accountsResponse.data.results || []);
          setTotalCount(accountsResponse.data.count || 0);
        } else {
          console.error('Unexpected data format from API:', accountsResponse.data);
          setAccounts([]);
          setTotalCount(0);
        }
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
      showSnackbar('Failed to load accounts', 'error');
      setAccounts([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
      setTableLoading(false);
      setInitialLoad(false);
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    fetchAccounts(newPage, rowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    fetchAccounts(0, newRowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
  };

  const handleBackToFolders = () => {
    navigate('/track-accounts/folders');
  };

  const handleGenerateReport = () => {
    navigate(`/report-folders/generate?folder_id=${folderId}`);
  };

  // Handle search input change
  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };
  
  // Handle search button click
  const handleSearch = () => {
    setPage(0);
    fetchAccounts(0, rowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
  };
  
  // Handle search on Enter key
  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };
  
  // Handle risk filter change
  const handleRiskFilterChange = (event: SelectChangeEvent) => {
    setRiskFilter(event.target.value);
    setPage(0);
    fetchAccounts(0, rowsPerPage, searchTerm, event.target.value, monitoringFilter, socialMediaFilters);
  };
  
  // Handle monitoring filter change
  const handleMonitoringFilterChange = (event: SelectChangeEvent) => {
    setMonitoringFilter(event.target.value);
    setPage(0);
    fetchAccounts(0, rowsPerPage, searchTerm, riskFilter, event.target.value, socialMediaFilters);
  };
  
  // Handle social media checkbox changes
  const handleSocialMediaFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    const updatedFilters = {
      ...socialMediaFilters,
      [name]: checked
    };
    setSocialMediaFilters(updatedFilters);
    setPage(0);
    fetchAccounts(0, rowsPerPage, searchTerm, riskFilter, monitoringFilter, updatedFilters);
  };
  
  // Clear all filters
  const handleClearFilters = () => {
    setSearchTerm('');
    setRiskFilter('');
    setMonitoringFilter('');
    setSocialMediaFilters({
      hasFacebook: false,
      hasInstagram: false,
      hasLinkedIn: false,
      hasTikTok: false
    });
    setPage(0);
    fetchAccounts(0, rowsPerPage, '', '', '', {
      hasFacebook: false,
      hasInstagram: false,
      hasLinkedIn: false,
      hasTikTok: false
    });
  };
  
  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 2 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 1 }}>
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
          onClick={handleBackToFolders}
          style={{ cursor: 'pointer' }}
        >
          <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Track Account Folders
        </Link>
        {folder && (
          <Typography
            sx={{ display: 'flex', alignItems: 'center' }}
            color="text.primary"
          >
            <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            {folder.name}
          </Typography>
        )}
      </Breadcrumbs>

      {/* Show loading spinner only on first load */}
      {loading && initialLoad ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <CircularProgress />
        </Box>
      ) : folder ? (
        <>
          {/* Folder Header */}
          <Paper sx={{ p: { xs: 1.5, md: 2 }, mb: 1.5 }}>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: { xs: 'column', sm: 'row' },
              justifyContent: 'space-between', 
              alignItems: { xs: 'flex-start', sm: 'center' },
              gap: { xs: 1, sm: 0 }
            }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" sx={{ mb: 0.5 }}>
                  {folder.name}
                </Typography>
                {folder.description && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    {folder.description}
                  </Typography>
                )}
                <Chip 
                  label={`${folder.account_count} accounts`} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                />
              </Box>
              <Box sx={{ 
                display: 'flex', 
                flexWrap: { xs: 'wrap', sm: 'nowrap' },
                gap: 1 
              }}>
                <Button
                  variant="outlined"
                  startIcon={<ArrowBackIcon />}
                  onClick={handleBackToFolders}
                  size="small"
                >
                  Back
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AssessmentIcon />}
                  onClick={handleGenerateReport}
                  size="small"
                >
                  Report
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<AddIcon />}
                  onClick={() => navigate(`/track-accounts/folders/${folderId}/create`)}
                  size="small"
                >
                  Add
                </Button>
              </Box>
            </Box>
          </Paper>

          {/* List of accounts */}
          <Paper sx={{ width: '100%', mb: 1.5, overflow: 'hidden' }}>
            <Box sx={{ 
              p: { xs: 1, md: 1.5 }, 
              borderBottom: '1px solid rgba(0, 0, 0, 0.12)', 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              flexWrap: { xs: 'wrap', sm: 'nowrap' },
              gap: { xs: 1, sm: 0 }
            }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Track Accounts
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button 
                  variant="outlined" 
                  startIcon={<AddIcon />}
                  onClick={() => navigate(`/track-accounts/folders/${folderId}/upload`)}
                  size="small"
                >
                  Upload
                </Button>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate(`/track-accounts/folders/${folderId}/create`)}
                  size="small"
                >
                  Add
                </Button>
              </Box>
            </Box>
            
            {/* Search and filters section - Compact version */}
            <Box sx={{ p: { xs: 1.5, md: 2 }, borderBottom: '1px solid rgba(0, 0, 0, 0.12)' }}>
              <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1, alignItems: 'center', mb: showFilters ? 1 : 0 }}>
                <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 70%', md: '1 1 75%' } }}>
                  <TextField
                    label="Search accounts"
                    variant="outlined"
                    fullWidth
                    value={searchTerm}
                    onChange={handleSearchChange}
                    onKeyPress={handleKeyPress}
                    size="small"
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton onClick={handleSearch} edge="end" size="small">
                            <SearchIcon />
                          </IconButton>
                          {searchTerm && (
                            <IconButton 
                              onClick={() => {
                                setSearchTerm('');
                                if (searchTerm) {
                                  setPage(0);
                                  fetchAccounts(0, rowsPerPage, '', riskFilter, monitoringFilter, socialMediaFilters);
                                }
                              }} 
                              edge="end"
                              size="small"
                            >
                              <ClearIcon />
                            </IconButton>
                          )}
                        </InputAdornment>
                      ),
                    }}
                  />
                </Box>
                <Box sx={{ 
                  flex: { xs: '1 1 100%', sm: '1 1 30%', md: '1 1 25%' },
                  display: 'flex', 
                  justifyContent: { xs: 'flex-start', sm: 'flex-end' }, 
                  gap: 1 
                }}>
                  <Button
                    variant="outlined"
                    startIcon={<FilterListIcon />}
                    onClick={toggleFilters}
                    size="small"
                  >
                    {showFilters ? 'Hide Filters' : 'Filters'}
                  </Button>
                  {(searchTerm || riskFilter || monitoringFilter || 
                    socialMediaFilters.hasFacebook || 
                    socialMediaFilters.hasInstagram || 
                    socialMediaFilters.hasLinkedIn || 
                    socialMediaFilters.hasTikTok) && (
                    <Button
                      variant="outlined"
                      startIcon={<ClearIcon />}
                      onClick={handleClearFilters}
                      size="small"
                      color="secondary"
                    >
                      Clear
                    </Button>
                  )}
                </Box>
              </Box>
              
              {/* Filter options - More compact */}
              {showFilters && (
                <Card variant="outlined" sx={{ mt: 1, borderRadius: 1 }}>
                  <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2 }}>
                      {/* Account status filters */}
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ 
                          mb: 1, 
                          pb: 0.5, 
                          borderBottom: '1px solid', 
                          borderColor: 'divider' 
                        }}>
                          Account Status
                        </Typography>
                        
                        <FormControl fullWidth sx={{ mb: 1 }} size="small">
                          <InputLabel id="risk-classification-filter-label">Risk Classification</InputLabel>
                          <Select
                            labelId="risk-classification-filter-label"
                            id="risk-classification-filter"
                            value={riskFilter}
                            label="Risk Classification"
                            onChange={handleRiskFilterChange}
                          >
                            <MenuItem value="">All Classifications</MenuItem>
                            <MenuItem value="Low">Low Risk</MenuItem>
                            <MenuItem value="Medium">Medium Risk</MenuItem>
                            <MenuItem value="High">High Risk</MenuItem>
                            <MenuItem value="Critical">Critical Risk</MenuItem>
                          </Select>
                        </FormControl>
                        
                        <FormControl fullWidth size="small">
                          <InputLabel id="monitoring-filter-label">Close Monitoring</InputLabel>
                          <Select
                            labelId="monitoring-filter-label"
                            id="monitoring-filter"
                            value={monitoringFilter}
                            label="Close Monitoring"
                            onChange={handleMonitoringFilterChange}
                          >
                            <MenuItem value="">All</MenuItem>
                            <MenuItem value="yes">Monitored Accounts</MenuItem>
                            <MenuItem value="no">Non-monitored Accounts</MenuItem>
                          </Select>
                        </FormControl>
                      </Box>
                      
                      <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
                      <Divider sx={{ display: { xs: 'block', md: 'none' }, my: 1 }} />
                      
                      {/* Social media filters */}
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ 
                          mb: 1, 
                          pb: 0.5, 
                          borderBottom: '1px solid', 
                          borderColor: 'divider' 
                        }}>
                          Social Media Presence
                        </Typography>
                        
                        <FormGroup>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                            <Box sx={{ width: { xs: '100%', sm: '50%' }, mb: 0.5, pr: 1 }}>
                              <FormControlLabel
                                control={
                                  <Checkbox 
                                    checked={socialMediaFilters.hasFacebook}
                                    onChange={handleSocialMediaFilterChange}
                                    name="hasFacebook"
                                    color="primary"
                                    size="small"
                                  />
                                }
                                label={
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <FacebookIcon sx={{ mr: 0.5, color: '#4267B2' }} />
                                    <Typography variant="body2">Facebook</Typography>
                                  </Box>
                                }
                              />
                            </Box>
                            
                            <Box sx={{ width: { xs: '100%', sm: '50%' }, mb: 0.5, pr: 1 }}>
                              <FormControlLabel
                                control={
                                  <Checkbox 
                                    checked={socialMediaFilters.hasInstagram}
                                    onChange={handleSocialMediaFilterChange}
                                    name="hasInstagram"
                                    color="primary"
                                    size="small"
                                  />
                                }
                                label={
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <InstagramIcon sx={{ mr: 0.5, color: '#E1306C' }} />
                                    <Typography variant="body2">Instagram</Typography>
                                  </Box>
                                }
                              />
                            </Box>
                            
                            <Box sx={{ width: { xs: '100%', sm: '50%' }, mb: 0.5, pr: 1 }}>
                              <FormControlLabel
                                control={
                                  <Checkbox 
                                    checked={socialMediaFilters.hasLinkedIn}
                                    onChange={handleSocialMediaFilterChange}
                                    name="hasLinkedIn"
                                    color="primary"
                                    size="small"
                                  />
                                }
                                label={
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <LinkedInIcon sx={{ mr: 0.5, color: '#0077B5' }} />
                                    <Typography variant="body2">LinkedIn</Typography>
                                  </Box>
                                }
                              />
                            </Box>
                            
                            <Box sx={{ width: { xs: '100%', sm: '50%' }, mb: 0.5, pr: 1 }}>
                              <FormControlLabel
                                control={
                                  <Checkbox 
                                    checked={socialMediaFilters.hasTikTok}
                                    onChange={handleSocialMediaFilterChange}
                                    name="hasTikTok"
                                    color="primary"
                                    size="small"
                                  />
                                }
                                label={
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <MusicNoteIcon sx={{ mr: 0.5 }} />
                                    <Typography variant="body2">TikTok</Typography>
                                  </Box>
                                }
                              />
                            </Box>
                          </Box>
                        </FormGroup>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
            
            {/* Show linear progress indicator for subsequent data loading */}
            {tableLoading && (
              <Box sx={{ width: '100%', height: 3 }}>
                <LinearProgress color="primary" />
              </Box>
            )}
            
            {accounts.length === 0 ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" paragraph sx={{ mb: 1 }}>
                  No accounts found matching your criteria.
                </Typography>
                {(searchTerm || riskFilter || monitoringFilter || 
                  socialMediaFilters.hasFacebook || 
                  socialMediaFilters.hasInstagram || 
                  socialMediaFilters.hasLinkedIn || 
                  socialMediaFilters.hasTikTok) && (
                  <Button 
                    variant="outlined" 
                    startIcon={<ClearIcon />}
                    onClick={handleClearFilters}
                    size="small"
                  >
                    Clear Filters
                  </Button>
                )}
              </Box>
            ) : (
              <>
                <TableContainer sx={{ maxHeight: 'calc(100vh - 250px)' }}>
                  <Table stickyHeader size="small" sx={{ '& .MuiTableCell-root': { py: 1, px: 1.5 } }}>
                    <TableHead>
                      <TableRow>
                        <TableCell width="25%" sx={{ fontWeight: 'bold' }}>Name</TableCell>
                        <TableCell width="15%" sx={{ fontWeight: 'bold' }}>IAC No.</TableCell>
                        <TableCell width="25%" sx={{ fontWeight: 'bold' }}>Social Media</TableCell>
                        <TableCell width="15%" sx={{ fontWeight: 'bold' }}>Risk</TableCell>
                        <TableCell width="10%" sx={{ fontWeight: 'bold' }}>Monitoring</TableCell>
                        <TableCell width="10%" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {accounts.map((account) => (
                        <TableRow 
                          key={account.id}
                          hover
                          sx={{ 
                            '&:hover': { 
                              backgroundColor: 'rgba(0, 0, 0, 0.04)'
                            }
                          }}
                        >
                          <TableCell sx={{ fontWeight: 'medium' }}>{account.name}</TableCell>
                          <TableCell>{account.iac_no}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 0.75 }}>
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
                                    <InstagramIcon fontSize="small" />
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
                                    <FacebookIcon fontSize="small" />
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
                                    <LinkedInIcon fontSize="small" />
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
                                    <MusicNoteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            {account.risk_classification ? (
                              <Chip 
                                label={account.risk_classification} 
                                size="small" 
                                color={
                                  account.risk_classification.toLowerCase() === 'high' ? 'error' :
                                  account.risk_classification.toLowerCase() === 'medium' ? 'warning' : 'success'
                                }
                                sx={{ fontWeight: 'medium', height: 22 }}
                              />
                            ) : (
                              '-'
                            )}
                          </TableCell>
                          <TableCell>
                            {account.close_monitoring ? (
                              <Chip label="Yes" size="small" color="primary" sx={{ height: 22 }} />
                            ) : (
                              <Chip label="No" size="small" color="default" variant="outlined" sx={{ height: 22 }} />
                            )}
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              startIcon={<EditIcon fontSize="small" />}
                              onClick={() => navigate(`/track-accounts/edit/${account.id}`)}
                              variant="outlined"
                              color="primary"
                              sx={{ py: 0.25, minWidth: 60 }}
                            >
                              Edit
                            </Button>
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
                  labelRowsPerPage="Rows:"
                  sx={{ 
                    borderTop: '1px solid rgba(0, 0, 0, 0.12)',
                    '.MuiTablePagination-selectLabel, .MuiTablePagination-select, .MuiTablePagination-displayedRows': {
                      fontWeight: 'medium'
                    },
                    py: 0.5
                  }}
                />
              </>
            )}
          </Paper>
        </>
      ) : (
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Folder not found or could not be loaded.
          </Typography>
          <Button
            variant="contained"
            onClick={handleBackToFolders}
            size="small"
          >
            Back to Folders
          </Button>
        </Paper>
      )}

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default TrackAccountFolderDetail; 
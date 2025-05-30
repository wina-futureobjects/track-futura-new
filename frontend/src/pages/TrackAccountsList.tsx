import { useState, useEffect, ChangeEvent } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
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
  IconButton,
  InputAdornment,
  CircularProgress,
  Snackbar,
  Alert,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Card,
  CardContent,
  Stack,
  SelectChangeEvent,
  Avatar,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  PersonAdd as PersonAddIcon,
  Facebook as FacebookIcon,
  Instagram as InstagramIcon,
  LinkedIn as LinkedInIcon,
  MusicNote as TikTokIcon,
  FilterList as FilterListIcon,
  Clear as ClearIcon,
  Folder as FolderIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material';

interface TrackSource {
  id: number;
  name: string;
  iac_no: string;
  facebook_link: string | null;
  instagram_link: string | null;
  linkedin_link: string | null;
  tiktok_link: string | null;
  other_social_media: string | null;
  risk_classification: string | null;
  close_monitoring: boolean;
  posting_frequency: string | null;
  folder: number | null;
  created_at: string;
  updated_at: string;
}

interface FilterStats {
  total: number;
  riskCounts: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  monitoringCounts: {
    monitored: number;
    unmonitored: number;
  };
  socialMediaCounts: {
    facebook: number;
    instagram: number;
    linkedin: number;
    tiktok: number;
  };
}

const TrackSourcesList = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Extract project ID from URL path or query parameters
  const getProjectId = () => {
    // First try to extract from URL path: /organizations/{orgId}/projects/{projectId}/...
    const pathMatch = location.pathname.match(/\/organizations\/\d+\/projects\/(\d+)/);
    if (pathMatch) {
      return pathMatch[1];
    }
    
    // Fallback to query parameter: ?project=13
    const queryParams = new URLSearchParams(location.search);
    return queryParams.get('project');
  };
  
  const projectId = getProjectId();
  
  const [sources, setSources] = useState<TrackSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalCount, setTotalCount] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter states
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [monitoringFilter, setMonitoringFilter] = useState<string>('');
  const [socialMediaFilters, setSocialMediaFilters] = useState({
    hasFacebook: false,
    hasInstagram: false,
    hasLinkedIn: false,
    hasTikTok: false,
  });
  
  // Stats for filter sidebar
  const [filterStats, setFilterStats] = useState<FilterStats>({
    total: 0,
    riskCounts: { low: 0, medium: 0, high: 0, critical: 0 },
    monitoringCounts: { monitored: 0, unmonitored: 0 },
    socialMediaCounts: { facebook: 0, instagram: 0, linkedin: 0, tiktok: 0 },
  });
  
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  // Fetch sources with filters
  const fetchSources = async (
    pageNumber = 0, 
    pageSize = 25, 
    searchQuery = '',
    risk = '',
    monitoring = '',
    socialMedia = socialMediaFilters
  ) => {
    try {
      setLoading(true);
      
      // Don't fetch sources if no project is found
      if (!projectId) {
        console.error('No project ID found in URL');
        setSources([]);
        setTotalCount(0);
        setLoading(false);
        return;
      }
      
      // Build query parameters
      let queryParams = `page=${pageNumber + 1}&page_size=${pageSize}`;
      
      // Add project ID (required)
      queryParams += `&project=${projectId}`;
      
      // Add search parameter
      if (searchQuery) {
        queryParams += `&search=${encodeURIComponent(searchQuery)}`;
      }
      
      // Add risk classification filter
      if (risk) {
        queryParams += `&risk_classification=${encodeURIComponent(risk)}`;
      }
      
      // Add monitoring filter
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
      
      console.log('=== FRONTEND FETCH SOURCES DEBUG ===');
      console.log('Project ID from URL:', projectId);
      console.log('Current URL:', location.pathname);
      console.log('Fetch URL:', `/api/track-accounts/sources/?${queryParams}`);
      
      const response = await fetch(`/api/track-accounts/sources/?${queryParams}`);
      console.log('Fetch response status:', response.status);
      console.log('Fetch response ok:', response.ok);
      
      if (!response.ok) {
        throw new Error('Failed to fetch sources');
      }
      
      const data = await response.json();
      console.log('Raw response data:', data);
      
      if (data && typeof data === 'object' && 'results' in data) {
        console.log('Using paginated data, count:', data.count);
        console.log('Results:', data.results);
        setSources(data.results || []);
        setTotalCount(data.count || 0);
        
        // Update filter stats
        if (data.filter_stats) {
          setFilterStats(data.filter_stats);
        }
      } else {
        console.error('Unexpected data format from API:', data);
        setSources([]);
        setTotalCount(0);
      }
      console.log('=== END FRONTEND FETCH SOURCES DEBUG ===');
    } catch (error) {
      console.error('Error fetching sources:', error);
      setSources([]);
      setTotalCount(0);
      showSnackbar('Failed to load sources. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Fetch filter statistics
  const fetchFilterStats = async () => {
    try {
      let queryParams = '';
      if (projectId) {
        queryParams = `?project=${projectId}`;
      }
      
      const response = await fetch(`/api/track-accounts/sources/stats/${queryParams}`);
      if (response.ok) {
        const stats = await response.json();
        setFilterStats(stats);
      }
    } catch (error) {
      console.error('Error fetching filter stats:', error);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchSources(page, rowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
    fetchFilterStats();
  }, []);

  // Handle pagination change
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    fetchSources(newPage, rowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    fetchSources(0, newRowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
  };

  // Handle search
  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSearch = () => {
    setPage(0);
    fetchSources(0, rowsPerPage, searchTerm, riskFilter, monitoringFilter, socialMediaFilters);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle filter changes
  const handleRiskFilterChange = (event: SelectChangeEvent) => {
    setRiskFilter(event.target.value);
    setPage(0);
    fetchSources(0, rowsPerPage, searchTerm, event.target.value, monitoringFilter, socialMediaFilters);
  };

  const handleMonitoringFilterChange = (event: SelectChangeEvent) => {
    setMonitoringFilter(event.target.value);
    setPage(0);
    fetchSources(0, rowsPerPage, searchTerm, riskFilter, event.target.value, socialMediaFilters);
  };

  const handleSocialMediaFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    const updatedFilters = {
      ...socialMediaFilters,
      [name]: checked
    };
    setSocialMediaFilters(updatedFilters);
    setPage(0);
    fetchSources(0, rowsPerPage, searchTerm, riskFilter, monitoringFilter, updatedFilters);
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
      hasTikTok: false,
    });
    setPage(0);
    fetchSources(0, rowsPerPage, '', '', '', {
      hasFacebook: false,
      hasInstagram: false,
      hasLinkedIn: false,
      hasTikTok: false,
    });
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

  // Navigation helper
  const getNavigationPath = (path: string) => {
    const pathMatch = location.pathname.match(/\/organizations\/(\d+)\/projects\/(\d+)/);
    if (pathMatch) {
      const [, orgId, projId] = pathMatch;
      return `/organizations/${orgId}/projects/${projId}${path}`;
    }
    return path;
  };

  // Check if any filters are active
  const hasActiveFilters = searchTerm || riskFilter || monitoringFilter || 
    socialMediaFilters.hasFacebook || socialMediaFilters.hasInstagram || 
    socialMediaFilters.hasLinkedIn || socialMediaFilters.hasTikTok;

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: '#f8fafc' }}>
      {/* Left Sidebar - Filters */}
      <Box sx={{ 
        width: 320, 
        bgcolor: 'white', 
        borderRight: '1px solid #e2e8f0',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Filter Header */}
        <Box sx={{ p: 3, borderBottom: '1px solid #e2e8f0' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
              Filters
            </Typography>
            {hasActiveFilters && (
              <Button
                size="small"
                startIcon={<ClearIcon />}
                onClick={handleClearFilters}
                sx={{ color: '#64748b', fontSize: '0.75rem' }}
              >
                Clear all
              </Button>
            )}
          </Box>
          
          {/* Search */}
          <TextField
            fullWidth
            placeholder="Search sources..."
            value={searchTerm}
            onChange={handleSearchChange}
            onKeyPress={handleKeyPress}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: '#64748b', fontSize: 20 }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: '#f8fafc',
                '&:hover': { bgcolor: '#f1f5f9' },
                '&.Mui-focused': { bgcolor: 'white' }
              }
            }}
          />
        </Box>

        {/* Filter Content */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          <Stack spacing={3}>
            {/* Risk Classification */}
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#374151' }}>
                Risk Classification
              </Typography>
              <FormControl fullWidth size="small">
                <Select
                  value={riskFilter}
                  onChange={handleRiskFilterChange}
                  displayEmpty
                  sx={{ bgcolor: '#f8fafc' }}
                >
                  <MenuItem value="">All Classifications</MenuItem>
                  <MenuItem value="Low">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#10b981', mr: 1 }} />
                        Low Risk
                      </Box>
                      <Chip label={filterStats.riskCounts.low} size="small" variant="outlined" />
                    </Box>
                  </MenuItem>
                  <MenuItem value="Medium">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#f59e0b', mr: 1 }} />
                        Medium Risk
                      </Box>
                      <Chip label={filterStats.riskCounts.medium} size="small" variant="outlined" />
                    </Box>
                  </MenuItem>
                  <MenuItem value="High">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#ef4444', mr: 1 }} />
                        High Risk
                      </Box>
                      <Chip label={filterStats.riskCounts.high} size="small" variant="outlined" />
                    </Box>
                  </MenuItem>
                  <MenuItem value="Critical">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#dc2626', mr: 1 }} />
                        Critical Risk
                      </Box>
                      <Chip label={filterStats.riskCounts.critical} size="small" variant="outlined" />
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Close Monitoring */}
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#374151' }}>
                Monitoring Status
              </Typography>
              <FormControl fullWidth size="small">
                <Select
                  value={monitoringFilter}
                  onChange={handleMonitoringFilterChange}
                  displayEmpty
                  sx={{ bgcolor: '#f8fafc' }}
                >
                  <MenuItem value="">All Sources</MenuItem>
                  <MenuItem value="yes">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <VisibilityIcon sx={{ fontSize: 16, color: '#3b82f6', mr: 1 }} />
                        Monitored
                      </Box>
                      <Chip label={filterStats.monitoringCounts.monitored} size="small" variant="outlined" />
                    </Box>
                  </MenuItem>
                  <MenuItem value="no">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <VisibilityOffIcon sx={{ fontSize: 16, color: '#64748b', mr: 1 }} />
                        Not Monitored
                      </Box>
                      <Chip label={filterStats.monitoringCounts.unmonitored} size="small" variant="outlined" />
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Social Media Presence */}
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#374151' }}>
                Social Media Presence
              </Typography>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={socialMediaFilters.hasFacebook}
                      onChange={handleSocialMediaFilterChange}
                      name="hasFacebook"
                      size="small"
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <FacebookIcon sx={{ fontSize: 16, color: '#4267B2', mr: 1 }} />
                        <Typography variant="body2">Facebook</Typography>
                      </Box>
                      <Chip label={filterStats.socialMediaCounts.facebook} size="small" variant="outlined" />
                    </Box>
                  }
                  sx={{ mb: 1 }}
                />
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={socialMediaFilters.hasInstagram}
                      onChange={handleSocialMediaFilterChange}
                      name="hasInstagram"
                      size="small"
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <InstagramIcon sx={{ fontSize: 16, color: '#E1306C', mr: 1 }} />
                        <Typography variant="body2">Instagram</Typography>
                      </Box>
                      <Chip label={filterStats.socialMediaCounts.instagram} size="small" variant="outlined" />
                    </Box>
                  }
                  sx={{ mb: 1 }}
                />
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={socialMediaFilters.hasLinkedIn}
                      onChange={handleSocialMediaFilterChange}
                      name="hasLinkedIn"
                      size="small"
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LinkedInIcon sx={{ fontSize: 16, color: '#0077B5', mr: 1 }} />
                        <Typography variant="body2">LinkedIn</Typography>
                      </Box>
                      <Chip label={filterStats.socialMediaCounts.linkedin} size="small" variant="outlined" />
                    </Box>
                  }
                  sx={{ mb: 1 }}
                />
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={socialMediaFilters.hasTikTok}
                      onChange={handleSocialMediaFilterChange}
                      name="hasTikTok"
                      size="small"
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TikTokIcon sx={{ fontSize: 16, color: '#000', mr: 1 }} />
                        <Typography variant="body2">TikTok</Typography>
                      </Box>
                      <Chip label={filterStats.socialMediaCounts.tiktok} size="small" variant="outlined" />
                    </Box>
                  }
                />
              </FormGroup>
            </Box>
          </Stack>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Header */}
        <Box sx={{ p: 3, bgcolor: 'white', borderBottom: '1px solid #e2e8f0' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b', mb: 1 }}>
                Input Collection
              </Typography>
              <Typography variant="body1" sx={{ color: '#64748b' }}>
                Manage and track social media accounts for monitoring
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<PersonAddIcon />}
              onClick={() => navigate(getNavigationPath('/track-sources/create'))}
              sx={{ 
                bgcolor: '#3b82f6',
                '&:hover': { bgcolor: '#2563eb' },
                borderRadius: 2,
                px: 3
              }}
            >
              Add Source
            </Button>
          </Box>
          
          {/* Stats Cards */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 2 }}>
            <Card sx={{ bgcolor: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#3b82f6', mr: 2 }}>
                    <FolderIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {totalCount}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Sources
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
            <Card sx={{ bgcolor: '#fef3c7', border: '1px solid #fbbf24' }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#f59e0b', mr: 2 }}>
                    <SecurityIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {filterStats.riskCounts.high + filterStats.riskCounts.critical}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      High Risk
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
            <Card sx={{ bgcolor: '#dbeafe', border: '1px solid #3b82f6' }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#3b82f6', mr: 2 }}>
                    <VisibilityIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {filterStats.monitoringCounts.monitored}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Monitored
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
            <Card sx={{ bgcolor: '#f0fdf4', border: '1px solid #10b981' }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#10b981', mr: 2 }}>
                    <TrendingUpIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {filterStats.socialMediaCounts.facebook + filterStats.socialMediaCounts.instagram + 
                       filterStats.socialMediaCounts.linkedin + filterStats.socialMediaCounts.tiktok}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Social Accounts
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Table Content */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          <Paper sx={{ width: '100%', borderRadius: 2, overflow: 'hidden' }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : sources.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom color="text.secondary">
                  No sources found
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {hasActiveFilters ? 'Try adjusting your filters or search terms.' : 'Get started by adding your first source.'}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate(getNavigationPath('/track-sources/create'))}
                  sx={{ bgcolor: '#3b82f6', '&:hover': { bgcolor: '#2563eb' } }}
                >
                  Add Source
                </Button>
              </Box>
            ) : (
              <>
                <TableContainer>
                  <Table>
                    <TableHead sx={{ bgcolor: '#f8fafc' }}>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Source</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#374151' }}>IAC Number</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#374151' }} align="center">Social Media</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Risk Level</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Monitoring</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#374151' }} align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sources.map((source) => (
                        <TableRow key={source.id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                          <TableCell>
                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                {source.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                ID: {source.id}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {source.iac_no}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5 }}>
                              {source.instagram_link && (
                                <Tooltip title={`Instagram: ${source.instagram_link}`}>
                                  <IconButton 
                                    size="small" 
                                    onClick={() => {
                                      const url = source.instagram_link?.startsWith('http') 
                                        ? source.instagram_link 
                                        : `https://www.instagram.com/${source.instagram_link}`;
                                      window.open(url, '_blank');
                                    }}
                                    sx={{ 
                                      bgcolor: '#fce7f3', 
                                      color: '#E1306C',
                                      '&:hover': { bgcolor: '#fbcfe8' }
                                    }}
                                  >
                                    <InstagramIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              
                              {source.facebook_link && (
                                <Tooltip title={`Facebook: ${source.facebook_link}`}>
                                  <IconButton 
                                    size="small" 
                                    onClick={() => {
                                      const url = source.facebook_link?.startsWith('http') 
                                        ? source.facebook_link 
                                        : `https://www.facebook.com/${source.facebook_link}`;
                                      window.open(url, '_blank');
                                    }}
                                    sx={{ 
                                      bgcolor: '#dbeafe', 
                                      color: '#4267B2',
                                      '&:hover': { bgcolor: '#bfdbfe' }
                                    }}
                                  >
                                    <FacebookIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              
                              {source.linkedin_link && (
                                <Tooltip title={`LinkedIn: ${source.linkedin_link}`}>
                                  <IconButton 
                                    size="small" 
                                    onClick={() => {
                                      const url = source.linkedin_link?.startsWith('http') 
                                        ? source.linkedin_link 
                                        : `https://www.linkedin.com/in/${source.linkedin_link}`;
                                      window.open(url, '_blank');
                                    }}
                                    sx={{ 
                                      bgcolor: '#e0f2fe', 
                                      color: '#0077B5',
                                      '&:hover': { bgcolor: '#b3e5fc' }
                                    }}
                                  >
                                    <LinkedInIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              
                              {source.tiktok_link && (
                                <Tooltip title={`TikTok: ${source.tiktok_link}`}>
                                  <IconButton 
                                    size="small" 
                                    onClick={() => {
                                      const url = source.tiktok_link?.startsWith('http') 
                                        ? source.tiktok_link 
                                        : `https://www.tiktok.com/@${source.tiktok_link}`;
                                      window.open(url, '_blank');
                                    }}
                                    sx={{ 
                                      bgcolor: '#f3f4f6', 
                                      color: '#000',
                                      '&:hover': { bgcolor: '#e5e7eb' }
                                    }}
                                  >
                                    <TikTokIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              
                              {!source.instagram_link && !source.facebook_link && 
                               !source.linkedin_link && !source.tiktok_link && (
                                <Typography variant="body2" color="text.secondary">
                                  No accounts
                                </Typography>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            {source.risk_classification ? (
                              <Chip 
                                label={source.risk_classification} 
                                size="small" 
                                sx={{
                                  bgcolor: source.risk_classification.toLowerCase() === 'critical' ? '#fee2e2' :
                                          source.risk_classification.toLowerCase() === 'high' ? '#fef3c7' :
                                          source.risk_classification.toLowerCase() === 'medium' ? '#fef3c7' : '#f0fdf4',
                                  color: source.risk_classification.toLowerCase() === 'critical' ? '#dc2626' :
                                         source.risk_classification.toLowerCase() === 'high' ? '#d97706' :
                                         source.risk_classification.toLowerCase() === 'medium' ? '#d97706' : '#059669',
                                  fontWeight: 600
                                }}
                              />
                            ) : (
                              <Typography variant="body2" color="text.secondary">
                                Not set
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            <Chip 
                              icon={source.close_monitoring ? <VisibilityIcon /> : <VisibilityOffIcon />}
                              label={source.close_monitoring ? 'Monitored' : 'Not Monitored'} 
                              size="small" 
                              variant={source.close_monitoring ? 'filled' : 'outlined'}
                              sx={{
                                bgcolor: source.close_monitoring ? '#dbeafe' : 'transparent',
                                color: source.close_monitoring ? '#1d4ed8' : '#64748b',
                                borderColor: source.close_monitoring ? '#3b82f6' : '#cbd5e1'
                              }}
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Button
                              size="small"
                              startIcon={<EditIcon />}
                              onClick={() => navigate(getNavigationPath(`/track-sources/edit/${source.id}`))}
                              sx={{ 
                                color: '#64748b',
                                '&:hover': { 
                                  bgcolor: '#f1f5f9',
                                  color: '#334155'
                                }
                              }}
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
                  sx={{ borderTop: '1px solid #e2e8f0' }}
                />
              </>
            )}
          </Paper>
        </Box>
      </Box>

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
    </Box>
  );
};

export default TrackSourcesList;

// Keep backward compatibility alias
export { TrackSourcesList as TrackAccountsList }; 
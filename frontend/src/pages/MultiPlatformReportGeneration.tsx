import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Snackbar,
  Alert,
  Breadcrumbs,
  Link,
  Tabs,
  Tab,
  Checkbox,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Divider,
  TextField,
  InputAdornment,
  FormGroup,
  FormControlLabel,
  Chip,
  LinearProgress,
  Grid,
} from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import SearchIcon from '@mui/icons-material/Search';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import InstagramIcon from '@mui/icons-material/Instagram';
import FacebookIcon from '@mui/icons-material/Facebook';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import axios from 'axios';

// Custom icon for TikTok since Material UI doesn't have one
const TikTokIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19.321 5.562a5.122 5.122 0 0 1-3.414-1.267 5.133 5.133 0 0 1-1.348-1.75H9.953v12.137a3.373 3.373 0 0 1-6.748 0 3.373 3.373 0 0 1 3.414-3.414c.236-.01.471.018.699.084V6.86c-.25-.034-.503-.05-.756-.05a7.865 7.865 0 0 0-7.865 7.865 7.865 7.865 0 0 0 7.865 7.865 7.865 7.865 0 0 0 7.865-7.865V8.338c1.672 1.199 3.695 1.85 5.766 1.85h1.008V5.74a8.05 8.05 0 0 1-1.88-.178z" />
  </svg>
);

// Inline implementation of the API client
const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add request interceptor to include CSRF token
api.interceptors.request.use((config) => {
  // Get CSRF token from cookie if it exists
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }

  return config;
});

// Generic folder interface that works for all platforms
interface PlatformFolder {
  id: number;
  name: string;
  description: string | null;
  post_count?: number;
  created_at: string;
  updated_at: string;
}

// Report parameters interface
interface ReportParams {
  name: string;
  description: string;
  start_date: Date;
  end_date: Date;
  platform_folders: {
    instagram: number[];
    facebook: number[];
    linkedin: number[];
    tiktok: number[];
  };
}

// Tab panel component for platform folder selection
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`platform-tabpanel-${index}`}
      aria-labelledby={`platform-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const MultiPlatformReportGeneration = () => {
  const navigate = useNavigate();
  const { reportId } = useParams();
  const [activeTab, setActiveTab] = useState(0);
  
  // Loading states
  const [loading, setLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  
  // Data states
  const [instagramFolders, setInstagramFolders] = useState<PlatformFolder[]>([]);
  const [facebookFolders, setFacebookFolders] = useState<PlatformFolder[]>([]);
  const [linkedinFolders, setLinkedinFolders] = useState<PlatformFolder[]>([]);
  const [tiktokFolders, setTiktokFolders] = useState<PlatformFolder[]>([]);
  
  // Search filters
  const [instagramSearch, setInstagramSearch] = useState('');
  const [facebookSearch, setFacebookSearch] = useState('');
  const [linkedinSearch, setLinkedinSearch] = useState('');
  const [tiktokSearch, setTiktokSearch] = useState('');
  
  // Report data
  const [reportData, setReportData] = useState<any>(null);
  const [reportParams, setReportParams] = useState<ReportParams>({
    name: '',
    description: '',
    start_date: new Date(new Date().setDate(new Date().getDate() - 30)), // Default to last 30 days
    end_date: new Date(),
    platform_folders: {
      instagram: [],
      facebook: [],
      linkedin: [],
      tiktok: [],
    },
  });
  
  // Snackbar state
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info' | 'warning'
  });

  // Initial data load
  useEffect(() => {
    if (reportId) {
      fetchReportDetails();
    }
    fetchAllPlatformFolders();
  }, [reportId]);

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbar({
      open: true,
      message,
      severity,
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const fetchReportDetails = async () => {
    try {
      setReportLoading(true);
      const response = await api.get(`/api/track-accounts/reports/${reportId}/`);
      if (response.status === 200) {
        const data = response.data;
        setReportData(data);
        
        // Parse source_folders JSON if it exists
        let platformFolders = {
          instagram: [],
          facebook: [],
          linkedin: [],
          tiktok: [],
        };
        
        if (data.source_folders) {
          try {
            const sourceFolders = JSON.parse(data.source_folders);
            if (typeof sourceFolders === 'object') {
              // Handle both formats - array or object
              if (Array.isArray(sourceFolders)) {
                // Legacy format - assume these are Instagram folders
                platformFolders.instagram = sourceFolders as number[];
              } else {
                // New format with platform keys
                platformFolders = {
                  instagram: sourceFolders.instagram || [],
                  facebook: sourceFolders.facebook || [],
                  linkedin: sourceFolders.linkedin || [],
                  tiktok: sourceFolders.tiktok || [],
                };
              }
            }
          } catch (e) {
            console.error('Error parsing source folders:', e);
          }
        }
        
        setReportParams(prev => ({
          ...prev,
          name: data.name,
          description: data.description || '',
          start_date: new Date(data.start_date),
          end_date: new Date(data.end_date),
          platform_folders: platformFolders,
        }));
      }
    } catch (error) {
      console.error('Error fetching report details:', error);
      showSnackbar('Failed to load report details', 'error');
    } finally {
      setReportLoading(false);
    }
  };

  // Function to fetch all platform folders
  const fetchAllPlatformFolders = () => {
    fetchInstagramFolders();
    fetchFacebookFolders();
    fetchLinkedinFolders();
    fetchTiktokFolders();
  };

  const fetchInstagramFolders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/instagram-data/folders/');
      if (response.status === 200) {
        const folderData = response.data.results || response.data;
        setInstagramFolders(folderData);
      }
    } catch (error) {
      console.error('Error fetching Instagram folders:', error);
      showSnackbar('Failed to load Instagram folders', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchFacebookFolders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/facebook-data/folders/');
      if (response.status === 200) {
        const folderData = response.data.results || response.data;
        setFacebookFolders(folderData);
      }
    } catch (error) {
      console.error('Error fetching Facebook folders:', error);
      showSnackbar('Failed to load Facebook folders', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchLinkedinFolders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/linkedin-data/folders/');
      if (response.status === 200) {
        const folderData = response.data.results || response.data;
        setLinkedinFolders(folderData);
      }
    } catch (error) {
      console.error('Error fetching LinkedIn folders:', error);
      showSnackbar('Failed to load LinkedIn folders', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchTiktokFolders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/tiktok-data/folders/');
      if (response.status === 200) {
        const folderData = response.data.results || response.data;
        setTiktokFolders(folderData);
      }
    } catch (error) {
      console.error('Error fetching TikTok folders:', error);
      showSnackbar('Failed to load TikTok folders', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // General input change handler for report params
  const handleInputChange = (name: keyof Omit<ReportParams, 'platform_folders'>, value: any) => {
    setReportParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle date changes
  const handleDateChange = (field: 'start_date' | 'end_date', date: Date | null) => {
    if (date) {
      handleInputChange(field, date);
    }
  };

  // Toggle folder selection for each platform
  const toggleInstagramFolder = (folderId: number) => {
    setReportParams(prev => {
      const currentFolders = [...prev.platform_folders.instagram];
      const newFolders = currentFolders.includes(folderId)
        ? currentFolders.filter(id => id !== folderId)
        : [...currentFolders, folderId];
      
      return {
        ...prev,
        platform_folders: {
          ...prev.platform_folders,
          instagram: newFolders
        }
      };
    });
  };

  const toggleFacebookFolder = (folderId: number) => {
    setReportParams(prev => {
      const currentFolders = [...prev.platform_folders.facebook];
      const newFolders = currentFolders.includes(folderId)
        ? currentFolders.filter(id => id !== folderId)
        : [...currentFolders, folderId];
      
      return {
        ...prev,
        platform_folders: {
          ...prev.platform_folders,
          facebook: newFolders
        }
      };
    });
  };

  const toggleLinkedinFolder = (folderId: number) => {
    setReportParams(prev => {
      const currentFolders = [...prev.platform_folders.linkedin];
      const newFolders = currentFolders.includes(folderId)
        ? currentFolders.filter(id => id !== folderId)
        : [...currentFolders, folderId];
      
      return {
        ...prev,
        platform_folders: {
          ...prev.platform_folders,
          linkedin: newFolders
        }
      };
    });
  };

  const toggleTiktokFolder = (folderId: number) => {
    setReportParams(prev => {
      const currentFolders = [...prev.platform_folders.tiktok];
      const newFolders = currentFolders.includes(folderId)
        ? currentFolders.filter(id => id !== folderId)
        : [...currentFolders, folderId];
      
      return {
        ...prev,
        platform_folders: {
          ...prev.platform_folders,
          tiktok: newFolders
        }
      };
    });
  };

  // Filter folders by search term for each platform
  const filteredInstagramFolders = instagramFolders.filter(folder =>
    folder.name.toLowerCase().includes(instagramSearch.toLowerCase()) ||
    (folder.description && folder.description.toLowerCase().includes(instagramSearch.toLowerCase()))
  );

  const filteredFacebookFolders = facebookFolders.filter(folder =>
    folder.name.toLowerCase().includes(facebookSearch.toLowerCase()) ||
    (folder.description && folder.description.toLowerCase().includes(facebookSearch.toLowerCase()))
  );

  const filteredLinkedinFolders = linkedinFolders.filter(folder =>
    folder.name.toLowerCase().includes(linkedinSearch.toLowerCase()) ||
    (folder.description && folder.description.toLowerCase().includes(linkedinSearch.toLowerCase()))
  );

  const filteredTiktokFolders = tiktokFolders.filter(folder =>
    folder.name.toLowerCase().includes(tiktokSearch.toLowerCase()) ||
    (folder.description && folder.description.toLowerCase().includes(tiktokSearch.toLowerCase()))
  );

  // Navigation handlers
  const handleBackToReports = () => {
    navigate('/report-folders');
  };

  // Generate report
  const handleGenerateReport = async () => {
    // Check if any folders are selected
    const totalSelectedFolders = 
      reportParams.platform_folders.instagram.length +
      reportParams.platform_folders.facebook.length +
      reportParams.platform_folders.linkedin.length +
      reportParams.platform_folders.tiktok.length;
    
    if (totalSelectedFolders === 0) {
      showSnackbar('Please select at least one folder', 'error');
      return;
    }

    // Validate other required fields
    if (!reportParams.name) {
      showSnackbar('Please enter a report name', 'error');
      return;
    }

    try {
      setGenerating(true);

      let response;
      if (reportId) {
        // Update existing report
        response = await api.put(`/api/track-accounts/reports/${reportId}/`, {
          name: reportParams.name,
          description: reportParams.description,
          start_date: reportParams.start_date.toISOString(),
          end_date: reportParams.end_date.toISOString(),
          source_folders: JSON.stringify(reportParams.platform_folders)
        });
      } else {
        // Create new report
        response = await api.post('/api/track-accounts/reports/', {
          name: reportParams.name,
          description: reportParams.description,
          start_date: reportParams.start_date.toISOString(),
          end_date: reportParams.end_date.toISOString(),
          source_folders: JSON.stringify(reportParams.platform_folders),
          total_posts: 0,
          matched_posts: 0
        });
      }

      if (response.status === 200 || response.status === 201) {
        const newReportId = response.data.id || reportId;
        
        // Generate the report content
        const generateResponse = await api.post(`/api/track-accounts/reports/${newReportId}/generate_report/`, {
          platform_folders: reportParams.platform_folders,
          start_date: reportParams.start_date.toISOString(),
          end_date: reportParams.end_date.toISOString(),
          name: reportParams.name,
          description: reportParams.description
        });

        if (generateResponse.status === 200 || generateResponse.status === 201) {
          showSnackbar('Report generated successfully', 'success');
          // Navigate to the report detail page
          setTimeout(() => {
            navigate(`/report-folders/${newReportId}`);
          }, 1500);
        } else {
          throw new Error('Failed to generate report content');
        }
      } else {
        throw new Error('Failed to create/update report');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      showSnackbar('Failed to generate report', 'error');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
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
          onClick={handleBackToReports}
          style={{ cursor: 'pointer' }}
        >
          <DescriptionIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Report Folders
        </Link>
        <Typography
          sx={{ display: 'flex', alignItems: 'center' }}
          color="text.primary"
        >
          {reportId ? 'Edit Report' : 'New Multi-Platform Report'}
        </Typography>
      </Breadcrumbs>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          {reportId ? 'Edit Multi-Platform Report' : 'Create Multi-Platform Report'}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={handleBackToReports}
        >
          Back to Reports
        </Button>
      </Box>

      {/* Report Details Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Report Details
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            label="Report Name"
            value={reportParams.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            fullWidth
            required
          />
          <TextField
            label="Description"
            value={reportParams.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            fullWidth
            multiline
            rows={2}
          />
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <DatePicker
                label="Start Date"
                value={reportParams.start_date}
                onChange={(date) => handleDateChange('start_date', date)}
              />
              <DatePicker
                label="End Date"
                value={reportParams.end_date}
                onChange={(date) => handleDateChange('end_date', date)}
              />
            </Box>
          </LocalizationProvider>
        </Box>
      </Paper>

      {/* Platform Selection Tabs */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Select Platform Data
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            aria-label="platform tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab 
              icon={<InstagramIcon />} 
              label="Instagram" 
              iconPosition="start" 
              id="platform-tab-0"
              aria-controls="platform-tabpanel-0"
            />
            <Tab 
              icon={<FacebookIcon />} 
              label="Facebook" 
              iconPosition="start"
              id="platform-tab-1"
              aria-controls="platform-tabpanel-1"
            />
            <Tab 
              icon={<LinkedInIcon />} 
              label="LinkedIn" 
              iconPosition="start"
              id="platform-tab-2"
              aria-controls="platform-tabpanel-2"
            />
            <Tab 
              icon={<TikTokIcon />} 
              label="TikTok" 
              iconPosition="start"
              id="platform-tab-3"
              aria-controls="platform-tabpanel-3"
            />
          </Tabs>
        </Box>

        {/* Instagram Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Select Instagram Folders ({reportParams.platform_folders.instagram.length} selected)
            </Typography>
            <TextField
              placeholder="Search folders..."
              value={instagramSearch}
              onChange={(e) => setInstagramSearch(e.target.value)}
              fullWidth
              variant="outlined"
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />
            
            {loading ? (
              <CircularProgress />
            ) : filteredInstagramFolders.length === 0 ? (
              <Typography>No Instagram folders found</Typography>
            ) : (
              <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                <List dense>
                  {filteredInstagramFolders.map((folder) => (
                    <React.Fragment key={folder.id}>
                      <ListItemButton
                        onClick={() => toggleInstagramFolder(folder.id)}
                        selected={reportParams.platform_folders.instagram.includes(folder.id)}
                        dense
                      >
                        <ListItemIcon>
                          <Checkbox
                            edge="start"
                            checked={reportParams.platform_folders.instagram.includes(folder.id)}
                            tabIndex={-1}
                            disableRipple
                          />
                        </ListItemIcon>
                        <ListItemText 
                          primary={folder.name} 
                          secondary={
                            <>
                              {folder.description && <span>{folder.description}<br /></span>}
                              <span>{typeof folder.post_count === 'number' ? folder.post_count : 'Unknown'} posts</span>
                            </>
                          }
                        />
                        <InstagramIcon color="action" />
                      </ListItemButton>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            )}
          </Box>
        </TabPanel>

        {/* Facebook Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Select Facebook Folders ({reportParams.platform_folders.facebook.length} selected)
            </Typography>
            <TextField
              placeholder="Search folders..."
              value={facebookSearch}
              onChange={(e) => setFacebookSearch(e.target.value)}
              fullWidth
              variant="outlined"
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />
            
            {loading ? (
              <CircularProgress />
            ) : filteredFacebookFolders.length === 0 ? (
              <Typography>No Facebook folders found</Typography>
            ) : (
              <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                <List dense>
                  {filteredFacebookFolders.map((folder) => (
                    <React.Fragment key={folder.id}>
                      <ListItemButton
                        onClick={() => toggleFacebookFolder(folder.id)}
                        selected={reportParams.platform_folders.facebook.includes(folder.id)}
                        dense
                      >
                        <ListItemIcon>
                          <Checkbox
                            edge="start"
                            checked={reportParams.platform_folders.facebook.includes(folder.id)}
                            tabIndex={-1}
                            disableRipple
                          />
                        </ListItemIcon>
                        <ListItemText 
                          primary={folder.name} 
                          secondary={
                            <>
                              {folder.description && <span>{folder.description}<br /></span>}
                              <span>{typeof folder.post_count === 'number' ? folder.post_count : 'Unknown'} posts</span>
                            </>
                          }
                        />
                        <FacebookIcon color="action" />
                      </ListItemButton>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            )}
          </Box>
        </TabPanel>

        {/* LinkedIn Tab */}
        <TabPanel value={activeTab} index={2}>
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Select LinkedIn Folders ({reportParams.platform_folders.linkedin.length} selected)
            </Typography>
            <TextField
              placeholder="Search folders..."
              value={linkedinSearch}
              onChange={(e) => setLinkedinSearch(e.target.value)}
              fullWidth
              variant="outlined"
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />
            
            {loading ? (
              <CircularProgress />
            ) : filteredLinkedinFolders.length === 0 ? (
              <Typography>No LinkedIn folders found</Typography>
            ) : (
              <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                <List dense>
                  {filteredLinkedinFolders.map((folder) => (
                    <React.Fragment key={folder.id}>
                      <ListItemButton
                        onClick={() => toggleLinkedinFolder(folder.id)}
                        selected={reportParams.platform_folders.linkedin.includes(folder.id)}
                        dense
                      >
                        <ListItemIcon>
                          <Checkbox
                            edge="start"
                            checked={reportParams.platform_folders.linkedin.includes(folder.id)}
                            tabIndex={-1}
                            disableRipple
                          />
                        </ListItemIcon>
                        <ListItemText 
                          primary={folder.name} 
                          secondary={
                            <>
                              {folder.description && <span>{folder.description}<br /></span>}
                              <span>{typeof folder.post_count === 'number' ? folder.post_count : 'Unknown'} posts</span>
                            </>
                          }
                        />
                        <LinkedInIcon color="action" />
                      </ListItemButton>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            )}
          </Box>
        </TabPanel>

        {/* TikTok Tab */}
        <TabPanel value={activeTab} index={3}>
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Select TikTok Folders ({reportParams.platform_folders.tiktok.length} selected)
            </Typography>
            <TextField
              placeholder="Search folders..."
              value={tiktokSearch}
              onChange={(e) => setTiktokSearch(e.target.value)}
              fullWidth
              variant="outlined"
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />
            
            {loading ? (
              <CircularProgress />
            ) : filteredTiktokFolders.length === 0 ? (
              <Typography>No TikTok folders found</Typography>
            ) : (
              <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                <List dense>
                  {filteredTiktokFolders.map((folder) => (
                    <React.Fragment key={folder.id}>
                      <ListItemButton
                        onClick={() => toggleTiktokFolder(folder.id)}
                        selected={reportParams.platform_folders.tiktok.includes(folder.id)}
                        dense
                      >
                        <ListItemIcon>
                          <Checkbox
                            edge="start"
                            checked={reportParams.platform_folders.tiktok.includes(folder.id)}
                            tabIndex={-1}
                            disableRipple
                          />
                        </ListItemIcon>
                        <ListItemText 
                          primary={folder.name} 
                          secondary={
                            <>
                              {folder.description && <span>{folder.description}<br /></span>}
                              <span>{typeof folder.post_count === 'number' ? folder.post_count : 'Unknown'} posts</span>
                            </>
                          }
                        />
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <TikTokIcon />
                        </Box>
                      </ListItemButton>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            )}
          </Box>
        </TabPanel>
      </Paper>

      {/* Generate Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={handleGenerateReport}
          disabled={generating}
          sx={{ minWidth: 200 }}
        >
          {generating ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Generating...
            </>
          ) : (
            reportId ? 'Update Report' : 'Generate Report'
          )}
        </Button>
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
    </Container>
  );
};

export default MultiPlatformReportGeneration; 
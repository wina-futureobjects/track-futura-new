import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  TextField,
  Grid as MuiGrid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Snackbar,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  Stack,
  Tooltip,
  Breadcrumbs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  FormHelperText,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextareaAutosize
} from '@mui/material';
import { Link } from 'react-router-dom';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';
import DateRangeIcon from '@mui/icons-material/DateRange';
import HomeIcon from '@mui/icons-material/Home';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicVideoIcon from '@mui/icons-material/MusicVideo';
import FolderIcon from '@mui/icons-material/Folder';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';

// Create a Grid component that inherits from MuiGrid to fix type issues
const Grid = (props: any) => <MuiGrid {...props} />;

// Interfaces
interface Folder {
  id: number;
  name: string;
  description: string | null;
}

interface ScraperRequest {
  id: number;
  platform: 'facebook' | 'instagram' | 'tiktok' | 'linkedin';
  content_type: 'post' | 'reel' | 'profile';
  target_url: string;
  num_of_posts: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  request_id: string | null;
  error_message: string | null;
  folder_id: number | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  start_date: string | null;
  end_date: string | null;
}

interface BrightdataConfig {
  id: number;
  name: string;
  is_active: boolean;
}

const BrightdataScraper = () => {
  // State for scraper form
  const [targetUrl, setTargetUrl] = useState('');
  const [platform, setPlatform] = useState<'facebook' | 'instagram' | 'tiktok' | 'linkedin'>('facebook');
  const [contentType, setContentType] = useState<'post' | 'reel' | 'profile'>('post');
  const [numPosts, setNumPosts] = useState(10);
  const [folderId, setFolderId] = useState<number | null>(null);
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  
  // State for data loading
  const [requests, setRequests] = useState<ScraperRequest[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [configs, setConfigs] = useState<BrightdataConfig[]>([]);
  const [hasActiveConfig, setHasActiveConfig] = useState(false);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [urlError, setUrlError] = useState<string | null>(null);
  
  // State for API response dialog
  const [apiResponseDialog, setApiResponseDialog] = useState(false);
  const [apiResponseText, setApiResponseText] = useState<string>('');
  const [testingConfig, setTestingConfig] = useState(false);
  
  // Load data on component mount
  useEffect(() => {
    fetchRequests();
    fetchFolders();
    fetchConfigs();
  }, []);
  
  // Fetch all scraper requests
  const fetchRequests = async () => {
    try {
      setRefreshing(true);
      const response = await fetch('/api/brightdata/requests/');
      if (!response.ok) {
        throw new Error('Failed to fetch scraper requests');
      }
      const responseData = await response.json();
      
      // Handle paginated response format (results array) or direct array
      const data = responseData.results || responseData;
      
      // Ensure data is an array before setting state
      setRequests(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching requests:', error);
      setError('Failed to load scraper requests');
      // Set requests to empty array on error
      setRequests([]);
    } finally {
      setRefreshing(false);
    }
  };
  
  // Fetch folders for the dropdown
  const fetchFolders = async () => {
    try {
      const platformEndpoint = platform === 'facebook' 
        ? 'facebook-data' 
        : platform === 'instagram' 
          ? 'instagram-data' 
          : platform === 'linkedin' 
            ? 'linkedin-data' 
            : 'tiktok-data';
            
      const response = await fetch(`/api/${platformEndpoint}/folders/`);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${platform} folders`);
      }
      const responseData = await response.json();
      
      // Handle paginated response format (results array) or direct array
      const data = responseData.results || responseData;
      
      // Ensure data is an array before setting state
      setFolders(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching folders:', error);
      // Set folders to empty array on error
      setFolders([]);
    }
  };
  
  // Fetch Brightdata configurations
  const fetchConfigs = async () => {
    try {
      const response = await fetch('/api/brightdata/configs/');
      if (!response.ok) {
        throw new Error('Failed to fetch Brightdata configurations');
      }
      const responseData = await response.json();
      
      // Handle paginated response format (results array) or direct array
      const data = responseData.results || responseData;
      
      // Ensure data is an array before setting state
      const configsArray = Array.isArray(data) ? data : [];
      setConfigs(configsArray);
      
      // Check if there's an active configuration
      const hasActive = configsArray.some((config: BrightdataConfig) => config.is_active);
      setHasActiveConfig(hasActive);
      
      if (!hasActive && configsArray.length > 0) {
        setError('No active Brightdata configuration found. Please set one in the settings.');
      }
    } catch (error) {
      console.error('Error fetching configs:', error);
      setError('Failed to load Brightdata configurations');
      setConfigs([]);
      setHasActiveConfig(false);
    }
  };
  
  // Update folders when platform changes
  useEffect(() => {
    fetchFolders();
  }, [platform]);
  
  // Validate URL
  const validateUrl = (url: string) => {
    if (!url) {
      setUrlError('URL is required');
      return false;
    }
    
    // Basic URL validation
    try {
      new URL(url);
      setUrlError(null);
      return true;
    } catch (e) {
      setUrlError('Please enter a valid URL');
      return false;
    }
  };
  
  // Handle form submission to trigger scraping
  const handleTriggerScrape = async () => {
    if (!validateUrl(targetUrl)) {
      return;
    }
    
    if (!hasActiveConfig) {
      setError('No active Brightdata configuration found. Please configure one in the settings.');
      return;
    }
    
    try {
      setLoading(true);
      
      const payload: any = {
        target_url: targetUrl,
        platform,
        content_type: contentType,
        num_of_posts: numPosts
      };
      
      // Add optional parameters if provided
      if (folderId) {
        payload.folder_id = folderId;
      }
      
      if (startDate) {
        // Format date as YYYY-MM-DD for the backend
        const year = startDate.getFullYear();
        const month = String(startDate.getMonth() + 1).padStart(2, '0');
        const day = String(startDate.getDate()).padStart(2, '0');
        payload.start_date = `${year}-${month}-${day}`;
      }
      
      if (endDate) {
        // Format date as YYYY-MM-DD for the backend
        const year = endDate.getFullYear();
        const month = String(endDate.getMonth() + 1).padStart(2, '0');
        const day = String(endDate.getDate()).padStart(2, '0');
        payload.end_date = `${year}-${month}-${day}`;
      }
      
      // Determine the endpoint based on the platform
      const endpoint = platform === 'facebook' 
        ? 'trigger_facebook_scrape' 
        : platform === 'instagram'
          ? 'trigger_instagram_scrape'
          : platform === 'linkedin'
            ? 'trigger_linkedin_scrape'
            : 'trigger_tiktok_scrape';
      
      // DEBUG: Log the full request payload
      console.log('DEBUG - Request details:');
      console.log('API Endpoint:', `/api/brightdata/requests/${endpoint}/`);
      console.log('Request payload:', JSON.stringify(payload, null, 2));
      console.log('Content type:', contentType);
      console.log('Platform:', platform);
      console.log('Target URL:', targetUrl);
      if (startDate) console.log('Start date:', payload.start_date);
      if (endDate) console.log('End date:', payload.end_date);
      if (folderId) console.log('Folder ID:', folderId);
      
      const response = await fetch(`/api/brightdata/requests/${endpoint}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      
      // Parse response data even for error responses
      let responseData;
      let responseText = '';
      try {
        const textResponse = await response.text();
        responseText = textResponse;
        setApiResponseText(textResponse); // Store raw response text
        
        if (textResponse.trim()) {
          responseData = JSON.parse(textResponse);
        } else {
          responseData = { error: 'Empty response from server' };
        }
      } catch (parseError) {
        console.error('Error parsing response:', parseError);
        responseData = { 
          error: 'Failed to parse server response', 
          details: parseError instanceof Error ? parseError.message : String(parseError),
          raw_response: responseText
        };
      }
      
      if (!response.ok) {
        // Try to extract a meaningful error message from the response
        let errorMessage = 'Server error';
        
        if (responseData) {
          if (typeof responseData === 'object' && responseData !== null) {
            errorMessage = responseData.error || 
                          responseData.detail || 
                          responseData.message || 
                          `Server error (${response.status})`;
                          
            // Include raw response if available
            if (responseData.raw_response) {
              console.error('Server raw response:', responseData.raw_response);
            }
            
            // Include Brightdata error details if available
            if (responseData.brightdata_response && typeof responseData.brightdata_response === 'object') {
              console.error('Brightdata response:', responseData.brightdata_response);
            }
          } else {
            errorMessage = `Server error (${response.status}): ${JSON.stringify(responseData)}`;
          }
        }
        
        console.error('Server error response:', responseData);
        throw new Error(errorMessage);
      }
      
      console.log('Scraper response:', responseData);
      setSuccessMessage('Scraper triggered successfully!');
      
      // Show the API response dialog
      setApiResponseDialog(true);
      
      // Refresh the list of requests
      fetchRequests();
      
      // Reset form
      setTargetUrl('');
    } catch (error: any) {
      console.error('Error triggering scraper:', error);
      
      // Show a more user-friendly error message
      const errorMessage = error.message || 'Failed to trigger scraper. Please try again.';
      
      if (error.message?.includes('NetworkError') || error.message?.includes('Failed to fetch')) {
        setError('Network error. Please check your internet connection and try again.');
      } else if (errorMessage.includes('Server error (500)')) {
        setError('Internal server error. This might be due to invalid inputs or configuration issues. Please verify your input data.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Handle closing API response dialog
  const handleCloseApiResponseDialog = () => {
    setApiResponseDialog(false);
  };
  
  // Handle snackbar close
  const handleCloseSnackbar = () => {
    setError(null);
    setSuccessMessage(null);
  };
  
  // Handle platform change
  const handlePlatformChange = (event: SelectChangeEvent) => {
    const newPlatform = event.target.value as 'facebook' | 'instagram' | 'tiktok' | 'linkedin';
    setPlatform(newPlatform);
    setFolderId(null); // Reset folder selection when platform changes
  };
  
  // Handle content type change
  const handleContentTypeChange = (event: SelectChangeEvent) => {
    setContentType(event.target.value as 'post' | 'reel' | 'profile');
  };
  
  // Handle folder change
  const handleFolderChange = (event: SelectChangeEvent) => {
    setFolderId(event.target.value === '' ? null : Number(event.target.value));
  };
  
  // Get platform icon
  const getPlatformIcon = (platformType: string) => {
    switch (platformType) {
      case 'facebook':
        return <FacebookIcon />;
      case 'instagram':
        return <InstagramIcon />;
      case 'linkedin':
        return <LinkedInIcon />;
      case 'tiktok':
        return <MusicVideoIcon />;
      default:
        return <InfoIcon />;
    }
  };
  
  // Test Brightdata configuration
  const testBrightdataConfig = async () => {
    try {
      setTestingConfig(true);
      
      const response = await fetch('/api/brightdata/configs/active/');
      
      // Parse response
      let textResponse = await response.text();
      setApiResponseText(textResponse);
      
      if (!response.ok) {
        setError('Failed to retrieve active Brightdata configuration');
      } else {
        const configData = JSON.parse(textResponse);
        
        // Now test the actual API
        const testResponse = await fetch('/api/brightdata/requests/test_connection/', {
          method: 'POST',
        });
        
        const testResponseText = await testResponse.text();
        setApiResponseText(testResponseText);
        
        if (testResponse.ok) {
          setSuccessMessage('Brightdata connection test successful!');
        } else {
          setError('Brightdata API connection test failed. Check the response for details.');
        }
      }
      
      // Show the dialog with results
      setApiResponseDialog(true);
      
    } catch (error: any) {
      console.error('Error testing configuration:', error);
      setError(error.message || 'Error testing Brightdata configuration');
    } finally {
      setTestingConfig(false);
    }
  };
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none', color: 'inherit' }}>
            <HomeIcon sx={{ mr: 0.5 }} fontSize="small" />
            Home
          </Link>
          <Typography sx={{ display: 'flex', alignItems: 'center' }} color="text.primary">
            <AutoAwesomeIcon sx={{ mr: 0.5 }} fontSize="small" />
            Brightdata Scraper
          </Typography>
        </Breadcrumbs>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Brightdata Scraper
          </Typography>
          <Button
            variant="outlined"
            onClick={testBrightdataConfig}
            disabled={testingConfig}
            startIcon={testingConfig ? <CircularProgress size={20} /> : null}
          >
            Test API Connection
          </Button>
        </Box>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Automate scraping of social media data using Brightdata's API services.
        </Typography>
      </Box>
      
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Trigger New Scraper
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Set up a new scraping job to collect data from social media platforms. The data will be automatically imported into your selected folder.
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Profile/Page URL"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="e.g., https://www.facebook.com/LeBron/"
                variant="outlined"
                error={!!urlError}
                helperText={urlError}
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="platform-select-label">Platform</InputLabel>
                <Select
                  labelId="platform-select-label"
                  value={platform}
                  label="Platform"
                  onChange={handlePlatformChange}
                  disabled={loading}
                  startAdornment={
                    <Box sx={{ mr: 1, display: 'flex', alignItems: 'center' }}>
                      {getPlatformIcon(platform)}
                    </Box>
                  }
                >
                  <MenuItem value="facebook">
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <FacebookIcon />
                      <span>Facebook</span>
                    </Stack>
                  </MenuItem>
                  <MenuItem value="instagram">
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <InstagramIcon />
                      <span>Instagram</span>
                    </Stack>
                  </MenuItem>
                  <MenuItem value="linkedin">
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <LinkedInIcon />
                      <span>LinkedIn</span>
                    </Stack>
                  </MenuItem>
                  <MenuItem value="tiktok">
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <MusicVideoIcon />
                      <span>TikTok</span>
                    </Stack>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="content-type-select-label">Content Type</InputLabel>
                <Select
                  labelId="content-type-select-label"
                  value={contentType}
                  label="Content Type"
                  onChange={handleContentTypeChange}
                  disabled={loading}
                >
                  <MenuItem value="post">Post</MenuItem>
                  <MenuItem value="reel">Reel</MenuItem>
                  <MenuItem value="profile">Profile</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Number of Posts"
                type="number"
                value={numPosts}
                onChange={(e) => setNumPosts(Number(e.target.value))}
                InputProps={{ inputProps: { min: 1, max: 100 } }}
                variant="outlined"
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="folder-select-label">Save to Folder</InputLabel>
                <Select
                  labelId="folder-select-label"
                  value={folderId !== null ? folderId.toString() : ''}
                  label="Save to Folder"
                  onChange={handleFolderChange}
                  disabled={loading}
                  startAdornment={
                    folderId !== null ? (
                      <Box sx={{ mr: 1, display: 'flex', alignItems: 'center' }}>
                        <FolderIcon />
                      </Box>
                    ) : null
                  }
                >
                  <MenuItem value="">
                    <em>None (Create a new folder)</em>
                  </MenuItem>
                  {Array.isArray(folders) && folders.map((folder) => (
                    <MenuItem key={folder.id} value={folder.id.toString()}>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <FolderIcon />
                        <span>{folder.name}</span>
                      </Stack>
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>
                  Select a folder to save the scraped data
                </FormHelperText>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Date Range (Optional)
              </Typography>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Start Date"
                    value={startDate}
                    onChange={(newValue) => setStartDate(newValue)}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        disabled: loading,
                        helperText: "Select a start date (will be converted to MM-DD-YYYY for Brightdata)"
                      }
                    }}
                  />
                  <DatePicker
                    label="End Date"
                    value={endDate}
                    onChange={(newValue) => setEndDate(newValue)}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        disabled: loading,
                        helperText: "Select an end date (will be converted to MM-DD-YYYY for Brightdata)"
                      }
                    }}
                  />
                </LocalizationProvider>
              </Stack>
              <FormHelperText>
                Dates will be sent to Brightdata API in MM-DD-YYYY format (e.g., 05-31-2025)
              </FormHelperText>
            </Grid>
            
            <Grid item xs={12}>
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <Button 
                  variant="contained" 
                  color="primary" 
                  startIcon={loading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
                  onClick={handleTriggerScrape}
                  disabled={loading || !hasActiveConfig}
                >
                  {loading ? 'Triggering...' : 'Trigger Scraper'}
                </Button>
              </Stack>
              {!hasActiveConfig && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  No active Brightdata configuration found. Please <Link to="/brightdata-settings">configure one</Link> first.
                </Alert>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {/* Table of scraped requests will be added in the next edit */}
      <Card>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">
              Scraper Requests
            </Typography>
            <Button 
              startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
              onClick={fetchRequests}
              disabled={refreshing}
            >
              Refresh
            </Button>
          </Stack>
          
          {refreshing && requests.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Platform</TableCell>
                    <TableCell>Target URL</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Completed</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {!Array.isArray(requests) || requests.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No scraper requests found. Trigger a new scrape above.
                      </TableCell>
                    </TableRow>
                  ) : (
                    requests.map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>
                          <Stack direction="row" alignItems="center" spacing={1}>
                            {getPlatformIcon(request.platform)}
                            <span>{request.platform.charAt(0).toUpperCase() + request.platform.slice(1)}</span>
                          </Stack>
                        </TableCell>
                        <TableCell>
                          <Tooltip title={request.target_url}>
                            <Link 
                              to={request.target_url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              style={{ display: 'flex', alignItems: 'center' }}
                            >
                              {request.target_url.length > 30 
                                ? request.target_url.substring(0, 30) + '...' 
                                : request.target_url}
                              <OpenInNewIcon fontSize="small" sx={{ ml: 0.5 }} />
                            </Link>
                          </Tooltip>
                        </TableCell>
                        <TableCell>{request.content_type}</TableCell>
                        <TableCell>
                          <Chip 
                            label={request.status} 
                            color={
                              request.status === 'completed' 
                                ? 'success' 
                                : request.status === 'failed' 
                                  ? 'error' 
                                  : request.status === 'processing' 
                                    ? 'primary' 
                                    : 'default'
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{new Date(request.created_at).toLocaleString()}</TableCell>
                        <TableCell>
                          {request.completed_at 
                            ? new Date(request.completed_at).toLocaleString() 
                            : request.status === 'failed' 
                              ? 'Failed' 
                              : 'In progress'}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
      
      {/* API Response Dialog */}
      <Dialog
        open={apiResponseDialog}
        onClose={handleCloseApiResponseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Brightdata API Response</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            This is the response from the API call. You can use this for debugging.
          </DialogContentText>
          
          {/* Try to parse and show structured response */}
          {apiResponseText && (
            <>
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 2 }}>
                Response Overview
              </Typography>
              
              <Box 
                sx={{ 
                  backgroundColor: '#f5f5f5', 
                  p: 2, 
                  borderRadius: 1,
                  mb: 2,
                  border: '1px solid #e0e0e0' 
                }}
              >
                {(() => {
                  try {
                    const parsedResponse = JSON.parse(apiResponseText);
                    
                    // Display status or error message
                    if (parsedResponse.status) {
                      return (
                        <Typography color="success.main">
                          Status: {parsedResponse.status}
                        </Typography>
                      );
                    } else if (parsedResponse.error) {
                      return (
                        <Typography color="error">
                          Error: {parsedResponse.error}
                          {parsedResponse.details && <Box component="div">Details: {parsedResponse.details}</Box>}
                          {parsedResponse.error_type && <Box component="div">Type: {parsedResponse.error_type}</Box>}
                        </Typography>
                      );
                    }
                    
                    // For other response formats
                    return (
                      <Box>
                        {Object.entries(parsedResponse).map(([key, value]) => (
                          <Typography key={key}>
                            <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </Typography>
                        ))}
                      </Box>
                    );
                  } catch (e) {
                    // If we can't parse the response, show it as text
                    return (
                      <Typography color="warning.main">
                        Unparseable Response: {apiResponseText}
                      </Typography>
                    );
                  }
                })()}
              </Box>
              
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 2 }}>
                Raw Response (JSON)
              </Typography>
            </>
          )}
          
          <TextareaAutosize
            style={{ 
              width: '100%', 
              minHeight: '300px', 
              padding: '8px',
              fontFamily: 'monospace',
              fontSize: '14px'
            }}
            value={apiResponseText}
            readOnly
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseApiResponseDialog}>Close</Button>
          <Button 
            onClick={() => {
              navigator.clipboard.writeText(apiResponseText);
              setSuccessMessage('Response copied to clipboard!');
            }}
          >
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>
      
      <Snackbar 
        open={!!error || !!successMessage} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={error ? "error" : "success"} 
          sx={{ width: '100%' }}
        >
          {error || successMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default BrightdataScraper; 
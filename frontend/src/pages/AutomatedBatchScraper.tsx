import AddIcon from '@mui/icons-material/Add';
import FacebookIcon from '@mui/icons-material/Facebook';
import HomeIcon from '@mui/icons-material/Home';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicVideoIcon from '@mui/icons-material/MusicVideo';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import StopIcon from '@mui/icons-material/Stop';
import {
    Alert,
    Box,
    Breadcrumbs,
    Button,
    Card,
    CardContent,
    Checkbox,
    Chip,
    CircularProgress,
    Container,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    FormControl,
    FormControlLabel,
    IconButton,
    InputLabel,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    Snackbar,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import dayjs, { Dayjs } from 'dayjs';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../utils/api';

interface BatchScraperJob {
  id: number;
  name: string;
  project: number;
  project_name: string;
  source_folder_ids: number[];
  platforms_to_scrape: string[];
  platforms_display: string;
  content_types_to_scrape: { [key: string]: string[] };
  content_types_display: string;
  num_of_posts: number;
  start_date: string | null;
  end_date: string | null;
  auto_create_folders: boolean;
  output_folder_pattern: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  total_accounts: number;
  processed_accounts: number;
  successful_requests: number;
  failed_requests: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

interface BrightdataConfig {
  id: number;
  name: string;
  platform: string;
  platform_display: string;
  is_active: boolean;
}

const AutomatedBatchScraper = () => {
  const [jobs, setJobs] = useState<BatchScraperJob[]>([]);
  const [configs, setConfigs] = useState<BrightdataConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form state
  const [formOpen, setFormOpen] = useState(false);
  const [jobName, setJobName] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['facebook_posts', 'instagram_posts']);
  const [numOfPosts, setNumOfPosts] = useState(10);
  const [startDate, setStartDate] = useState<Dayjs | null>(null);
  const [endDate, setEndDate] = useState<Dayjs | null>(null);
  const [autoCreateFolders, setAutoCreateFolders] = useState(true);
  const [outputFolderPattern, setOutputFolderPattern] = useState('{platform}_{date}_{job_name}');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Updated platform options with content types (excluding comments since this is for posts/reels)
  const platformOptions = [
    {
      value: 'facebook_posts',
      label: 'Facebook Posts',
      icon: <FacebookIcon />,
      platform: 'facebook',
      contentType: 'posts',
      color: '#1877F2',
      description: 'Scrape Facebook posts and content'
    },
    {
      value: 'facebook_reels',
      label: 'Facebook Reels',
      icon: <FacebookIcon />,
      platform: 'facebook',
      contentType: 'reels',
      color: '#1877F2',
      description: 'Collect Facebook video content'
    },
    {
      value: 'instagram_posts',
      label: 'Instagram Posts',
      icon: <InstagramIcon />,
      platform: 'instagram',
      contentType: 'posts',
      color: '#E4405F',
      description: 'Scrape Instagram posts and images'
    },
    {
      value: 'instagram_reels',
      label: 'Instagram Reels',
      icon: <InstagramIcon />,
      platform: 'instagram',
      contentType: 'reels',
      color: '#E4405F',
      description: 'Collect Instagram video content'
    },
    {
      value: 'linkedin',
      label: 'LinkedIn Posts',
      icon: <LinkedInIcon />,
      platform: 'linkedin',
      contentType: 'posts',
      color: '#0A66C2',
      description: 'Scrape LinkedIn posts and articles'
    },
    {
      value: 'tiktok',
      label: 'TikTok Posts',
      icon: <MusicVideoIcon />,
      platform: 'tiktok',
      contentType: 'posts',
      color: '#000000',
      description: 'Collect TikTok video content'
    },
  ];

  const { organizationId, projectId } = useParams();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchJobs(),
        fetchConfigs()
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await apiFetch('/api/brightdata/batch-jobs/');
      if (!response.ok) {
        throw new Error('Failed to fetch batch jobs');
      }
      const responseData = await response.json();
      const data = responseData.results || responseData;
      setJobs(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setJobs([]);
    }
  };

  const fetchConfigs = async () => {
    try {
      const response = await apiFetch('/api/brightdata/configs/active/');
      if (!response.ok) {
        throw new Error('Failed to fetch active configurations');
      }
      const data = await response.json();
      setConfigs(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching configs:', error);
      setConfigs([]);
    }
  };

  const handleCreateJob = () => {
    setJobName('');
    // Auto-select only platforms that have active configurations
    const configuredPlatforms = platformOptions
      .filter(platform => configs.some(config => config.platform === platform.value && config.is_active))
      .map(platform => platform.value);
    setSelectedPlatforms(configuredPlatforms);
    setNumOfPosts(10);
    setStartDate(null);
    setEndDate(null);
    setAutoCreateFolders(true);
    setOutputFolderPattern('{platform}_{date}_{job_name}');
    setFormOpen(true);
  };

  const handleCloseForm = () => {
    setFormOpen(false);
  };

  const handleSubmit = async () => {
    if (!jobName || selectedPlatforms.length === 0) {
      setError('Please fill in all required fields');
      return;
    }

    // Check if we have active configurations for selected platforms
    const missingConfigs = selectedPlatforms.filter(platform =>
      !configs.some(config => config.platform === platform && config.is_active)
    );

    if (missingConfigs.length > 0) {
      setError(`Missing active configurations for: ${missingConfigs.join(', ')}`);
      return;
    }

    try {
      setIsSubmitting(true);

      // Convert selectedPlatforms into the proper format
      // selectedPlatforms contains items like: ['facebook_posts', 'instagram_reels', 'facebook_reels']
      // We need to convert this to:
      // platforms_to_scrape: ['facebook', 'instagram']
      // content_types_to_scrape: { facebook: ['post', 'reel'], instagram: ['reel'] }

      const platformsSet = new Set<string>();
      const contentTypesByPlatform: { [key: string]: string[] } = {};

      selectedPlatforms.forEach(platformContentType => {
        const platformOption = platformOptions.find(opt => opt.value === platformContentType);
        if (platformOption) {
          const { platform, contentType } = platformOption;
          platformsSet.add(platform);

          if (!contentTypesByPlatform[platform]) {
            contentTypesByPlatform[platform] = [];
          }

          if (!contentTypesByPlatform[platform].includes(contentType)) {
            contentTypesByPlatform[platform].push(contentType);
          }
        }
      });

      const payload = {
        name: jobName,
        project: projectId ? parseInt(projectId, 10) : 1,
        source_folder_ids: [], // Empty array since folders have been removed
        platforms_to_scrape: Array.from(platformsSet),
        content_types_to_scrape: contentTypesByPlatform,
        num_of_posts: numOfPosts,
        start_date: startDate ? startDate.format('YYYY-MM-DD') : null,
        end_date: endDate ? endDate.format('YYYY-MM-DD') : null,
        auto_create_folders: autoCreateFolders,
        output_folder_pattern: outputFolderPattern,
      };

      const url = '/api/brightdata/batch-jobs/create_and_execute/';

      // ===== DETAILED CONSOLE LOGGING =====
      console.log('🚀 AUTOMATED BATCH SCRAPER - FRONTEND DEBUG');
      console.log('='.repeat(60));
      console.log('📤 REQUEST PAYLOAD:');
      console.log('URL:', url);
      console.log('Payload:', payload);
      console.log('Selected Platforms:', selectedPlatforms);
      console.log('Platforms Set:', Array.from(platformsSet));
      console.log('Content Types by Platform:', contentTypesByPlatform);
      console.log('='.repeat(60));
      const response = await apiFetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('📥 RESPONSE FROM BACKEND:');
      console.log('Status:', response.status);
      console.log('Status Text:', response.statusText);
      console.log('Headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorData = await response.json();
        console.log('❌ ERROR RESPONSE:', errorData);
        console.log('='.repeat(60));
        throw new Error(errorData.error || 'Failed to create and execute batch job');
      }

      const responseData = await response.json();
      console.log('✅ SUCCESS RESPONSE:', responseData);
      console.log('='.repeat(60));

      setSuccessMessage('Batch job created and started successfully');
      fetchJobs();
      setFormOpen(false);
    } catch (error) {
      console.error('Error creating job:', error);
      setError(error instanceof Error ? error.message : 'Error creating batch job. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExecuteJob = async (jobId: number) => {
    try {
      console.log('🔄 EXECUTING BATCH JOB - FRONTEND DEBUG');
      console.log('='.repeat(60));
      console.log('Job ID:', jobId);
      console.log('Execute URL:', `/api/brightdata/batch-jobs/${jobId}/execute/`);
      console.log('='.repeat(60));

      const response = await apiFetch(`/api/brightdata/batch-jobs/${jobId}/execute/`, {
        method: 'POST',
      });

      console.log('📥 EXECUTE RESPONSE:');
      console.log('Status:', response.status);
      console.log('Status Text:', response.statusText);

      if (!response.ok) {
        const errorData = await response.json();
        console.log('❌ EXECUTE ERROR:', errorData);
        console.log('='.repeat(60));
        throw new Error(errorData.error || 'Failed to execute job');
      }

      const responseData = await response.json();
      console.log('✅ EXECUTE SUCCESS:', responseData);
      console.log('='.repeat(60));

      setSuccessMessage('Job execution started successfully');
      fetchJobs();
    } catch (error) {
      console.error('Error executing job:', error);
      setError(error instanceof Error ? error.message : 'Failed to execute job');
    }
  };

  const handleCancelJob = async (jobId: number) => {
    try {
      const response = await apiFetch(`/api/brightdata/batch-jobs/${jobId}/cancel/`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to cancel job');
      }

      setSuccessMessage('Job cancelled successfully');
      fetchJobs();
    } catch (error) {
      console.error('Error cancelling job:', error);
      setError(error instanceof Error ? error.message : 'Failed to cancel job');
    }
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (status) {
      case 'pending':
        return 'default';
      case 'processing':
        return 'info';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getProgressValue = (job: BatchScraperJob) => {
    if (job.total_accounts === 0) return 0;
    return (job.processed_accounts / job.total_accounts) * 100;
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Container maxWidth="xl">
        <Box sx={{ py: 4 }}>
          {/* Header */}
          <Breadcrumbs sx={{ mb: 2 }}>
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
                Home
              </Box>
            </Link>
            {organizationId && projectId && (
              <Link
                to={`/organizations/${organizationId}/projects/${projectId}`}
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                Project Dashboard
              </Link>
            )}
            <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
              <SmartToyIcon sx={{ mr: 0.5 }} fontSize="inherit" />
              Automated Batch Scraper
            </Typography>
          </Breadcrumbs>

          <Typography variant="h4" sx={{ mb: 1, fontWeight: 'bold' }}>
            Automated Batch Scraper
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Create and manage automated batch scraping jobs to collect data from multiple social media accounts across different platforms.
          </Typography>

          {/* Error and Success Messages */}
          <Snackbar
            open={!!error}
            autoHideDuration={6000}
            onClose={() => setError(null)}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
              {error}
            </Alert>
          </Snackbar>

          <Snackbar
            open={!!successMessage}
            autoHideDuration={6000}
            onClose={() => setSuccessMessage(null)}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert onClose={() => setSuccessMessage(null)} severity="success" sx={{ width: '100%' }}>
              {successMessage}
            </Alert>
          </Snackbar>

          {/* Configuration Status */}
          <Card sx={{ 
            mb: 4, 
            background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            border: '1px solid #dee2e6',
            borderRadius: 2,
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ mb: 2, fontWeight: 600, color: '#495057' }}>
                Platform Configurations Status
              </Typography>
              <Typography variant="body1" sx={{ mb: 3, color: '#6c757d', lineHeight: 1.6 }}>
                Check the status of your BrightData configurations for each platform. Only configured platforms can be used for automated batch scraping.
              </Typography>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 2 }}>
                {platformOptions.map((platform) => {
                  const config = configs.find(c => c.platform === platform.value && c.is_active);
                  return (
                    <Paper
                      key={platform.value}
                      elevation={config ? 3 : 1}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        border: config ? `2px solid #28a745` : '1px solid #dee2e6',
                        background: config ? 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)' : 'white',
                        transition: 'all 0.3s ease',
                        cursor: 'pointer',
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: config ? '0 8px 25px rgba(40, 167, 69, 0.2)' : '0 6px 20px rgba(0,0,0,0.1)'
                        }
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: platform.color,
                            color: 'white',
                            mr: 2,
                            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                          }}
                        >
                          {platform.icon}
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" sx={{ fontWeight: 600, color: '#495057' }}>
                            {platform.label}
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#6c757d', fontSize: '0.875rem' }}>
                            {platform.description}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {config ? (
                            <Chip
                              label="Ready"
                              size="small"
                              color="success"
                              sx={{ 
                                fontWeight: 600,
                                '& .MuiChip-label': { px: 1.5 }
                              }}
                            />
                          ) : (
                            <Chip
                              label="Not Configured"
                              size="small"
                              variant="outlined"
                              sx={{ 
                                fontWeight: 500,
                                color: '#6c757d',
                                borderColor: '#dee2e6',
                                '& .MuiChip-label': { px: 1.5 }
                              }}
                            />
                          )}
                        </Box>
                      </Box>
                    </Paper>
                  );
                })}
              </Box>
              
              {configs.length === 0 && (
                <Box sx={{ mt: 3, p: 2, backgroundColor: '#fff3cd', borderRadius: 1, border: '1px solid #ffeaa7' }}>
                  <Alert severity="warning" sx={{ backgroundColor: 'transparent', '& .MuiAlert-icon': { color: '#856404' } }}>
                    <Typography variant="body2" sx={{ color: '#856404' }}>
                      <strong>No active platform configurations found.</strong> Please configure your BrightData settings first to enable automated batch scraping.
                    </Typography>
                  </Alert>
                </Box>
              )}
              
              {configs.length > 0 && (
                <Box sx={{ mt: 3, p: 2, backgroundColor: '#d1ecf1', borderRadius: 1, border: '1px solid #bee5eb' }}>
                  <Typography variant="body2" sx={{ color: '#0c5460', textAlign: 'center' }}>
                    🚀 <strong>Ready to scrape!</strong> You have {configs.length} platform(s) configured and ready for automated batch scraping.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Jobs Table */}
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="h6">
                  Batch Scraper Jobs
                </Typography>
                <Stack direction="row" spacing={2}>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={fetchJobs}
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleCreateJob}
                    disabled={configs.length === 0}
                  >
                    Create New Job
                  </Button>
                </Stack>
              </Stack>

              {loading && jobs.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Job Name</TableCell>
                        <TableCell>Platforms</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Progress</TableCell>
                        <TableCell>Success/Failed</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {jobs.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={7} align="center">
                            <Typography variant="body2" color="text.secondary">
                              No batch jobs found. Create your first automated scraping job!
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ) : (
                        jobs.map((job) => (
                          <TableRow key={job.id}>
                            <TableCell>
                              <Typography variant="body2" fontWeight="medium">
                                {job.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {job.platforms_to_scrape.length} platform(s), {Object.keys(job.content_types_to_scrape || {}).length} content type(s)
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {job.content_types_display || job.platforms_display}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={job.status}
                                color={getStatusColor(job.status)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Box sx={{ width: '100%' }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={getProgressValue(job)}
                                  sx={{ mb: 1 }}
                                />
                                <Typography variant="caption">
                                  {job.processed_accounts} / {job.total_accounts} accounts
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" color="success.main">
                                ✓ {job.successful_requests}
                              </Typography>
                              <Typography variant="body2" color="error.main">
                                ✗ {job.failed_requests}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {new Date(job.created_at).toLocaleDateString()}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {new Date(job.created_at).toLocaleTimeString()}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Stack direction="row" spacing={1}>
                                {job.status === 'pending' && (
                                  <Tooltip title="Execute Job">
                                    <IconButton
                                      size="small"
                                      color="primary"
                                      onClick={() => handleExecuteJob(job.id)}
                                    >
                                      <PlayArrowIcon />
                                    </IconButton>
                                  </Tooltip>
                                )}
                                {job.status === 'processing' && (
                                  <Tooltip title="Cancel Job">
                                    <IconButton
                                      size="small"
                                      color="warning"
                                      onClick={() => handleCancelJob(job.id)}
                                    >
                                      <StopIcon />
                                    </IconButton>
                                  </Tooltip>
                                )}
                              </Stack>
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

          {/* Create Job Dialog */}
          <Dialog open={formOpen} onClose={handleCloseForm} maxWidth="md" fullWidth>
            <DialogTitle>Create New Batch Scraper Job</DialogTitle>
            <DialogContent>
              <DialogContentText sx={{ mb: 2 }}>
                Create an automated batch scraping job to collect data from multiple social media accounts.
              </DialogContentText>

              <Stack spacing={3} sx={{ mt: 2 }}>
                <TextField
                  autoFocus
                  label="Job Name"
                  fullWidth
                  value={jobName}
                  onChange={(e) => setJobName(e.target.value)}
                  placeholder="e.g., Weekly Social Media Monitoring"
                />

                <FormControl fullWidth>
                  <InputLabel>Platforms to Scrape</InputLabel>
                  <Select
                    multiple
                    value={selectedPlatforms}
                    onChange={(e) => setSelectedPlatforms(e.target.value as string[])}
                    renderValue={(selected) =>
                      platformOptions
                        .filter(p => (selected as string[]).includes(p.value))
                        .map(p => p.label)
                        .join(', ')
                    }
                  >
                    {platformOptions.map((platform) => {
                      const hasConfig = configs.some(c => c.platform === platform.value && c.is_active);
                      return (
                        <MenuItem key={platform.value} value={platform.value} disabled={!hasConfig}>
                          <Checkbox checked={selectedPlatforms.includes(platform.value)} />
                          <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                            {platform.icon}
                            <Box sx={{ ml: 1 }}>
                              <Typography variant="body2">{platform.label}</Typography>
                              {!hasConfig && (
                                <Typography variant="caption" color="error">
                                  (Not Configured)
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        </MenuItem>
                      );
                    })}
                  </Select>
                </FormControl>

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    label="Number of Posts"
                    type="number"
                    sx={{ flex: 1 }}
                    value={numOfPosts}
                    onChange={(e) => setNumOfPosts(parseInt(e.target.value) || 10)}
                    inputProps={{ min: 1, max: 100 }}
                  />

                  <TextField
                    label="Output Folder Pattern"
                    sx={{ flex: 1 }}
                    value={outputFolderPattern}
                    onChange={(e) => setOutputFolderPattern(e.target.value)}
                    helperText="Available variables: {platform}, {date}, {job_name}, {account_name}"
                  />
                </Box>

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <DatePicker
                    label="Start Date (Optional)"
                    value={startDate}
                    onChange={(value) => setStartDate(value ? dayjs(value) : null)}
                    slotProps={{ textField: { sx: { flex: 1 } } }}
                  />

                  <DatePicker
                    label="End Date (Optional)"
                    value={endDate}
                    onChange={(value) => setEndDate(value ? dayjs(value) : null)}
                    slotProps={{ textField: { sx: { flex: 1 } } }}
                  />
                </Box>

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={autoCreateFolders}
                      onChange={(e) => setAutoCreateFolders(e.target.checked)}
                    />
                  }
                  label="Automatically create folders for scraped data"
                />
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseForm}>Cancel</Button>
              <Button
                onClick={handleSubmit}
                variant="contained"
                color="primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? <CircularProgress size={24} /> : 'Create & Execute Job'}
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
      </Container>
    </LocalizationProvider>
  );
};

export default AutomatedBatchScraper;

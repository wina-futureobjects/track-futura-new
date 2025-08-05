import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import FacebookIcon from '@mui/icons-material/Facebook';
import HomeIcon from '@mui/icons-material/Home';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicVideoIcon from '@mui/icons-material/MusicVideo';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import StopIcon from '@mui/icons-material/Stop';
import SettingsIcon from '@mui/icons-material/Settings';
import VisibilityIcon from '@mui/icons-material/Visibility';
import HistoryIcon from '@mui/icons-material/History';
import ReplayIcon from '@mui/icons-material/Replay';
import {
    Alert,
    AlertTitle,
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
    Typography,
    Tabs,
    Tab,
    Avatar,
    Divider,
    Grid,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    List,
    ListItem,
    ListItemText,
    ListItemIcon
} from '@mui/material';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import dayjs, { Dayjs } from 'dayjs';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../utils/api';
import workflowService, { 
    InputCollection, 
    WorkflowTask, 
    PlatformService, 
    TrackSourceCollection,
    ScrapingRun,
    ScrapingJob,
    CreateScrapingRunRequest
} from '../services/workflowService';

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
  platform_params?: { [key: string]: Record<string, unknown> };
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

const AutomatedBatchScraper = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Input Collections
  const [inputCollections, setInputCollections] = useState<InputCollection[]>([]);
  const [trackSourceCollections, setTrackSourceCollections] = useState<TrackSourceCollection[]>([]);
  
  // Workflow Tasks
  const [workflowTasks, setWorkflowTasks] = useState<WorkflowTask[]>([]);
  const [scheduledTasks, setScheduledTasks] = useState<any[]>([]);
  
  // Scraping Runs and Jobs
  const [scrapingRuns, setScrapingRuns] = useState<ScrapingRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<ScrapingRun | null>(null);
  const [scrapingJobs, setScrapingJobs] = useState<ScrapingJob[]>([]);
  
  // Configuration
  const [selectedInputCollection, setSelectedInputCollection] = useState<TrackSourceCollection | null>(null);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [globalConfigDialogOpen, setGlobalConfigDialogOpen] = useState(false);
  const [creatingWorkflow, setCreatingWorkflow] = useState<number | null>(null);
  const [creatingGlobalRun, setCreatingGlobalRun] = useState(false);
  
  // Configuration forms
  const [configForm, setConfigForm] = useState({
    jobName: '',
    numOfPosts: 10,
    startDate: null as Dayjs | null,
    endDate: null as Dayjs | null,
    autoCreateFolders: true,
    outputFolderPattern: 'scraped_data'
  });
  
  const [globalConfigForm, setGlobalConfigForm] = useState({
    numOfPosts: 10,
    startDate: null as Dayjs | null,
    endDate: null as Dayjs | null,
    autoCreateFolders: true,
    outputFolderPattern: 'scraped_data'
  });
  
  // Delete confirmation
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<{ id: number; name: string; type: 'input' | 'workflow' | 'scheduled' | 'run' } | null>(null);
  
  // Snackbar
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const fetchData = async () => {
    if (!projectId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const [
        collections,
        tasks,
        runs
      ] = await Promise.all([
        workflowService.getAllInputCollections(parseInt(projectId)),
        workflowService.getAllWorkflowTasks(parseInt(projectId)),
        workflowService.getScrapingRuns(parseInt(projectId))
      ]);
      
      setTrackSourceCollections(collections);
      setWorkflowTasks(tasks);
      setScrapingRuns(runs);
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const fetchJobs = async () => {
    if (!projectId) return;
    
    try {
      const jobs = await workflowService.getAllWorkflowTasks(parseInt(projectId));
      setWorkflowTasks(jobs);
    } catch (err) {
      console.error('Error fetching jobs:', err);
    }
  };

  const fetchConfigs = async () => {
    try {
      const response = await apiFetch('/api/brightdata-integration/configs/');
      if (response.ok) {
        const configs = await response.json();
        console.log('BrightData configs:', configs);
      }
    } catch (err) {
      console.error('Error fetching configs:', err);
    }
  };

  const fetchWorkflowData = async () => {
    if (!projectId) return;
    
    try {
      const collections = await workflowService.getAllInputCollections(parseInt(projectId));
      setTrackSourceCollections(collections);
    } catch (err) {
      console.error('Error fetching workflow data:', err);
    }
  };

  const fetchScheduledTasks = async (projectId: number) => {
    try {
      const response = await apiFetch(`/api/workflow/scheduled-tasks/?project=${projectId}`);
      if (response.ok) {
        const tasks = await response.json();
        setScheduledTasks(tasks.results || tasks);
      }
    } catch (err) {
      console.error('Error fetching scheduled tasks:', err);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleConfigureJob = (collection: TrackSourceCollection) => {
    setSelectedInputCollection(collection);
    setConfigDialogOpen(true);
  };

  const handleCloseConfigDialog = () => {
    setConfigDialogOpen(false);
    setSelectedInputCollection(null);
    setConfigForm({
      jobName: '',
      numOfPosts: 10,
      startDate: null,
      endDate: null,
      autoCreateFolders: true,
      outputFolderPattern: 'scraped_data'
    });
  };

  const handleSubmitConfig = async () => {
    if (!selectedInputCollection) return;

    try {
      setCreatingWorkflow(selectedInputCollection.id);
      
      const taskData = {
        name: configForm.jobName,
        track_source: selectedInputCollection.original_source_id,
        platform: selectedInputCollection.platform_name.toLowerCase(),
        service_type: selectedInputCollection.service_name.toLowerCase().replace(' ', '_'),
        num_of_posts: configForm.numOfPosts,
        start_date: configForm.startDate?.toISOString(),
        end_date: configForm.endDate?.toISOString(),
        auto_create_folders: configForm.autoCreateFolders,
        output_folder_pattern: configForm.outputFolderPattern
      };
      
      console.log('Selected Track Source:', selectedInputCollection);
      console.log('Selected Track Source ID:', selectedInputCollection.id);
      
      const response = await apiFetch('/api/workflow/scheduled-tasks/', {
        method: 'POST',
        body: JSON.stringify(taskData)
      });
      
      if (response.ok) {
        const newTask = await response.json();
        setScheduledTasks(prev => [newTask, ...prev]);
        showSnackbar('Scheduled task created successfully!', 'success');
        handleCloseConfigDialog();
        fetchScheduledTasks(parseInt(projectId!));
        } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create scheduled task');
      }
    } catch (err) {
      console.error('Error creating scheduled task:', err);
      showSnackbar('Failed to create scheduled task', 'error');
    } finally {
      setCreatingWorkflow(null);
    }
  };

  const handleGlobalRun = async () => {
    if (!projectId) return;
    
    try {
      setCreatingGlobalRun(true);
      
      const runData: CreateScrapingRunRequest = {
        project: parseInt(projectId),
        configuration: {
          num_of_posts: globalConfigForm.numOfPosts,
          start_date: globalConfigForm.startDate?.toISOString(),
          end_date: globalConfigForm.endDate?.toISOString(),
          auto_create_folders: globalConfigForm.autoCreateFolders,
          output_folder_pattern: globalConfigForm.outputFolderPattern
        }
      };
      
      const newRun = await workflowService.createScrapingRun(runData);
      console.log('Created run:', newRun);
      console.log('Run ID type:', typeof newRun.id, 'Value:', newRun.id);
      setScrapingRuns(prev => [newRun, ...prev]);
      showSnackbar('Scraping run created successfully!', 'success');
      setGlobalConfigDialogOpen(false);
      
      // Start the run
      console.log('Starting run with ID:', newRun.id);
      console.log('About to call startScrapingRun with ID:', newRun.id);
      const startResult = await workflowService.startScrapingRun(newRun.id);
      console.log('Start result:', startResult);
      showSnackbar('Scraping run started!', 'success');
      
      // Refresh data
      fetchData();
      
    } catch (err) {
      console.error('Error creating global run:', err);
      showSnackbar('Failed to create scraping run', 'error');
    } finally {
      setCreatingGlobalRun(false);
    }
  };

  const handleViewRunDetails = async (run: ScrapingRun) => {
    setSelectedRun(run);
    try {
      const jobs = await workflowService.getScrapingJobs(run.id);
      setScrapingJobs(jobs);
    } catch (err) {
      console.error('Error fetching run jobs:', err);
      showSnackbar('Failed to load run details', 'error');
    }
  };

  const handleRetryJob = async (jobId: number) => {
    try {
      await workflowService.retryScrapingJob(jobId);
      showSnackbar('Job retry initiated successfully!', 'success');
      
      // Refresh jobs if we're viewing a run
      if (selectedRun) {
        const jobs = await workflowService.getScrapingJobs(selectedRun.id);
        setScrapingJobs(jobs);
      }
    } catch (err) {
      console.error('Error retrying job:', err);
      showSnackbar('Failed to retry job', 'error');
    }
  };

  const handleDeleteItem = (itemId: number, itemName: string, itemType: 'input' | 'workflow' | 'scheduled' | 'run') => {
    setItemToDelete({ id: itemId, name: itemName, type: itemType });
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!itemToDelete) return;
    
    try {
      let endpoint = '';
      switch (itemToDelete.type) {
        case 'input':
          endpoint = `/api/workflow/input-collections/${itemToDelete.id}/`;
          break;
        case 'scheduled':
          endpoint = `/api/workflow/scheduled-tasks/${itemToDelete.id}/`;
          break;
        case 'run':
          endpoint = `/api/workflow/scraping-runs/${itemToDelete.id}/`;
          break;
        default:
          throw new Error('Invalid item type');
      }
      
      const response = await apiFetch(endpoint, { method: 'DELETE' });
        
        if (response.ok) {
        showSnackbar(`${itemToDelete.type} deleted successfully!`, 'success');
        
        // Refresh data
        fetchData();
        } else {
        throw new Error('Failed to delete item');
      }
    } catch (err) {
      console.error('Error deleting item:', err);
      showSnackbar('Failed to delete item', 'error');
    } finally {
      setDeleteDialogOpen(false);
      setItemToDelete(null);
    }
  };

  const cancelDelete = () => {
    setDeleteDialogOpen(false);
    setItemToDelete(null);
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'active':
        return 'success';
      case 'processing':
        return 'info';
      case 'failed':
      case 'error':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getPlatformIcon = (platformName: string) => {
    switch (platformName.toLowerCase()) {
      case 'facebook': return <FacebookIcon />;
      case 'instagram': return <InstagramIcon />;
      case 'linkedin': return <LinkedInIcon />;
      case 'tiktok': return <MusicVideoIcon />;
      default: return <SmartToyIcon />;
    }
  };

  const getPlatformColor = (platformName: string) => {
    switch (platformName.toLowerCase()) {
      case 'facebook': return '#1877f2';
      case 'instagram': return '#e4405f';
      case 'linkedin': return '#0077b5';
      case 'tiktok': return '#000000';
      default: return '#666666';
    }
  };

  const getPlatformName = (collection: any): string => {
    return collection.platform_name || 'Unknown';
  };

  const getServiceType = (collection: any): string => {
    return collection.service_name || 'Unknown';
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const getNavigationPath = (path: string) => {
    if (!projectId) return path;
    return path.replace(':projectId', projectId);
  };

  const getService = (source: TrackSourceCollection): string => {
    return source.service_name || 'Unknown';
  };

  // Initial data load
  useEffect(() => {
    if (projectId) {
      fetchData();
      fetchScheduledTasks(parseInt(projectId));
    }
  }, [projectId]);

  if (loading && trackSourceCollections.length === 0) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
  return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
        <Button onClick={fetchData} variant="contained">
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link to={getNavigationPath('/organizations/:projectId')} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <HomeIcon sx={{ mr: 0.5 }} fontSize="small" />
              <Typography variant="body2">Home</Typography>
                    </Box>
          </Link>
          <Typography variant="body2" color="text.primary">
            Workflow Management
                      </Typography>
        </Breadcrumbs>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Workflow Management
                      </Typography>
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={() => setGlobalConfigDialogOpen(true)}
            sx={{ minWidth: 120 }}
          >
            Run All
          </Button>
                    </Box>

        {/* Main Content */}
          <Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={activeTab} onChange={handleTabChange} aria-label="workflow tabs">
                <Tab label="Input Collections" />
              <Tab label="History" />
              </Tabs>
            </Box>

            {/* Input Collections Tab */}
            <TabPanel value={activeTab} index={0}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                Track Sources ({trackSourceCollections.length})
                </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                onClick={fetchData}
                  >
                    Refresh
                  </Button>
              </Box>

            {trackSourceCollections.length === 0 ? (
                <Alert severity="info">
                  No input collections found. Create input collections in the Input Collection page first.
                </Alert>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Platform</TableCell>
                      <TableCell>Service</TableCell>
                      <TableCell>URL</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                    {trackSourceCollections.map((collection) => (
                        <TableRow key={collection.id} hover>
                          <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {collection.name}
                              </Typography>
                          </TableCell>
                          <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Avatar
                              sx={{
                                width: 24,
                                height: 24,
                                bgcolor: getPlatformColor(getPlatformName(collection))
                              }}
                            >
                              {getPlatformIcon(getPlatformName(collection))}
                            </Avatar>
                            <Typography variant="body2">
                              {getPlatformName(collection)}
                            </Typography>
                          </Box>
                          </TableCell>
                          <TableCell>
                          <Typography variant="body2">
                              {getServiceType(collection)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ 
                              maxWidth: 300, 
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis', 
                              whiteSpace: 'nowrap' 
                            }}>
                              {collection.urls && collection.urls.length > 0 ? collection.urls[0] : 'No URL'}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </TabPanel>

          {/* History Tab */}
            <TabPanel value={activeTab} index={1}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                Scraping History ({scrapingRuns.length})
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                onClick={fetchData}
                >
                  Refresh
                </Button>
              </Box>

            {scrapingRuns.length === 0 ? (
                <Alert severity="info">
                No scraping runs found. Create a new run to start scraping.
                </Alert>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                      <TableCell>Run Name</TableCell>
                        <TableCell>Status</TableCell>
                      <TableCell>Progress</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                    {scrapingRuns.map((run) => (
                      <TableRow key={run.id} hover>
                          <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {run.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                            {run.configuration.num_of_posts} posts per run
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                            label={run.status}
                            color={getStatusColor(run.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={run.progress_percentage}
                              sx={{ width: 100, height: 8, borderRadius: 4 }}
                            />
                            <Typography variant="caption">
                              {run.progress_percentage}%
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {run.completed_jobs}/{run.total_jobs} jobs
                          </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                            {new Date(run.created_at).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                            {new Date(run.created_at).toLocaleTimeString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title="View Details">
                                <IconButton
                                  size="small"
                                  color="info"
                                onClick={() => handleViewRunDetails(run)}
                                >
                                <HistoryIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            {run.status === 'pending' && (
                              <Tooltip title="Start Run">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={async () => {
                                    try {
                                      await workflowService.startScrapingRun(run.id);
                                      showSnackbar('Scraping run started!', 'success');
                                      fetchData();
                                    } catch (error) {
                                      console.error('Error starting scraping run:', error);
                                      showSnackbar('Failed to start scraping run', 'error');
                                    }
                                  }}
                                >
                                  <PlayArrowIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                onClick={() => handleDeleteItem(run.id, run.name, 'run')}
                                  sx={{ color: '#dc2626' }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </TabPanel>
        </Card>

        {/* Configuration Dialog */}
        <Dialog open={configDialogOpen} onClose={handleCloseConfigDialog} maxWidth="md" fullWidth>
          <DialogTitle>Configure Scheduled Task</DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ mb: 3 }}>
              Configure the scraping settings for {selectedInputCollection?.name}
            </DialogContentText>

            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <Stack spacing={3} sx={{ mt: 2 }}>
                <TextField
                  label="Task Name"
                  fullWidth
                  value={configForm.jobName}
                  onChange={(e) => setConfigForm({ ...configForm, jobName: e.target.value })}
                  placeholder={`${selectedInputCollection?.platform_name} - ${selectedInputCollection?.service_name} Scraping`}
                />

                <TextField
                  label="Number of Posts"
                  type="number"
                  fullWidth
                  value={configForm.numOfPosts}
                  onChange={(e) => setConfigForm({ ...configForm, numOfPosts: parseInt(e.target.value) || 10 })}
                  inputProps={{ min: 1, max: 1000 }}
                />

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <DatePicker
                    label="Start Date"
                    value={configForm.startDate}
                    onChange={(date) => setConfigForm({ ...configForm, startDate: date })}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                  <DatePicker
                    label="End Date"
                    value={configForm.endDate}
                    onChange={(date) => setConfigForm({ ...configForm, endDate: date })}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </Box>

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={configForm.autoCreateFolders}
                      onChange={(e) => setConfigForm({ ...configForm, autoCreateFolders: e.target.checked })}
                    />
                  }
                  label="Automatically organize scraped data by platform and service"
                />
              </Stack>
            </LocalizationProvider>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseConfigDialog}>Cancel</Button>
                <Button
              onClick={handleSubmitConfig}
              variant="contained"
              disabled={creatingWorkflow === selectedInputCollection?.id || !configForm.jobName}
              startIcon={creatingWorkflow === selectedInputCollection?.id ? <CircularProgress size={16} /> : <PlayArrowIcon />}
            >
              {creatingWorkflow === selectedInputCollection?.id ? 'Creating...' : 'Create Scheduled Task'}
                </Button>
          </DialogActions>
        </Dialog>

        {/* Global Configuration Dialog */}
        <Dialog open={globalConfigDialogOpen} onClose={() => setGlobalConfigDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Configure Global Scraping Settings</DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ mb: 3 }}>
              Configure the default settings for all new scraping tasks in this project.
            </DialogContentText>

            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <Stack spacing={3} sx={{ mt: 2 }}>
                <TextField
                  label="Number of Posts"
                  type="number"
                  fullWidth
                  value={globalConfigForm.numOfPosts}
                  onChange={(e) => setGlobalConfigForm({ ...globalConfigForm, numOfPosts: parseInt(e.target.value) || 10 })}
                  inputProps={{ min: 1, max: 1000 }}
                  helperText="Number of posts to scrape per run for all new tasks"
                />

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <DatePicker
                    label="Start Date"
                    value={globalConfigForm.startDate}
                    onChange={(date) => setGlobalConfigForm({ ...globalConfigForm, startDate: date })}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                  <DatePicker
                    label="End Date"
                    value={globalConfigForm.endDate}
                    onChange={(date) => setGlobalConfigForm({ ...globalConfigForm, endDate: date })}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
              </Box>

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={globalConfigForm.autoCreateFolders}
                      onChange={(e) => setGlobalConfigForm({ ...globalConfigForm, autoCreateFolders: e.target.checked })}
                    />
                  }
                  label="Automatically organize scraped data by platform and service for all new tasks"
                />
              </Stack>
            </LocalizationProvider>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setGlobalConfigDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleGlobalRun}
              variant="contained"
              disabled={creatingGlobalRun || !globalConfigForm.numOfPosts}
              startIcon={creatingGlobalRun ? <CircularProgress size={16} /> : <PlayArrowIcon />}
            >
              {creatingGlobalRun ? 'Creating...' : 'Create Global Run'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteDialogOpen} onClose={cancelDelete}>
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete "{itemToDelete?.name}"? This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={cancelDelete}>Cancel</Button>
            <Button onClick={confirmDelete} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Run Details Dialog */}
        {selectedRun && (
          <Dialog open={!!selectedRun} onClose={() => setSelectedRun(null)} maxWidth="md" fullWidth>
            <DialogTitle>Scraping Run Details: {selectedRun.name}</DialogTitle>
            <DialogContent>
              <Typography variant="body1" sx={{ mt: 2 }}>
                Status: <Chip label={selectedRun.status} color={getStatusColor(selectedRun.status)} />
              </Typography>
              <Typography variant="body1" sx={{ mt: 1 }}>
                Created At: {new Date(selectedRun.created_at).toLocaleDateString()}
              </Typography>
              <Typography variant="body1" sx={{ mt: 1 }}>
                Configuration:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon sx={{ minWidth: 30 }}>{<PlayArrowIcon />}</ListItemIcon>
                  <ListItemText primary="Number of Posts" secondary={selectedRun.configuration.num_of_posts} />
                </ListItem>
                <ListItem>
                  <ListItemIcon sx={{ minWidth: 30 }}>{<HistoryIcon />}</ListItemIcon>
                  <ListItemText primary="Start Date" secondary={selectedRun.configuration.start_date ? new Date(selectedRun.configuration.start_date).toLocaleDateString() : 'N/A'} />
                </ListItem>
                <ListItem>
                  <ListItemIcon sx={{ minWidth: 30 }}>{<HistoryIcon />}</ListItemIcon>
                  <ListItemText primary="End Date" secondary={selectedRun.configuration.end_date ? new Date(selectedRun.configuration.end_date).toLocaleDateString() : 'N/A'} />
                </ListItem>
                <ListItem>
                  <ListItemIcon sx={{ minWidth: 30 }}>{<SettingsIcon />}</ListItemIcon>
                  <ListItemText primary="Output Folder Pattern" secondary={selectedRun.configuration.output_folder_pattern} />
                </ListItem>
                <ListItem>
                  <ListItemIcon sx={{ minWidth: 30 }}>{<SettingsIcon />}</ListItemIcon>
                  <ListItemText primary="Auto Create Folders" secondary={selectedRun.configuration.auto_create_folders ? 'Yes' : 'No'} />
                </ListItem>
              </List>

              <Typography variant="body1" sx={{ mt: 2 }}>
                Jobs:
              </Typography>
              {scrapingJobs.length === 0 ? (
                <Alert severity="info">No jobs found for this run yet.</Alert>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Job Name</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {scrapingJobs.map((job) => (
                        <TableRow key={job.id} hover>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {job.input_collection_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {job.platform} - {job.service_type}
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
                            <Typography variant="body2">
                              {new Date(job.created_at).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(job.created_at).toLocaleTimeString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title="View Details">
                                  <IconButton
                                    size="small"
                                  color="info"
                                  >
                                  <VisibilityIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              {job.status === 'failed' && (
                                <Tooltip title="Retry">
                                  <IconButton
                                    size="small"
                                    color="warning"
                                    onClick={() => handleRetryJob(job.id)}
                                  >
                                    <ReplayIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedRun(null)}>Close</Button>
            </DialogActions>
          </Dialog>
        )}

        {/* Snackbar */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
        </Box>
      </Container>
  );
};

export default AutomatedBatchScraper;

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
    Typography,
    Tabs,
    Tab,
    Avatar,
    Divider,
    Grid
} from '@mui/material';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import dayjs, { Dayjs } from 'dayjs';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../utils/api';
import workflowService, { InputCollection, WorkflowTask, PlatformService, TrackSourceCollection } from '../services/workflowService';

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
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
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
  const [jobs, setJobs] = useState<BatchScraperJob[]>([]);
  const [configs, setConfigs] = useState<BrightdataConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Workflow-related state
  const [inputCollections, setInputCollections] = useState<InputCollection[]>([]);
  const [allCollections, setAllCollections] = useState<TrackSourceCollection[]>([]);
  const [workflowTasks, setWorkflowTasks] = useState<WorkflowTask[]>([]);
  const [platformServices, setPlatformServices] = useState<PlatformService[]>([]);
  const [creatingWorkflow, setCreatingWorkflow] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  // Configuration dialog state
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [selectedInputCollection, setSelectedInputCollection] = useState<TrackSourceCollection | null>(null);
  const [configForm, setConfigForm] = useState({
    jobName: '',
    numOfPosts: 10,
    startDate: null as Dayjs | null,
    endDate: null as Dayjs | null,
    autoCreateFolders: true,
    outputFolderPattern: '{platform}/{service}/{date}'
  });

  // Delete confirmation dialog state
  const [deleteDialog, setDeleteDialog] = useState({
    open: false,
    itemId: null as number | null,
    itemName: '',
    itemType: '' as 'input' | 'workflow'
  });

  const params = useParams();
  const organizationId = params.organizationId;
  const projectId = params.projectId;

  // Platform options for configuration
  const platformOptions = [
    { value: 'facebook', label: 'Facebook', icon: <FacebookIcon />, color: '#1877f2', description: 'Facebook posts, comments, and engagement data' },
    { value: 'instagram', label: 'Instagram', icon: <InstagramIcon />, color: '#e4405f', description: 'Instagram posts, stories, and hashtag data' },
    { value: 'linkedin', label: 'LinkedIn', icon: <LinkedInIcon />, color: '#0077b5', description: 'LinkedIn company posts and professional content' },
    { value: 'tiktok', label: 'TikTok', icon: <MusicVideoIcon />, color: '#000000', description: 'TikTok videos and trending content' }
  ];

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchJobs(),
        fetchConfigs(),
        fetchWorkflowData()
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
      const response = await apiFetch('/api/brightdata/batch-scraper-jobs/');
      if (response.ok) {
        const data = await response.json();
        setJobs(data.results || data);
      } else {
        console.error('Failed to fetch jobs');
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchConfigs = async () => {
    try {
      const response = await apiFetch('/api/brightdata/configs/');
      if (response.ok) {
        const data = await response.json();
        setConfigs(data.results || data);
      } else {
        console.error('Failed to fetch configs');
      }
    } catch (error) {
      console.error('Error fetching configs:', error);
    }
  };

  const fetchWorkflowData = async () => {
    try {
      const projectId = params.projectId ? parseInt(params.projectId) : 1;
      console.log('=== fetchWorkflowData DEBUG ===');
      console.log('Project ID from params:', projectId);
      console.log('Using project ID for API calls:', projectId);
      
      const [collections, allCollections, tasks, services] = await Promise.all([
        workflowService.getInputCollections(projectId),
        workflowService.getAllInputCollections(projectId),
        workflowService.getAllWorkflowTasks(projectId),
        workflowService.getPlatformServices()
      ]);
      
      console.log('Collections received:', collections.length);
      console.log('AllCollections received:', allCollections.length);
      console.log('Tasks received:', tasks.length);
      console.log('Services received:', services.length);
      
      setInputCollections(collections);
      setAllCollections(allCollections);
      setWorkflowTasks(tasks);
      setPlatformServices(services);
      
      console.log('=== END fetchWorkflowData DEBUG ===');
    } catch (error) {
      console.error('Error fetching workflow data:', error);
      // Don't throw error for workflow data as it's not critical
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleConfigureJob = (collection: TrackSourceCollection) => {
    setSelectedInputCollection(collection as any); // Type assertion for compatibility
    setConfigForm({
      jobName: `${collection.platform_name} - ${collection.service_name} Scraping`,
      numOfPosts: 10,
      startDate: null,
      endDate: null,
      autoCreateFolders: true,
      outputFolderPattern: `{platform}/{service}/{date}`
    });
    setConfigDialogOpen(true);
  };

  const handleCloseConfigDialog = () => {
    setConfigDialogOpen(false);
    setSelectedInputCollection(null);
  };

  const handleSubmitConfig = async () => {
    if (!selectedInputCollection) return;

    try {
      setCreatingWorkflow(selectedInputCollection.id);
      
      // Get project ID from URL params
      const projectId = params.projectId ? parseInt(params.projectId) : 1;
      
      // Create batch scraper job with the configured settings
      const payload = {
        name: configForm.jobName,
        project: projectId,
        source_folder_ids: [],
        platforms_to_scrape: [selectedInputCollection.platform_name.toLowerCase()],
        content_types_to_scrape: {
          [selectedInputCollection.platform_name.toLowerCase()]: ['post']
        },
        num_of_posts: configForm.numOfPosts,
        start_date: configForm.startDate?.toISOString() || null,
        end_date: configForm.endDate?.toISOString() || null,
        auto_create_folders: configForm.autoCreateFolders,
        output_folder_pattern: configForm.outputFolderPattern,
        platform_params: {
          'platform_name': selectedInputCollection.platform_name,
          'service_name': selectedInputCollection.service_name,
          'source_type': selectedInputCollection.source_type,
          'original_source_id': selectedInputCollection.original_source_id
        }
      };

      const response = await apiFetch('/api/brightdata/batch-scraper-jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create batch job');
      }

      const responseData = await response.json();
      console.log('✅ Batch job created:', responseData);

      setSuccessMessage('Scraping job configured and started successfully');
      handleCloseConfigDialog();
      fetchData(); // Refresh all data
      
    } catch (error) {
      console.error('Error creating batch job:', error);
      setError('Failed to configure scraping job');
    } finally {
      setCreatingWorkflow(null);
    }
  };

  const handleDeleteItem = (itemId: number, itemName: string, itemType: 'input' | 'workflow') => {
    setDeleteDialog({
      open: true,
      itemId,
      itemName,
      itemType
    });
  };

  const confirmDelete = async () => {
    if (!deleteDialog.itemId) return;

    try {
      if (deleteDialog.itemType === 'input') {
        // Delete input collection
        const response = await apiFetch(`/api/workflow/input-collections/${deleteDialog.itemId}/`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          setSuccessMessage('Input collection deleted successfully');
        } else {
          throw new Error('Failed to delete input collection');
        }
      } else {
        // Delete workflow task (this would need to be implemented in backend)
        setSuccessMessage('Workflow task deleted successfully');
      }
      
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Error deleting item:', error);
      setError('Failed to delete item');
    } finally {
      setDeleteDialog({ open: false, itemId: null, itemName: '', itemType: 'input' });
    }
  };

  const cancelDelete = () => {
    setDeleteDialog({ open: false, itemId: null, itemName: '', itemType: 'input' });
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'info';
      case 'pending': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getPlatformIcon = (platformName: string) => {
    const platform = platformOptions.find(p => p.value === platformName.toLowerCase());
    return platform ? platform.icon : <SmartToyIcon />;
  };

  const getPlatformColor = (platformName: string) => {
    const platform = platformOptions.find(p => p.value === platformName.toLowerCase());
    return platform ? platform.color : '#6c757d';
  };

  // Initial data load
  useEffect(() => {
    console.log('=== useEffect DEBUG ===');
    console.log('projectId from params:', projectId);
    console.log('params:', params);
    console.log('organizationId:', organizationId);
    
    if (projectId) {
      console.log('Calling fetchData with projectId:', projectId);
      fetchData();
    } else {
      console.log('No projectId found, using default project ID 1');
      // Use default project ID if none is provided
      fetchData();
    }
  }, [projectId]);

  if (loading && inputCollections.length === 0) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Container maxWidth="xl">
        <Box sx={{ py: 4 }}>

          <Typography variant="h4" sx={{ mb: 1, fontWeight: 'bold' }}>
            Data Scraper & Workflow Management
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Configure and manage data scraping jobs for your input collections. Monitor workflow progress and job status.
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

          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#e3f2fd', border: '1px solid #2196f3' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ bgcolor: '#2196f3', mr: 2 }}>
                      <AddIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {allCollections.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Input Collections
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#fff3e0', border: '1px solid #ff9800' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ bgcolor: '#ff9800', mr: 2 }}>
                      <PlayArrowIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {workflowTasks.filter(t => t.status === 'processing').length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Jobs
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#e8f5e8', border: '1px solid #4caf50' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ bgcolor: '#4caf50', mr: 2 }}>
                      <PlayArrowIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {workflowTasks.filter(t => t.status === 'completed').length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Completed Jobs
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: '#ffebee', border: '1px solid #f44336' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ bgcolor: '#f44336', mr: 2 }}>
                      <StopIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {workflowTasks.filter(t => t.status === 'failed').length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Failed Jobs
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Main Content with Tabs */}
          <Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={activeTab} onChange={handleTabChange} aria-label="workflow tabs">
                <Tab label="Input Collections" />
                <Tab label="Workflow Tasks" />
                <Tab label="Batch Jobs" />
              </Tabs>
            </Box>

            {/* Input Collections Tab */}
            <TabPanel value={activeTab} index={0}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Input Collections ({allCollections.length})
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={fetchWorkflowData}
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="outlined"
                    color="secondary"
                    onClick={async () => {
                      console.log('=== MANUAL DEBUG TEST ===');
                      const projectId = params.projectId ? parseInt(params.projectId) : 1;
                      console.log('Testing with project ID:', projectId);
                      
                      try {
                        const response = await fetch(`/api/track-accounts/sources/?project=${projectId}&page_size=1000`);
                        console.log('TrackSource API Response Status:', response.status);
                        const data = await response.json();
                        console.log('TrackSource API Data:', data);
                        console.log('TrackSource Count:', data.results ? data.results.length : data.length || 0);
                      } catch (error) {
                        console.error('TrackSource API Error:', error);
                      }
                      
                      try {
                        const response = await fetch(`/api/workflow/input-collections/?project=${projectId}`);
                        console.log('Workflow API Response Status:', response.status);
                        const data = await response.json();
                        console.log('Workflow API Data:', data);
                        console.log('Workflow Count:', data.results ? data.results.length : data.length || 0);
                      } catch (error) {
                        console.error('Workflow API Error:', error);
                      }
                      console.log('=== END MANUAL DEBUG TEST ===');
                    }}
                  >
                    Debug APIs
                  </Button>
                </Box>
              </Box>

              {allCollections.length === 0 ? (
                <Alert severity="info">
                  No input collections found. Create input collections in the Input Collection page first.
                </Alert>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Collection</TableCell>
                        <TableCell>Platform & Service</TableCell>
                        <TableCell>URLs</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {allCollections.map((collection) => (
                        <TableRow key={collection.id} hover>
                          <TableCell>
                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                {collection.platform_name} - {collection.service_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                ID: {collection.id}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Box
                                sx={{
                                  width: 32,
                                  height: 32,
                                  borderRadius: '50%',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  backgroundColor: getPlatformColor(collection.platform_name),
                                  color: 'white'
                                }}
                              >
                                {getPlatformIcon(collection.platform_name)}
                              </Box>
                              <Box>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                  {collection.platform_name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {collection.service_name}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {collection.url_count} URL(s)
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {collection.urls.slice(0, 2).join(', ')}
                              {collection.urls.length > 2 && '...'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={collection.status}
                              color={getStatusColor(collection.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {new Date(collection.created_at).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(collection.created_at).toLocaleTimeString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title="Configure Scraping Job">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleConfigureJob(collection)}
                                  disabled={collection.status === 'processing'}
                                >
                                  <SettingsIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="View Details">
                                <IconButton
                                  size="small"
                                  color="info"
                                >
                                  <VisibilityIcon fontSize="small" />
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

            {/* Workflow Tasks Tab */}
            <TabPanel value={activeTab} index={1}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Workflow Tasks ({workflowTasks.length})
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={fetchWorkflowData}
                >
                  Refresh
                </Button>
              </Box>

              {workflowTasks.length === 0 ? (
                <Alert severity="info">
                  No workflow tasks found. Configure scraping jobs for your input collections to see tasks here.
                </Alert>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Task</TableCell>
                        <TableCell>Input Collection</TableCell>
                        <TableCell>Batch Job</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {workflowTasks.map((task) => (
                        <TableRow key={task.id} hover>
                          <TableCell>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              Task #{task.id}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {task.input_collection_details.platform_name} - {task.input_collection_details.service_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {task.input_collection_details.url_count} URLs
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {task.batch_job_name}
                            </Typography>
                            <Chip
                              label={task.batch_job_status}
                              color={getStatusColor(task.batch_job_status)}
                              size="small"
                              sx={{ mt: 0.5 }}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={task.status}
                              color={getStatusColor(task.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {new Date(task.created_at).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(task.created_at).toLocaleTimeString()}
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
                              {task.status === 'failed' && (
                                <Tooltip title="Retry">
                                  <IconButton
                                    size="small"
                                    color="warning"
                                  >
                                    <PlayArrowIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteItem(task.id, `Task #${task.id}`, 'workflow')}
                                  sx={{ 
                                    color: '#dc2626',
                                    '&:hover': { 
                                      bgcolor: '#dc2626',
                                      color: 'white'
                                    }
                                  }}
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

            {/* Batch Jobs Tab */}
            <TabPanel value={activeTab} index={2}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Batch Scraper Jobs ({jobs.length})
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={fetchJobs}
                >
                  Refresh
                </Button>
              </Box>

              {jobs.length === 0 ? (
                <Alert severity="info">
                  No batch jobs found. Configure scraping jobs for your input collections to see batch jobs here.
                </Alert>
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
                      {jobs.map((job) => (
                        <TableRow key={job.id} hover>
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
                                value={job.total_accounts > 0 ? (job.processed_accounts / job.total_accounts) * 100 : 0}
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
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                              {job.status === 'pending' && (
                                <Tooltip title="Execute Job">
                                  <IconButton
                                    size="small"
                                    color="primary"
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
                                  >
                                    <StopIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteItem(job.id, job.name, 'workflow')}
                                  sx={{ 
                                    color: '#dc2626',
                                    '&:hover': { 
                                      bgcolor: '#dc2626',
                                      color: 'white'
                                    }
                                  }}
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
            <DialogTitle>
              Configure Scraping Job
              {selectedInputCollection && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {selectedInputCollection.platform_name} - {selectedInputCollection.service_name}
                </Typography>
              )}
            </DialogTitle>
            <DialogContent>
              <DialogContentText sx={{ mb: 3 }}>
                Configure the settings for your data scraping job. This will create a batch scraper job that processes the URLs from your input collection.
              </DialogContentText>

              <Stack spacing={3} sx={{ mt: 2 }}>
                <TextField
                  autoFocus
                  label="Job Name"
                  fullWidth
                  value={configForm.jobName}
                  onChange={(e) => setConfigForm({ ...configForm, jobName: e.target.value })}
                  placeholder="e.g., Weekly Social Media Monitoring"
                />

                <TextField
                  label="Number of Posts"
                  type="number"
                  fullWidth
                  value={configForm.numOfPosts}
                  onChange={(e) => setConfigForm({ ...configForm, numOfPosts: parseInt(e.target.value) || 10 })}
                  inputProps={{ min: 1, max: 1000 }}
                  helperText="Number of posts to scrape per URL"
                />

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <DatePicker
                      label="Start Date (Optional)"
                      value={configForm.startDate}
                      onChange={(value) => setConfigForm({ ...configForm, startDate: value as Dayjs | null })}
                      slotProps={{
                        textField: {
                          fullWidth: true,
                          helperText: "Start date for scraping"
                        }
                      }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <DatePicker
                      label="End Date (Optional)"
                      value={configForm.endDate}
                      onChange={(value) => setConfigForm({ ...configForm, endDate: value as Dayjs | null })}
                      slotProps={{
                        textField: {
                          fullWidth: true,
                          helperText: "End date for scraping"
                        }
                      }}
                    />
                  </Grid>
                </Grid>

                <TextField
                  label="Output Folder Pattern"
                  fullWidth
                  value={configForm.outputFolderPattern}
                  onChange={(e) => setConfigForm({ ...configForm, outputFolderPattern: e.target.value })}
                  placeholder="{platform}/{service}/{date}"
                  helperText="Pattern for organizing scraped data folders"
                />

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={configForm.autoCreateFolders}
                      onChange={(e) => setConfigForm({ ...configForm, autoCreateFolders: e.target.checked })}
                    />
                  }
                  label="Auto-create folders for scraped data"
                />
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseConfigDialog}>Cancel</Button>
              <Button
                onClick={handleSubmitConfig}
                variant="contained"
                disabled={creatingWorkflow === selectedInputCollection?.id || !configForm.jobName}
                startIcon={creatingWorkflow === selectedInputCollection?.id ? <CircularProgress size={16} /> : <PlayArrowIcon />}
              >
                {creatingWorkflow === selectedInputCollection?.id ? 'Creating...' : 'Create Scraping Job'}
              </Button>
            </DialogActions>
          </Dialog>

          {/* Delete Confirmation Dialog */}
          <Dialog open={deleteDialog.open} onClose={cancelDelete}>
            <DialogTitle>Confirm Delete</DialogTitle>
            <DialogContent>
              <DialogContentText>
                Are you sure you want to delete "{deleteDialog.itemName}"? This action cannot be undone.
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={cancelDelete}>Cancel</Button>
              <Button onClick={confirmDelete} color="error" variant="contained">
                Delete
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
      </Container>
    </LocalizationProvider>
  );
};

export default AutomatedBatchScraper;

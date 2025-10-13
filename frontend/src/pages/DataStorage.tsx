import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Tabs,
  Tab,
  IconButton,
  Menu,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Tooltip,
} from '@mui/material';
import {
  Folder as FolderIcon,
  Instagram as InstagramIcon,
  Facebook as FacebookIcon,
  LinkedIn as LinkedInIcon,
  MusicVideo as TikTokIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  SelectAll as SelectAllIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import UploadDataDialog from '../components/UploadDataDialog';
import UploadToFolderDialog from '../components/UploadToFolderDialog';
import { apiFetch } from '../utils/api';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  category: string;
  category_display: string;
  platform: string;
  created_at?: string;
  post_count?: number;
  parent_folder?: number;
  folder_type: string;
  scraping_run?: number;
  subfolders?: Folder[];
}

interface FolderStats {
  totalFolders: number;
  platforms: {
    instagram: number;
    facebook: number;
    linkedin: number;
    tiktok: number;
  };
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
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}



const DataStorage = () => {
  const { organizationId, projectId } = useParams<{ organizationId: string; projectId: string }>();
  const navigate = useNavigate();
  
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [activeTab, setActiveTab] = useState(0);
  const [stats, setStats] = useState<FolderStats>({
    totalFolders: 0,
    platforms: { instagram: 0, facebook: 0, linkedin: 0, tiktok: 0 }
  });

  // Folder creation state
  const [openNewFolderDialog, setOpenNewFolderDialog] = useState(false);
  const [folderName, setFolderName] = useState('');
  const [folderDescription, setFolderDescription] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('instagram');
  const [selectedCategory, setSelectedCategory] = useState<string>('posts');
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Folder edit state
  const [openEditFolderDialog, setOpenEditFolderDialog] = useState(false);
  const [editingFolder, setEditingFolder] = useState<Folder | null>(null);
  const [isEditingFolder, setIsEditingFolder] = useState(false);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{ mouseX: number; mouseY: number; folder: Folder } | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [selectedFolderForMenu, setSelectedFolderForMenu] = useState<Folder | null>(null);

  // Batch selection state
  const [selectedFolders, setSelectedFolders] = useState<Set<number>>(new Set());
  const [isDeleteMode, setIsDeleteMode] = useState(false);

  // Upload dialog state
  const [openUploadDialog, setOpenUploadDialog] = useState(false);
  const [openUploadToFolderDialog, setOpenUploadToFolderDialog] = useState(false);

  const platforms = [
    { key: 'instagram', label: 'Instagram', icon: <InstagramIcon />, color: '#E4405F' },
    { key: 'facebook', label: 'Facebook', icon: <FacebookIcon />, color: '#1877F2' },
    { key: 'linkedin', label: 'LinkedIn', icon: <LinkedInIcon />, color: '#0A66C2' },
    { key: 'tiktok', label: 'TikTok', icon: <TikTokIcon />, color: '#000000' }
  ];

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'posts', label: 'Posts' },
    { value: 'reels', label: 'Reels' },
    { value: 'comments', label: 'Comments' }
  ];

  const fetchFolders = async (platform: string) => {
    try {
      const response = await apiFetch(`/api/${platform}-data/folders/?project=${projectId}&include_hierarchy=true`);
      if (response.ok) {
        const data = await response.json();
        const folders = data.results || data;
        return folders;
      }
      return [];
    } catch (error: any) {
      // Handle 404s and other client errors gracefully
      if (error.status === 404 || (error.message && error.message.includes('404'))) {
        console.log(`No ${platform} folders found (404) - this is normal if platform has no data yet`);
        return [];
      }
      
      console.warn(`Error fetching ${platform} folders:`, error);
      return [];
    }
  };

  const fetchUnifiedChildren = async (parentId: number, type: string) => {
    try {
      const resp = await apiFetch(`/api/track-accounts/report-folders/?project=${projectId}&parent_folder=${parentId}&folder_type=${type}&include_hierarchy=true`);
      if (resp.ok) {
        const data = await resp.json();
        return data.results || data || [];
      }
    } catch (e) {
      console.warn('Failed to fetch unified children', parentId, type, e);
    }
    return [];
  };

  const fetchAllFolders = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 🎯 FIRST: Fetch BrightData folders (SIMPLE & DIRECT)
      let brightDataFolders: any[] = [];
      try {
        console.log('🎯 Fetching BrightData scraped jobs...');
        const brightDataResponse = await apiFetch('/api/brightdata/simple-jobs/');
        if (brightDataResponse.ok) {
          const brightDataResult = await brightDataResponse.json();
          if (brightDataResult.success) {
            brightDataFolders = brightDataResult.results || [];
            console.log('🎉 Found BrightData folders:', brightDataFolders.length);
          }
        }
      } catch (error) {
        console.warn('Could not fetch BrightData folders:', error);
      }

      // Fetch run folders and job folders (including BrightData folders) with complete hierarchy from track_accounts
      let runFolders: any[] = [];
      let jobFolders: any[] = [];
      try {
        // Fetch run folders
        const runFoldersResponse = await apiFetch(`/api/track-accounts/report-folders/?project=${projectId}&folder_type=run&filter_empty=false`);
        if (runFoldersResponse.ok) {
          const runData = await runFoldersResponse.json();
          runFolders = (runData.results || runData).map((folder: any) => ({
            ...folder,
            platform: 'unified'
          }));
        }

        // Fetch job folders (including BrightData folders)
        const jobFoldersResponse = await apiFetch(`/api/track-accounts/report-folders/?project=${projectId}&folder_type=job&filter_empty=false`);
        if (jobFoldersResponse.ok) {
          const jobData = await jobFoldersResponse.json();
          jobFolders = (jobData.results || jobData).map((folder: any) => ({
            ...folder,
            platform: folder.platform_code || 'unified'
          }));
        }
      } catch (error) {
        console.warn('Could not fetch folders from track_accounts:', error);
      }

      // Flatten the hierarchy to a single array for filtering/searching
      // This recursively extracts all folders from the nested structure
      const flattenFolders = (folder: any): any[] => {
        const result = [folder];
        if (folder.subfolders && folder.subfolders.length > 0) {
          folder.subfolders.forEach((subfolder: any) => {
            result.push(...flattenFolders(subfolder));
          });
        }
        return result;
      };

      const allRunFolders = runFolders.flatMap(flattenFolders);
      const allJobFolders = jobFolders.flatMap(flattenFolders);
      const allFoldersFromHierarchy = [...allRunFolders, ...allJobFolders];

      // Also fetch standalone platform-specific folders (not linked to unified structure)
      const platformFolders = await Promise.all(
        platforms.map(p => fetchFolders(p.key))
      );
      const allPlatformFolders = platformFolders.flat();

      // Filter out platform folders that are already in the hierarchy (have unified_job_folder_id)
      const standalonePlatformFolders = allPlatformFolders.filter(
        (pf: any) => !pf.unified_job_folder_id && !pf.unified_job_folder
      );

      // Combine BrightData folders + hierarchical folders + standalone platform folders
      const allFolders = [
        ...brightDataFolders,
        ...allFoldersFromHierarchy,
        ...standalonePlatformFolders,
      ];

      setFolders(allFolders);
      
      const totalFolders = allFolders.length;
      const platformCounts = {
        instagram: allFolders.filter(f => f.platform === 'instagram').length,
        facebook: allFolders.filter(f => f.platform === 'facebook').length,
        linkedin: allFolders.filter(f => f.platform === 'linkedin').length,
        tiktok: allFolders.filter(f => f.platform === 'tiktok').length
      };
      
      setStats({
        totalFolders,
        platforms: platformCounts
      });
      
    } catch (error) {
      console.error('Error fetching folders:', error);
      setError('Some data folders may be unavailable. This is normal if data is still being processed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchAllFolders();
    }
  }, [projectId]);



  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleCategoryFilterChange = (event: SelectChangeEvent) => {
    setCategoryFilter(event.target.value);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getFilteredFolders = () => {
    return folders.filter(folder => {
      const matchesSearch = folder.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (folder.description && folder.description.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesCategory = categoryFilter === 'all' || folder.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  };

  const getHierarchicalFolders = () => {
    // Use the subfolders structure already provided by the API
    // The backend already returns the complete nested hierarchy with subfolders populated
    const runFoldersUnified = folders.filter(folder => folder.platform === 'unified' && folder.folder_type === 'run');

    // The run folders already have their complete hierarchy in the 'subfolders' field from the API
    // No need to manually rebuild it
    const hierarchy = runFoldersUnified;

    // Also include platform-specific folders that don't have unified_job_folder link
    // These are standalone scraped data folders (e.g., from Apify direct creation)
    const standalonePlatformFolders = folders.filter(folder =>
      folder.platform !== 'unified' &&
      folder.folder_type === 'content' &&
      !folder.parent_folder
    );

    // Convert standalone folders to look like run folders for consistent UI
    const standaloneAsRuns = standalonePlatformFolders.map(folder => ({
      ...folder,
      folder_type: 'run' as const, // Display as run-level folders
      subfolders: []
    }));

    return [...hierarchy, ...standaloneAsRuns];
  };

  const handleFolderClick = (platform: string, folder: Folder) => {
    // Navigate to folder contents page
    navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/${platform}/${folder.id}`);
  };

  const handleRunFolderClick = (runFolder: Folder) => {
    // Navigate to run folder contents page using human-friendly URL
    // Format: /data-storage/{folder-name}/1/ (assuming scrape #1)
    const folderName = encodeURIComponent(runFolder.name);
    navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/run/${runFolder.id}`);
    
    // TODO: Update to use human-friendly URLs when frontend routing is updated
    // navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/${folderName}/1`);
  };

  const handleServiceFolderClick = (serviceFolder: Folder) => {
    // Navigate to service folder contents page
    navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/service/${serviceFolder.id}`);
  };


  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'posts': return 'primary';
      case 'reels': return 'secondary';
      case 'comments': return 'success';
      default: return 'default';
    }
  };

  // Folder creation handlers
  const handleNewFolder = () => {
    setFolderName('');
    setFolderDescription('');
    setSelectedPlatform('instagram');
    setSelectedCategory('posts');
    setOpenNewFolderDialog(true);
  };

  const handleCreateFolder = async () => {
    if (!folderName.trim()) {
      setSnackbarMessage('Please enter a folder name');
      setSnackbarOpen(true);
      return;
    }

    try {
      setIsCreatingFolder(true);
      
      const folderData = {
        name: folderName.trim(),
        description: folderDescription.trim() || null,
        folder_type: 'run', // Create as run folder - main container
        project_id: projectId
      };

      console.log('Creating empty folder with data:', folderData);

      // Create unified run folder using track-accounts API
      const response = await apiFetch(`/api/track-accounts/report-folders/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(folderData),
      });

      if (!response.ok) {
        let errorDetail = 'Failed to create folder';
        try {
          const errorData = await response.json();
          console.error('Error data from server:', errorData);
          if (errorData.detail) {
            errorDetail = errorData.detail;
          } else if (typeof errorData === 'object') {
            errorDetail = Object.entries(errorData)
              .map(([field, errors]) => `${field}: ${errors}`)
              .join(', ');
          }
        } catch (e) {
          console.error('Could not parse error response:', e);
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      console.log('Empty folder created successfully:', data);
      
      setSnackbarMessage('Empty folder created successfully! You can now upload data files to organize them by platform.');
      setSnackbarOpen(true);
      setOpenNewFolderDialog(false);
      
      // Refresh the folders list
      fetchAllFolders();
      
    } catch (error) {
      console.error('Error creating empty folder:', error);
      setSnackbarMessage(error instanceof Error ? error.message : 'Failed to create folder. Please try again.');
      setSnackbarOpen(true);
    } finally {
      setIsCreatingFolder(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  // Folder edit handlers
  const handleEditFolder = (folder: Folder) => {
    setEditingFolder(folder);
    setFolderName(folder.name);
    setFolderDescription(folder.description || '');
    setSelectedPlatform(folder.platform);
    setSelectedCategory(folder.category);
    setOpenEditFolderDialog(true);
  };

  const handleUpdateFolder = async () => {
    if (!editingFolder || !folderName.trim()) {
      setSnackbarMessage('Please enter a folder name');
      setSnackbarOpen(true);
      return;
    }

    try {
      setIsEditingFolder(true);

      const folderData = {
        name: folderName.trim(),
        description: folderDescription.trim() || null,
        category: selectedCategory,
        project: projectId
      };

      console.log('Updating folder with data:', folderData);
      console.log('Platform:', selectedPlatform);
      console.log('Editing folder:', editingFolder);

      // Use the correct endpoint based on folder type
      // UnifiedRunFolders use the report-folders endpoint
      // Platform-specific folders use the platform-specific endpoint
      const isUnifiedFolder = selectedPlatform === 'unified' || editingFolder.folder_type === 'run';
      const endpoint = isUnifiedFolder
        ? `/api/track-accounts/report-folders/${editingFolder.id}/`
        : `/api/${selectedPlatform}-data/folders/${editingFolder.id}/`;

      console.log('Using endpoint:', endpoint);
      console.log('Is unified folder:', isUnifiedFolder);

      const response = await apiFetch(endpoint, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(folderData),
      });

      if (!response.ok) {
        let errorDetail = `Failed to update folder (Status: ${response.status})`;
        try {
          const errorData = await response.json();
          console.error('Error response status:', response.status);
          console.error('Error data from server:', errorData);
          console.error('Response headers:', response.headers);
          if (errorData.detail) {
            errorDetail = errorData.detail;
          } else if (typeof errorData === 'object') {
            errorDetail = Object.entries(errorData)
              .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
              .join('; ');
          }
        } catch (e) {
          console.error('Could not parse error response:', e);
          errorDetail = `Failed to update folder. Status: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      console.log('Folder updated successfully:', data);
      
      setSnackbarMessage('Folder updated successfully!');
      setSnackbarOpen(true);
      setOpenEditFolderDialog(false);
      setEditingFolder(null);
      
      // Refresh the folders list
      fetchAllFolders();
      
    } catch (error) {
      console.error('Error updating folder:', error);
      setSnackbarMessage(error instanceof Error ? error.message : 'Failed to update folder. Please try again.');
      setSnackbarOpen(true);
    } finally {
      setIsEditingFolder(false);
    }
  };

  // Folder delete handler
  const handleDeleteFolder = async (folder: Folder) => {
    if (!window.confirm(`Are you sure you want to delete the folder "${folder.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      console.log('Attempting to delete folder:', folder);
      
      // Determine the correct API endpoint based on folder type
      let deleteUrl: string;
      
      if (folder.platform === 'unified') {
        // For unified folders, use the track-accounts API
        deleteUrl = `/api/track-accounts/report-folders/${folder.id}/`;
      } else {
        // For platform-specific folders, use the platform-specific API
        deleteUrl = `/api/${folder.platform}-data/folders/${folder.id}/`;
      }
      
      console.log('Delete API URL:', deleteUrl);
      
      const response = await apiFetch(deleteUrl, {
        method: 'DELETE',
      });

      console.log('Delete response status:', response.status);
      console.log('Delete response ok:', response.ok);

      if (!response.ok) {
        // Try to get error details from the response
        let errorMessage = 'Failed to delete folder';
        try {
          const errorData = await response.json();
          console.log('Error response data:', errorData);
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } catch (e) {
          console.log('Could not parse error response as JSON');
          // If we can't parse JSON, try to get text
          try {
            const errorText = await response.text();
            console.log('Error response text:', errorText);
            if (errorText) errorMessage = errorText;
          } catch (e2) {
            console.log('Could not get error response text');
          }
        }
        throw new Error(errorMessage);
      }

      setSnackbarMessage('Folder deleted successfully!');
      setSnackbarOpen(true);
      
      // Refresh the folders list
      fetchAllFolders();
      
    } catch (error) {
      console.error('Error deleting folder:', error);
      setSnackbarMessage(error instanceof Error ? error.message : 'Failed to delete folder. Please try again.');
      setSnackbarOpen(true);
    }
  };

  // Context menu handlers
  const handleContextMenu = (event: React.MouseEvent, folder: Folder) => {
    event.preventDefault();
    event.stopPropagation();
    setContextMenu({
      mouseX: event.clientX + 2,
      mouseY: event.clientY - 6,
      folder
    });
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, folder: Folder) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedFolderForMenu(folder);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setSelectedFolderForMenu(null);
  };

  const handleEditFromMenu = () => {
    if (selectedFolderForMenu) {
      handleEditFolder(selectedFolderForMenu);
    }
    handleCloseMenu();
  };

  const handleDeleteFromMenu = () => {
    if (selectedFolderForMenu) {
      handleDeleteFolder(selectedFolderForMenu);
    }
    handleCloseMenu();
  };

  // Batch operations
  const handleToggleDeleteMode = () => {
    setIsDeleteMode(!isDeleteMode);
    setSelectedFolders(new Set());
  };

  const handleFolderSelection = (folderId: number, checked: boolean) => {
    const newSelected = new Set(selectedFolders);
    if (checked) {
      newSelected.add(folderId);
    } else {
      newSelected.delete(folderId);
    }
    setSelectedFolders(newSelected);
  };

  const handleSelectAll = () => {
    const allFolderIds = getHierarchicalFolders().map(f => f.id);
    setSelectedFolders(new Set(allFolderIds));
  };

  const handleClearSelection = () => {
    setSelectedFolders(new Set());
  };

  const handleBatchDelete = async () => {
    if (selectedFolders.size === 0) return;

    const folderNames = getHierarchicalFolders()
      .filter(f => selectedFolders.has(f.id))
      .map(f => f.name)
      .join(', ');

    if (!window.confirm(`Are you sure you want to delete ${selectedFolders.size} folder(s)?\n\n${folderNames}\n\nThis action cannot be undone.`)) {
      return;
    }

    try {
      const deletePromises = Array.from(selectedFolders).map(async (folderId) => {
        const folder = getHierarchicalFolders().find(f => f.id === folderId);
        if (folder) {
          console.log('Bulk deleting folder:', folder);
          
          // Determine the correct API endpoint based on folder type
          let deleteUrl: string;
          
          if (folder.platform === 'unified') {
            // For unified folders, use the track-accounts API
            deleteUrl = `/api/track-accounts/report-folders/${folder.id}/`;
          } else {
            // For platform-specific folders, use the platform-specific API
            deleteUrl = `/api/${folder.platform}-data/folders/${folder.id}/`;
          }
          
          console.log('Bulk delete API URL:', deleteUrl);
          
          const response = await apiFetch(deleteUrl, {
            method: 'DELETE',
          });
          
          console.log(`Delete response for ${folder.name}:`, response.status, response.ok);
          
          if (!response.ok) {
            // Try to get error details from the response
            let errorMessage = `Failed to delete folder: ${folder.name}`;
            try {
              const errorData = await response.json();
              console.log(`Error response data for ${folder.name}:`, errorData);
              errorMessage = errorData.error || errorData.detail || errorMessage;
            } catch (e) {
              try {
                const errorText = await response.text();
                console.log(`Error response text for ${folder.name}:`, errorText);
                if (errorText) errorMessage = `${folder.name}: ${errorText}`;
              } catch (e2) {
                console.log(`Could not get error response for ${folder.name}`);
              }
            }
            throw new Error(errorMessage);
          }
        }
      });

      await Promise.all(deletePromises);

      setSnackbarMessage(`Successfully deleted ${selectedFolders.size} folder(s)!`);
      setSnackbarOpen(true);
      setSelectedFolders(new Set());
      setIsDeleteMode(false);
      
      // Refresh the folders list
      fetchAllFolders();
      
    } catch (error) {
      console.error('Error deleting folders:', error);
      setSnackbarMessage(error instanceof Error ? error.message : 'Failed to delete some folders. Please try again.');
      setSnackbarOpen(true);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Box sx={{ 
      width: '100%', 
      padding: '16px 32px',
      bgcolor: '#f5f5f5',
      minHeight: 'calc(100vh - 56px)',
    }}>

      
            {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="500" mt={2}>
          Data Storage
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<FolderIcon />}
            onClick={handleNewFolder}
          >
            Create Empty Folder
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenUploadToFolderDialog(true)}
          >
            Upload to Folder
          </Button>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setOpenUploadDialog(true)}
          >
            Quick Upload (Auto-Create)
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchAllFolders}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="data storage tabs">
          <Tab label="Instant Run" />
          <Tab label="Periodic Run" />
        </Tabs>
      </Box>

      {/* Instant Run Tab */}
      <TabPanel value={activeTab} index={0}>
        {/* Search and filters bar */}
        <Box
          display="flex" 
          justifyContent="space-between" 
          alignItems="center" 
          sx={{
            mb: 1,
          }}
        >
          <Box display="flex" alignItems="center" gap={2}>
            <TextField
              placeholder="Search folders"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={handleSearchChange}
              sx={{ 
                width: '300px',
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'white',
                  '& fieldset': {
                    borderColor: 'rgba(0, 0, 0, 0.23)',
                  },
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            
            {/* Batch Delete Controls */}
            {isDeleteMode && (
              <Box display="flex" alignItems="center" gap={1}>
                <Tooltip title="Select All">
                  <IconButton 
                    size="small" 
                    onClick={handleSelectAll}
                    disabled={getHierarchicalFolders().length === 0}
                  >
                    <SelectAllIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Clear Selection">
                  <IconButton 
                    size="small" 
                    onClick={handleClearSelection}
                    disabled={selectedFolders.size === 0}
                  >
                    <ClearIcon />
                  </IconButton>
                </Tooltip>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<DeleteIcon />}
                  onClick={handleBatchDelete}
                  disabled={selectedFolders.size === 0}
                >
                  Delete ({selectedFolders.size})
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleToggleDeleteMode}
                >
                  Cancel
                </Button>
              </Box>
            )}
          </Box>

          <Box display="flex" alignItems="center" gap={2}>
            <FormControl size="small" sx={{ minWidth: 180, backgroundColor: 'white' }}>
              <InputLabel id="category-select-label">Category</InputLabel>
              <Select
                labelId="category-select-label"
                id="category-select"
                value={categoryFilter}
                label="Category"
                onChange={handleCategoryFilterChange}
              >
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            {!isDeleteMode && (
              <Tooltip title="Delete Mode">
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<DeleteIcon />}
                  onClick={handleToggleDeleteMode}
                  disabled={getHierarchicalFolders().length === 0}
                >
                  Delete
                </Button>
              </Tooltip>
            )}
          </Box>
        </Box>

        {/* Folders Count */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {isDeleteMode ? (
            `${selectedFolders.size} of ${getHierarchicalFolders().length} folder${getHierarchicalFolders().length !== 1 ? 's' : ''} selected`
          ) : (
            `Showing ${getHierarchicalFolders().length} run folder${getHierarchicalFolders().length !== 1 ? 's' : ''}`
          )}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Folders Table */}
        {loading ? (
          <Box display="flex" justifyContent="center" mt={4}>
            <CircularProgress />
          </Box>
        ) : (
          <>
           {/* File Explorer Style Folder Display */}
             {getHierarchicalFolders().length > 0 && (
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 500 }}>
                    Scraping Runs
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 2 }}>
                    {getHierarchicalFolders().map((runFolder) => (
                      <Paper 
                        key={`run-folder-${runFolder.id}-${runFolder.name?.replace(/\s+/g, '-').toLowerCase()}`}
                        sx={{ 
                          p: 2, 
                          border: isDeleteMode && selectedFolders.has(runFolder.id) ? '2px solid #f44336' : '1px solid #e0e0e0',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease-in-out',
                          backgroundColor: isDeleteMode && selectedFolders.has(runFolder.id) ? '#ffebee' : 'white',
                          '&:hover': { 
                            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                            transform: !isDeleteMode ? 'translateY(-2px)' : 'none'
                          }
                        }}
                        onClick={() => {
                          if (isDeleteMode) {
                            handleFolderSelection(runFolder.id, !selectedFolders.has(runFolder.id));
                          } else {
                            handleRunFolderClick(runFolder);
                          }
                        }}
                        onContextMenu={(e) => !isDeleteMode && handleContextMenu(e, runFolder)}
                      >
                        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                          <Box display="flex" alignItems="center">
                            {isDeleteMode && (
                              <Checkbox
                                checked={selectedFolders.has(runFolder.id)}
                                onChange={(e) => {
                                  e.stopPropagation();
                                  handleFolderSelection(runFolder.id, e.target.checked);
                                }}
                                sx={{ mr: 1 }}
                              />
                            )}
                            <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="h6" sx={{ fontWeight: 500 }}>
                              {runFolder.name}
                            </Typography>
                          </Box>
                          {!isDeleteMode && (
                            <IconButton
                              size="small"
                              onClick={(e) => handleMenuClick(e, runFolder)}
                              sx={{ opacity: 0.7, '&:hover': { opacity: 1 } }}
                            >
                              <MoreVertIcon />
                            </IconButton>
                          )}
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {`${runFolder.post_count || 0} folders`} 
                        </Typography>
                        
                      </Paper>
                    ))}
                  </Box>
                </Box>
              )}

            {/* Fallback: Show if no hierarchical folders but regular folders exist */}
            {getHierarchicalFolders().length === 0 && getFilteredFolders().length > 0 && (
              <Paper sx={{ p: 4, textAlign: 'center', mt: 2, borderRadius: 2 }}>
                <Typography variant="h6" gutterBottom>No hierarchical folders found</Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Found {getFilteredFolders().length} folders but they are not organized in a hierarchical structure.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This might indicate an issue with the folder structure or data.
                </Typography>
              </Paper>
            )}

            {/* No folders at all */}
            {getHierarchicalFolders().length === 0 && getFilteredFolders().length === 0 && (
              <Paper sx={{ p: 4, textAlign: 'center', mt: 2, borderRadius: 2 }}>
                <Typography variant="h6" gutterBottom>No folders found</Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {searchTerm || categoryFilter !== 'all' 
                    ? 'Try adjusting your search or filters'
                    : 'No folders have been created yet.'
                  }
                </Typography>
              </Paper>
            )}
           </>
          )}
      </TabPanel>

      {/* Periodic Run Tab */}
      <TabPanel value={activeTab} index={1}>
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Periodic Run Data
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This tab will display periodic run data when available.
          </Typography>
        </Box>
      </TabPanel>

             {/* New Folder Dialog */}
       <Dialog 
         open={openNewFolderDialog} 
         onClose={() => setOpenNewFolderDialog(false)}
         fullWidth
         maxWidth="sm"
       >
         <DialogTitle>Create Empty Folder</DialogTitle>
         <DialogContent>
           <TextField
             autoFocus
             margin="dense"
             id="name"
             name="folderName"
             label="Folder Name"
             type="text"
             fullWidth
             variant="outlined"
             value={folderName}
             onChange={(e) => setFolderName(e.target.value)}
             sx={{ mb: 2 }}
             placeholder="e.g., Nike Campaign Data, Q4 Social Media Posts"
           />
           <TextField
             margin="dense"
             id="description"
             name="folderDescription"
             label="Description (Optional)"
             type="text"
             fullWidth
             variant="outlined"
             multiline
             rows={3}
             value={folderDescription}
             onChange={(e) => setFolderDescription(e.target.value)}
             sx={{ mb: 2 }}
             placeholder="Brief description of what data this folder will contain"
           />
           
           <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1, mt: 2 }}>
             <Typography variant="body2" color="text.secondary" gutterBottom>
               <strong>How it works:</strong>
             </Typography>
             <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
               • This creates an empty main folder for organizing your data
             </Typography>
             <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
               • When you upload data files, platform subfolders (Instagram, Facebook, etc.) will be automatically created
             </Typography>
             <Typography variant="body2" color="text.secondary">
               • Example: "Nike Campaign" → "Instagram" → uploaded Instagram posts
             </Typography>
           </Box>
         </DialogContent>
         <DialogActions>
           <Button onClick={() => setOpenNewFolderDialog(false)}>Cancel</Button>
           <Button 
             onClick={handleCreateFolder} 
             variant="contained"
             disabled={isCreatingFolder || !folderName.trim()}
           >
             {isCreatingFolder ? 'Creating...' : 'Create Empty Folder'}
           </Button>
         </DialogActions>
       </Dialog>

       {/* Edit Folder Dialog */}
       <Dialog 
         open={openEditFolderDialog} 
         onClose={() => setOpenEditFolderDialog(false)}
         fullWidth
         maxWidth="sm"
       >
         <DialogTitle>Edit Folder</DialogTitle>
         <DialogContent>
           <TextField
             autoFocus
             margin="dense"
             id="edit-name"
             label="Folder Name"
             type="text"
             fullWidth
             variant="outlined"
             value={folderName}
             onChange={(e) => setFolderName(e.target.value)}
             sx={{ mb: 2 }}
           />
           <TextField
             margin="dense"
             id="edit-description"
             label="Description (Optional)"
             type="text"
             fullWidth
             variant="outlined"
             multiline
             rows={3}
             value={folderDescription}
             onChange={(e) => setFolderDescription(e.target.value)}
             sx={{ mb: 2 }}
           />
           <FormControl fullWidth sx={{ mb: 2 }}>
             <InputLabel id="edit-platform-select-label">Platform</InputLabel>
             <Select
               labelId="edit-platform-select-label"
               id="edit-platform-select"
               value={selectedPlatform}
               label="Platform"
               onChange={(e) => setSelectedPlatform(e.target.value)}
             >
               {platforms.map((platform) => (
                 <MenuItem key={platform.key} value={platform.key}>
                   <Box sx={{ display: 'flex', alignItems: 'center' }}>
                     <Box sx={{ color: platform.color, mr: 1 }}>
                       {platform.icon}
                     </Box>
                     {platform.label}
                   </Box>
                 </MenuItem>
               ))}
             </Select>
           </FormControl>
           <FormControl fullWidth>
             <InputLabel id="edit-category-select-label">Category</InputLabel>
             <Select
               labelId="edit-category-select-label"
               id="edit-category-select"
               value={selectedCategory}
               label="Category"
               onChange={(e) => setSelectedCategory(e.target.value)}
             >
               {categories.filter(cat => cat.value !== 'all').map((category) => (
                 <MenuItem key={category.value} value={category.value}>
                   {category.label}
                 </MenuItem>
               ))}
             </Select>
           </FormControl>
         </DialogContent>
         <DialogActions>
           <Button onClick={() => setOpenEditFolderDialog(false)}>Cancel</Button>
           <Button 
             onClick={handleUpdateFolder} 
             variant="contained"
             disabled={isEditingFolder || !folderName.trim()}
           >
             {isEditingFolder ? 'Updating...' : 'Update'}
           </Button>
         </DialogActions>
       </Dialog>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      />

      {/* Context Menu */}
      <Menu
        open={contextMenu !== null}
        onClose={handleCloseContextMenu}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        <MenuItem onClick={() => {
          if (contextMenu?.folder) {
            handleEditFolder(contextMenu.folder);
          }
          handleCloseContextMenu();
        }}>
          <ListItemText>Edit Folder</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          if (contextMenu?.folder) {
            handleDeleteFolder(contextMenu.folder);
          }
          handleCloseContextMenu();
        }}>
          <ListItemIcon>
            <DeleteIcon color="error" />
          </ListItemIcon>
          <ListItemText sx={{ color: 'error.main' }}>Delete Folder</ListItemText>
        </MenuItem>
      </Menu>

      {/* Dropdown Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleEditFromMenu}>
          <ListItemText>Edit Folder</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDeleteFromMenu}>
          <ListItemIcon>
            <DeleteIcon color="error" />
          </ListItemIcon>
          <ListItemText sx={{ color: 'error.main' }}>Delete Folder</ListItemText>
        </MenuItem>
      </Menu>

      {/* Upload Data Dialog */}
      <UploadDataDialog
        open={openUploadDialog}
        onClose={() => setOpenUploadDialog(false)}
        onSuccess={(folderId, folderName) => {
          setSnackbarMessage(`Successfully created folder "${folderName}" with uploaded data!`);
          setSnackbarOpen(true);
          fetchAllFolders(); // Refresh the folders list
          // Navigate to the new folder
          navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/run/${folderId}`);
        }}
      />

      {/* Upload to Folder Dialog */}
      <UploadToFolderDialog
        open={openUploadToFolderDialog}
        onClose={() => setOpenUploadToFolderDialog(false)}
        projectId={projectId || ''}
        onSuccess={(folderId, folderHierarchy, platform) => {
          setSnackbarMessage(`Successfully uploaded data to "${folderHierarchy}" → "${platform.charAt(0).toUpperCase() + platform.slice(1)}"!`);
          setSnackbarOpen(true);
          fetchAllFolders(); // Refresh the folders list
          // Navigate to the folder
          navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/run/${folderId}`);
        }}
      />
     </Box>
   );
 };

export default DataStorage; 
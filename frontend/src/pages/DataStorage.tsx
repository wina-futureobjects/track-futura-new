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
import WebUnlockerScraper from '../components/WebUnlockerScraper';
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

  /**
   * 🚀 UNIFIED API FETCH - Single endpoint for all folder data
   */
  const fetchAllFolders = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🚀 Fetching unified folder data...');
      
      // Use the correct report-folders API endpoint with proper parameters
      const response = await apiFetch(`/api/track-accounts/report-folders/?project=${projectId}&folder_type=run&include_hierarchy=true`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch folders: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📊 Unified API Response:', data);
      
      // Extract folders from unified response
      const allFolders: Folder[] = data.folders || [];
      
      // Flatten hierarchical structure for display
      const flattenFolders = (folder: any): Folder[] => {
        const result = [folder];
        if (folder.subfolders && folder.subfolders.length > 0) {
          folder.subfolders.forEach((subfolder: any) => {
            result.push(...flattenFolders(subfolder));
          });
        }
        return result;
      };
      
      const flatFolders = allFolders.flatMap(flattenFolders);
      setFolders(flatFolders);
      
      // Calculate statistics
      const totalFolders = flatFolders.length;
      const platformCounts = {
        instagram: flatFolders.filter(f => f.platform === 'instagram').length,
        facebook: flatFolders.filter(f => f.platform === 'facebook').length,
        linkedin: flatFolders.filter(f => f.platform === 'linkedin').length,
        tiktok: flatFolders.filter(f => f.platform === 'tiktok').length
      };
      
      setStats({
        totalFolders,
        platforms: platformCounts
      });
      
      console.log(`✅ Loaded ${totalFolders} folders from unified API`);
      
    } catch (error) {
      console.error('❌ Error fetching unified folders:', error);
      setError('Failed to load folder data. Please refresh to try again.');
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
    // Group folders by their hierarchy
    const runFolders = folders.filter(f => f.folder_type === 'run');
    const jobFolders = folders.filter(f => f.folder_type === 'job');
    const platformFolders = folders.filter(f => f.folder_type === 'platform');
    const serviceFolders = folders.filter(f => f.folder_type === 'service');
    
    return {
      runs: runFolders,
      jobs: jobFolders,
      platforms: platformFolders,
      services: serviceFolders
    };
  };

  const getPlatformFolders = (platformKey: string) => {
    return folders.filter(folder => folder.platform === platformKey);
  };

  const getPlatformIcon = (platform: string) => {
    const platformData = platforms.find(p => p.key === platform);
    return platformData ? platformData.icon : <FolderIcon />;
  };

  const getPlatformColor = (platform: string) => {
    const platformData = platforms.find(p => p.key === platform);
    return platformData ? platformData.color : '#666666';
  };

  const handleFolderClick = (folder: Folder) => {
    // Navigate to folder details
    const folderUrl = `/organizations/${organizationId}/projects/${projectId}/data-storage/${folder.folder_type}/${folder.id}`;
    navigate(folderUrl);
  };

  const handleCreateFolder = async () => {
    if (!folderName.trim()) return;
    
    setIsCreatingFolder(true);
    try {
      const response = await apiFetch('/api/create-folder/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: folderName,
          description: folderDescription,
          platform: selectedPlatform,
          category: selectedCategory,
          project: projectId
        }),
      });

      if (response.ok) {
        setSnackbarMessage('Folder created successfully');
        setSnackbarOpen(true);
        setOpenNewFolderDialog(false);
        setFolderName('');
        setFolderDescription('');
        fetchAllFolders(); // Refresh the list
      } else {
        throw new Error('Failed to create folder');
      }
    } catch (error) {
      console.error('Error creating folder:', error);
      setSnackbarMessage('Failed to create folder');
      setSnackbarOpen(true);
    } finally {
      setIsCreatingFolder(false);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, folder: Folder) => {
    setAnchorEl(event.currentTarget);
    setSelectedFolderForMenu(folder);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedFolderForMenu(null);
  };

  const handleDeleteFolder = async (folderId: number) => {
    try {
      const response = await apiFetch(`/api/folders/${folderId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setSnackbarMessage('Folder deleted successfully');
        setSnackbarOpen(true);
        fetchAllFolders(); // Refresh the list
      } else {
        throw new Error('Failed to delete folder');
      }
    } catch (error) {
      console.error('Error deleting folder:', error);
      setSnackbarMessage('Failed to delete folder');
      setSnackbarOpen(true);
    }
  };

  const handleEditFolder = (folder: Folder) => {
    setEditingFolder(folder);
    setFolderName(folder.name);
    setFolderDescription(folder.description || '');
    setSelectedPlatform(folder.platform);
    setSelectedCategory(folder.category);
    setOpenEditFolderDialog(true);
    handleMenuClose();
  };

  const handleUpdateFolder = async () => {
    if (!editingFolder || !folderName.trim()) return;
    
    setIsEditingFolder(true);
    try {
      const response = await apiFetch(`/api/folders/${editingFolder.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: folderName,
          description: folderDescription,
          platform: selectedPlatform,
          category: selectedCategory
        }),
      });

      if (response.ok) {
        setSnackbarMessage('Folder updated successfully');
        setSnackbarOpen(true);
        setOpenEditFolderDialog(false);
        setEditingFolder(null);
        setFolderName('');
        setFolderDescription('');
        fetchAllFolders(); // Refresh the list
      } else {
        throw new Error('Failed to update folder');
      }
    } catch (error) {
      console.error('Error updating folder:', error);
      setSnackbarMessage('Failed to update folder');
      setSnackbarOpen(true);
    } finally {
      setIsEditingFolder(false);
    }
  };

  const toggleFolderSelection = (folderId: number) => {
    const newSelection = new Set(selectedFolders);
    if (newSelection.has(folderId)) {
      newSelection.delete(folderId);
    } else {
      newSelection.add(folderId);
    }
    setSelectedFolders(newSelection);
  };

  const selectAllFolders = () => {
    const filteredFolders = getFilteredFolders();
    setSelectedFolders(new Set(filteredFolders.map(f => f.id)));
  };

  const clearSelection = () => {
    setSelectedFolders(new Set());
  };

  const handleBatchDelete = async () => {
    const folderIds = Array.from(selectedFolders);
    
    try {
      await Promise.all(folderIds.map(id => handleDeleteFolder(id)));
      setSnackbarMessage(`${folderIds.length} folders deleted successfully`);
      setSnackbarOpen(true);
      setSelectedFolders(new Set());
      setIsDeleteMode(false);
    } catch (error) {
      console.error('Error in batch delete:', error);
      setSnackbarMessage('Failed to delete some folders');
      setSnackbarOpen(true);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
          <Box ml={2}>
            <Typography variant="h6">Loading folder data...</Typography>
            <Typography variant="body2" color="textSecondary">
              Fetching from unified data sources
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={fetchAllFolders}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  const filteredFolders = getFilteredFolders();
  const hierarchicalData = getHierarchicalFolders();

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Data Storage
          </Typography>
          <Typography variant="body1" color="textSecondary" gutterBottom>
            Manage your social media data and scraped content
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchAllFolders}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenNewFolderDialog(true)}
          >
            New Folder
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Box display="flex" gap={2} mb={4}>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Box display="flex" alignItems="center">
            <StorageIcon color="primary" sx={{ mr: 1 }} />
            <Box>
              <Typography variant="h6">{stats.totalFolders}</Typography>
              <Typography variant="body2" color="textSecondary">Total Folders</Typography>
            </Box>
          </Box>
        </Paper>
        {platforms.map(platform => (
          <Paper key={platform.key} sx={{ p: 2, flex: 1 }}>
            <Box display="flex" alignItems="center">
              <Box sx={{ color: platform.color, mr: 1 }}>{platform.icon}</Box>
              <Box>
                <Typography variant="h6">{stats.platforms[platform.key as keyof typeof stats.platforms]}</Typography>
                <Typography variant="body2" color="textSecondary">{platform.label}</Typography>
              </Box>
            </Box>
          </Paper>
        ))}
      </Box>

      {/* Search and Filter Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          <TextField
            placeholder="Search folders..."
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 200 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={categoryFilter}
              onChange={handleCategoryFilterChange}
              label="Category"
            >
              {categories.map(category => (
                <MenuItem key={category.value} value={category.value}>
                  {category.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
            {isDeleteMode && (
              <>
                <Tooltip title="Select All">
                  <IconButton onClick={selectAllFolders} size="small">
                    <SelectAllIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Clear Selection">
                  <IconButton onClick={clearSelection} size="small">
                    <ClearIcon />
                  </IconButton>
                </Tooltip>
                <Button
                  variant="contained"
                  color="error"
                  size="small"
                  disabled={selectedFolders.size === 0}
                  onClick={handleBatchDelete}
                >
                  Delete Selected ({selectedFolders.size})
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    setIsDeleteMode(false);
                    setSelectedFolders(new Set());
                  }}
                >
                  Cancel
                </Button>
              </>
            )}
            {!isDeleteMode && (
              <Button
                variant="outlined"
                startIcon={<DeleteIcon />}
                size="small"
                onClick={() => setIsDeleteMode(true)}
                disabled={filteredFolders.length === 0}
              >
                Delete Mode
              </Button>
            )}
          </Box>
        </Box>
      </Paper>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="All Folders" />
          <Tab label="Hierarchical View" />
          <Tab label="Instagram" />
          <Tab label="Facebook" />
          <Tab label="LinkedIn" />
          <Tab label="TikTok" />
          <Tab label="Web Unlocker" />
        </Tabs>
      </Box>

      {/* All Folders Tab */}
      <TabPanel value={activeTab} index={0}>
        {filteredFolders.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <StorageIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No folders found
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              {searchTerm || categoryFilter !== 'all' 
                ? 'Try adjusting your search filters'
                : 'Create your first folder to get started'}
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenNewFolderDialog(true)}
              sx={{ mt: 2 }}
            >
              Create Folder
            </Button>
          </Paper>
        ) : (
          <Box display="flex" flexDirection="column" gap={2}>
            {filteredFolders.map((folder) => (
              <Paper 
                key={folder.id} 
                sx={{ 
                  p: 3, 
                  cursor: 'pointer', 
                  '&:hover': { bgcolor: 'action.hover' },
                  border: selectedFolders.has(folder.id) ? '2px solid' : '1px solid',
                  borderColor: selectedFolders.has(folder.id) ? 'primary.main' : 'divider'
                }}
                onClick={() => {
                  if (isDeleteMode) {
                    toggleFolderSelection(folder.id);
                  } else {
                    handleFolderClick(folder);
                  }
                }}
              >
                <Box display="flex" alignItems="center" justifyContent="between">
                  <Box display="flex" alignItems="center" flex={1}>
                    {isDeleteMode && (
                      <Checkbox
                        checked={selectedFolders.has(folder.id)}
                        onChange={() => toggleFolderSelection(folder.id)}
                        sx={{ mr: 2 }}
                        onClick={(e) => e.stopPropagation()}
                      />
                    )}
                    
                    <Box sx={{ color: getPlatformColor(folder.platform), mr: 2 }}>
                      {getPlatformIcon(folder.platform)}
                    </Box>
                    
                    <Box flex={1}>
                      <Typography variant="h6" component="h3">
                        {folder.name}
                      </Typography>
                      {folder.description && (
                        <Typography variant="body2" color="textSecondary">
                          {folder.description}
                        </Typography>
                      )}
                      <Box display="flex" gap={1} mt={1}>
                        <Chip 
                          label={folder.category_display || folder.category} 
                          size="small" 
                          color="primary" 
                          variant="outlined" 
                        />
                        <Chip 
                          label={folder.folder_type} 
                          size="small" 
                          color="secondary" 
                          variant="outlined" 
                        />
                        {folder.post_count !== undefined && (
                          <Chip 
                            label={`${folder.post_count} posts`} 
                            size="small" 
                            color="success" 
                            variant="outlined" 
                          />
                        )}
                      </Box>
                    </Box>
                  </Box>
                  
                  {!isDeleteMode && (
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMenuOpen(e, folder);
                      }}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  )}
                </Box>
              </Paper>
            ))}
          </Box>
        )}
      </TabPanel>

      {/* Hierarchical View Tab */}
      <TabPanel value={activeTab} index={1}>
        <Box display="flex" flexDirection="column" gap={3}>
          {/* Runs */}
          {hierarchicalData.runs.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Scraping Runs ({hierarchicalData.runs.length})
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                {hierarchicalData.runs.map((folder) => (
                  <Box 
                    key={folder.id}
                    sx={{ 
                      p: 2, 
                      border: '1px solid', 
                      borderColor: 'divider', 
                      borderRadius: 1,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                    onClick={() => handleFolderClick(folder)}
                  >
                    <Typography variant="subtitle1">{folder.name}</Typography>
                    {folder.description && (
                      <Typography variant="body2" color="textSecondary">
                        {folder.description}
                      </Typography>
                    )}
                  </Box>
                ))}
              </Box>
            </Paper>
          )}

          {/* Jobs */}
          {hierarchicalData.jobs.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Scraping Jobs ({hierarchicalData.jobs.length})
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                {hierarchicalData.jobs.map((folder) => (
                  <Box 
                    key={folder.id}
                    sx={{ 
                      p: 2, 
                      border: '1px solid', 
                      borderColor: 'divider', 
                      borderRadius: 1,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                    onClick={() => handleFolderClick(folder)}
                  >
                    <Box display="flex" alignItems="center">
                      <Box sx={{ color: getPlatformColor(folder.platform), mr: 2 }}>
                        {getPlatformIcon(folder.platform)}
                      </Box>
                      <Box>
                        <Typography variant="subtitle1">{folder.name}</Typography>
                        {folder.description && (
                          <Typography variant="body2" color="textSecondary">
                            {folder.description}
                          </Typography>
                        )}
                        <Box display="flex" gap={1} mt={1}>
                          <Chip label={folder.platform} size="small" />
                          {folder.post_count !== undefined && (
                            <Chip 
                              label={`${folder.post_count} posts`} 
                              size="small" 
                              color="success" 
                              variant="outlined" 
                            />
                          )}
                        </Box>
                      </Box>
                    </Box>
                  </Box>
                ))}
              </Box>
            </Paper>
          )}
        </Box>
      </TabPanel>

      {/* Platform-specific tabs */}
      {platforms.map((platform, index) => (
        <TabPanel key={platform.key} value={activeTab} index={index + 2}>
          {(() => {
            const platformFolders = getPlatformFolders(platform.key);
            
            if (platformFolders.length === 0) {
              return (
                <Paper sx={{ p: 4, textAlign: 'center' }}>
                  <Box sx={{ color: platform.color, mb: 2 }}>
                    {platform.icon}
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    No {platform.label} folders yet
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Start scraping {platform.label} data to see folders here
                  </Typography>
                </Paper>
              );
            }
            
            return (
              <Box display="flex" flexDirection="column" gap={2}>
                {platformFolders.map((folder) => (
                  <Paper 
                    key={folder.id} 
                    sx={{ 
                      p: 3, 
                      cursor: 'pointer', 
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                    onClick={() => handleFolderClick(folder)}
                  >
                    <Box display="flex" alignItems="center">
                      <Box sx={{ color: platform.color, mr: 2 }}>
                        {platform.icon}
                      </Box>
                      <Box>
                        <Typography variant="h6">{folder.name}</Typography>
                        {folder.description && (
                          <Typography variant="body2" color="textSecondary">
                            {folder.description}
                          </Typography>
                        )}
                        <Box display="flex" gap={1} mt={1}>
                          <Chip 
                            label={folder.category_display || folder.category} 
                            size="small" 
                            color="primary" 
                            variant="outlined" 
                          />
                          {folder.post_count !== undefined && (
                            <Chip 
                              label={`${folder.post_count} posts`} 
                              size="small" 
                              color="success" 
                              variant="outlined" 
                            />
                          )}
                        </Box>
                      </Box>
                    </Box>
                  </Paper>
                ))}
              </Box>
            );
          })()}
        </TabPanel>
      ))}

      {/* Web Unlocker Tab */}
      <TabPanel value={activeTab} index={6}>
        <WebUnlockerScraper />
      </TabPanel>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => selectedFolderForMenu && handleEditFolder(selectedFolderForMenu)}>
          <ListItemText>Edit Folder</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => {
            if (selectedFolderForMenu) {
              handleDeleteFolder(selectedFolderForMenu.id);
            }
            handleMenuClose();
          }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete Folder</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create Folder Dialog */}
      <Dialog open={openNewFolderDialog} onClose={() => setOpenNewFolderDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Folder Name"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              variant="outlined"
            />
            
            <TextField
              fullWidth
              label="Description (Optional)"
              value={folderDescription}
              onChange={(e) => setFolderDescription(e.target.value)}
              variant="outlined"
              multiline
              rows={3}
            />
            
            <FormControl fullWidth>
              <InputLabel>Platform</InputLabel>
              <Select
                value={selectedPlatform}
                onChange={(e) => setSelectedPlatform(e.target.value)}
                label="Platform"
              >
                {platforms.map(platform => (
                  <MenuItem key={platform.key} value={platform.key}>
                    <Box display="flex" alignItems="center">
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
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                {categories.slice(1).map(category => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNewFolderDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateFolder}
            variant="contained"
            disabled={!folderName.trim() || isCreatingFolder}
          >
            {isCreatingFolder ? <CircularProgress size={20} /> : 'Create Folder'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Folder Dialog */}
      <Dialog open={openEditFolderDialog} onClose={() => setOpenEditFolderDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Folder</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Folder Name"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              variant="outlined"
            />
            
            <TextField
              fullWidth
              label="Description (Optional)"
              value={folderDescription}
              onChange={(e) => setFolderDescription(e.target.value)}
              variant="outlined"
              multiline
              rows={3}
            />
            
            <FormControl fullWidth>
              <InputLabel>Platform</InputLabel>
              <Select
                value={selectedPlatform}
                onChange={(e) => setSelectedPlatform(e.target.value)}
                label="Platform"
              >
                {platforms.map(platform => (
                  <MenuItem key={platform.key} value={platform.key}>
                    <Box display="flex" alignItems="center">
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
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                {categories.slice(1).map(category => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditFolderDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleUpdateFolder}
            variant="contained"
            disabled={!folderName.trim() || isEditingFolder}
          >
            {isEditingFolder ? <CircularProgress size={20} /> : 'Update Folder'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upload Dialogs */}
      <UploadDataDialog
        open={openUploadDialog}
        onClose={() => setOpenUploadDialog(false)}
        projectId={projectId}
        onUploadComplete={fetchAllFolders}
      />
      
      <UploadToFolderDialog
        open={openUploadToFolderDialog}
        onClose={() => setOpenUploadToFolderDialog(false)}
        projectId={projectId}
        onUploadComplete={fetchAllFolders}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default DataStorage;

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
} from '@mui/icons-material';
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



const DataStorage = () => {
  const { organizationId, projectId } = useParams<{ organizationId: string; projectId: string }>();
  const navigate = useNavigate();
  
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
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
    } catch (error) {
      console.error(`Error fetching ${platform} folders:`, error);
      return [];
    }
  };

  const fetchAllFolders = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch run folders from track_accounts (unified run folders)
      let runFolders: any[] = [];
      try {
        const runFoldersResponse = await apiFetch(`/api/track-accounts/report-folders/?project=${projectId}&include_hierarchy=true`);
        if (runFoldersResponse.ok) {
          const runData = await runFoldersResponse.json();
          runFolders = (runData.results || runData).map((folder: any) => ({
            ...folder,
            platform: 'unified'
          }));
        }
      } catch (error) {
        console.warn('Could not fetch run folders from track_accounts:', error);
      }

      // Fetch folders from all platforms (Instagram, Facebook, LinkedIn, TikTok)
      const allPlatforms = ['instagram', 'facebook', 'linkedin', 'tiktok'];
      const folderPromises = allPlatforms.map(async (platform) => {
        const platformFolders = await fetchFolders(platform);
        // Add platform information to each folder
        return platformFolders.map((folder: any) => ({
          ...folder,
          platform: platform
        }));
      });

      const results = await Promise.all(folderPromises);
      const platformFolders = results.flat(); // Combine all platform folders into a single array

      // Combine run folders with platform folders
      const allFolders = [...runFolders, ...platformFolders];

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
      setError('Failed to load data folders. Please try again.');
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

  const getFilteredFolders = () => {
    return folders.filter(folder => {
      const matchesSearch = folder.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (folder.description && folder.description.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesCategory = categoryFilter === 'all' || folder.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  };

  const getHierarchicalFolders = () => {
    // Group folders by platform and type
    const foldersByPlatform = {
      facebook: folders.filter(f => f.platform === 'facebook'),
      instagram: folders.filter(f => f.platform === 'instagram'),
      linkedin: folders.filter(f => f.platform === 'linkedin'),
      tiktok: folders.filter(f => f.platform === 'tiktok')
    };
    
    // Get unified run folders (from track_accounts)
    const runFolders = folders.filter(folder => folder.folder_type === 'run' && folder.platform === 'unified');
    
    // Build hierarchy for each run folder
    const hierarchy = runFolders.map(runFolder => {
      const runServices: Folder[] = [];
      
      // Find ALL service folders that belong to this run (across all platforms)
      const allServiceFolders = folders.filter(f => f.folder_type === 'service' && f.scraping_run === runFolder.scraping_run);
      
      allServiceFolders.forEach((serviceFolder: Folder) => {
        // Find content folder for this service (in the same platform)
        const platformFolders = foldersByPlatform[serviceFolder.platform as keyof typeof foldersByPlatform] || [];
        const contentFolder = platformFolders.find((f: Folder) => f.folder_type === 'content' && f.parent_folder === serviceFolder.id);
        runServices.push({
          ...serviceFolder,
          subfolders: contentFolder ? [contentFolder] : []
        });
      });
      
      return {
        ...runFolder,
        subfolders: runServices
      };
    });
    
    return hierarchy;
  };

  const handleFolderClick = (platform: string, folder: Folder) => {
    // Navigate to folder contents page
    navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/${platform}/${folder.id}`);
  };

  const handleRunFolderClick = (runFolder: Folder) => {
    // Navigate to run folder contents page
    navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/run/${runFolder.id}`);
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
        category: selectedCategory,
        project: projectId
      };

      console.log('Creating folder with data:', folderData);
      console.log('Platform:', selectedPlatform);

      const response = await apiFetch(`/api/${selectedPlatform}-data/folders/`, {
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
      console.log('Folder created successfully:', data);
      
      setSnackbarMessage('Folder created successfully!');
      setSnackbarOpen(true);
      setOpenNewFolderDialog(false);
      
      // Refresh the folders list
      fetchAllFolders();
      
    } catch (error) {
      console.error('Error creating folder:', error);
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

      const response = await apiFetch(`/api/${selectedPlatform}-data/folders/${editingFolder.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(folderData),
      });

      if (!response.ok) {
        let errorDetail = 'Failed to update folder';
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
      const response = await apiFetch(`/api/${folder.platform}-data/folders/${folder.id}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete folder');
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

      
      {/* Header and actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="500">
          Data Storage
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleNewFolder}
            sx={{ 
              borderRadius: 1,
              bgcolor: '#e5e8eb', 
              color: '#000000', 
              textTransform: 'none',
              fontWeight: 500,
              boxShadow: 'none',
              '&:hover': {
                bgcolor: '#d5d8db',
                boxShadow: 'none'
              }
            }}
          >
            Create Folder
          </Button>
          <Button 
            variant="contained" 
            startIcon={<RefreshIcon />}
            onClick={fetchAllFolders}
            sx={{ 
              borderRadius: 1,
              bgcolor: '#e5e8eb', 
              color: '#000000', 
              textTransform: 'none',
              fontWeight: 500,
              boxShadow: 'none',
              '&:hover': {
                bgcolor: '#d5d8db',
                boxShadow: 'none'
              }
            }}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Search and filters bar */}
      <Box
        display="flex" 
        justifyContent="space-between" 
        alignItems="center" 
        sx={{
          mb: 1,
        }}
      >
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
      </Box>

      {/* Folders Count */}
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        Showing {getFilteredFolders().length} folder{getFilteredFolders().length !== 1 ? 's' : ''}
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
                    key={`${runFolder.platform}-${runFolder.id}`}
                    sx={{ 
                      p: 2, 
                      border: '1px solid #e0e0e0',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': { 
                        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                        transform: 'translateY(-2px)'
                      }
                    }}
                    onClick={() => handleRunFolderClick(runFolder)}
                  >
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                      <Box display="flex" alignItems="center">
                        <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="h6" sx={{ fontWeight: 500 }}>
                          {runFolder.name}
                        </Typography>
                      </Box>
                      <Chip 
                        label={`${runFolder.post_count || 0} items`} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Click to view contents
                    </Typography>
                    
                    {runFolder.subfolders && runFolder.subfolders.length > 0 && (
                      <Box>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                          Contains {runFolder.subfolders.length} service folder{runFolder.subfolders.length !== 1 ? 's' : ''}:
                        </Typography>
                        {runFolder.subfolders.slice(0, 3).map((serviceFolder) => (
                          <Chip 
                            key={`${serviceFolder.platform}-${serviceFolder.id}`}
                            label={serviceFolder.name}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                        {runFolder.subfolders.length > 3 && (
                          <Typography variant="caption" color="text.secondary">
                            +{runFolder.subfolders.length - 3} more
                          </Typography>
                        )}
                      </Box>
                    )}
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

             {/* New Folder Dialog */}
       <Dialog 
         open={openNewFolderDialog} 
         onClose={() => setOpenNewFolderDialog(false)}
         fullWidth
         maxWidth="sm"
       >
         <DialogTitle>Create New Folder</DialogTitle>
         <DialogContent>
           <TextField
             autoFocus
             margin="dense"
             id="name"
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
             id="description"
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
             <InputLabel id="platform-select-label">Platform</InputLabel>
             <Select
               labelId="platform-select-label"
               id="platform-select"
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
             <InputLabel id="category-select-label">Category</InputLabel>
             <Select
               labelId="category-select-label"
               id="category-select"
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
           <Button onClick={() => setOpenNewFolderDialog(false)}>Cancel</Button>
           <Button 
             onClick={handleCreateFolder} 
             variant="contained"
             disabled={isCreatingFolder || !folderName.trim()}
           >
             {isCreatingFolder ? 'Creating...' : 'Create'}
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
     </Box>
   );
 };

export default DataStorage; 
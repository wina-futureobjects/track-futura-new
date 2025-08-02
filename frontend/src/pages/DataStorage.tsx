import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Breadcrumbs,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Tooltip,
  IconButton,
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
  OpenInNew as OpenInNewIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Storage as StorageIcon,
  CalendarToday as CalendarIcon,
  MoreVert as MoreVertIcon,
  FolderOutlined as FolderOutlinedIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
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
      const response = await apiFetch(`/api/${platform}-data/folders/?project=${projectId}`);
      if (response.ok) {
        const data = await response.json();
        return data.results || data;
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
      const allFolders = results.flat(); // Combine all folders into a single array

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

  const handleFolderClick = (platform: string, folder: Folder) => {
    navigate(`/organizations/${organizationId}/projects/${projectId}/data/${platform}/${folder.id}`);
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
          {getFilteredFolders().length > 0 ? (
            <TableContainer component={Paper} sx={{ 
              boxShadow: 'none', 
              borderRadius: '4px',
              border: '1px solid rgba(0,0,0,0.12)'
            }}>
              <Table>
                <TableHead sx={{ bgcolor: '#f9fafb' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Folder name</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Platform</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Category</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Posts</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Description</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Created</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {getFilteredFolders().map((folder) => {
                    const platformConfig = platforms.find(p => p.key === folder.platform) || 
                      { key: folder.platform, label: folder.platform.charAt(0).toUpperCase() + folder.platform.slice(1), icon: <FolderIcon />, color: '#666' };
                    
                    return (
                      <TableRow 
                        key={folder.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleFolderClick(folder.platform, folder)}
                      >
                        <TableCell sx={{ color: 'primary.main', fontWeight: 500 }}>
                          <Box display="flex" alignItems="center">
                            <Box sx={{ color: platformConfig.color, mr: 1 }}>
                              {platformConfig.icon}
                            </Box>
                            {folder.name}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={platformConfig.label}
                            size="small"
                            sx={{ 
                              bgcolor: platformConfig.color,
                              color: 'white',
                              fontWeight: 500
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={folder.category_display || folder.category}
                            color={getCategoryColor(folder.category) as any}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          {folder.post_count !== undefined ? folder.post_count : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {folder.description || 'No description'}
                        </TableCell>
                        <TableCell>{formatDate(folder.created_at || '')}</TableCell>
                                                 <TableCell align="center">
                           <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                             <Tooltip title="Open Folder">
                               <IconButton 
                                 size="small"
                                 onClick={(e) => {
                                   e.stopPropagation();
                                   handleFolderClick(folder.platform, folder);
                                 }}
                               >
                                 <OpenInNewIcon fontSize="small" />
                               </IconButton>
                             </Tooltip>
                             <Tooltip title="Edit Folder">
                               <IconButton 
                                 size="small"
                                 onClick={(e) => {
                                   e.stopPropagation();
                                   handleEditFolder(folder);
                                 }}
                               >
                                 <EditIcon fontSize="small" />
                               </IconButton>
                             </Tooltip>
                                                           <Tooltip title="Delete Folder">
                                <IconButton 
                                  size="small"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteFolder(folder);
                                  }}
                                  sx={{ color: 'warning.main' }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                           </Box>
                         </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
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
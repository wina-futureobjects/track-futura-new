import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Stack,
  Card,
  CardContent,
  CardActions,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  CircularProgress,
  Divider,
  ToggleButtonGroup,
  ToggleButton,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Tooltip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import FolderIcon from '@mui/icons-material/Folder';
import CommentIcon from '@mui/icons-material/Comment';
import PostAddIcon from '@mui/icons-material/PostAdd';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import GridViewIcon from '@mui/icons-material/GridView';
import ViewListIcon from '@mui/icons-material/ViewList';
import { apiFetch } from '../utils/api';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  category: 'posts' | 'comments';
  category_display: string;
  created_at: string;
  updated_at: string;
  content_count: number;
}

const FacebookFolders = () => {
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
  
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [openNewFolderDialog, setOpenNewFolderDialog] = useState(false);
  const [openEditFolderDialog, setOpenEditFolderDialog] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null);
  const [folderName, setFolderName] = useState('');
  const [folderDescription, setFolderDescription] = useState('');
  const [folderCategory, setFolderCategory] = useState<'posts' | 'comments'>('posts');
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  // Fetch folders
  const fetchFolders = async () => {
    try {
      setLoading(true);
      
      // Don't fetch folders if no project is found
      if (!projectId) {
        console.error('No project ID found in URL');
        setError('No project context found. Please navigate to this page from within a project.');
        setFolders([]);
        setLoading(false);
        return;
      }
      
      // Add project filter
      const url = `/api/facebook-data/folders/?project=${projectId}`;
      
      console.log('=== FRONTEND FETCH FACEBOOK FOLDERS DEBUG ===');
      console.log('Project ID from URL path:', projectId);
      console.log('Current URL:', location.pathname);
      console.log('Fetch URL:', url);
      
      const response = await apiFetch(url);
      console.log('Fetch response status:', response.status);
      console.log('Fetch response ok:', response.ok);
      
      if (!response.ok) {
        throw new Error('Failed to fetch folders');
      }
      
      const data = await response.json();
      console.log('Raw response data:', data);
      
      // Check if the response is paginated (has a 'results' key)
      if (data && typeof data === 'object' && 'results' in data) {
        console.log('Using paginated data, count:', data.count);
        console.log('Results:', data.results);
        setFolders(data.results || []);
      } else if (Array.isArray(data)) {
        // Handle case where API returns direct array
        console.log('Using direct array data, length:', data.length);
        setFolders(data);
      } else {
        console.error('API returned unexpected data format:', data);
        setFolders([]);
        setError('Received invalid data format from server. Please try again.');
      }
      console.log('=== END FRONTEND FETCH FACEBOOK FOLDERS DEBUG ===');
    } catch (error) {
      console.error('Error fetching folders:', error);
      setFolders([]);
      setError('Failed to load folders. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFolders();
  }, [projectId]); // Add projectId as dependency

  const handleOpenFolder = (folderId: number) => {
    // Extract organization and project IDs from URL
    const match = location.pathname.match(/\/organizations\/(\d+)\/projects\/(\d+)/);
    
    if (match) {
      const [, orgId, projId] = match;
      navigate(`/organizations/${orgId}/projects/${projId}/facebook-data/${folderId}`);
    } else if (projectId) {
      // If not in the pathname but we have projectId in query params
      navigate(`/facebook-data/${folderId}?project=${projectId}`);
    } else {
      navigate(`/facebook-data/${folderId}`);
    }
  };

  const handleNewFolder = () => {
    setFolderName('');
    setFolderDescription('');
    setFolderCategory('posts');
    setOpenNewFolderDialog(true);
  };

  const handleEditFolder = (folder: Folder) => {
    setSelectedFolder(folder);
    setFolderName(folder.name);
    setFolderDescription(folder.description || '');
    setFolderCategory(folder.category);
    setOpenEditFolderDialog(true);
  };

  const handleCreateFolder = async () => {
    if (!folderName.trim()) {
      return;
    }

    try {
      const requestData = {
        name: folderName,
        description: folderDescription || null,
        category: folderCategory,
        project: projectId ? parseInt(projectId, 10) : null,
      };
      
      console.log('=== FRONTEND FACEBOOK FOLDER CREATION DEBUG ===');
      console.log('Project ID from URL:', projectId);
      console.log('Request data being sent:', requestData);
      console.log('API endpoint:', '/api/facebook-data/folders/');
      
      const response = await apiFetch('/api/facebook-data/folders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        const errorData = await response.text();
        console.log('Error response:', errorData);
        throw new Error('Failed to create folder');
      }

      const responseData = await response.json();
      console.log('Success response data:', responseData);
      console.log('=== END FRONTEND FACEBOOK FOLDER CREATION DEBUG ===');

      // Refresh folders list
      fetchFolders();
      setOpenNewFolderDialog(false);
    } catch (error) {
      console.error('Error creating folder:', error);
      setError('Failed to create folder. Please try again.');
    }
  };

  const handleUpdateFolder = async () => {
    if (!selectedFolder || !folderName.trim()) {
      return;
    }

    try {
      const response = await apiFetch(`/api/facebook-data/folders/${selectedFolder.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: folderName,
          description: folderDescription || null,
          category: folderCategory,
          project: projectId ? parseInt(projectId, 10) : null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update folder');
      }

      // Refresh folders list
      fetchFolders();
      setOpenEditFolderDialog(false);
    } catch (error) {
      console.error('Error updating folder:', error);
      setError('Failed to update folder. Please try again.');
    }
  };

  const handleDeleteFolder = async (folderId: number) => {
    if (!window.confirm('Are you sure you want to delete this folder? All posts inside will be moved to uncategorized.')) {
      return;
    }

    try {
      const response = await apiFetch(`/api/facebook-data/folders/${folderId}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete folder');
      }

      // Refresh folders list
      fetchFolders();
    } catch (error) {
      console.error('Error deleting folder:', error);
      setError('Failed to delete folder. Please try again.');
    }
  };

  const handleViewModeChange = (
    event: React.MouseEvent<HTMLElement>,
    newViewMode: 'list' | 'grid',
  ) => {
    if (newViewMode !== null) {
      setViewMode(newViewMode);
    }
  };

  const renderGridView = () => (
    <Stack spacing={3} direction="row" useFlexGap flexWrap="wrap">
      {folders.map((folder) => (
        <Box key={folder.id} sx={{ width: { xs: '100%', sm: '45%', md: '30%' }, mb: 3 }}>
          <Card 
            sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                cursor: 'pointer'
              }
            }}
          >
            <CardContent 
              sx={{ flexGrow: 1 }}
              onClick={() => handleOpenFolder(folder.id)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {folder.category === 'comments' ? (
                  <CommentIcon color="secondary" sx={{ mr: 1, fontSize: 30 }} />
                ) : (
                  <PostAddIcon color="primary" sx={{ mr: 1, fontSize: 30 }} />
                )}
                <Typography variant="h6" component="div">
                  {folder.name}
                </Typography>
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Chip 
                  label={folder.category_display} 
                  size="small" 
                  color={folder.category === 'comments' ? 'secondary' : 'primary'}
                  variant="outlined"
                />
              </Box>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {folder.description || 'No description'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                {folder.content_count} {folder.category === 'comments' ? 
                  (folder.content_count === 1 ? 'comment' : 'comments') : 
                  (folder.content_count === 1 ? 'post' : 'posts')
                }
              </Typography>
              
              <Typography variant="caption" color="text.secondary" display="block">
                Created: {new Date(folder.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
            
            <CardActions sx={{ justifyContent: 'flex-end', p: 1 }}>
              <IconButton 
                size="small" 
                onClick={(e) => {
                  e.stopPropagation();
                  handleEditFolder(folder);
                }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
              <IconButton 
                size="small" 
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteFolder(folder.id);
                }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </CardActions>
          </Card>
        </Box>
      ))}
    </Stack>
  );

  const renderListView = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Description</TableCell>
            <TableCell align="right">Content Count</TableCell>
            <TableCell>Created</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {folders.map((folder) => (
            <TableRow 
              key={folder.id}
              hover
              onClick={() => handleOpenFolder(folder.id)}
              sx={{ cursor: 'pointer' }}
            >
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {folder.category === 'comments' ? (
                    <CommentIcon color="secondary" sx={{ mr: 1 }} />
                  ) : (
                    <PostAddIcon color="primary" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="body1">{folder.name}</Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Chip 
                  label={folder.category_display} 
                  size="small" 
                  color={folder.category === 'comments' ? 'secondary' : 'primary'}
                  variant="outlined"
                />
              </TableCell>
              <TableCell>{folder.description || 'No description'}</TableCell>
              <TableCell align="right">
                {folder.content_count} {folder.category === 'comments' ? 
                  (folder.content_count === 1 ? 'comment' : 'comments') : 
                  (folder.content_count === 1 ? 'post' : 'posts')
                }
              </TableCell>
              <TableCell>{new Date(folder.created_at).toLocaleDateString()}</TableCell>
              <TableCell align="center">
                <IconButton 
                  size="small" 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEditFolder(folder);
                  }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton 
                  size="small" 
                  color="error"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteFolder(folder.id);
                  }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Facebook Data Folders
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={handleViewModeChange}
              aria-label="view mode"
              size="small"
              sx={{ mr: 2 }}
            >
              <ToggleButton value="list" aria-label="list view">
                <Tooltip title="List View">
                  <ViewListIcon />
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="grid" aria-label="grid view">
                <Tooltip title="Grid View">
                  <GridViewIcon />
                </Tooltip>
              </ToggleButton>
            </ToggleButtonGroup>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleNewFolder}
              disabled={!projectId}
            >
              New Folder
            </Button>
          </Box>
        </Box>
        <Divider sx={{ mb: 4 }} />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : folders.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              No folders yet
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Create a new folder to organize your Facebook data
            </Typography>
            <Button
              variant="outlined"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleNewFolder}
              disabled={!projectId}
            >
              Create First Folder
            </Button>
          </Paper>
        ) : (
          viewMode === 'grid' ? renderGridView() : renderListView()
        )}
      </Box>

      {/* Create New Folder Dialog */}
      <Dialog open={openNewFolderDialog} onClose={() => setOpenNewFolderDialog(false)}>
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent sx={{ minWidth: 400 }}>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            type="text"
            fullWidth
            variant="outlined"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            required
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={folderCategory}
              label="Category"
              onChange={(e) => setFolderCategory(e.target.value as 'posts' | 'comments')}
            >
              <MenuItem value="posts">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PostAddIcon sx={{ mr: 1 }} />
                  Posts & Reels
                </Box>
              </MenuItem>
              <MenuItem value="comments">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CommentIcon sx={{ mr: 1 }} />
                  Comments
                </Box>
              </MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            label="Description (optional)"
            type="text"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={folderDescription}
            onChange={(e) => setFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNewFolderDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateFolder} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Folder Dialog */}
      <Dialog open={openEditFolderDialog} onClose={() => setOpenEditFolderDialog(false)}>
        <DialogTitle>Edit Folder</DialogTitle>
        <DialogContent sx={{ minWidth: 400 }}>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            type="text"
            fullWidth
            variant="outlined"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            required
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={folderCategory}
              label="Category"
              onChange={(e) => setFolderCategory(e.target.value as 'posts' | 'comments')}
            >
              <MenuItem value="posts">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PostAddIcon sx={{ mr: 1 }} />
                  Posts & Reels
                </Box>
              </MenuItem>
              <MenuItem value="comments">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CommentIcon sx={{ mr: 1 }} />
                  Comments
                </Box>
              </MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            label="Description (optional)"
            type="text"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={folderDescription}
            onChange={(e) => setFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditFolderDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdateFolder} variant="contained">Update</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FacebookFolders; 
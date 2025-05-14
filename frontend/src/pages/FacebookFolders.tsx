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
  Breadcrumbs,
  Link,
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
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import FolderIcon from '@mui/icons-material/Folder';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import GridViewIcon from '@mui/icons-material/GridView';
import ViewListIcon from '@mui/icons-material/ViewList';
import HomeIcon from '@mui/icons-material/Home';
import { apiFetch } from '../utils/api';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  post_count: number;
}

const FacebookFolders = () => {
  const navigate = useNavigate();
  const location = useLocation();
  // Get project ID from URL query parameter
  const queryParams = new URLSearchParams(location.search);
  const projectId = queryParams.get('project');
  
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [openNewFolderDialog, setOpenNewFolderDialog] = useState(false);
  const [openEditFolderDialog, setOpenEditFolderDialog] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null);
  const [folderName, setFolderName] = useState('');
  const [folderDescription, setFolderDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  // Fetch folders
  const fetchFolders = async () => {
    try {
      setLoading(true);
      // Add project filter if projectId is available
      const url = projectId 
        ? `/api/facebook-data/folders/?project=${projectId}` 
        : '/api/facebook-data/folders/';
      
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch folders');
      }
      
      const data = await response.json();
      // Check if the response is paginated (has a 'results' key)
      if (data && typeof data === 'object' && 'results' in data) {
        setFolders(data.results || []);
      } else if (Array.isArray(data)) {
        // Handle case where API returns direct array
        setFolders(data);
      } else {
        console.error('API returned unexpected data format:', data);
        setFolders([]);
        setError('Received invalid data format from server. Please try again.');
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
      setFolders([]); // Ensure folders is an empty array when there's an error
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
    setOpenNewFolderDialog(true);
  };

  const handleEditFolder = (folder: Folder) => {
    setSelectedFolder(folder);
    setFolderName(folder.name);
    setFolderDescription(folder.description || '');
    setOpenEditFolderDialog(true);
  };

  const handleCreateFolder = async () => {
    if (!folderName.trim()) {
      return;
    }

    try {
      const response = await apiFetch('/api/facebook-data/folders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: folderName,
          description: folderDescription || null,
          project: projectId ? parseInt(projectId, 10) : null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create folder');
      }

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
                <FolderIcon color="primary" sx={{ mr: 1, fontSize: 30 }} />
                <Typography variant="h6" component="div">
                  {folder.name}
                </Typography>
              </Box>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {folder.description || 'No description'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                {folder.post_count} {folder.post_count === 1 ? 'post' : 'posts'}
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
            <TableCell>Description</TableCell>
            <TableCell align="right">Posts</TableCell>
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
                  <FolderIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body1">{folder.name}</Typography>
                </Box>
              </TableCell>
              <TableCell>{folder.description || 'No description'}</TableCell>
              <TableCell align="right">{folder.post_count}</TableCell>
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
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
            <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Facebook Data
          </Typography>
        </Breadcrumbs>

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
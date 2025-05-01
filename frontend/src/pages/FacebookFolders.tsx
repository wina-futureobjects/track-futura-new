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
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import FolderIcon from '@mui/icons-material/Folder';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import GridViewIcon from '@mui/icons-material/GridView';
import ViewListIcon from '@mui/icons-material/ViewList';
import HomeIcon from '@mui/icons-material/Home';

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
      const response = await fetch('/api/facebook-data/folders/');
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
  }, []);

  const handleOpenFolder = (folderId: number) => {
    navigate(`/facebook-data/${folderId}`);
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
      const response = await fetch('/api/facebook-data/folders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: folderName,
          description: folderDescription || null,
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
      const response = await fetch(`/api/facebook-data/folders/${selectedFolder.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: folderName,
          description: folderDescription || null,
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
      const response = await fetch(`/api/facebook-data/folders/${folderId}/`, {
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
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 3, mt: 2 }}>
      {folders.map((folder) => (
        <Card key={folder.id} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <CardContent sx={{ flexGrow: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <FolderIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div" noWrap title={folder.name}>
                {folder.name}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {folder.description || 'No description'}
            </Typography>
            <Typography variant="body2">
              {folder.post_count} posts
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Created: {new Date(folder.created_at).toLocaleDateString()}
            </Typography>
          </CardContent>
          <Divider />
          <CardActions>
            <Button size="small" onClick={() => handleOpenFolder(folder.id)}>
              Open
            </Button>
            <Box sx={{ flexGrow: 1 }} />
            <IconButton size="small" aria-label="edit" onClick={() => handleEditFolder(folder)}>
              <EditIcon fontSize="small" />
            </IconButton>
            <IconButton size="small" aria-label="delete" onClick={() => handleDeleteFolder(folder.id)}>
              <DeleteIcon fontSize="small" />
            </IconButton>
          </CardActions>
        </Card>
      ))}
    </Box>
  );

  const renderListView = () => (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell align="right">Posts</TableCell>
            <TableCell align="right">Created</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {folders.map((folder) => (
            <TableRow key={folder.id} hover>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FolderIcon color="primary" sx={{ mr: 1 }} />
                  <Typography>{folder.name}</Typography>
                </Box>
              </TableCell>
              <TableCell>{folder.description || '-'}</TableCell>
              <TableCell align="right">{folder.post_count}</TableCell>
              <TableCell align="right">{new Date(folder.created_at).toLocaleDateString()}</TableCell>
              <TableCell align="right">
                <Button size="small" onClick={() => handleOpenFolder(folder.id)}>
                  Open
                </Button>
                <IconButton size="small" aria-label="edit" onClick={() => handleEditFolder(folder)}>
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton size="small" aria-label="delete" onClick={() => handleDeleteFolder(folder.id)}>
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
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Breadcrumbs sx={{ mb: 2 }}>
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

        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" component="h1">
              Facebook Data Folders
            </Typography>
            <Box>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={handleViewModeChange}
                aria-label="view mode"
                size="small"
                sx={{ mr: 2 }}
              >
                <ToggleButton value="list" aria-label="list view">
                  <ViewListIcon />
                </ToggleButton>
                <ToggleButton value="grid" aria-label="grid view">
                  <GridViewIcon />
                </ToggleButton>
              </ToggleButtonGroup>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleNewFolder}
              >
                New Folder
              </Button>
            </Box>
          </Box>

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
              <Typography variant="subtitle1" gutterBottom>
                No folders found
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Create your first folder to start organizing your Facebook data.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleNewFolder}
              >
                Create Folder
              </Button>
            </Paper>
          ) : viewMode === 'grid' ? (
            renderGridView()
          ) : (
            renderListView()
          )}
        </Paper>
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
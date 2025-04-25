import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  TextField,
  IconButton,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
  Alert,
  CircularProgress,
  Breadcrumbs,
  Link,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FolderIcon from '@mui/icons-material/Folder';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  account_count: number;
  created_at: string;
  updated_at: string;
}

const TrackAccountFolders = () => {
  const navigate = useNavigate();
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderDescription, setNewFolderDescription] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [currentFolder, setCurrentFolder] = useState<Folder | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  // Fetch folders
  const fetchFolders = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/track-accounts/folders/');
      if (!response.ok) {
        throw new Error('Failed to fetch folders');
      }
      const data = await response.json();
      console.log('Fetched folders data:', data);
      
      // Ensure data is an array before setting folders
      if (data.results && Array.isArray(data.results)) {
        // Handle paginated response
        setFolders(data.results);
      } else if (Array.isArray(data)) {
        // Handle array response
        setFolders(data);
      } else {
        console.error('Unexpected data format from API:', data);
        setFolders([]);
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
      showSnackbar('Failed to load folders', 'error');
      setFolders([]); // Reset to empty array on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFolders();
  }, []);

  // Show snackbar message
  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  // Handle dialogs
  const handleOpenAddDialog = () => {
    setNewFolderName('');
    setNewFolderDescription('');
    setIsAddDialogOpen(true);
  };

  const handleOpenEditDialog = (folder: Folder) => {
    setCurrentFolder(folder);
    setNewFolderName(folder.name);
    setNewFolderDescription(folder.description || '');
    setIsEditDialogOpen(true);
  };

  const handleOpenDeleteDialog = (folder: Folder) => {
    setCurrentFolder(folder);
    setIsDeleteDialogOpen(true);
  };

  const handleCloseDialogs = () => {
    setIsAddDialogOpen(false);
    setIsEditDialogOpen(false);
    setIsDeleteDialogOpen(false);
    setCurrentFolder(null);
  };

  // CRUD operations
  const handleCreateFolder = async () => {
    try {
      const response = await fetch('/api/track-accounts/folders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newFolderName,
          description: newFolderDescription || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Create folder error response:', errorData);
        throw new Error(errorData.detail || 'Failed to create folder');
      }

      const newFolder = await response.json();
      console.log('Created new folder:', newFolder);

      handleCloseDialogs();
      // Update local state with the new folder instead of fetching again
      if (newFolder && newFolder.id) {
        setFolders(prevFolders => [...prevFolders, {
          ...newFolder,
          account_count: 0 // New folder has no accounts initially
        }]);
        showSnackbar('Folder created successfully', 'success');
      } else {
        // Fallback to fetching all folders if we don't get a valid response
        fetchFolders();
        showSnackbar('Folder created successfully', 'success');
      }
    } catch (error) {
      console.error('Error creating folder:', error);
      showSnackbar(error instanceof Error ? error.message : 'Failed to create folder', 'error');
    }
  };

  const handleUpdateFolder = async () => {
    if (!currentFolder) return;

    try {
      const response = await fetch(`/api/track-accounts/folders/${currentFolder.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newFolderName,
          description: newFolderDescription || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Update folder error response:', errorData);
        throw new Error(errorData.detail || 'Failed to update folder');
      }

      const updatedFolder = await response.json();
      console.log('Updated folder:', updatedFolder);

      handleCloseDialogs();
      
      // Update the folder in the local state
      if (updatedFolder && updatedFolder.id) {
        setFolders(prevFolders => 
          prevFolders.map(folder => 
            folder.id === updatedFolder.id ? { ...folder, ...updatedFolder } : folder
          )
        );
        showSnackbar('Folder updated successfully', 'success');
      } else {
        // Fallback to fetching all folders if we don't get a valid response
        fetchFolders();
        showSnackbar('Folder updated successfully', 'success');
      }
    } catch (error) {
      console.error('Error updating folder:', error);
      showSnackbar(error instanceof Error ? error.message : 'Failed to update folder', 'error');
    }
  };

  const handleDeleteFolder = async () => {
    if (!currentFolder) return;

    try {
      const response = await fetch(`/api/track-accounts/folders/${currentFolder.id}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Delete folder error response:', errorData);
        throw new Error(errorData.detail || 'Failed to delete folder');
      }

      handleCloseDialogs();
      
      // Remove the deleted folder from local state
      setFolders(prevFolders => prevFolders.filter(folder => folder.id !== currentFolder.id));
      showSnackbar('Folder deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting folder:', error);
      showSnackbar(error instanceof Error ? error.message : 'Failed to delete folder', 'error');
    }
  };

  const handleFolderClick = (folderId: number) => {
    navigate(`/track-accounts/folders/${folderId}`);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs navigation */}
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
        <Typography
          sx={{ display: 'flex', alignItems: 'center' }}
          color="text.primary"
        >
          <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Track Account Folders
        </Typography>
      </Breadcrumbs>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Track Account Folders
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenAddDialog}
        >
          Create Folder
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', margin: -1.5 }}>
          {!Array.isArray(folders) || folders.length === 0 ? (
            <Box sx={{ width: '100%', p: 1.5 }}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body1">
                  No folders found. Create a new folder to get started.
                </Typography>
              </Paper>
            </Box>
          ) : (
            folders.map((folder) => (
              <Box key={folder.id} sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 1.5 }}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => handleFolderClick(folder.id)}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <FolderIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6" component="div">
                        {folder.name}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {folder.description || 'No description'}
                    </Typography>
                    <Typography variant="body2">
                      Accounts: {folder.account_count}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Created: {new Date(folder.created_at).toLocaleDateString()}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end' }}>
                    <IconButton
                      aria-label="edit"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenEditDialog(folder);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      aria-label="delete"
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenDeleteDialog(folder);
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Box>
            ))
          )}
        </Box>
      )}

      {/* Add Folder Dialog */}
      <Dialog open={isAddDialogOpen} onClose={handleCloseDialogs}>
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Create a new folder to organize your track accounts.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Folder Name"
            type="text"
            fullWidth
            variant="outlined"
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            sx={{ mb: 2, mt: 2 }}
          />
          <TextField
            margin="dense"
            id="description"
            label="Description (Optional)"
            type="text"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newFolderDescription}
            onChange={(e) => setNewFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button
            onClick={handleCreateFolder}
            variant="contained"
            disabled={!newFolderName.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Folder Dialog */}
      <Dialog open={isEditDialogOpen} onClose={handleCloseDialogs}>
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
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            sx={{ mb: 2, mt: 2 }}
          />
          <TextField
            margin="dense"
            id="edit-description"
            label="Description (Optional)"
            type="text"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newFolderDescription}
            onChange={(e) => setNewFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button
            onClick={handleUpdateFolder}
            variant="contained"
            color="primary"
            disabled={!newFolderName.trim()}
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Folder Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseDialogs}>
        <DialogTitle>Delete Folder</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the folder "{currentFolder?.name}"? This action cannot be undone.
            {currentFolder && currentFolder.account_count > 0 && (
              <Box component="span" sx={{ display: 'block', mt: 2, color: 'error.main' }}>
                Warning: This folder contains {currentFolder.account_count} accounts that will be orphaned.
              </Box>
            )}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleDeleteFolder} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default TrackAccountFolders; 
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
  Grid,
  Card,
  CardContent,
  CardActions,
  Divider,
  Tooltip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Folder as FolderIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  UploadFile as UploadFileIcon,
} from '@mui/icons-material';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  posts_count?: number;
}

const TikTokFolders = () => {
  const navigate = useNavigate();
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderDescription, setNewFolderDescription] = useState('');
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null);
  const [editFolderName, setEditFolderName] = useState('');
  const [editFolderDescription, setEditFolderDescription] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  // Fetch folders on component mount
  useEffect(() => {
    fetchFolders();
  }, []);

  const fetchFolders = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/tiktok-data/folders/');
      
      if (!response.ok) {
        throw new Error('Failed to fetch folders');
      }
      
      const data = await response.json();
      // Get the results array from the paginated response
      const foldersData = data.results || [];
      
      // Fetch post counts for each folder
      const foldersWithCounts = await Promise.all(
        foldersData.map(async (folder: Folder) => {
          try {
            const countResponse = await fetch(`/api/tiktok-data/posts/?folder_id=${folder.id}&page_size=1`);
            if (countResponse.ok) {
              const countData = await countResponse.json();
              return { ...folder, posts_count: countData.count || 0 };
            }
            return folder;
          } catch (e) {
            return folder;
          }
        })
      );
      
      setFolders(foldersWithCounts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching folders:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      setSnackbarMessage('Folder name cannot be empty');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      return;
    }
    
    try {
      const response = await fetch('/api/tiktok-data/folders/', {
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
        throw new Error('Failed to create folder');
      }
      
      const newFolder = await response.json();
      setFolders([...folders, { ...newFolder, posts_count: 0 }]);
      setNewFolderName('');
      setNewFolderDescription('');
      setOpenCreateDialog(false);
      
      setSnackbarMessage('Folder created successfully');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (err) {
      setSnackbarMessage(err instanceof Error ? err.message : 'Failed to create folder');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleUpdateFolder = async () => {
    if (!selectedFolder) return;
    
    if (!editFolderName.trim()) {
      setSnackbarMessage('Folder name cannot be empty');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      return;
    }
    
    try {
      const response = await fetch(`/api/tiktok-data/folders/${selectedFolder.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: editFolderName,
          description: editFolderDescription || null,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update folder');
      }
      
      const updatedFolder = await response.json();
      setFolders(folders.map(folder => 
        folder.id === selectedFolder.id 
          ? { ...updatedFolder, posts_count: folder.posts_count } 
          : folder
      ));
      setOpenEditDialog(false);
      
      setSnackbarMessage('Folder updated successfully');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (err) {
      setSnackbarMessage(err instanceof Error ? err.message : 'Failed to update folder');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleDeleteFolder = async () => {
    if (!selectedFolder) return;
    
    try {
      const response = await fetch(`/api/tiktok-data/folders/${selectedFolder.id}/`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete folder');
      }
      
      setFolders(folders.filter(folder => folder.id !== selectedFolder.id));
      setOpenDeleteDialog(false);
      
      setSnackbarMessage('Folder deleted successfully');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (err) {
      setSnackbarMessage(err instanceof Error ? err.message : 'Failed to delete folder');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleOpenFolder = (folder: Folder) => {
    navigate(`/tiktok-data/${folder.id}`);
  };

  const handleOpenEditDialog = (folder: Folder) => {
    setSelectedFolder(folder);
    setEditFolderName(folder.name);
    setEditFolderDescription(folder.description || '');
    setOpenEditDialog(true);
  };

  const handleOpenDeleteDialog = (folder: Folder) => {
    setSelectedFolder(folder);
    setOpenDeleteDialog(true);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          TikTok Data Folders
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setOpenCreateDialog(true)}
        >
          Create Folder
        </Button>
      </Box>
      
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {folders.length === 0 ? (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="textSecondary">
                  No folders found. Create your first folder to get started.
                </Typography>
              </Paper>
            </Grid>
          ) : (
            folders.map((folder) => (
              <Grid item xs={12} sm={6} md={4} key={folder.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <FolderIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6" component="h2" noWrap>
                        {folder.name}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      {folder.description || 'No description'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>{folder.posts_count || 0}</strong> posts
                    </Typography>
                  </CardContent>
                  <Divider />
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<UploadFileIcon />}
                      onClick={() => handleOpenFolder(folder)}
                    >
                      Open
                    </Button>
                    <Box flexGrow={1} />
                    <Tooltip title="Edit">
                      <IconButton 
                        size="small"
                        onClick={() => handleOpenEditDialog(folder)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton 
                        size="small"
                        onClick={() => handleOpenDeleteDialog(folder)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}
      
      {/* Create Folder Dialog */}
      <Dialog 
        open={openCreateDialog} 
        onClose={() => setOpenCreateDialog(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            fullWidth
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            fullWidth
            multiline
            rows={3}
            value={newFolderDescription}
            onChange={(e) => setNewFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateFolder} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Edit Folder Dialog */}
      <Dialog 
        open={openEditDialog} 
        onClose={() => setOpenEditDialog(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Edit Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            fullWidth
            value={editFolderName}
            onChange={(e) => setEditFolderName(e.target.value)}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            fullWidth
            multiline
            rows={3}
            value={editFolderDescription}
            onChange={(e) => setEditFolderDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdateFolder} variant="contained" color="primary">
            Update
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Folder Dialog */}
      <Dialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the folder "{selectedFolder?.name}"? 
            This will also delete all posts inside this folder. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDeleteFolder} color="error">
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

export default TikTokFolders; 
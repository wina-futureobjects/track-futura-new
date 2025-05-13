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
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  ToggleButtonGroup,
  ToggleButton,
  Link,
  Breadcrumbs,
} from '@mui/material';
import {
  Add as AddIcon,
  Folder as FolderIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Home as HomeIcon,
  ViewList as ViewListIcon,
  GridView as GridViewIcon,
} from '@mui/icons-material';
import { apiFetch } from '../utils/api';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  posts_count?: number;
  created_at?: string;
}

const LinkedInFolders = () => {
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
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  // Fetch folders on component mount
  useEffect(() => {
    fetchFolders();
  }, []);

  const fetchFolders = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiFetch('/api/linkedin-data/folders/');
      
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
            const countResponse = await apiFetch(`/api/linkedin-data/posts/?folder_id=${folder.id}&page_size=1`);
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
      const response = await apiFetch('/api/linkedin-data/folders/', {
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
      const response = await apiFetch(`/api/linkedin-data/folders/${selectedFolder.id}/`, {
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
      const response = await apiFetch(`/api/linkedin-data/folders/${selectedFolder.id}/`, {
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
    navigate(`/linkedin-data/${folder.id}`);
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
        <Card key={folder.id} sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: '100%',
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
            cursor: 'pointer'
          }
        }}
          onClick={() => handleOpenFolder(folder)}
        >
          <CardContent 
            sx={{ flexGrow: 1 }}
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
              {folder.posts_count || 0} posts
            </Typography>
          </CardContent>
          <Divider />
          <CardActions onClick={(e) => e.stopPropagation()}>
            <Box sx={{ flexGrow: 1 }} />
            <Tooltip title="Edit">
              <IconButton 
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleOpenEditDialog(folder);
                }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton 
                size="small"
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  handleOpenDeleteDialog(folder);
                }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </CardActions>
        </Card>
      ))}
    </Box>
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
              onClick={() => handleOpenFolder(folder)}
              sx={{ cursor: 'pointer' }}
            >
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FolderIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body1">{folder.name}</Typography>
                </Box>
              </TableCell>
              <TableCell>{folder.description || 'No description'}</TableCell>
              <TableCell align="right">{folder.posts_count || 0}</TableCell>
              <TableCell>{folder.created_at ? new Date(folder.created_at).toLocaleDateString() : 'Unknown'}</TableCell>
              <TableCell align="center">
                <IconButton 
                  size="small" 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenEditDialog(folder);
                  }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton 
                  size="small" 
                  color="error"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenDeleteDialog(folder);
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
            LinkedIn Data
          </Typography>
        </Breadcrumbs>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            LinkedIn Data Folders
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
              onClick={() => setOpenCreateDialog(true)}
            >
              New Folder
            </Button>
          </Box>
        </Box>
        <Divider sx={{ mb: 4 }} />
      
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        ) : folders.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              No folders yet
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Create a new folder to organize your LinkedIn data
            </Typography>
            <Button
              variant="outlined"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setOpenCreateDialog(true)}
            >
              Create First Folder
            </Button>
          </Paper>
        ) : (
          viewMode === 'grid' ? renderGridView() : renderListView()
        )}
      </Box>
      
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

export default LinkedInFolders; 
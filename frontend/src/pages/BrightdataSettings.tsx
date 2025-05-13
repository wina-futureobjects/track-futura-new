import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  TextField,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Snackbar,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  Stack,
  Tooltip,
  Breadcrumbs,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import HomeIcon from '@mui/icons-material/Home';
import SettingsIcon from '@mui/icons-material/Settings';

interface BrightdataConfig {
  id: number;
  name: string;
  dataset_id: string;
  api_token: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const BrightdataSettings = () => {
  const [configs, setConfigs] = useState<BrightdataConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Form state
  const [formOpen, setFormOpen] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [name, setName] = useState('');
  const [apiToken, setApiToken] = useState('');
  const [datasetId, setDatasetId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Delete confirmation dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [configToDelete, setConfigToDelete] = useState<number | null>(null);

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/brightdata/configs/');
      if (!response.ok) {
        throw new Error('Failed to fetch configurations');
      }
      const responseData = await response.json();
      
      // Handle paginated response format (results array) or direct array
      const data = responseData.results || responseData;
      
      // Ensure data is an array before setting state
      const configsArray = Array.isArray(data) ? data : [];
      setConfigs(configsArray);
      
      // Check if there's an active configuration
      const hasActive = configsArray.some((config) => config.is_active);
      
      if (!hasActive && configsArray.length > 0) {
        setError('No active Brightdata configuration found. Please set one in the settings.');
      }
    } catch (error) {
      console.error('Error fetching configs:', error);
      setError('Failed to load Brightdata configurations');
      setConfigs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConfig = () => {
    setEditId(null);
    setName('');
    setApiToken('');
    setDatasetId('');
    setFormOpen(true);
  };

  const handleEditConfig = (config: BrightdataConfig) => {
    setEditId(config.id);
    setName(config.name);
    setApiToken(''); // Don't set the API token for security reasons
    setDatasetId(config.dataset_id);
    setFormOpen(true);
  };

  const handleCloseForm = () => {
    setFormOpen(false);
  };

  const handleSubmit = async () => {
    if (!name || !datasetId || (editId === null && !apiToken)) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setIsSubmitting(true);
      
      const payload: any = {
        name,
        dataset_id: datasetId,
      };
      
      // Only include API token for new configs or if the user has entered a new one
      if (apiToken) {
        payload.api_token = apiToken;
      }
      
      const url = editId !== null 
        ? `/api/brightdata/configs/${editId}/` 
        : '/api/brightdata/configs/';
      
      const method = editId !== null ? 'PATCH' : 'POST';
      
      console.log('Submitting config:', url, method, payload);
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save configuration');
      }

      setSuccessMessage(editId !== null ? 'Configuration updated successfully' : 'Configuration created successfully');
      fetchConfigs();
      setFormOpen(false);
    } catch (error: any) {
      console.error('Error saving config:', error);
      setError(error.message || 'Error saving configuration. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSetActive = async (configId: number) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/brightdata/configs/${configId}/set_active/`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to set configuration as active');
      }

      setSuccessMessage('Configuration set as active');
      fetchConfigs();
    } catch (error) {
      console.error('Error setting active config:', error);
      setError('Failed to set configuration as active');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (configId: number) => {
    setConfigToDelete(configId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (configToDelete === null) return;
    
    try {
      setLoading(true);
      const response = await fetch(`/api/brightdata/configs/${configToDelete}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete configuration');
      }

      setSuccessMessage('Configuration deleted successfully');
      fetchConfigs();
    } catch (error) {
      console.error('Error deleting config:', error);
      setError('Failed to delete configuration');
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
      setConfigToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setConfigToDelete(null);
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccessMessage(null);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none', color: 'inherit' }}>
            <HomeIcon sx={{ mr: 0.5 }} fontSize="small" />
            Home
          </Link>
          <Typography sx={{ display: 'flex', alignItems: 'center' }} color="text.primary">
            <SettingsIcon sx={{ mr: 0.5 }} fontSize="small" />
            Brightdata Settings
          </Typography>
        </Breadcrumbs>
        
        <Typography variant="h4" gutterBottom component="h1">
          Brightdata API Settings
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Manage your Brightdata API configurations for automated data scraping.
        </Typography>
      </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">
              API Configurations
            </Typography>
            <Button 
              variant="contained" 
              startIcon={<AddIcon />} 
              onClick={handleCreateConfig}
            >
              Add New Configuration
            </Button>
          </Stack>

          {loading && configs.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Status</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Dataset ID</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Updated</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {!Array.isArray(configs) || configs.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No configurations found. Click "Add New Configuration" to create one.
                      </TableCell>
                    </TableRow>
                  ) : (
                    configs.map((config) => (
                      <TableRow key={config.id}>
                        <TableCell>
                          <Tooltip title={config.is_active ? "Active Configuration" : "Set as Active"}>
                            <IconButton 
                              color={config.is_active ? "primary" : "default"} 
                              onClick={() => !config.is_active && handleSetActive(config.id)}
                              disabled={config.is_active}
                            >
                              {config.is_active ? <CheckCircleIcon /> : <RadioButtonUncheckedIcon />}
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                        <TableCell>{config.name}</TableCell>
                        <TableCell>{config.dataset_id}</TableCell>
                        <TableCell>{new Date(config.created_at).toLocaleString()}</TableCell>
                        <TableCell>{new Date(config.updated_at).toLocaleString()}</TableCell>
                        <TableCell>
                          <IconButton onClick={() => handleEditConfig(config)}>
                            <EditIcon />
                          </IconButton>
                          <IconButton onClick={() => handleDeleteClick(config.id)} color="error">
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Dialog open={formOpen} onClose={handleCloseForm}>
        <DialogTitle>{editId !== null ? 'Edit Configuration' : 'Add New Configuration'}</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            {editId !== null 
              ? 'Update your Brightdata API configuration.' 
              : 'Create a new Brightdata API configuration for data scraping.'}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Configuration Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Dataset ID"
            fullWidth
            value={datasetId}
            onChange={(e) => setDatasetId(e.target.value)}
            sx={{ mb: 2 }}
            helperText="The ID of the Brightdata dataset (found in the dataset settings)"
          />
          <TextField
            margin="dense"
            label="API Token"
            type="password"
            fullWidth
            value={apiToken}
            onChange={(e) => setApiToken(e.target.value)}
            helperText={editId !== null 
              ? "Leave blank to keep the current API token" 
              : "Your Brightdata API token (found in your account settings)"}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseForm}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            color="primary" 
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={deleteDialogOpen}
        onClose={handleCancelDelete}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this configuration? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar 
        open={!!error || !!successMessage} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={error ? "error" : "success"} 
          sx={{ width: '100%' }}
        >
          {error || successMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default BrightdataSettings; 
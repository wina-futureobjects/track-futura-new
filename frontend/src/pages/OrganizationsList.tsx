import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import SearchIcon from '@mui/icons-material/Search';
import {
    Box,
    Breadcrumbs,
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    IconButton,
    InputAdornment,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    SelectChangeEvent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../utils/api';
import { getAuthToken } from '../utils/auth';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { apiFetch } from '../utils/api';

interface Organization {
  id: number;
  name: string;
  description: string | null;
  owner: number;
  owner_name: string;
  members_count: number;
  created_at: string;
  updated_at: string;
}

const OrganizationsList = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [openNewDialog, setOpenNewDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
  const [orgName, setOrgName] = useState('');
  const [orgDescription, setOrgDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('last viewed');

  // Fetch organizations
  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/users/organizations/');
      if (!response.ok) {
        throw new Error('Failed to fetch organizations');
      }
      
      const data = await response.json();
      
      if (Array.isArray(data)) {
        setOrganizations(data);
      } else if (data && typeof data === 'object' && 'results' in data) {
        setOrganizations(data.results || []);
      } else {
        console.error('API returned unexpected data format:', data);
        setOrganizations([]);
        setError('Received invalid data format from server.');
      }
    } catch (error) {
      console.error('Error fetching organizations:', error);
      setOrganizations([]);
      setError('Failed to load organizations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const handleOpenOrganization = (organizationId: number) => {
    navigate(`/organizations/${organizationId}/projects`);
  };

  const handleNewOrganization = () => {
    setOrgName('');
    setOrgDescription('');
    setOpenNewDialog(true);
  };

  const handleEditOrganization = (organization: Organization) => {
    setSelectedOrganization(organization);
    setOrgName(organization.name);
    setOrgDescription(organization.description || '');
    setOpenEditDialog(true);
  };

  const handleCreateOrganization = async () => {
    if (!orgName.trim()) {
      return;
    }

    try {
      const response = await apiFetch('/api/users/organizations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: orgName,
          description: orgDescription || null,
        }),
      });

      if (!response.ok) {
        // Try to get the detailed error message
        let errorDetail = 'Failed to create organization';
        try {
          const errorData = await response.json();
          console.error('Error data from server:', errorData);
          if (errorData.detail) {
            errorDetail = errorData.detail;
          } else if (typeof errorData === 'object') {
            // For field-specific errors
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
      
      fetchOrganizations();
      setOpenNewDialog(false);
    } catch (error) {
      console.error('Error creating organization:', error);
      setError(error instanceof Error ? error.message : 'Failed to create organization. Please try again.');
    }
  };

  const handleUpdateOrganization = async () => {
    if (!selectedOrganization || !orgName.trim()) {
      return;
    }

    try {
      const response = await apiFetch(`/api/users/organizations/${selectedOrganization.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: orgName,
          description: orgDescription || null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update organization');
      }

      fetchOrganizations();
      setOpenEditDialog(false);
    } catch (error) {
      console.error('Error updating organization:', error);
      setError('Failed to update organization. Please try again.');
    }
  };

  const handleDeleteOrganization = async (organizationId: number) => {
    if (!window.confirm('Are you sure you want to delete this organization? All projects inside this organization will be deleted.')) {
      return;
    }

    try {
      const response = await apiFetch(`/api/users/organizations/${organizationId}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete organization');
      }

      fetchOrganizations();
    } catch (error) {
      console.error('Error deleting organization:', error);
      setError('Failed to delete organization. Please try again.');
    }
  };

  const handleSortChange = (event: SelectChangeEvent) => {
    setSortBy(event.target.value);
  };

  // Filter organizations based on search query
  const filteredOrganizations = organizations.filter(org => 
    org.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ 
      width: '100%', 
      padding: '16px 32px',
      bgcolor: '#f5f5f5',
      minHeight: 'calc(100vh - 56px)',
    }}>
      {/* Breadcrumbs */}
      <Box sx={{ mb: 2 }}>
        <Breadcrumbs aria-label="breadcrumb">
          <Typography color="text.primary">Organizations</Typography>
        </Breadcrumbs>
      </Box>
      
      {/* Header and actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="500">
          Organizations
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={handleNewOrganization}
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
          Create organization
        </Button>
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
          placeholder="Search organizations"
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
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
          <InputLabel id="sort-select-label">Sort by</InputLabel>
          <Select
            labelId="sort-select-label"
            id="sort-select"
            value={sortBy}
            label="Sort by"
            onChange={handleSortChange}
          >
            <MenuItem value="last viewed">last viewed</MenuItem>
            <MenuItem value="newest">newest</MenuItem>
            <MenuItem value="oldest">oldest</MenuItem>
            <MenuItem value="name">name</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Organizations Count */}
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        Showing {filteredOrganizations.length} organization{filteredOrganizations.length !== 1 ? 's' : ''}
      </Typography>

      {/* Organizations Table */}
      {loading ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {filteredOrganizations.length > 0 ? (
            <TableContainer component={Paper} sx={{ 
              boxShadow: 'none', 
              borderRadius: '4px',
              border: '1px solid rgba(0,0,0,0.12)'
            }}>
              <Table>
                <TableHead sx={{ bgcolor: '#f9fafb' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Organization name</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Owner</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Members</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Projects</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Created</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredOrganizations.map((org) => (
                    <TableRow 
                      key={org.id}
                      hover
                      sx={{ cursor: 'pointer' }}
                      onClick={() => handleOpenOrganization(org.id)}
                    >
                      <TableCell sx={{ color: theme.palette.primary.main, fontWeight: 500 }}>{org.name}</TableCell>
                      <TableCell>{org.owner_name}</TableCell>
                      <TableCell>{org.members_count}</TableCell>
                      <TableCell>-</TableCell>
                      <TableCell>{new Date(org.created_at).toLocaleDateString()}</TableCell>
                      <TableCell align="center">
                        <IconButton 
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditOrganization(org);
                          }}
                        >
                          <MoreVertIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center', mt: 2, borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom>No organizations found</Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Create your first organization to get started.
              </Typography>
              <Button 
                variant="contained" 
                startIcon={<AddIcon />} 
                onClick={handleNewOrganization}
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
                Create Organization
              </Button>
            </Paper>
          )}
        </>
      )}

      {/* New Organization Dialog */}
      <Dialog open={openNewDialog} onClose={() => setOpenNewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Organization</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Organization Name"
            type="text"
            fullWidth
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            required
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            type="text"
            fullWidth
            multiline
            rows={3}
            value={orgDescription}
            onChange={(e) => setOrgDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNewDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateOrganization} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Organization Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Organization</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Organization Name"
            type="text"
            fullWidth
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            required
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            type="text"
            fullWidth
            multiline
            rows={3}
            value={orgDescription}
            onChange={(e) => setOrgDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => selectedOrganization && handleDeleteOrganization(selectedOrganization.id)} 
            color="error"
          >
            Delete
          </Button>
          <Box sx={{ flexGrow: 1 }} />
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdateOrganization} variant="contained" color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error message */}
      {error && (
        <Box mt={2} p={2} bgcolor="error.light" color="error.dark" borderRadius={1}>
          <Typography variant="body2">{error}</Typography>
        </Box>
      )}
    </Box>
  );
};

export default OrganizationsList; 

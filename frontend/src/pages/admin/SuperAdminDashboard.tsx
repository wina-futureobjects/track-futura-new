import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  CircularProgress,
  Grid as MuiGrid,
  Card,
  CardContent,
  IconButton,
  Chip,
  InputAdornment,
  Snackbar,
  Alert,
  Switch,
  FormControlLabel,
  Breadcrumbs,
  Menu,
} from '@mui/material';

// Create a Grid component that inherits from MuiGrid to fix type issues
const Grid = (props: any) => <MuiGrid {...props} />;
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  SupervisorAccount as AdminIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Facebook as FacebookIcon,
  Instagram as InstagramIcon,
  LinkedIn as LinkedInIcon,
  MusicVideo as MusicVideoIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { apiFetch } from '../../utils/api';

interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  global_role?: {
    role: string;
    role_display: string;
  };
}

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

const SuperAdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [openUserDialog, setOpenUserDialog] = useState(false);
  const [openOrgDialog, setOpenOrgDialog] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    role: 'tenant_admin',
  });

  const [newOrg, setNewOrg] = useState({
    name: '',
    description: '',
    owner_id: 0,
  });
  const [error, setError] = useState<string | null>(null);
  
  // Brightdata configuration dialog state
  const [brightdataDialogOpen, setBrightdataDialogOpen] = useState(false);
  const [brightdataForm, setBrightdataForm] = useState({
    name: '',
    platform: '',
    description: '',
    apiToken: '',
    datasetId: '',
    isActive: true,
  });
  const [brightdataConfigs, setBrightdataConfigs] = useState<any[]>([]);
  const [brightdataLoading, setBrightdataLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editConfigId, setEditConfigId] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [configToDelete, setConfigToDelete] = useState<number | null>(null);
  const [deleteUserDialogOpen, setDeleteUserDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<number | null>(null);
  const [deleteOrgDialogOpen, setDeleteOrgDialogOpen] = useState(false);
  const [orgToDelete, setOrgToDelete] = useState<number | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [roleMenuAnchor, setRoleMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [roleChangeDialogOpen, setRoleChangeDialogOpen] = useState(false);
  const [pendingRoleChange, setPendingRoleChange] = useState<{ userId: number; newRole: string } | null>(null);
  const [statusChangeDialogOpen, setStatusChangeDialogOpen] = useState(false);
  const [pendingStatusChange, setPendingStatusChange] = useState<{ userId: number; newStatus: boolean } | null>(null);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalOrgs: 0,
    totalProjects: 0,
    superAdmins: 0,
    tenantAdmins: 0,
    regularUsers: 0,
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Fetch Brightdata configurations when Brightdata tab is active
  useEffect(() => {
    if (activeTab === 3) {
      fetchBrightdataConfigs();
    }
  }, [activeTab]);

  const fetchBrightdataConfigs = async () => {
    try {
      setBrightdataLoading(true);
      const response = await apiFetch('/api/brightdata/configs/');
      if (!response.ok) {
        throw new Error('Failed to fetch configurations');
      }
      const responseData = await response.json();
      const data = responseData.results || responseData;
      const configsArray = Array.isArray(data) ? data : [];
      setBrightdataConfigs(configsArray);
    } catch (error) {
      console.error('Error fetching brightdata configs:', error);
    } finally {
      setBrightdataLoading(false);
    }
  };

  const handleCreateBrightdataConfig = async () => {
    // Validate required fields
    if (!brightdataForm.name || !brightdataForm.platform || !brightdataForm.datasetId) {
      setSuccessMessage('Please fill in all required fields');
      return;
    }

    // For new configurations, API token is required
    if (editConfigId === null && !brightdataForm.apiToken) {
      setSuccessMessage('API token is required for new configurations');
      return;
    }

    // For editing, if API token is provided, validate it's not just whitespace
    if (editConfigId !== null && brightdataForm.apiToken && brightdataForm.apiToken.trim() === '') {
      setSuccessMessage('API token cannot be empty. Leave the field empty to keep existing token.');
      return;
    }

    try {
      setIsSubmitting(true);
      
      const payload: any = {
        name: brightdataForm.name,
        platform: brightdataForm.platform,
        dataset_id: brightdataForm.datasetId,
        description: brightdataForm.description || '',
        is_active: brightdataForm.isActive,
      };
      
      // Only include API token for new configs or if the user has entered a new one
      if (brightdataForm.apiToken) {
        payload.api_token = brightdataForm.apiToken;
      }
      
      const url = editConfigId !== null 
        ? `/api/brightdata/configs/${editConfigId}/` 
        : '/api/brightdata/configs/';
      
      const method = editConfigId !== null ? 'PATCH' : 'POST';
      
      const response = await apiFetch(url, {
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

      setSuccessMessage(editConfigId !== null ? 'Configuration updated successfully!' : 'Configuration created successfully!');
      setBrightdataDialogOpen(false);
      setBrightdataForm({ name: '', platform: '', description: '', apiToken: '', datasetId: '', isActive: true });
      setEditConfigId(null);
      fetchBrightdataConfigs(); // Refresh the list
    } catch (error: any) {
      console.error('Error saving config:', error);
      setSuccessMessage(error.message || 'Error saving configuration. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditConfig = (config: any) => {
    setEditConfigId(config.id);
    setBrightdataForm({
      name: config.name,
      platform: config.platform,
      description: config.description || '',
      apiToken: '', // Don't set API token for security
      datasetId: config.dataset_id,
      isActive: config.is_active,
    });
    setBrightdataDialogOpen(true);
  };

  const handleDeleteClick = (configId: number) => {
    setConfigToDelete(configId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (configToDelete === null) return;
    
    try {
      setBrightdataLoading(true);
      const response = await apiFetch(`/api/brightdata/configs/${configToDelete}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete configuration');
      }

      setSuccessMessage('Configuration deleted successfully');
      fetchBrightdataConfigs();
    } catch (error) {
      console.error('Error deleting config:', error);
      setSuccessMessage('Failed to delete configuration');
    } finally {
      setBrightdataLoading(false);
      setDeleteDialogOpen(false);
      setConfigToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setConfigToDelete(null);
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchUsers(),
        fetchOrganizations(),
        fetchStats(),
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await apiFetch('/api/admin/users/');
      if (response.ok) {
        const data = await response.json();
        setUsers(Array.isArray(data) ? data : data.results || []);
      } else {
        throw new Error('Failed to fetch users');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users.');
    }
  };

  const fetchOrganizations = async () => {
    try {
      const response = await apiFetch('/api/admin/organizations/');
      if (response.ok) {
        const data = await response.json();
        setOrganizations(Array.isArray(data) ? data : data.results || []);
      } else {
        throw new Error('Failed to fetch organizations');
      }
    } catch (error) {
      console.error('Error fetching organizations:', error);
      setError('Failed to load organizations.');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await apiFetch('/api/admin/stats/');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        throw new Error('Failed to fetch stats');
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCreateUser = async () => {
    try {
      // Validate required fields
      if (!newUser.username || !newUser.email) {
        setError('Username and email are required');
        return;
      }

      const response = await apiFetch('/api/admin/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newUser),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.message || 'Failed to create user');
      }

      const result = await response.json();
      setOpenUserDialog(false);
      fetchUsers();
      resetNewUser();
      
      // Show success message
      setSuccessMessage(result.message || 'User created successfully. Welcome email sent.');
    } catch (error) {
      console.error('Error creating user:', error);
      setError(error instanceof Error ? error.message : 'Failed to create user');
    }
  };

  const handleCreateOrganization = async () => {
    try {
      const response = await apiFetch('/api/admin/organizations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newOrg),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create organization');
      }

      setOpenOrgDialog(false);
      fetchOrganizations();
      setNewOrg({
        name: '',
        description: '',
        owner_id: 0,
      });
    } catch (error) {
      console.error('Error creating organization:', error);
      setError(error instanceof Error ? error.message : 'Failed to create organization');
    }
  };

  const handleChangeUserRole = async (userId: number, newRole: string) => {
    try {
      const response = await apiFetch(`/api/admin/users/${userId}/role/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ role: newRole }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user role');
      }

      fetchUsers();
    } catch (error) {
      console.error('Error updating user role:', error);
      setError('Failed to update user role');
    }
  };

  const handleDeleteUserClick = (userId: number) => {
    setUserToDelete(userId);
    setDeleteUserDialogOpen(true);
  };

  const handleConfirmDeleteUser = async () => {
    if (userToDelete === null) return;
    
    try {
      const response = await apiFetch(`/api/admin/users/${userToDelete}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete user');
      }

      fetchUsers();
      setSuccessMessage('User deleted successfully');
    } catch (error) {
      console.error('Error deleting user:', error);
      setError(error instanceof Error ? error.message : 'Failed to delete user');
    } finally {
      setDeleteUserDialogOpen(false);
      setUserToDelete(null);
    }
  };

  const handleCancelDeleteUser = () => {
    setDeleteUserDialogOpen(false);
    setUserToDelete(null);
  };

  const handleDeleteOrganizationClick = (orgId: number) => {
    setOrgToDelete(orgId);
    setDeleteOrgDialogOpen(true);
  };

  const handleConfirmDeleteOrganization = async () => {
    if (orgToDelete === null) return;
    
    try {
      const response = await apiFetch(`/api/admin/organizations/${orgToDelete}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete organization');
      }

      fetchOrganizations();
      setSuccessMessage('Organization deleted successfully');
    } catch (error) {
      console.error('Error deleting organization:', error);
      setError('Failed to delete organization');
    } finally {
      setDeleteOrgDialogOpen(false);
      setOrgToDelete(null);
    }
  };

  const handleCancelDeleteOrganization = () => {
    setDeleteOrgDialogOpen(false);
    setOrgToDelete(null);
  };

  const handleConfirmRoleChange = async () => {
    if (pendingRoleChange) {
      await handleChangeUserRole(pendingRoleChange.userId, pendingRoleChange.newRole);
      setRoleChangeDialogOpen(false);
      setPendingRoleChange(null);
    }
  };

  const handleCancelRoleChange = () => {
    setRoleChangeDialogOpen(false);
    setPendingRoleChange(null);
  };

  const handleChangeUserStatus = async (userId: number, newStatus: boolean) => {
    try {
      const response = await apiFetch(`/api/admin/users/${userId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: newStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user status');
      }

      // Update the user in the local state
      setUsers(prevUsers => 
        prevUsers.map(user => 
          user.id === userId 
            ? { ...user, is_active: newStatus }
            : user
        )
      );

      setSuccessMessage(`User status updated successfully to ${newStatus ? 'Active' : 'Inactive'}`);
    } catch (error) {
      console.error('Error updating user status:', error);
      setError('Failed to update user status');
    }
  };

  const handleStatusChangeClick = (userId: number, currentStatus: boolean) => {
    setPendingStatusChange({ userId, newStatus: !currentStatus });
    setStatusChangeDialogOpen(true);
  };

  const handleConfirmStatusChange = async () => {
    if (pendingStatusChange) {
      await handleChangeUserStatus(pendingStatusChange.userId, pendingStatusChange.newStatus);
      setStatusChangeDialogOpen(false);
      setPendingStatusChange(null);
    }
  };

  const handleCancelStatusChange = () => {
    setStatusChangeDialogOpen(false);
    setPendingStatusChange(null);
  };

  const resetNewUser = () => {
    setNewUser({
      username: '',
      email: '',
      role: 'tenant_admin',
    });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(search.toLowerCase()) ||
                         user.email.toLowerCase().includes(search.toLowerCase());
    
    const matchesRoleFilter = roleFilter === 'all' || 
                             user.global_role?.role === roleFilter;
    
    return matchesSearch && matchesRoleFilter;
  });

  const filteredOrganizations = organizations.filter(org => 
    org.name.toLowerCase().includes(search.toLowerCase()) ||
    (org.description && org.description.toLowerCase().includes(search.toLowerCase())) ||
    org.owner_name.toLowerCase().includes(search.toLowerCase())
  );

  const getRoleChip = (role: string | undefined, userId: number) => {
    if (!role) return null;
    
    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
      setRoleMenuAnchor(event.currentTarget);
      setSelectedUserId(userId);
    };
    
    const handleClose = () => {
      setRoleMenuAnchor(null);
      setSelectedUserId(null);
    };
    
    const handleRoleChange = (newRole: string) => {
      if (selectedUserId) {
        setPendingRoleChange({ userId: selectedUserId, newRole });
        setRoleChangeDialogOpen(true);
      }
      handleClose();
    };
    
    const getRoleConfig = (roleType: string) => {
      switch (roleType) {
        case 'super_admin':
          return { icon: <AdminIcon />, label: "Super Admin", color: "primary" as const };
        case 'tenant_admin':
          return { icon: <BusinessIcon />, label: "Tenant Admin", color: "secondary" as const };
        case 'user':
          return { icon: <PersonIcon />, label: "User", color: "default" as const };
        default:
          return { icon: <PersonIcon />, label: roleType, color: "default" as const };
      }
    };
    
    const roleConfig = getRoleConfig(role);
    const open = Boolean(roleMenuAnchor) && selectedUserId === userId;
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <Chip 
          icon={roleConfig.icon} 
          label={roleConfig.label} 
          color={roleConfig.color} 
          size="small"
          onClick={handleClick}
          sx={{ 
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            '&:hover': {
              transform: 'scale(1.05)',
              boxShadow: 2
            }
          }}
        />
        <Menu
          anchorEl={roleMenuAnchor}
          open={open}
          onClose={handleClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'left',
          }}
          sx={{
            '& .MuiPaper-root': {
              minWidth: '120px',
              maxWidth: '150px',
            },
            '& .MuiMenuItem-root': {
              fontSize: '0.875rem',
              padding: '6px 12px',
              minHeight: '32px',
            },
            '& .MuiSvgIcon-root': {
              fontSize: '1rem',
            }
          }}
        >
          <MenuItem
            onClick={() => handleRoleChange('super_admin')}
            sx={{
              color: '#7b1fa2',
              '&:hover': {
                backgroundColor: '#f3e5f5',
                color: '#4a148c'
              }
            }}
          >
            <AdminIcon sx={{ mr: 1, fontSize: '1rem', color: '#7b1fa2' }} />
            Super Admin
          </MenuItem>
          <MenuItem
            onClick={() => handleRoleChange('tenant_admin')}
            sx={{
              color: '#1565c0',
              '&:hover': {
                backgroundColor: '#e3f2fd',
                color: '#0d47a1'
              }
            }}
          >
            <BusinessIcon sx={{ mr: 1, fontSize: '1rem', color: '#1565c0' }} />
            Tenant Admin
          </MenuItem>
          <MenuItem
            onClick={() => handleRoleChange('user')}
            sx={{
              color: '#424242',
              '&:hover': {
                backgroundColor: '#f5f5f5',
                color: '#212121'
              }
            }}
          >
            <PersonIcon sx={{ mr: 1, fontSize: '1rem', color: '#424242' }} />
            User
          </MenuItem>
        </Menu>
      </Box>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{
      width: '100%',
      padding: '16px 32px',
      bgcolor: '#f5f5f5',
      minHeight: 'calc(100vh - 56px)',
    }}>
      {/* Breadcrumbs */}
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs aria-label="breadcrumb">
          <Typography color="text.primary">Dashboard</Typography>
        </Breadcrumbs>
      </Box>

      {/* Header and actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h3" component="h1" fontWeight="500">
          Super Admin Dashboard
        </Typography>
        <Box sx={{ width: 200 }} /> {/* Spacer to match the button width in OrganizationsList */}
      </Box>

      {/* Stats Cards */}
      <Box sx={{ mb: 4, width: '100%', overflow: 'hidden' }}>
        <Grid container spacing={3} sx={{ width: '100%', margin: 0 }}>
          <Grid item xs={12} sm={6} lg={3} sx={{ padding: '12px !important', minWidth: '280px' }}>
            <Card sx={{ height: '100%', overflow: 'hidden', width: '100%', minWidth: '260px' }}>
              <CardContent sx={{ p: 3, '&:last-child': { pb: 3 }, height: '100%' }}>
                <Typography variant="h6" color="text.secondary" sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}>
                  Total Users
                </Typography>
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
                    fontWeight: 600,
                    wordBreak: 'break-word',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}
                >
                  {stats.totalUsers}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} lg={3} sx={{ padding: '12px !important', minWidth: '280px' }}>
            <Card sx={{ height: '100%', overflow: 'hidden', width: '100%', minWidth: '260px' }}>
              <CardContent sx={{ p: 3, '&:last-child': { pb: 3 }, height: '100%' }}>
                <Typography variant="h6" color="text.secondary" sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}>
                  Organizations
                </Typography>
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
                    fontWeight: 600,
                    wordBreak: 'break-word',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}
                >
                  {stats.totalOrgs}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} lg={3} sx={{ padding: '12px !important', minWidth: '280px' }}>
            <Card sx={{ height: '100%', overflow: 'hidden', width: '100%', minWidth: '260px' }}>
              <CardContent sx={{ p: 3, '&:last-child': { pb: 3 }, height: '100%' }}>
                <Typography variant="h6" color="text.secondary" sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}>
                  Projects
                </Typography>
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
                    fontWeight: 600,
                    wordBreak: 'break-word',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}
                >
                  {stats.totalProjects}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} lg={3} sx={{ padding: '12px !important', minWidth: '280px' }}>
            <Card sx={{ height: '100%', overflow: 'hidden', width: '100%', minWidth: '260px' }}>
              <CardContent sx={{ p: 3, '&:last-child': { pb: 3 }, height: '100%' }}>
                <Typography variant="h6" color="text.secondary" sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}>
                  User Distribution
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <AdminIcon color="primary" sx={{ mr: 1, fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                  <Typography variant="body2" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    Super Admins: {stats.superAdmins}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                  <BusinessIcon color="secondary" sx={{ mr: 1, fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                  <Typography variant="body2" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    Tenant Admins: {stats.tenantAdmins}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                  <PersonIcon sx={{ mr: 1, fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                  <Typography variant="body2" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    Users: {stats.regularUsers}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} centered>
          <Tab label="Users" />
          <Tab label="Companies" />
          <Tab label="System Settings" />
          <Tab label="Scraper Configuration" />
        </Tabs>
      </Paper>

      {/* Search and Add Button - Only for Users and Organizations tabs */}
      {(activeTab === 0 || activeTab === 1) && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            {activeTab === 0 && (
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Filter by Role</InputLabel>
                <Select
                  value={roleFilter}
                  label="Filter by Role"
                  onChange={(e) => setRoleFilter(e.target.value)}
                >
                  <MenuItem value="all">All Roles</MenuItem>
                  <MenuItem value="super_admin">Super Admin</MenuItem>
                  <MenuItem value="tenant_admin">Tenant Admin</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                </Select>
              </FormControl>
            )}
            <TextField
              placeholder="Search..."
              variant="outlined"
              size="small"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              sx={{ width: 300 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Box>
          {activeTab === 0 && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => {
              setOpenUserDialog(true);
              resetNewUser(); // Generate random password when opening dialog
            }}
            >
              Add User
            </Button>
          )}
          {activeTab === 1 && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenOrgDialog(true)}
            >
              Add Organization
            </Button>
          )}
        </Box>
      )}



      {/* Users Tab */}
      {activeTab === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      {getRoleChip(user.global_role?.role, user.id)}
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={user.is_active ? <CheckCircleIcon /> : <CancelIcon />}
                        label={user.is_active ? 'Active' : 'Inactive'}
                        color={user.is_active ? 'success' : 'error'}
                        size="small"
                        variant="filled"
                        onClick={() => handleStatusChangeClick(user.id, user.is_active)}
                        sx={{ 
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          fontWeight: 400,
                          fontSize: '0.75rem',
                          minWidth: '80px',
                          backgroundColor: user.is_active ? '#219653' : '#d32f2f', // lighter dark green or dark red
                          color: '#fff',
                          '&:hover': {
                            transform: 'scale(1.08)',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                            filter: 'brightness(1.1)',
                            backgroundColor: user.is_active
                              ? '#17643a' // darker green on hover
                              : '#b71c1c', // darker red on hover for inactive
                          },
                          '& .MuiChip-icon': {
                            fontSize: '0.85rem',
                            marginLeft: '4px'
                          },
                          '& .MuiChip-label': {
                            paddingLeft: '4px',
                            paddingRight: '8px'
                          }
                        }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton 
                        sx={{ 
                          color: '#d32f2f',
                          '&:hover': {
                            backgroundColor: '#f44336',
                            color: 'white'
                          }
                        }}
                        onClick={() => handleDeleteUserClick(user.id)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No users found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Organizations Tab */}
      {activeTab === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Owner</TableCell>
                <TableCell>Members</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredOrganizations.length > 0 ? (
                filteredOrganizations.map((org) => (
                  <TableRow key={org.id}>
                    <TableCell>{org.id}</TableCell>
                    <TableCell>{org.name}</TableCell>
                    <TableCell>{org.description || 'N/A'}</TableCell>
                    <TableCell>{org.owner_name}</TableCell>
                    <TableCell>{org.members_count}</TableCell>
                    <TableCell>{new Date(org.created_at).toLocaleDateString()}</TableCell>
                    <TableCell align="right">
                      <IconButton 
                        sx={{ 
                          color: '#d32f2f',
                          '&:hover': {
                            backgroundColor: '#f44336',
                            color: 'white'
                          }
                        }}
                        onClick={() => handleDeleteOrganizationClick(org.id)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No organizations found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* System Settings Tab */}
      {activeTab === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>System Settings</Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            This section is under development. It will include settings for:
          </Typography>
          <ul>
            <li>Email configuration</li>
            <li>Storage settings</li>
            <li>Security policies</li>
            <li>API rate limits</li>
            <li>Backup and maintenance</li>
          </ul>
        </Paper>
      )}

      {/* Brightdata API Tab */}
      {activeTab === 3 && (
        <Box>
          <Typography variant="h4" gutterBottom component="h1">
            Scraper Configuration
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 3 }}>
            Manage your platform-specific scraper configurations for automated data scraping. Each platform and service requires its own configuration with a unique dataset ID.
          </Typography>

          {/* Platform Overview Cards */}
          <Card sx={{ 
            mb: 4, 
            background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            border: '1px solid #dee2e6',
            borderRadius: 2,
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ mb: 2, fontWeight: 600, color: '#495057' }}>
                Platform-Specific Configurations
              </Typography>
              <Typography variant="body1" sx={{ mb: 3, color: '#6c757d', lineHeight: 1.6 }}>
                The automated batch scraper requires separate Brightdata configurations for each social media platform. 
                Each platform uses different dataset structures and may require different API tokens.
              </Typography>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 2 }}>
                {[
                  { value: 'facebook_posts', label: 'Facebook Posts', icon: <FacebookIcon />, color: '#1877F2', description: 'Scrape Facebook posts and content' },
                  { value: 'facebook_reels', label: 'Facebook Reels', icon: <FacebookIcon />, color: '#1877F2', description: 'Collect Facebook video content' },
                  { value: 'facebook_comments', label: 'Facebook Comments', icon: <FacebookIcon />, color: '#1877F2', description: 'Extract comment data from posts' },
                  { value: 'instagram_posts', label: 'Instagram Posts', icon: <InstagramIcon />, color: '#E4405F', description: 'Scrape Instagram posts and images' },
                  { value: 'instagram_reels', label: 'Instagram Reels', icon: <InstagramIcon />, color: '#E4405F', description: 'Collect Instagram video content' },
                  { value: 'instagram_comments', label: 'Instagram Comments', icon: <InstagramIcon />, color: '#E4405F', description: 'Extract comment data from posts' },
                  { value: 'linkedin_posts', label: 'LinkedIn Posts', icon: <LinkedInIcon />, color: '#0A66C2', description: 'Scrape LinkedIn posts and articles' },
                  { value: 'tiktok_posts', label: 'TikTok Posts', icon: <MusicVideoIcon />, color: '#000000', description: 'Collect TikTok video content' },
                ].map((platform) => {
                  const hasConfig = brightdataConfigs.some(c => c.platform === platform.value);
                  return (
                    <Paper
                      key={platform.value}
                      elevation={hasConfig ? 3 : 1}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        border: hasConfig ? `2px solid #28a745` : '1px solid #dee2e6',
                        background: hasConfig ? 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)' : 'white',
                        transition: 'all 0.3s ease',
                        cursor: 'pointer',
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: hasConfig ? '0 8px 25px rgba(40, 167, 69, 0.2)' : '0 6px 20px rgba(0,0,0,0.1)'
                        }
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: platform.color,
                            color: 'white',
                            mr: 2,
                            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                          }}
                        >
                          {platform.icon}
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" sx={{ fontWeight: 600, color: '#495057' }}>
                            {platform.label}
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#6c757d', fontSize: '0.875rem' }}>
                            {platform.description}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {hasConfig ? (
                            <Chip
                              label="Configured"
                              size="small"
                              color="success"
                              sx={{ 
                                fontWeight: 600,
                                '& .MuiChip-label': { px: 1.5 }
                              }}
                            />
                          ) : (
                            <Chip
                              label="Not Configured"
                              size="small"
                              variant="outlined"
                              sx={{ 
                                fontWeight: 500,
                                color: '#6c757d',
                                borderColor: '#dee2e6',
                                '& .MuiChip-label': { px: 1.5 }
                              }}
                            />
                          )}
                        </Box>
                      </Box>
                    </Paper>
                  );
                })}
              </Box>
            </CardContent>
          </Card>

          {/* Configurations Table */}
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  API Configurations
                </Typography>
                <Button 
                  variant="contained" 
                  startIcon={<AddIcon />} 
                  onClick={() => {
                    setEditConfigId(null);
                    setBrightdataForm({ name: '', platform: '', description: '', apiToken: '', datasetId: '', isActive: true });
                    setBrightdataDialogOpen(true);
                  }}
                >
                  Add New Configuration
                </Button>
              </Box>

              {brightdataLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Status</TableCell>
                        <TableCell>Platform</TableCell>
                        <TableCell>Name</TableCell>
                        <TableCell>Dataset ID</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Updated</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {brightdataConfigs.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={7} align="center">
                            No configurations found. Click "Add New Configuration" to create one.
                          </TableCell>
                        </TableRow>
                      ) : (
                        brightdataConfigs.map((config) => (
                          <TableRow key={config.id}>
                            <TableCell>
                              <Chip
                                label={config.is_active ? "Active" : "Inactive"}
                                color={config.is_active ? "success" : "default"}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                {config.platform === 'linkedin_posts' && <LinkedInIcon />}
                                {config.platform === 'tiktok_posts' && <MusicVideoIcon />}
                                {config.platform.includes('instagram') && <InstagramIcon />}
                                {config.platform.includes('facebook') && <FacebookIcon />}
                                <Typography sx={{ ml: 1 }}>
                                  {config.platform_display || config.platform}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>{config.name}</TableCell>
                            <TableCell>{config.dataset_id}</TableCell>
                            <TableCell>{new Date(config.created_at).toLocaleString()}</TableCell>
                            <TableCell>{new Date(config.updated_at).toLocaleString()}</TableCell>
                            <TableCell>
                              <IconButton size="small" onClick={() => handleEditConfig(config)}>
                                <EditIcon />
                              </IconButton>
                              <IconButton 
                                size="small" 
                                sx={{ 
                                  color: '#d32f2f',
                                  '&:hover': {
                                    backgroundColor: '#f44336',
                                    color: 'white'
                                  }
                                }}
                                onClick={() => handleDeleteClick(config.id)}
                              >
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
        </Box>
      )}

             {/* Create User Dialog */}
       <Dialog open={openUserDialog} onClose={() => setOpenUserDialog(false)} maxWidth="sm" fullWidth>
         <DialogTitle>Create New User</DialogTitle>
         <DialogContent>
           <DialogContentText sx={{ mb: 2 }}>
             Enter the user's information below. A secure password will be automatically generated and sent to their email address.
           </DialogContentText>
          <TextField
            label="Username"
            fullWidth
            margin="normal"
            value={newUser.username}
            onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
            required
          />
          <TextField
            label="Email"
            type="email"
            fullWidth
            margin="normal"
            value={newUser.email}
            onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
            required
          />
          

          <FormControl fullWidth margin="normal">
            <InputLabel>Role</InputLabel>
            <Select
              value={newUser.role}
              label="Role"
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
            >
              <MenuItem value="super_admin">Super Admin</MenuItem>
              <MenuItem value="tenant_admin">Tenant Admin</MenuItem>
              <MenuItem value="user">User</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUserDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateUser} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Organization Dialog */}
      <Dialog open={openOrgDialog} onClose={() => setOpenOrgDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Organization</DialogTitle>
        <DialogContent>
          <TextField
            label="Organization Name"
            fullWidth
            margin="normal"
            value={newOrg.name}
            onChange={(e) => setNewOrg({ ...newOrg, name: e.target.value })}
            required
          />
          <TextField
            label="Description"
            fullWidth
            margin="normal"
            multiline
            rows={3}
            value={newOrg.description}
            onChange={(e) => setNewOrg({ ...newOrg, description: e.target.value })}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Owner</InputLabel>
            <Select
              value={newOrg.owner_id || ''}
              label="Owner"
              onChange={(e) => setNewOrg({ ...newOrg, owner_id: Number(e.target.value) })}
            >
              {users
                .filter(user => user.global_role?.role === 'tenant_admin' || user.global_role?.role === 'super_admin')
                .map(user => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.username} ({user.email}) - {user.global_role?.role_display}
                  </MenuItem>
                ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenOrgDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateOrganization} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Brightdata Configuration Dialog */}
      <Dialog open={brightdataDialogOpen} onClose={() => setBrightdataDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editConfigId !== null ? 'Edit Configuration' : 'Add New Brightdata Configuration'}</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            {editConfigId !== null 
              ? 'Edit your Brightdata API configuration. API tokens are securely stored and will not be displayed.'
              : 'Create a new Brightdata API configuration for data scraping. API tokens are securely stored and encrypted.'
            }
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Configuration Name"
            fullWidth
            value={brightdataForm.name}
            onChange={(e) => setBrightdataForm({ ...brightdataForm, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description (Optional)"
            fullWidth
            value={brightdataForm.description}
            onChange={(e) => setBrightdataForm({ ...brightdataForm, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Platform</InputLabel>
            <Select
              value={brightdataForm.platform}
              onChange={(e) => {
                const selectedPlatform = e.target.value;
                let datasetId = '';
                
                // Set dataset ID based on platform selection
                switch (selectedPlatform) {
                  case 'linkedin_posts':
                    datasetId = 'gd_lyy3tktm25m4avu764';
                    break;
                  case 'tiktok_posts':
                    datasetId = 'gd_lu702nij2f790tmv9h';
                    break;
                  case 'instagram_posts':
                    datasetId = 'gd_lk5ns7kz21pck8jpis';
                    break;
                  case 'instagram_reels':
                    datasetId = 'gd_lyclm20il4r5helnj';
                    break;
                  case 'instagram_comments':
                    datasetId = 'gd_ltppn085pokosxh13';
                    break;
                  case 'facebook_comments':
                    datasetId = 'gd_lkay758p1eanlolqw8';
                    break;
                  case 'facebook_reels':
                    datasetId = 'gd_lyclm3ey2q6rww027t';
                    break;
                  case 'facebook_posts':
                    datasetId = 'gd_lkaxegm826bjpoo9m5';
                    break;
                  default:
                    datasetId = '';
                }
                
                setBrightdataForm({ 
                  ...brightdataForm, 
                  platform: selectedPlatform,
                  datasetId: datasetId
                });
              }}
              label="Platform"
            >
              <MenuItem value="linkedin_posts">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinkedInIcon />
                  <Typography sx={{ ml: 1 }}>LinkedIn Posts</Typography>
                </Box>
              </MenuItem>
              <MenuItem value="tiktok_posts">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <MusicVideoIcon />
                  <Typography sx={{ ml: 1 }}>TikTok Posts</Typography>
                </Box>
              </MenuItem>
              <MenuItem value="instagram_posts">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <InstagramIcon />
                  <Typography sx={{ ml: 1 }}>Instagram Posts</Typography>
                </Box>
              </MenuItem>
              <MenuItem value="instagram_reels">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <InstagramIcon />
                  <Typography sx={{ ml: 1 }}>Instagram Reels</Typography>
                </Box>
              </MenuItem>
              <MenuItem value="instagram_comments">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <InstagramIcon />
                  <Typography sx={{ ml: 1 }}>Instagram Comments</Typography>
                </Box>
              </MenuItem>
              <MenuItem value="facebook_comments">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FacebookIcon />
                  <Typography sx={{ ml: 1 }}>Facebook Comments</Typography>
                </Box>
              </MenuItem>
              <MenuItem value="facebook_reels">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FacebookIcon />
                  <Typography sx={{ ml: 1 }}>Facebook Reels</Typography>
                </Box>
              </MenuItem>
              <MenuItem value="facebook_posts">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FacebookIcon />
                  <Typography sx={{ ml: 1 }}>Facebook Posts</Typography>
                </Box>
              </MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Dataset ID"
            fullWidth
            value={brightdataForm.datasetId}
            InputProps={{
              readOnly: true,
            }}
            sx={{ mb: 2 }}
            helperText="Automatically set based on the selected platform"
          />
          <TextField
            margin="dense"
            label="Brightdata API Token"
            type="password"
            fullWidth
            value={brightdataForm.apiToken}
            onChange={(e) => setBrightdataForm({ ...brightdataForm, apiToken: e.target.value })}
            helperText={
              editConfigId !== null 
                ? "Leave empty to keep existing token unchanged" 
                : "Authentication API token assigned to access to the services"
            }
            placeholder={editConfigId !== null ? "••••••••••••••••" : ""}
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: editConfigId !== null && brightdataForm.apiToken === '' ? (
                <InputAdornment position="end">
                  <Chip 
                    label="Keep Existing" 
                    size="small" 
                    color="info" 
                    variant="outlined"
                  />
                </InputAdornment>
              ) : undefined
            }}
          />
          {editConfigId !== null && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Security Note:</strong> For security reasons, existing API tokens are not displayed. 
                Leave the token field empty to keep the current token unchanged, or enter a new token to update it.
              </Typography>
            </Alert>
          )}
          <FormControlLabel
            control={
              <Switch
                checked={brightdataForm.isActive}
                onChange={(e) => setBrightdataForm({ ...brightdataForm, isActive: e.target.checked })}
                color="primary"
              />
            }
            label="Active Configuration"
            sx={{ mb: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBrightdataDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateBrightdataConfig}
            variant="contained" 
            color="primary"
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : (editConfigId !== null ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </Dialog>

             {/* Success Message */}
       {successMessage && (
         <Snackbar 
           open={!!successMessage} 
           autoHideDuration={6000} 
           onClose={() => setSuccessMessage(null)}
         >
           <Alert 
             onClose={() => setSuccessMessage(null)} 
             severity="success" 
             sx={{ width: '100%' }}
           >
             {successMessage}
           </Alert>
         </Snackbar>
       )}

       {/* Error Message */}
       {error && (
         <Snackbar 
           open={!!error} 
           autoHideDuration={6000} 
           onClose={() => setError(null)}
         >
           <Alert 
             onClose={() => setError(null)} 
             severity="error" 
             sx={{ width: '100%' }}
           >
             {error}
           </Alert>
         </Snackbar>
       )}

             {/* Delete Confirmation Dialog for Brightdata Configurations */}
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

       {/* Delete User Confirmation Dialog */}
       <Dialog
         open={deleteUserDialogOpen}
         onClose={handleCancelDeleteUser}
       >
         <DialogTitle>Confirm User Deletion</DialogTitle>
         <DialogContent>
           <DialogContentText>
             Are you sure you want to delete this user? This action cannot be undone and will permanently remove the user from the system.
           </DialogContentText>
         </DialogContent>
         <DialogActions>
           <Button onClick={handleCancelDeleteUser}>Cancel</Button>
           <Button
             onClick={handleConfirmDeleteUser}
             variant="contained"
             sx={{
               backgroundColor: '#d32f2f',
               color: '#fff',
               '&:hover': {
                 backgroundColor: '#b71c1c',
                 color: '#fff',
               },
             }}
           >
             Delete User
           </Button>
         </DialogActions>
       </Dialog>

       {/* Delete Organization Confirmation Dialog */}
       <Dialog
         open={deleteOrgDialogOpen}
         onClose={handleCancelDeleteOrganization}
       >
         <DialogTitle>Confirm Organization Deletion</DialogTitle>
         <DialogContent>
           <DialogContentText>
             Are you sure you want to delete this organization? This action cannot be undone and will permanently remove the organization and all associated data.
           </DialogContentText>
         </DialogContent>
         <DialogActions>
           <Button onClick={handleCancelDeleteOrganization}>Cancel</Button>
           <Button onClick={handleConfirmDeleteOrganization} color="error" variant="contained">
             Delete Organization
           </Button>
         </DialogActions>
       </Dialog>

       {/* Role Change Confirmation Dialog */}
       <Dialog
         open={roleChangeDialogOpen}
         onClose={handleCancelRoleChange}
       >
         <DialogTitle>Confirm Role Change</DialogTitle>
         <DialogContent>
           <DialogContentText>
             Are you sure you want to change this user's role to{' '}
             <strong>
               {pendingRoleChange?.newRole === 'super_admin' ? 'Super Admin' :
                pendingRoleChange?.newRole === 'tenant_admin' ? 'Tenant Admin' : 'User'}
             </strong>?
             <br></br>
             This action will immediately update the user's permissions and access levels.
           </DialogContentText>
         </DialogContent>
         <DialogActions>
           <Button onClick={handleCancelRoleChange}>Cancel</Button>
           <Button 
             onClick={handleConfirmRoleChange} 
             variant="contained"
             sx={{
               backgroundColor: '#d32f2f',
               color: '#fff',
               '&:hover': {
                 backgroundColor: '#b71c1c',
                 color: '#fff',
               },
             }}
           >
             Confirm Role Change
           </Button>
         </DialogActions>
       </Dialog>

       {/* Status Change Confirmation Dialog */}
       <Dialog
         open={statusChangeDialogOpen}
         onClose={handleCancelStatusChange}
       >
         <DialogTitle>Confirm Status Change</DialogTitle>
         <DialogContent>
           <DialogContentText>
             Are you sure you want to change this user's status to{' '}
             <strong>
               {pendingStatusChange?.newStatus ? 'Active' : 'Inactive'}
             </strong>?
             <br></br>
             {pendingStatusChange?.newStatus 
               ? 'This will allow the user to access the system and perform their assigned tasks.'
               : 'This will prevent the user from accessing the system and performing any actions.'
             }
           </DialogContentText>
         </DialogContent>
         <DialogActions>
           <Button onClick={handleCancelStatusChange}>Cancel</Button>
           <Button 
             onClick={handleConfirmStatusChange} 
             variant="contained"
             sx={{
               backgroundColor: '#d32f2f',
               color: '#fff',
               '&:hover': {
                 backgroundColor: '#b71c1c',
                 color: '#fff',
               },
             }}
           >
             Confirm Status Change
           </Button>
         </DialogActions>
       </Dialog>
    </Box>
  );
};

export default SuperAdminDashboard; 
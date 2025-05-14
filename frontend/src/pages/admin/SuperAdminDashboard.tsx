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
  DialogTitle,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  IconButton,
  Chip,
  InputAdornment,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  SupervisorAccount as AdminIcon,
} from '@mui/icons-material';
import { apiFetch } from '../../utils/api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
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
  const [openUserDialog, setOpenUserDialog] = useState(false);
  const [openOrgDialog, setOpenOrgDialog] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password2: '',
    role: 'user',
  });
  const [newOrg, setNewOrg] = useState({
    name: '',
    description: '',
    owner_id: 0,
  });
  const [error, setError] = useState<string | null>(null);
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
      const response = await apiFetch('/api/admin/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newUser),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create user');
      }

      setOpenUserDialog(false);
      fetchUsers();
      resetNewUser();
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

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await apiFetch(`/api/admin/users/${userId}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete user');
      }

      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Failed to delete user');
    }
  };

  const handleDeleteOrganization = async (orgId: number) => {
    if (!window.confirm('Are you sure you want to delete this organization? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await apiFetch(`/api/admin/organizations/${orgId}/`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete organization');
      }

      fetchOrganizations();
    } catch (error) {
      console.error('Error deleting organization:', error);
      setError('Failed to delete organization');
    }
  };

  const resetNewUser = () => {
    setNewUser({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      password2: '',
      role: 'user',
    });
  };

  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(search.toLowerCase()) ||
    user.email.toLowerCase().includes(search.toLowerCase()) ||
    (user.first_name + ' ' + user.last_name).toLowerCase().includes(search.toLowerCase())
  );

  const filteredOrganizations = organizations.filter(org => 
    org.name.toLowerCase().includes(search.toLowerCase()) ||
    (org.description && org.description.toLowerCase().includes(search.toLowerCase())) ||
    org.owner_name.toLowerCase().includes(search.toLowerCase())
  );

  const getRoleChip = (role: string | undefined) => {
    if (!role) return null;
    
    switch (role) {
      case 'super_admin':
        return <Chip icon={<AdminIcon />} label="Super Admin" color="primary" size="small" />;
      case 'tenant_admin':
        return <Chip icon={<BusinessIcon />} label="Tenant Admin" color="secondary" size="small" />;
      case 'user':
        return <Chip icon={<PersonIcon />} label="User" color="default" size="small" />;
      default:
        return <Chip label={role} size="small" />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Super Admin Dashboard
      </Typography>

      {/* Stats Cards */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Total Users</Typography>
                <Typography variant="h3">{stats.totalUsers}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Organizations</Typography>
                <Typography variant="h3">{stats.totalOrgs}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Projects</Typography>
                <Typography variant="h3">{stats.totalProjects}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="text.secondary">User Distribution</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <AdminIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2">Super Admins: {stats.superAdmins}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                  <BusinessIcon color="secondary" sx={{ mr: 1 }} />
                  <Typography variant="body2">Tenant Admins: {stats.tenantAdmins}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                  <PersonIcon sx={{ mr: 1 }} />
                  <Typography variant="body2">Users: {stats.regularUsers}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} centered>
          <Tab label="Users" />
          <Tab label="Organizations" />
          <Tab label="System Settings" />
        </Tabs>
      </Paper>

      {/* Search and Add Button */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
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
        {activeTab === 0 && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenUserDialog(true)}
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

      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light', color: 'error.dark' }}>
          <Typography>{error}</Typography>
        </Paper>
      )}

      {/* Users Tab */}
      {activeTab === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{`${user.first_name} ${user.last_name}`}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{getRoleChip(user.global_role?.role)}</TableCell>
                    <TableCell align="right">
                      <FormControl variant="outlined" size="small" sx={{ minWidth: 120, mr: 1 }}>
                        <Select
                          value={user.global_role?.role || 'user'}
                          onChange={(e) => handleChangeUserRole(user.id, e.target.value)}
                          displayEmpty
                        >
                          <MenuItem value="user">User</MenuItem>
                          <MenuItem value="tenant_admin">Tenant Admin</MenuItem>
                          <MenuItem value="super_admin">Super Admin</MenuItem>
                        </Select>
                      </FormControl>
                      <IconButton 
                        color="error" 
                        onClick={() => handleDeleteUser(user.id)}
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
                        color="error" 
                        onClick={() => handleDeleteOrganization(org.id)}
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

      {/* Create User Dialog */}
      <Dialog open={openUserDialog} onClose={() => setOpenUserDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
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
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="First Name"
              fullWidth
              margin="normal"
              value={newUser.first_name}
              onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
            />
            <TextField
              label="Last Name"
              fullWidth
              margin="normal"
              value={newUser.last_name}
              onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="Password"
              type="password"
              fullWidth
              margin="normal"
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              required
            />
            <TextField
              label="Confirm Password"
              type="password"
              fullWidth
              margin="normal"
              value={newUser.password2}
              onChange={(e) => setNewUser({ ...newUser, password2: e.target.value })}
              required
            />
          </Box>
          <FormControl fullWidth margin="normal">
            <InputLabel>Role</InputLabel>
            <Select
              value={newUser.role}
              label="Role"
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
            >
              <MenuItem value="user">User</MenuItem>
              <MenuItem value="tenant_admin">Tenant Admin</MenuItem>
              <MenuItem value="super_admin">Super Admin</MenuItem>
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
    </Box>
  );
};

export default SuperAdminDashboard; 
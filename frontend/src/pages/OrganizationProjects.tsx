import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  Paper,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  CircularProgress,
  Breadcrumbs,
  Link,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Tabs,
  Tab,
  Select,
  MenuItem,
  InputAdornment,
  FormControl,
  InputLabel,
  SelectChangeEvent,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import GroupIcon from '@mui/icons-material/Group';
import SettingsIcon from '@mui/icons-material/Settings';
import { apiFetch } from '../utils/api';

interface Project {
  id: number;
  name: string;
  description: string | null;
  owner: number;
  owner_name: string;
  organization: number;
  organization_name: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
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

interface Member {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  role: string;
  date_joined: string;
}

const OrganizationProjects = () => {
  const navigate = useNavigate();
  const { organizationId } = useParams<{ organizationId: string }>();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [activeTab, setActiveTab] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [openNewProjectDialog, setOpenNewProjectDialog] = useState(false);
  const [openAddMemberDialog, setOpenAddMemberDialog] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [projectPublic, setProjectPublic] = useState<boolean>(false);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState('member');
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('last viewed');

  useEffect(() => {
    if (organizationId) {
      fetchOrganizationDetails();
      fetchProjects();
      if (activeTab === 1) {
        fetchMembers();
      }
    }
  }, [organizationId, activeTab]);

  const fetchOrganizationDetails = async () => {
    try {
      const response = await apiFetch(`/api/users/organizations/${organizationId}/`);
      if (!response.ok) {
        throw new Error('Failed to fetch organization details');
      }
      
      const data = await response.json();
      setOrganization(data);
    } catch (error) {
      console.error('Error fetching organization details:', error);
      setError('Failed to load organization details.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await apiFetch(`/api/users/projects/?organization=${organizationId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      
      const data = await response.json();
      
      if (Array.isArray(data)) {
        setProjects(data);
      } else if (data && typeof data === 'object' && 'results' in data) {
        setProjects(data.results || []);
      } else {
        console.error('API returned unexpected data format:', data);
        setProjects([]);
        setError('Received invalid data format from server.');
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
      setProjects([]);
      setError('Failed to load projects.');
    } finally {
      setLoading(false);
    }
  };

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const response = await apiFetch(`/api/users/organizations/${organizationId}/members/`);
      if (!response.ok) {
        throw new Error('Failed to fetch members');
      }
      
      const data = await response.json();
      setMembers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching members:', error);
      setMembers([]);
      setError('Failed to load organization members.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenProject = (projectId: number) => {
    navigate(`/organizations/${organizationId}/projects/${projectId}`);
  };

  const handleNewProject = () => {
    setProjectName('');
    setProjectDescription('');
    setProjectPublic(false);
    setOpenNewProjectDialog(true);
  };

  const handleAddMember = () => {
    setNewMemberEmail('');
    setNewMemberRole('member');
    setOpenAddMemberDialog(true);
  };

  const handleCreateProject = async () => {
    if (!projectName.trim()) {
      return;
    }

    try {
      const response = await apiFetch('/api/users/projects/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: projectName,
          description: projectDescription || null,
          organization: Number(organizationId),
          is_public: projectPublic
        }),
      });

      if (!response.ok) {
        let errorDetail = 'Failed to create project';
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorDetail = errorData.detail;
          } else if (typeof errorData === 'object') {
            errorDetail = Object.entries(errorData)
              .map(([field, errors]) => `${field}: ${errors}`)
              .join(', ');
          }
        } catch (e) {
          console.error('Could not parse error response:', e);
        }
        throw new Error(errorDetail);
      }

      fetchProjects();
      setOpenNewProjectDialog(false);
    } catch (error) {
      console.error('Error creating project:', error);
      setError(error instanceof Error ? error.message : 'Failed to create project. Please try again.');
    }
  };

  const handleAddMemberSubmit = async () => {
    if (!newMemberEmail.trim()) {
      setError('Email is required');
      return;
    }

    try {
      // First, try to find the user by email
      const userResponse = await apiFetch(`/api/users/search/?email=${encodeURIComponent(newMemberEmail)}`);
      
      if (!userResponse.ok) {
        throw new Error('Failed to find user with this email');
      }
      
      const userData = await userResponse.json();
      
      if (!userData || !userData.id) {
        throw new Error('User not found with this email');
      }
      
      // Now add the user to the organization
      const response = await apiFetch(`/api/users/organizations/${organizationId}/members/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userData.id,
          role: newMemberRole
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add member to organization');
      }

      fetchMembers();
      setOpenAddMemberDialog(false);
    } catch (error) {
      console.error('Error adding member:', error);
      setError(error instanceof Error ? error.message : 'Failed to add member. Please try again.');
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSortChange = (event: SelectChangeEvent) => {
    setSortBy(event.target.value);
  };

  // Filter projects based on search query
  const filteredProjects = projects.filter(project => 
    project.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Filter members based on search query
  const filteredMembers = members.filter(member => 
    member.user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    `${member.user.first_name} ${member.user.last_name}`.toLowerCase().includes(searchQuery.toLowerCase())
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
          <Link 
            underline="hover" 
            color="inherit" 
            onClick={() => navigate('/organizations')}
            sx={{ cursor: 'pointer' }}
          >
            Organizations
          </Link>
          <Typography color="text.primary">
            {organization?.name || 'Organization'}
          </Typography>
        </Breadcrumbs>
      </Box>
      
      {/* Organization Header */}
      {organization && (
        <Box mb={3}>
          <Typography variant="h4" component="h1" fontWeight="500" gutterBottom>
            {organization.name}
          </Typography>
          {organization.description && (
            <Typography variant="body1" color="text.secondary">
              {organization.description}
            </Typography>
          )}
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Owner: {organization.owner_name} • Members: {organization.members_count}
            </Typography>
          </Box>
        </Box>
      )}
      
      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="organization tabs">
          <Tab label="Projects" id="tab-0" />
          <Tab label="Members" id="tab-1" />
          <Tab label="Settings" id="tab-2" />
        </Tabs>
      </Box>
      
      {/* Projects Tab */}
      <Box role="tabpanel" hidden={activeTab !== 0}>
        {activeTab === 0 && (
          <>
            {/* Header and actions */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h5" component="h2" fontWeight="500">
                Projects
              </Typography>
              <Button 
                variant="contained" 
                startIcon={<AddIcon />}
                onClick={handleNewProject}
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
                Create project
              </Button>
            </Box>

            {/* Search and filters bar */}
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center" 
              sx={{ mb: 1 }}
            >
              <TextField
                placeholder="Search projects"
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

            {/* Projects Count */}
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Showing {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''}
            </Typography>

            {/* Projects Table */}
            {loading ? (
              <Box display="flex" justifyContent="center" mt={4}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                {filteredProjects.length > 0 ? (
                  <TableContainer component={Paper} sx={{ 
                    boxShadow: 'none', 
                    borderRadius: '4px',
                    border: '1px solid rgba(0,0,0,0.12)'
                  }}>
                    <Table>
                      <TableHead sx={{ bgcolor: '#f9fafb' }}>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Project name</TableCell>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Owner</TableCell>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Access</TableCell>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Created</TableCell>
                          <TableCell align="center" sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {filteredProjects.map((project) => (
                          <TableRow 
                            key={project.id}
                            hover
                            sx={{ cursor: 'pointer' }}
                            onClick={() => handleOpenProject(project.id)}
                          >
                            <TableCell sx={{ color: '#1a73e8', fontWeight: 500 }}>{project.name}</TableCell>
                            <TableCell>{project.owner_name}</TableCell>
                            <TableCell>{project.is_public ? 'Public' : 'Private'}</TableCell>
                            <TableCell>{new Date(project.created_at).toLocaleDateString()}</TableCell>
                            <TableCell align="center">
                              <IconButton 
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // Project actions menu
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
                    <Typography variant="h6" gutterBottom>No projects found</Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Create your first project in this organization to get started.
                    </Typography>
                    <Button 
                      variant="contained" 
                      startIcon={<AddIcon />} 
                      onClick={handleNewProject}
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
                      Create Project
                    </Button>
                  </Paper>
                )}
              </>
            )}
          </>
        )}
      </Box>
      
      {/* Members Tab */}
      <Box role="tabpanel" hidden={activeTab !== 1}>
        {activeTab === 1 && (
          <>
            {/* Header and actions */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h5" component="h2" fontWeight="500">
                Members
              </Typography>
              <Button 
                variant="contained" 
                startIcon={<GroupIcon />}
                onClick={handleAddMember}
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
                Add member
              </Button>
            </Box>

            {/* Search for members */}
            <TextField
              placeholder="Search members"
              variant="outlined"
              size="small"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              sx={{ 
                width: '300px',
                mb: 2,
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

            {/* Members Count */}
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Showing {filteredMembers.length} member{filteredMembers.length !== 1 ? 's' : ''}
            </Typography>

            {/* Members Table */}
            {loading ? (
              <Box display="flex" justifyContent="center" mt={4}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                {filteredMembers.length > 0 ? (
                  <TableContainer component={Paper} sx={{ 
                    boxShadow: 'none', 
                    borderRadius: '4px',
                    border: '1px solid rgba(0,0,0,0.12)'
                  }}>
                    <Table>
                      <TableHead sx={{ bgcolor: '#f9fafb' }}>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Name</TableCell>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Email</TableCell>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Role</TableCell>
                          <TableCell sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Joined</TableCell>
                          <TableCell align="center" sx={{ fontWeight: 600, color: 'rgba(0, 0, 0, 0.87)', py: 1.5 }}>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {filteredMembers.map((member) => (
                          <TableRow key={member.id}>
                            <TableCell>
                              {member.user.first_name} {member.user.last_name}
                            </TableCell>
                            <TableCell>{member.user.email}</TableCell>
                            <TableCell sx={{ textTransform: 'capitalize' }}>{member.role}</TableCell>
                            <TableCell>{new Date(member.date_joined).toLocaleDateString()}</TableCell>
                            <TableCell align="center">
                              <IconButton 
                                size="small"
                                onClick={() => {
                                  // Member actions menu
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
                    <Typography variant="h6" gutterBottom>No members found</Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Add members to your organization to collaborate on projects.
                    </Typography>
                    <Button 
                      variant="contained" 
                      startIcon={<GroupIcon />} 
                      onClick={handleAddMember}
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
                      Add Member
                    </Button>
                  </Paper>
                )}
              </>
            )}
          </>
        )}
      </Box>
      
      {/* Settings Tab */}
      <Box role="tabpanel" hidden={activeTab !== 2}>
        {activeTab === 2 && (
          <>
            <Typography variant="h5" component="h2" fontWeight="500" mb={3}>
              Organization Settings
            </Typography>
            
            {/* Organization settings content goes here */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>Organization Information</Typography>
              <TextField
                label="Organization Name"
                fullWidth
                margin="normal"
                value={organization?.name || ''}
                InputProps={{
                  readOnly: true,
                }}
              />
              <TextField
                label="Description"
                fullWidth
                margin="normal"
                multiline
                rows={3}
                value={organization?.description || ''}
                InputProps={{
                  readOnly: true,
                }}
              />
              <Box mt={2}>
                <Button 
                  variant="outlined" 
                  startIcon={<SettingsIcon />}
                >
                  Edit Organization
                </Button>
              </Box>
            </Paper>
            
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'error.main' }}>Danger Zone</Typography>
              <Box mt={2}>
                <Button 
                  variant="outlined" 
                  color="error"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this organization? This action cannot be undone.')) {
                      // Delete organization API call
                    }
                  }}
                >
                  Delete Organization
                </Button>
              </Box>
            </Paper>
          </>
        )}
      </Box>

      {/* New Project Dialog */}
      <Dialog open={openNewProjectDialog} onClose={() => setOpenNewProjectDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Project</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Project Name"
            type="text"
            fullWidth
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            required
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            type="text"
            fullWidth
            multiline
            rows={3}
            value={projectDescription}
            onChange={(e) => setProjectDescription(e.target.value)}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel id="project-access-label">Access</InputLabel>
            <Select
              labelId="project-access-label"
              value={projectPublic ? 'public' : 'private'}
              label="Access"
              onChange={(e) => setProjectPublic(e.target.value === 'public')}
            >
              <MenuItem value="private">Private - Only you and users you add can access</MenuItem>
              <MenuItem value="public">Public - All organization members can access</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNewProjectDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateProject} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Member Dialog */}
      <Dialog open={openAddMemberDialog} onClose={() => setOpenAddMemberDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Member to Organization</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Email Address"
            type="email"
            fullWidth
            value={newMemberEmail}
            onChange={(e) => setNewMemberEmail(e.target.value)}
            required
            helperText="Enter the email of a registered user"
          />
          <FormControl fullWidth margin="dense">
            <InputLabel id="member-role-label">Role</InputLabel>
            <Select
              labelId="member-role-label"
              value={newMemberRole}
              label="Role"
              onChange={(e) => setNewMemberRole(e.target.value)}
            >
              <MenuItem value="admin">Admin - Full access to organization</MenuItem>
              <MenuItem value="member">Member - Can create projects and access public projects</MenuItem>
              <MenuItem value="viewer">Viewer - Can only view public projects</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddMemberDialog(false)}>Cancel</Button>
          <Button onClick={handleAddMemberSubmit} variant="contained" color="primary">
            Add Member
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

export default OrganizationProjects; 
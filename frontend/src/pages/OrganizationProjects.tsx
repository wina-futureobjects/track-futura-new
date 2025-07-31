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
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import GroupIcon from '@mui/icons-material/Group';
import SettingsIcon from '@mui/icons-material/Settings';
import ViewListIcon from '@mui/icons-material/ViewList';
import GridViewIcon from '@mui/icons-material/GridView';
import { apiFetch } from '../utils/api';
import { useTheme } from '@mui/material/styles';

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

// Helper function to convert legacy routes to new organization/project structure
const convertLegacyRoute = (
  legacyRoute: string, 
  organizationId: string, 
  projectId: string
): string => {
  const baseOrgProjectPath = `/organizations/${organizationId}/projects/${projectId}`;
  
  // Remove query parameters for route mapping
  const [path] = legacyRoute.split('?');
  
  // Route conversion mappings
  const routeMappings: Record<string, string> = {
    '/dashboard': baseOrgProjectPath,
    '/track-accounts': `${baseOrgProjectPath}/source-tracking`,
    '/track-accounts/accounts': `${baseOrgProjectPath}/source-tracking/sources`,
    '/track-accounts/upload': `${baseOrgProjectPath}/source-tracking/upload`,
    '/track-accounts/create': `${baseOrgProjectPath}/source-tracking/create`,
    '/analysis': `${baseOrgProjectPath}/analysis`,
    '/instagram-folders': `${baseOrgProjectPath}/instagram-folders`,
    '/facebook-folders': `${baseOrgProjectPath}/facebook-folders`,
    '/linkedin-folders': `${baseOrgProjectPath}/linkedin-folders`,
    '/tiktok-folders': `${baseOrgProjectPath}/tiktok-folders`,
    '/report-folders': `${baseOrgProjectPath}/report-folders`,
    '/reports/generated': `${baseOrgProjectPath}/reports/generated`,
    '/report': `${baseOrgProjectPath}/report`,
    '/comments-scraper': `${baseOrgProjectPath}/comments-scraper`,
    '/facebook-comment-scraper': `${baseOrgProjectPath}/facebook-comment-scraper`,
    '/brightdata-settings': `${baseOrgProjectPath}/brightdata-settings`,
    '/brightdata-scraper': `${baseOrgProjectPath}/brightdata-scraper`,
    '/automated-batch-scraper': `${baseOrgProjectPath}/automated-batch-scraper`,
    '/settings': `${baseOrgProjectPath}/settings`,
  };

  // Check for direct mapping
  if (routeMappings[path]) {
    return routeMappings[path];
  }

  // Handle dynamic routes with parameters
  if (path.startsWith('/track-accounts/edit/')) {
    const accountId = path.split('/track-accounts/edit/')[1];
    return `${baseOrgProjectPath}/source-tracking/edit/${accountId}`;
  }

  if (path.startsWith('/instagram-data/')) {
    const folderId = path.split('/instagram-data/')[1];
    return `${baseOrgProjectPath}/instagram-data/${folderId}`;
  }

  if (path.startsWith('/facebook-data/')) {
    const folderId = path.split('/facebook-data/')[1];
    return `${baseOrgProjectPath}/facebook-data/${folderId}`;
  }

  if (path.startsWith('/linkedin-data/')) {
    const folderId = path.split('/linkedin-data/')[1];
    return `${baseOrgProjectPath}/linkedin-data/${folderId}`;
  }

  if (path.startsWith('/tiktok-data/')) {
    const folderId = path.split('/tiktok-data/')[1];
    return `${baseOrgProjectPath}/tiktok-data/${folderId}`;
  }

  if (path.startsWith('/report-folders/')) {
    const segments = path.split('/');
    if (segments.length === 3) {
      // /report-folders/:reportId
      const reportId = segments[2];
      return `${baseOrgProjectPath}/report-folders/${reportId}`;
    }
    if (segments.length >= 4) {
      // /report-folders/:reportId/... 
      const remainingPath = segments.slice(2).join('/');
      return `${baseOrgProjectPath}/report-folders/${remainingPath}`;
    }
  }

  if (path.startsWith('/report/')) {
    const reportId = path.split('/report/')[1];
    return `${baseOrgProjectPath}/report/${reportId}`;
  }

  // Default fallback to project dashboard
  return baseOrgProjectPath;
};

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
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('grid');
  const theme = useTheme();

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
    const intendedDestination = sessionStorage.getItem('intendedDestination');
    
    if (intendedDestination && organizationId) {
      // Clear the stored destination
      sessionStorage.removeItem('intendedDestination');
      
      // Convert legacy route to new organization/project structure
      const convertedRoute = convertLegacyRoute(intendedDestination, organizationId, projectId.toString());
      navigate(convertedRoute, { replace: true });
    } else {
      // Normal navigation to project dashboard
      navigate(`/organizations/${organizationId}/projects/${projectId}`);
    }
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

  const handleViewModeChange = (
    event: React.MouseEvent<HTMLElement>,
    newViewMode: 'list' | 'grid',
  ) => {
    if (newViewMode !== null) {
      setViewMode(newViewMode);
    }
  };

  // Filter projects based on search query
  const filteredProjects = projects.filter(project => 
    project.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Return either grid or list view of projects
  const renderProjects = () => {
    if (filteredProjects.length === 0) {
      return (
        <Paper sx={{ p: 4, textAlign: 'center', mt: 2, borderRadius: 8, border: '1px solid rgba(0,0,0,0.08)' }}>
          <Typography variant="h6" gutterBottom>No projects found</Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Create your first project in this organization to get started.
          </Typography>
                     <Button 
             variant="contained" 
             startIcon={<AddIcon />} 
             onClick={handleNewProject}
             sx={{
               borderRadius: 2,
               bgcolor: '#62EF83', 
               color: '#000000', 
               textTransform: 'none',
               fontWeight: 500,
               boxShadow: 'none',
               px: 3,
               py: 1,
               transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
               '&:hover': {
                 bgcolor: '#4FD16C',
                 boxShadow: '0 2px 8px rgba(98, 239, 131, 0.3)'
               }
             }}
           >
             Create Project
           </Button>
        </Paper>
      );
    }

    if (viewMode === 'grid') {
      return (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', mx: -1 }}>
          {filteredProjects.map((project) => (
            <Box 
              key={project.id} 
              sx={{ 
                width: { xs: '100%', sm: '50%', md: '33.33%', lg: '25%' },
                p: 1
              }}
            >
              <Card 
                                 sx={{ 
                   height: '100%',
                   display: 'flex',
                   flexDirection: 'column',
                   transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                   '&:hover': {
                     transform: 'translateY(-4px)',
                     boxShadow: '0 10px 20px rgba(0,0,0,0.1)',
                   },
                   cursor: 'pointer',
                   borderRadius: '12px',
                   overflow: 'hidden',
                   border: '1px solid rgba(0,0,0,0.08)',
                   boxShadow: 'none',
                   position: 'relative'
                 }}
              >
                {/* Action button outside CardActionArea */}
                <IconButton 
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    // Project actions menu
                  }}
                  sx={{ 
                    position: 'absolute', 
                    top: 8, 
                    right: 8,
                    zIndex: 1
                  }}
                >
                  <MoreVertIcon fontSize="small" />
                </IconButton>
                
                <CardActionArea 
                                   sx={{ 
                   flexGrow: 1, 
                   display: 'flex', 
                   flexDirection: 'column', 
                   alignItems: 'flex-start', 
                   p: 2.5,
                   transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                   '&:hover': {
                     bgcolor: 'transparent'
                   }
                 }}
                  onClick={() => handleOpenProject(project.id)}
                >
                  <Box 
                    sx={{ 
                      width: '100%', 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      mb: 1
                    }}
                  >
                    <Typography 
                      variant="h6" 
                      component="div" 
                      sx={{ 
                        fontWeight: 500,
                        color: theme => theme.palette.primary.main,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {project.name}
                    </Typography>
                  </Box>
                  
                  {project.description && (
                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {project.description}
                    </Typography>
                  )}
                  
                  <Box sx={{ 
                    mt: 'auto',
                    display: 'flex',
                    justifyContent: 'space-between',
                    width: '100%'
                  }}>
                    <Chip 
                      label={project.is_public ? 'Public' : 'Private'} 
                      size="small"
                      sx={{ 
                        bgcolor: project.is_public ? 'rgba(46, 204, 113, 0.1)' : 'rgba(52, 152, 219, 0.1)',
                        color: project.is_public ? 'rgb(46, 204, 113)' : 'rgb(52, 152, 219)',
                        borderRadius: '4px',
                        fontWeight: 500,
                        fontSize: '0.7rem',
                        height: '24px'
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {new Date(project.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                </CardActionArea>
              </Card>
            </Box>
          ))}
        </Box>
      );
    }

    // List View
    return (
      <TableContainer component={Paper} sx={{ 
        boxShadow: 'none', 
        borderRadius: '8px',
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
              >
                <TableCell 
                  sx={{ color: theme => theme.palette.primary.main, fontWeight: 500 }}
                  onClick={() => handleOpenProject(project.id)}
                >
                  {project.name}
                </TableCell>
                <TableCell onClick={() => handleOpenProject(project.id)}>
                  {project.owner_name}
                </TableCell>
                <TableCell onClick={() => handleOpenProject(project.id)}>
                  <Chip 
                    label={project.is_public ? 'Public' : 'Private'} 
                    size="small"
                    sx={{ 
                      bgcolor: project.is_public ? 'rgba(46, 204, 113, 0.1)' : 'rgba(52, 152, 219, 0.1)',
                      color: project.is_public ? 'rgb(46, 204, 113)' : 'rgb(52, 152, 219)',
                      borderRadius: '4px',
                      fontWeight: 500,
                      fontSize: '0.7rem',
                      height: '24px'
                    }}
                  />
                </TableCell>
                <TableCell onClick={() => handleOpenProject(project.id)}>
                  {new Date(project.created_at).toLocaleDateString()}
                </TableCell>
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
    );
  };

  // Filter members based on search query
  const filteredMembers = members.filter(member => 
    member.user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    `${member.user.first_name} ${member.user.last_name}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ 
      width: '100%', 
      padding: '24px 32px',
      bgcolor: '#f8f9fa',
      minHeight: 'calc(100vh - 64px)',
    }}>
      {/* Tabs */}
      <Box sx={{ mb: 4, display: 'flex', borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          aria-label="organization tabs"
          sx={{
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 500,
              fontSize: '1rem',
              color: 'rgba(0, 0, 0, 0.7)',
              minWidth: 100,
              py: 1.5,
            },
            '& .Mui-selected': {
              color: theme => theme.palette.primary.main,
              fontWeight: 600,
            },
            '& .MuiTabs-indicator': {
              backgroundColor: theme => theme.palette.primary.main,
              height: 3,
            },
          }}
        >
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
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
              <Typography variant="h4" component="h1" fontWeight="600" my={1.5}>
                {organization?.name || 'Organization'} Projects
              </Typography>
                             <Button 
                 variant="contained" 
                 startIcon={<AddIcon />}
                 onClick={handleNewProject}
                 sx={{ 
                   borderRadius: 8,
                   bgcolor: '#62EF83', 
                   color: '#000000', 
                   textTransform: 'none',
                   fontWeight: 500,
                   boxShadow: 'none',
                   px: 3,
                   py: 1.2,
                   transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                   '&:hover': {
                     bgcolor: '#4FD16C',
                     boxShadow: '0 2px 8px rgba(98, 239, 131, 0.3)'
                   }
                 }}
               >
                 Create project
               </Button>
            </Box>

            {/* Search and filters bar */}
            <Paper
              elevation={0}
              sx={{ 
                p: 1.5, 
                mb: 3, 
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderRadius: 3,
                border: '1px solid rgba(0, 0, 0, 0.08)',
                bgcolor: 'white' 
              }}
            >
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                width: '100%',
                maxWidth: 500,
                borderRadius: 2,
                px: 2,
                py: 0.5,
                bgcolor: 'rgba(0, 0, 0, 0.03)'
              }}>
                <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
                <TextField
                  placeholder="Search projects"
                  variant="standard"
                  fullWidth
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ 
                    '& .MuiInput-root': {
                      '&::before, &::after': {
                        display: 'none'
                      }
                    },
                    '& .MuiInputBase-input': {
                      py: 1
                    }
                  }}
                />
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1,
                  py: 0.75,
                  px: 2,
                  borderRadius: 2,
                  bgcolor: 'rgba(0, 0, 0, 0.03)'
                }}>
                  <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500 }}>
                    Sort by:
                  </Typography>
                  <Select
                    value={sortBy}
                    onChange={handleSortChange}
                    size="small"
                    variant="standard"
                    disableUnderline
                    sx={{ 
                      minWidth: 120,
                      '& .MuiSelect-select': {
                        fontWeight: 500,
                        py: 0,
                        color: theme => theme.palette.primary.main
                      }
                    }}
                  >
                    <MenuItem value="last viewed">Last viewed</MenuItem>
                    <MenuItem value="newest">Newest</MenuItem>
                    <MenuItem value="oldest">Oldest</MenuItem>
                    <MenuItem value="name">Name</MenuItem>
                  </Select>
                </Box>
                
                                 <ToggleButtonGroup
                   value={viewMode}
                   exclusive
                   onChange={handleViewModeChange}
                   aria-label="view mode"
                   size="small"
                   sx={{ 
                     border: 'none',
                     bgcolor: 'rgba(0, 0, 0, 0.03)',
                     borderRadius: 2,
                     '& .MuiToggleButton-root': {
                       border: 'none',
                       py: 0.75,
                       transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                       '&.Mui-selected': {
                         bgcolor: 'white',
                         boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
                         '&:hover': {
                           bgcolor: 'white'
                         }
                       }
                     }
                   }}
                 >
                  <ToggleButton value="grid" aria-label="grid view">
                    <GridViewIcon />
                  </ToggleButton>
                  <ToggleButton value="list" aria-label="list view">
                    <ViewListIcon />
                  </ToggleButton>
                </ToggleButtonGroup>
              </Box>
            </Paper>

            {/* Projects Count */}
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Showing {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''}
            </Typography>

            {/* Projects Display */}
            {loading ? (
              <Box display="flex" justifyContent="center" mt={4}>
                <CircularProgress />
              </Box>
            ) : (
              renderProjects()
            )}
          </>
        )}
      </Box>
      
      {/* Members Tab */}
      <Box role="tabpanel" hidden={activeTab !== 1}>
        {activeTab === 1 && (
          <>
            {/* Header and actions */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
              <Typography variant="h4" component="h1" fontWeight="600" my={1.5}>
                {organization?.name || 'Organization'} Members
              </Typography>
                <Button 
                 variant="contained" 
                 startIcon={<GroupIcon />}
                 onClick={handleAddMember}
                 sx={{ 
                   borderRadius: 8,
                   bgcolor: '#62EF83', 
                   color: '#000000', 
                   textTransform: 'none',
                   fontWeight: 500,
                   boxShadow: 'none',
                   px: 3,
                   py: 1.2,
                   transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                   '&:hover': {
                     bgcolor: '#4FD16C',
                     boxShadow: '0 2px 8px rgba(98, 239, 131, 0.3)'
                   }
                 }}
                >
                  Add Member
                </Button>
            </Box>

            {/* Search for members */}
            <Paper
              elevation={0}
              sx={{ 
                p: 1.5, 
                mb: 3, 
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderRadius: 3,
                border: '1px solid rgba(0, 0, 0, 0.08)',
                bgcolor: 'white' 
              }}
            >
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                width: '100%',
                maxWidth: 500,
                borderRadius: 2,
                px: 2,
                py: 0.5,
                bgcolor: 'rgba(0, 0, 0, 0.03)'
              }}>
                <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
                <TextField
                  placeholder="Search members by name or email"
                  variant="standard"
                  fullWidth
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ 
                    '& .MuiInput-root': {
                      '&::before, &::after': {
                        display: 'none'
                      }
                    },
                    '& .MuiInputBase-input': {
                      py: 1
                    }
                  }}
                />
              </Box>
            </Paper>

            {/* Members Count */}
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
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
                    borderRadius: '8px',
                    border: '1px solid rgba(0,0,0,0.08)',
                    overflow: 'hidden'
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
                          <TableRow key={member.id} hover>
                            <TableCell sx={{ fontWeight: 500 }}>
                              {member.user.first_name} {member.user.last_name}
                            </TableCell>
                            <TableCell>{member.user.email}</TableCell>
                            <TableCell>
                              <Chip 
                                label={member.role} 
                                size="small"
                                sx={{ 
                                  bgcolor: 
                                    member.role === 'admin' ? 'rgba(250, 173, 20, 0.1)' : 
                                    member.role === 'member' ? 'rgba(52, 152, 219, 0.1)' : 
                                    'rgba(149, 165, 166, 0.1)',
                                  color:
                                    member.role === 'admin' ? 'rgb(250, 173, 20)' : 
                                    member.role === 'member' ? 'rgb(52, 152, 219)' : 
                                    'rgb(149, 165, 166)',
                                  borderRadius: '4px',
                                  fontWeight: 500,
                                  fontSize: '0.7rem',
                                  height: '24px',
                                  textTransform: 'capitalize'
                                }}
                              />
                            </TableCell>
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
                  <Paper sx={{ p: 4, textAlign: 'center', mt: 2, borderRadius: 8, border: '1px solid rgba(0,0,0,0.08)' }}>
                    <Typography variant="h6" gutterBottom>No members found</Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Add members to your organization to collaborate on projects.
                    </Typography>
                                         <Button 
                       variant="contained" 
                       startIcon={<GroupIcon />} 
                       onClick={handleAddMember}
                       sx={{
                         borderRadius: 8,
                         bgcolor: '#62EF83', 
                         color: '#000000', 
                         textTransform: 'none',
                         fontWeight: 500,
                         boxShadow: 'none',
                         px: 3,
                         py: 1.2,
                         transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                         '&:hover': {
                           bgcolor: '#4FD16C',
                           boxShadow: '0 2px 8px rgba(98, 239, 131, 0.3)'
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
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
              <Typography variant="h4" component="h1" fontWeight="600" my={1.5}>
                {organization?.name || 'Organization'} Settings
              </Typography>
            </Box>
            
            {/* Organization settings content */}
            <Paper sx={{ 
              p: 4, 
              mb: 4, 
              borderRadius: 3,
              boxShadow: 'none',
              border: '1px solid rgba(0,0,0,0.08)'
            }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>Organization Information</Typography>
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>
                  Organization Name
                </Typography>
                <TextField
                  fullWidth
                  variant="outlined"
                  size="small"
                  value={organization?.name || ''}
                  InputProps={{
                    readOnly: true,
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      borderRadius: 2
                    }
                  }}
                />
              </Box>
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={500}>
                  Description
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  variant="outlined"
                  size="small"
                  value={organization?.description || ''}
                  InputProps={{
                    readOnly: true,
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      borderRadius: 2
                    }
                  }}
                />
              </Box>
              
              <Box mt={3}>
                                 <Button 
                   variant="outlined" 
                   startIcon={<SettingsIcon />}
                   sx={{
                     borderRadius: 8,
                     borderColor: theme.palette.primary.main,
                     color: theme.palette.primary.main,
                     textTransform: 'none',
                     fontWeight: 500,
                     px: 3,
                     py: 1,
                     transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                     '&:hover': {
                       backgroundColor: theme => theme.palette.primary.main,
                       color: '#fff',
                       borderColor: theme => theme.palette.primary.dark,
                     }
                   }}
                 >
                   Edit Organization
                 </Button>
              </Box>
            </Paper>
            
            <Paper sx={{ 
              p: 4, 
              borderRadius: 3,
              boxShadow: 'none',
              border: '1px solid rgba(255, 68, 68, 0.3)',
              bgcolor: 'rgba(255, 68, 68, 0.12)'
            }}>
              <Typography variant="h6" gutterBottom fontWeight={600} sx={{ color: 'warning.main' }}>
                Danger Zone
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Permanently delete this organization and all its data. This action cannot be undone.
              </Typography>
              <Box mt={2}>
                                 <Button 
                   variant="outlined" 
                   color="warning"
                   sx={{
                     borderRadius: 8,
                     textTransform: 'none',
                     fontWeight: 500,
                     px: 3,
                     py: 1,
                     borderColor: 'warning.main',
                     color: 'warning.main',
                     transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                     '&:hover': {
                       borderColor: 'warning.dark',
                       backgroundColor: 'rgba(255, 68, 68, 0.08)',
                     }
                   }}
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
      <Dialog 
        open={openNewProjectDialog} 
        onClose={() => setOpenNewProjectDialog(false)}
        fullWidth
        maxWidth="sm"
        PaperProps={{
          sx: {
            borderRadius: '12px',
            boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
          }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight={600}>Create New Project</Typography>
        </DialogTitle>
        <DialogContent sx={{ pb: 2, pt: 2 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            Create a new project to organize your documents, assistants, and more.
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Project Name"
            type="text"
            fullWidth
            variant="outlined"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            sx={{ mb: 3, mt: 2 }}
          />
          <TextField
            margin="dense"
            id="description"
            label="Description (Optional)"
            type="text"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={projectDescription}
            onChange={(e) => setProjectDescription(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" sx={{ mr: 2 }}>
              Project visibility:
            </Typography>
            <FormControl component="fieldset">
              <Select
                value={projectPublic ? "public" : "private"}
                onChange={(e) => setProjectPublic(e.target.value === "public")}
                size="small"
                sx={{ minWidth: 120 }}
              >
                <MenuItem value="private">Private</MenuItem>
                <MenuItem value="public">Public</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Typography variant="caption" color="text.secondary">
            {projectPublic 
              ? "Public projects can be viewed by anyone with the link." 
              : "Private projects are only visible to organization members."}
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid rgba(0, 0, 0, 0.05)' }}>
          <Button 
            onClick={() => setOpenNewProjectDialog(false)}
            sx={{ color: 'text.secondary' }}
          >
            Cancel
          </Button>
                     <Button 
             onClick={handleCreateProject} 
             variant="contained"
             disabled={!projectName.trim()}
             sx={{ 
               borderRadius: 2,
               bgcolor: '#62EF83',
               color: '#000000',
               textTransform: 'none',
               px: 3,
               transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
               '&.Mui-disabled': {
                 bgcolor: 'rgba(26, 115, 232, 0.5)',
                 color: 'white'
               }
             }}
           >
             Create
           </Button>
        </DialogActions>
      </Dialog>

      {/* Add Member Dialog */}
      <Dialog 
        open={openAddMemberDialog} 
        onClose={() => setOpenAddMemberDialog(false)}
        fullWidth
        maxWidth="sm"
        PaperProps={{
          sx: {
            borderRadius: '12px',
            boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
          }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight={600}>Invite New Member</Typography>
        </DialogTitle>
        <DialogContent sx={{ pb: 2, pt: 2 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            Invite a new member to join your organization. They will receive an email invitation.
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            id="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={newMemberEmail}
            onChange={(e) => setNewMemberEmail(e.target.value)}
            sx={{ mb: 3, mt: 2 }}
          />
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" sx={{ mr: 2 }}>
              Member role:
            </Typography>
            <FormControl component="fieldset">
              <Select
                value={newMemberRole}
                onChange={(e) => setNewMemberRole(e.target.value)}
                size="small"
                sx={{ minWidth: 120 }}
              >
                <MenuItem value="admin">Admin</MenuItem>
                <MenuItem value="member">Member</MenuItem>
                <MenuItem value="viewer">Viewer</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Typography variant="caption" color="text.secondary">
            {newMemberRole === 'admin' 
              ? "Admins can manage members, projects, and organization settings." 
              : newMemberRole === 'member'
                ? "Members can create and edit projects, but cannot manage organization settings."
                : "Viewers can only view projects, but cannot edit them."}
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid rgba(0, 0, 0, 0.05)' }}>
          <Button 
            onClick={() => setOpenAddMemberDialog(false)}
            sx={{ color: 'text.secondary' }}
          >
            Cancel
          </Button>
                     <Button 
             onClick={handleAddMemberSubmit} 
             variant="contained"
             disabled={!newMemberEmail.trim()}
             sx={{ 
               borderRadius: 2,
               bgcolor: '#62EF83',
               color: '#000000',
               textTransform: 'none',
               px: 3,
               transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
               '&.Mui-disabled': {
                 bgcolor: 'rgba(26, 115, 232, 0.5)',
                 color: 'white'
               }
             }}
           >
             Send Invitation
           </Button>
        </DialogActions>
      </Dialog>

      {/* Error message */}
      {error && (
        <Paper sx={{ 
          mt: 3,
          p: 2, 
                     bgcolor: 'rgba(255, 68, 68, 0.05)',
           color: 'warning.main',
           borderRadius: 3,
           border: '1px solid rgba(255, 68, 68, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <Typography variant="body2" fontWeight={500}>{error}</Typography>
        </Paper>
      )}
    </Box>
  );
};

export default OrganizationProjects; 
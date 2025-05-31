import React, { useState, useEffect, useCallback } from 'react';
import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Typography,
  Menu,
  MenuItem,
  Avatar,
  Button,
  Chip,
  Divider,
  Breadcrumbs,
  Link,
  Popover,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  ListItemButton,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  Menu as MenuIcon,
  KeyboardArrowDown,
  AdminPanelSettings as AdminIcon,
  Business as TenantIcon,
  LightMode as LightIcon,
  NavigateNext as NavigateNextIcon,
  Folder as FolderIcon,
  Dashboard as DashboardIcon,
  Description as DescriptionIcon,
  Storage as StorageIcon,
  HomeOutlined as HomeIcon,
  FolderOutlined as FolderOutlinedIcon,
  DashboardOutlined as DashboardOutlinedIcon,
  InsertDriveFileOutlined as FileOutlinedIcon,
  Dataset as DatabaseIcon,
  Hub as HubIcon,
  BusinessOutlined as BusinessOutlinedIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { logout, getUserRole, getCurrentUser } from '../../utils/auth';
import { apiFetch } from '../../utils/api';

interface HeaderProps {
  open: boolean;
  onToggle: () => void;
}

// Define interfaces for Organization and Project
interface Organization {
  id: number;
  name: string;
  description: string | null;
}

interface Project {
  id: number;
  name: string;
  description: string | null;
  organization: number;
  organization_name: string;
}

// Helper function to get page title from path
const getPageTitle = (pathname: string): string => {
  // Default title if pathname is empty or undefined
  if (!pathname) return 'Dashboard';
  
  const parts = pathname.split('/').filter(Boolean);
  
  // Handle empty paths
  if (parts.length === 0) return 'Dashboard';
  
  const lastPart = parts[parts.length - 1];
  
  // Map of route paths to display names
  const routeNames: Record<string, string> = {
    'dashboard': 'Dashboard',
    'instagram-folders': 'Instagram Folders',
    'instagram-data': 'Instagram Data',
    'facebook-folders': 'Facebook Folders',
    'facebook-data': 'Facebook Data',
    'linkedin-folders': 'LinkedIn Folders',
    'linkedin-data': 'LinkedIn Data',
    'tiktok-folders': 'TikTok Folders',
    'tiktok-data': 'TikTok Data',
    'track-accounts': 'Track Accounts',
    'settings': 'Settings',
    'report-folders': 'Reports',
    'brightdata-settings': 'Brightdata Settings',
    'brightdata-scraper': 'Brightdata Scraper',
    'super': 'Super Admin Dashboard',
    'tenant': 'Tenant Admin Dashboard',
    'projects': 'Projects',
    'organizations': 'Organizations',
  };
  
  // Safety check for undefined or empty lastPart
  if (!lastPart) return 'Dashboard';
  
  // If we have a mapping, use it; otherwise, format the string
  return routeNames[lastPart] || lastPart.charAt(0).toUpperCase() + lastPart.slice(1).replace(/-/g, ' ');
};

// Extract organization and project IDs/names from path
const getPathInfo = (pathname: string): { 
  organizationId: string | null; 
  projectId: string | null;
  projectPath: boolean;
  projectsListPath: boolean;
  isDashboardPath: boolean;
  showDashboardLabel: boolean;
} => {
  // Default return value for empty or undefined pathname
  if (!pathname) return { 
    organizationId: null, 
    projectId: null,
    projectPath: false,
    projectsListPath: false,
    isDashboardPath: false,
    showDashboardLabel: false
  };
  
  const parts = pathname.split('/').filter(Boolean);
  let organizationId: string | null = null;
  let projectId: string | null = null;
  let projectsListPath = false;
  let projectPath = false;
  let isDashboardPath = false;
  let showDashboardLabel = false;
  
  // Check for exact match of /organizations/1/projects/1 pattern
  if (parts.length === 4 && 
      parts[0] === 'organizations' && 
      parts[2] === 'projects') {
    organizationId = parts[1];
    projectId = parts[3];
    projectPath = true;
    showDashboardLabel = false; // Don't show Dashboard label for this exact pattern
    return { organizationId, projectId, projectsListPath, projectPath, isDashboardPath, showDashboardLabel };
  }
  
  // Process each part of the path
  for (let i = 0; i < parts.length; i++) {
    // Handle organization ID extraction
    if (parts[i] === 'organizations' && i + 1 < parts.length) {
      organizationId = parts[i + 1];
      
      // Check if this is the projects list path
      if (i + 2 < parts.length && parts[i + 2] === 'projects' && i + 3 >= parts.length) {
        projectsListPath = true;
      }
      
      // Check if this is a specific project path
      if (i + 2 < parts.length && parts[i + 2] === 'projects' && i + 3 < parts.length) {
        projectId = parts[i + 3];
        projectPath = true;
        
        // Don't show dashboard label for root project view
        if (i + 4 >= parts.length) {
          showDashboardLabel = false;
        } else {
          showDashboardLabel = true;
        }
      }
    }
    
    // Legacy dashboard path handling
    if (parts[i] === 'dashboard' && i + 1 < parts.length) {
      projectId = parts[i + 1];
      isDashboardPath = true;
    }
  }
  
  return { organizationId, projectId, projectsListPath, projectPath, isDashboardPath, showDashboardLabel };
};

const Header: React.FC<HeaderProps> = ({ open, onToggle }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const isMenuOpen = Boolean(anchorEl);
  const [userRole, setUserRole] = useState(getUserRole());
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  
  // Breadcrumb state
  const [organizationName, setOrganizationName] = useState('Organization');
  const [projectName, setProjectName] = useState('Project');
  
  // Dropdown state
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingOrgs, setLoadingOrgs] = useState(false);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [orgDropAnchorEl, setOrgDropAnchorEl] = useState<HTMLElement | null>(null);
  const [projectDropAnchorEl, setProjectDropAnchorEl] = useState<HTMLElement | null>(null);
  
  // Organization dropdown
  const orgDropdownOpen = Boolean(orgDropAnchorEl);
  const orgDropdownId = orgDropdownOpen ? 'org-dropdown-menu' : undefined;
  
  // Project dropdown
  const projectDropdownOpen = Boolean(projectDropAnchorEl);
  const projectDropdownId = projectDropdownOpen ? 'project-dropdown-menu' : undefined;
  
  // Get path info safely - memoize to prevent recalculations
  const pathInfo = React.useMemo(() => getPathInfo(location.pathname), [location.pathname]);
  const organizationId = pathInfo.organizationId;
  const projectId = pathInfo.projectId;
  const isProjectsListPath = pathInfo.projectsListPath;
  const isProjectPath = pathInfo.projectPath;
  const isDashboardPath = pathInfo.isDashboardPath;
  const showDashboardLabel = pathInfo.showDashboardLabel;
  
  // Get current page title safely - memoize
  const currentPage = React.useMemo(() => getPageTitle(location.pathname), [location.pathname]);

  // State to track if the image failed to load
  const [imageError, setImageError] = useState(false);
  
  // Effect to load user data only once on mount
  useEffect(() => {
    // Load user data
    const user = getCurrentUser();
    if (user) {
      setUserName(`${user.first_name} ${user.last_name}`.trim() || user.username);
      setUserEmail(user.email || '');
    }
  }, []);
  
  // Separate effect for organization name to prevent unnecessary re-renders
  useEffect(() => {
    if (organizationId && typeof organizationId === 'string') {
      fetchOrganizationName(organizationId);
    } else {
      // Reset to default if no valid ID
      setOrganizationName('Organization');
    }
  }, [organizationId]);
  
  // Separate effect for project name to prevent unnecessary re-renders
  useEffect(() => {
    if (projectId && typeof projectId === 'string') {
      fetchProjectName(projectId);
    } else {
      // Reset to default if no valid ID
      setProjectName('Project');
    }
  }, [projectId]);
  
  // Fetch all organizations for the dropdown
  const fetchAllOrganizations = async () => {
    if (organizations.length > 0) return; // Don't fetch if we already have them
    
    try {
      setLoadingOrgs(true);
      const response = await apiFetch('/api/users/organizations/');
      
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          setOrganizations(data);
        } else if (data && typeof data === 'object' && 'results' in data) {
          setOrganizations(data.results || []);
        }
      }
    } catch (error) {
      console.error('Error fetching organizations:', error);
    } finally {
      setLoadingOrgs(false);
    }
  };
  
  // Fetch projects for the current organization
  const fetchOrganizationProjects = async () => {
    if (!organizationId) return;
    
    try {
      setLoadingProjects(true);
      const response = await apiFetch(`/api/users/projects/?organization=${organizationId}`);
      
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          setProjects(data);
        } else if (data && typeof data === 'object' && 'results' in data) {
          setProjects(data.results || []);
        }
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoadingProjects(false);
    }
  };
  
  // Handler functions must be defined before they're used in useMemo
  // Handle image load error
  const handleImageError = useCallback(() => {
    setImageError(true);
  }, []);
  
  // Handle organization dropdown open
  const handleOrgDropdownOpen = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setOrgDropAnchorEl(event.currentTarget);
    fetchAllOrganizations();
  }, []);
  
  // Handle project dropdown open
  const handleProjectDropdownOpen = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setProjectDropAnchorEl(event.currentTarget);
    fetchOrganizationProjects();
  }, [organizationId]);
  
  // Memoize breadcrumb components to prevent re-rendering
  const renderBreadcrumbs = React.useMemo(() => (
    <Breadcrumbs 
      separator={
        <Typography 
          sx={{ 
            color: '#9e9e9e', 
            fontSize: '16px',
            fontWeight: 300,
            mx: 0.5
          }}
        >
          |
        </Typography>
      } 
      aria-label="breadcrumb"
      sx={{ 
        display: 'flex', 
        alignItems: 'center',
        height: '100%',
        maxWidth: '60%',
        flexShrink: 1,
        '& .MuiBreadcrumbs-ol': {
          alignItems: 'center',
          height: '100%',
        },
        '& a': {
          textDecoration: 'none !important',
          color: '#2c3e50',
          '&:hover': {
            textDecoration: 'none !important',
            color: theme.palette.primary.main,
          }
        }
      }}
    >
      {/* Track Futura (always fixed) */}
      <Link
        sx={{ 
          display: 'flex', 
          alignItems: 'center',
          fontWeight: 600,
          fontSize: '16px',
          color: '#2c3e50',
          textDecoration: 'none !important',
          cursor: 'pointer',
          '&:hover': {
            color: theme.palette.primary.main,
          }
        }}
        onClick={() => navigate('/')}
        component="button"
        underline="none"
      >
        Track Futura
      </Link>
      
      {/* Organization dropdown (if available) */}
      {organizationId && (
        <Link
          sx={{ 
            fontWeight: 500,
            fontSize: '15px',
            display: 'flex',
            alignItems: 'center',
            color: '#2c3e50',
            textDecoration: 'none !important',
            cursor: 'pointer',
            height: '32px',
            padding: '0 8px',
            borderRadius: '6px',
            transition: 'all 0.2s ease',
            '&:hover': {
              color: theme.palette.primary.main,
              backgroundColor: 'rgba(225, 37, 27, 0.04)',
            }
          }}
          component="button"
          onClick={handleOrgDropdownOpen}
          aria-describedby={orgDropdownId}
          underline="none"
        >
          <BusinessOutlinedIcon sx={{ mr: 0.5, fontSize: 18 }} />
          {organizationName}
          <KeyboardArrowDown sx={{ 
            ml: 0.5, 
            fontSize: 18,
            transition: 'transform 0.2s ease',
            transform: orgDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)'
          }} />
        </Link>
      )}
      
      {/* Projects list link */}
      {isProjectsListPath && (
        <Typography
          sx={{ 
            fontWeight: 500,
            fontSize: '15px',
            color: '#2c3e50',
            display: 'flex',
            alignItems: 'center',
            height: '32px',
          }}
        >
          <FolderOutlinedIcon sx={{ mr: 0.5, fontSize: 18 }} />
          All Projects
        </Typography>
      )}
      
      {/* Project dropdown (for specific project page) */}
      {isProjectPath && projectId && (
        <Link
          sx={{ 
            fontWeight: 500,
            fontSize: '15px',
            display: 'flex',
            alignItems: 'center',
            color: '#2c3e50',
            textDecoration: 'none !important',
            cursor: 'pointer',
            height: '32px',
            padding: '0 8px',
            borderRadius: '6px',
            transition: 'all 0.2s ease',
            '&:hover': {
              color: theme.palette.primary.main,
              backgroundColor: 'rgba(225, 37, 27, 0.04)',
            }
          }}
          component="button"
          onClick={handleProjectDropdownOpen}
          aria-describedby={projectDropdownId}
          underline="none"
        >
          <FolderOutlinedIcon sx={{ mr: 0.5, fontSize: 18 }} />
          {projectName}
          <KeyboardArrowDown sx={{ 
            ml: 0.5, 
            fontSize: 18,
            transition: 'transform 0.2s ease',
            transform: projectDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)'
          }} />
        </Link>
      )}
      
      {/* Current page (only in project and not at root project URL) */}
      {isProjectPath && showDashboardLabel && (
        <Typography
          sx={{ 
            fontWeight: 500,
            fontSize: '15px',
            color: '#2c3e50',
            display: 'flex',
            alignItems: 'center',
            height: '32px',
          }}
        >
          <DashboardOutlinedIcon sx={{ mr: 0.5, fontSize: 18 }} />
          Dashboard
        </Typography>
      )}
      
      {/* Legacy project (if not using the new URL pattern) */}
      {projectId && !isProjectPath && !isProjectsListPath && (
        <Link
          sx={{ 
            fontWeight: 500,
            fontSize: '15px',
            display: 'flex',
            alignItems: 'center',
            color: '#2c3e50',
            textDecoration: 'none !important',
            height: '32px',
            padding: '0 8px',
            borderRadius: '6px',
            transition: 'all 0.2s ease',
            '&:hover': {
              color: theme.palette.primary.main,
              backgroundColor: 'rgba(225, 37, 27, 0.04)',
            }
          }}
          onClick={handleProjectDropdownOpen}
          aria-describedby={projectDropdownId}
          underline="none"
        >
          <FolderOutlinedIcon sx={{ mr: 0.5, fontSize: 18 }} />
          {projectName}
          <KeyboardArrowDown sx={{ 
            ml: 0.5, 
            fontSize: 18,
            transition: 'transform 0.2s ease',
            transform: projectDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)'
          }} />
        </Link>
      )}
      
      {/* Current page (if not at dashboard root) */}
      {(isDashboardPath || (projectId && !isProjectPath && !isProjectsListPath)) && currentPage !== 'Dashboard' && (
        <Typography
          sx={{ 
            fontWeight: 500,
            fontSize: '15px',
            color: '#2c3e50',
            display: 'flex',
            alignItems: 'center',
            height: '32px',
          }}
        >
          <DashboardOutlinedIcon sx={{ mr: 0.5, fontSize: 18 }} />
          {currentPage}
        </Typography>
      )}
    </Breadcrumbs>
  ), [theme, navigate, organizationId, organizationName, handleOrgDropdownOpen, orgDropdownId, orgDropdownOpen, isProjectsListPath, isProjectPath, projectId, projectName, handleProjectDropdownOpen, projectDropdownId, projectDropdownOpen, showDashboardLabel, isDashboardPath, currentPage]);

  // Handle menu operations
  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleNavigateToAdmin = () => {
    if (userRole === 'super_admin') {
      navigate('/super');
    } else if (userRole === 'tenant_admin') {
      navigate('/tenant');
    }
  };

  // Handle dropdown closes
  const handleOrgDropdownClose = () => {
    setOrgDropAnchorEl(null);
  };

  const handleProjectDropdownClose = () => {
    setProjectDropAnchorEl(null);
  };

  // Handle organization selection
  const handleOrganizationSelect = (orgId: number) => {
    navigate(`/organizations/${orgId}/projects`);
    handleOrgDropdownClose();
  };

  // Handle project selection
  const handleProjectSelect = (projId: number) => {
    if (organizationId) {
      navigate(`/organizations/${organizationId}/projects/${projId}`);
    } else {
      navigate(`/dashboard/${projId}`);
    }
    handleProjectDropdownClose();
  };

  // Async functions that are used in effects
  const fetchOrganizationName = async (id: string) => {
    try {
      const response = await apiFetch(`/api/users/organizations/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setOrganizationName(data.name || 'Organization');
      }
    } catch (error) {
      console.error('Error fetching organization name:', error);
      setOrganizationName('Organization');
    }
  };

  const fetchProjectName = async (id: string) => {
    try {
      const response = await apiFetch(`/api/users/projects/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setProjectName(data.name || 'Project');
      }
    } catch (error) {
      console.error('Error fetching project name:', error);
      setProjectName('Project');
    }
  };

  // Watch for organization/project changes in the URL
  useEffect(() => {
    // For project pages where we don't have organization in breadcrumb but have project
    if (projectId && !organizationId && !isDashboardPath) {
      // This is for URLs like /dashboard/1 where we need to get org from project
      const fetchProjectOrganization = async (id: string) => {
        try {
          const response = await apiFetch(`/api/users/projects/${id}/`);
          if (response.ok) {
            const data = await response.json();
            if (data.organization) {
              // Fetch organization name for this project
              const orgResponse = await apiFetch(`/api/users/organizations/${data.organization}/`);
              if (orgResponse.ok) {
                const orgData = await orgResponse.json();
                setOrganizationName(orgData.name || 'Organization');
              }
            }
          }
        } catch (error) {
          console.error('Error fetching project organization:', error);
        }
      };
      
      fetchProjectOrganization(projectId);
    }
  }, [location.pathname, isDashboardPath, projectId]);

  const menuId = 'primary-search-account-menu';
  const renderMenu = (
    <Menu
      anchorEl={anchorEl}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      id={menuId}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isMenuOpen}
      onClose={handleMenuClose}
      sx={{
        mt: 1.5,
        '& .MuiPaper-root': {
          borderRadius: '12px',
          boxShadow: 'none',
          border: '1px solid #e0e0e0',
          minWidth: '240px',
        }
      }}
    >
      {/* User Info */}
      <Box sx={{ px: 2, py: 1.5 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, fontSize: '14px' }}>
          {userName}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '13px' }}>
          {userEmail}
        </Typography>
      </Box>
      
      <Divider sx={{ my: 1, borderColor: '#f0f0f0' }} />
      
      <MenuItem 
        onClick={() => { handleMenuClose(); navigate('/settings'); }}
        sx={{ 
          fontSize: '14px',
          py: 1,
          '&:hover': { backgroundColor: '#f8f9fa' }
        }}
      >
        Account
      </MenuItem>
      
      <MenuItem 
        onClick={() => { handleMenuClose(); navigate('/settings'); }}
        sx={{ 
          fontSize: '14px',
          py: 1,
          '&:hover': { backgroundColor: '#f8f9fa' }
        }}
      >
        Billing
        <Box component="span" sx={{ ml: 1, fontSize: '11px', color: 'primary.main', fontWeight: 'bold' }}>
          Upgrade
        </Box>
      </MenuItem>
      
      <MenuItem 
        onClick={() => { handleMenuClose(); navigate('/settings'); }}
        sx={{ 
          fontSize: '14px',
          py: 1,
          '&:hover': { backgroundColor: '#f8f9fa' }
        }}
      >
        Organization settings
      </MenuItem>
      
      <MenuItem 
        onClick={() => { handleMenuClose(); }}
        sx={{ 
          fontSize: '14px',
          py: 1,
          '&:hover': { backgroundColor: '#f8f9fa' }
        }}
      >
        Product releases
        <Box component="span" sx={{ ml: 1, fontSize: '11px', color: 'primary.main', fontWeight: 'bold' }}>
          New
        </Box>
      </MenuItem>
      
      <MenuItem sx={{ fontSize: '14px', py: 1, '&:hover': { backgroundColor: '#f8f9fa' } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
          <span>Theme: Light</span>
          <LightIcon fontSize="small" />
        </Box>
      </MenuItem>
      
      <Divider sx={{ my: 1, borderColor: '#f0f0f0' }} />
      
      <MenuItem 
        onClick={handleLogout}
        sx={{ 
          fontSize: '14px',
          py: 1,
          '&:hover': { backgroundColor: '#f8f9fa' }
        }}
      >
        Log out
      </MenuItem>
    </Menu>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          backgroundColor: '#ffffff',
          color: '#2c3e50',
          boxShadow: 'none',
          borderBottom: '1px solid #e8eaed',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          top: '28px',
          minHeight: '60px',
        }}
      >
        <Toolbar sx={{ 
          minHeight: '60px !important', 
          display: 'flex', 
          alignItems: 'center', 
          gap: 2,
          px: 3
        }}>
          <IconButton
            size="medium"
            edge="start"
            color="inherit"
            aria-label="toggle sidebar"
            sx={{ 
              flexShrink: 0,
              '&:hover': {
                backgroundColor: 'rgba(225, 37, 27, 0.08)',
                color: '#E1251B',
              }
            }}
            onClick={onToggle}
          >
            <MenuIcon />
          </IconButton>
          
          {/* Use memoized breadcrumb component */}
          {renderBreadcrumbs}
          
          {/* Right side content */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, ml: 'auto' }}>
            {/* Admin link based on role */}
            {userRole === 'super_admin' && (
              <Chip
                icon={<AdminIcon />}
                label="Admin Dashboard"
                color="primary"
                clickable
                onClick={handleNavigateToAdmin}
                sx={{ 
                  backgroundColor: '#E1251B',
                  color: '#FFFFFF',
                  '&:hover': {
                    backgroundColor: '#B31D15',
                  }
                }}
              />
            )}
            
            <Button 
              color="inherit" 
              sx={{ 
                textTransform: 'none', 
                fontWeight: 500,
                color: '#2c3e50',
                fontSize: '14px',
                px: 2,
                py: 1,
                borderRadius: '8px',
                '&:hover': {
                  backgroundColor: 'rgba(225, 37, 27, 0.04)',
                  color: '#E1251B',
                }
              }}
              onClick={() => {}}
            >
              Docs
            </Button>
            
            <Button 
              color="inherit" 
              sx={{ 
                textTransform: 'none', 
                fontWeight: 500,
                color: '#2c3e50',
                fontSize: '14px',
                px: 2,
                py: 1,
                borderRadius: '8px',
                '&:hover': {
                  backgroundColor: 'rgba(225, 37, 27, 0.04)',
                  color: '#E1251B',
                }
              }}
              onClick={() => navigate('/settings')}
            >
              Settings
            </Button>
            
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center',
                cursor: 'pointer',
                p: 1,
                borderRadius: '8px',
                '&:hover': { 
                  backgroundColor: 'rgba(225, 37, 27, 0.04)',
                }
              }}
              onClick={handleProfileMenuOpen}
            >
              <Avatar 
                sx={{ 
                  width: 32, 
                  height: 32,
                  fontSize: '14px',
                  bgcolor: '#E1251B',
                  color: '#FFFFFF'
                }}
              >
                {userName ? userName.substring(0, 2).toUpperCase() : 'U'}
              </Avatar>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>
      {renderMenu}

      {/* Organization Dropdown Menu */}
      <Popover
        id={orgDropdownId}
        open={orgDropdownOpen}
        anchorEl={orgDropAnchorEl}
        onClose={handleOrgDropdownClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        sx={{
          mt: 1,
          '& .MuiPaper-root': {
            borderRadius: '12px',
            boxShadow: 'none',
            border: '1px solid #e0e0e0',
            minWidth: '240px',
          }
        }}
      >
        <List sx={{ py: 1 }}>
          {loadingOrgs ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={24} />
            </Box>
          ) : (
            organizations.map((org) => (
              <ListItemButton 
                key={org.id} 
                onClick={() => handleOrganizationSelect(org.id)}
                selected={organizationId === org.id.toString()}
                sx={{
                  mx: 1,
                  borderRadius: '8px',
                  '&:hover': { backgroundColor: '#f8f9fa' },
                  '&.Mui-selected': { 
                    backgroundColor: 'rgba(225, 37, 27, 0.08)',
                    '&:hover': { backgroundColor: 'rgba(225, 37, 27, 0.12)' }
                  }
                }}
              >
                <ListItemText 
                  primary={org.name} 
                  secondary={org.description || ''}
                  primaryTypographyProps={{ 
                    noWrap: true,
                    fontSize: '14px',
                    fontWeight: 500
                  }}
                  secondaryTypographyProps={{ 
                    noWrap: true,
                    fontSize: '12px'
                  }}
                />
              </ListItemButton>
            ))
          )}
        </List>
      </Popover>

      {/* Project Dropdown Menu */}
      <Popover
        id={projectDropdownId}
        open={projectDropdownOpen}
        anchorEl={projectDropAnchorEl}
        onClose={handleProjectDropdownClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        sx={{
          mt: 1,
          '& .MuiPaper-root': {
            borderRadius: '12px',
            boxShadow: 'none',
            border: '1px solid #e0e0e0',
            minWidth: '240px',
          }
        }}
      >
        <List sx={{ py: 1 }}>
          {loadingProjects ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={24} />
            </Box>
          ) : (
            projects.map((project) => (
              <ListItemButton 
                key={project.id} 
                onClick={() => handleProjectSelect(project.id)}
                selected={projectId === project.id.toString()}
                sx={{
                  mx: 1,
                  borderRadius: '8px',
                  '&:hover': { backgroundColor: '#f8f9fa' },
                  '&.Mui-selected': { 
                    backgroundColor: 'rgba(225, 37, 27, 0.08)',
                    '&:hover': { backgroundColor: 'rgba(225, 37, 27, 0.12)' }
                  }
                }}
              >
                <ListItemText 
                  primary={project.name} 
                  secondary={project.description || ''}
                  primaryTypographyProps={{ 
                    noWrap: true,
                    fontSize: '14px',
                    fontWeight: 500
                  }}
                  secondaryTypographyProps={{ 
                    noWrap: true,
                    fontSize: '12px'
                  }}
                />
              </ListItemButton>
            ))
          )}
        </List>
      </Popover>
    </Box>
  );
};

export default Header; 
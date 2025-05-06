import React, { useState, useCallback } from 'react';
import { styled, useTheme } from '@mui/material/styles';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Box,
  Typography,
  Tooltip,
  useMediaQuery,
  Collapse
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Timeline as TimelineIcon,
  Language as LanguageIcon,
  Message as MessageIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Notifications as NotificationsIcon,
  CloudQueue as CloudQueueIcon,
  Logout as LogoutIcon,
  AccountBox as AccountBoxIcon,
  Description as DescriptionIcon,
  Mood as MoodIcon,
  Assessment as AssessmentIcon,
  Instagram as InstagramIcon,
  Analytics as AnalyticsIcon,
  TrackChanges as TrackChangesIcon,
  Facebook as FacebookIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  DataUsage as DataUsageIcon,
  InsertChart as ChartIcon
} from '@mui/icons-material';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicVideoIcon from '@mui/icons-material/MusicVideo';
import { useNavigate, useLocation } from 'react-router-dom';
// Import the GE logo
import GELogo from '../../assets/images/logos/GE-logo.png';

// Inline minimal implementation of useAuth to avoid path resolution issues
const useAuth = () => {
  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  };
  
  return { logout };
};

const drawerWidth = 240;
const miniDrawerWidth = 65;

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  onToggle: () => void;
}

// Define menu structure with categories
interface MenuItem {
  text: string;
  path: string;
  icon: React.ReactNode;
  subItems?: MenuItem[];
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { logout } = useAuth();
  
  // State to track expanded menu categories
  const [expandedMenus, setExpandedMenus] = useState<Record<string, boolean>>({
    socialMedia: true,
    analysis: true
  });
  
  // Menu items with categories
  const menuItems: MenuItem[] = [
    { text: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { text: 'Track Accounts', path: '/track-accounts/folders', icon: <TrackChangesIcon /> },
    { 
      text: 'Social Media Data', 
      path: '#social-media', 
      icon: <DataUsageIcon />,
      subItems: [
        { text: 'Instagram Data', path: '/instagram-folders', icon: <InstagramIcon /> },
        { text: 'Facebook Data', path: '/facebook-folders', icon: <FacebookIcon /> },
        { text: 'LinkedIn Data', path: '/linkedin-folders', icon: <LinkedInIcon /> },
        { text: 'TikTok Data', path: '/tiktok-folders', icon: <MusicVideoIcon /> },
      ]
    },
    { 
      text: 'Analysis', 
      path: '#analysis', 
      icon: <ChartIcon />,
      subItems: [
        { text: 'Social Analysis', path: '/social-analysis', icon: <AnalyticsIcon /> },
        { text: 'Web Presence', path: '/web-presence', icon: <LanguageIcon /> },
        { text: 'Sentiment Analysis', path: '/sentiment', icon: <MoodIcon /> },
        { text: 'Word Cloud', path: '/word-cloud', icon: <CloudQueueIcon /> },
        { text: 'NPS Reports', path: '/nps', icon: <AssessmentIcon /> },
      ]
    },
    { text: 'Report Folders', path: '/report-folders', icon: <DescriptionIcon /> },
  ];

  // Function to check if a menu item is active based on the current path
  const isActive = useCallback((itemPath: string) => {
    // Special handling for root path
    if (itemPath === '/') {
      return location.pathname === '/';
    }
    
    // Skip category headers with hash paths
    if (itemPath.startsWith('#')) {
      return false;
    }
    
    // Special handling for social media data sections
    if (itemPath === '/instagram-folders') {
      return location.pathname.startsWith('/instagram');
    }
    if (itemPath === '/facebook-folders') {
      return location.pathname.startsWith('/facebook');
    }
    if (itemPath === '/linkedin-folders') {
      return location.pathname.startsWith('/linkedin');
    }
    if (itemPath === '/tiktok-folders') {
      return location.pathname.startsWith('/tiktok');
    }
    if (itemPath === '/track-accounts/folders') {
      return location.pathname.startsWith('/track-accounts');
    }
    
    // For other paths, check if the current path starts with the menu item path
    return location.pathname.startsWith(itemPath);
  }, [location.pathname]);

  // Check if any sub-item is active
  const isAnyCategoryItemActive = useCallback((items: MenuItem[] | undefined) => {
    if (!items) return false;
    return items.some(item => isActive(item.path));
  }, [isActive]);

  // Handle toggle of collapsible menu categories
  const handleToggleMenu = (menuId: string) => {
    setExpandedMenus(prev => ({
      ...prev,
      [menuId]: !prev[menuId]
    }));
  };

  const handleNavigate = useCallback((path: string) => {
    // Skip navigation for category headers
    if (path.startsWith('#')) {
      return;
    }
    
    // Prevent navigation if already on the same path or subpath
    if (location.pathname === path || 
        (path !== '/' && location.pathname.startsWith(path))) {
      return;
    }
    
    navigate(path);
    if (isMobile) {
      onClose();
    }
  }, [location.pathname, navigate, isMobile, onClose]);

  const handleLogout = useCallback(() => {
    logout();
    navigate('/login');
  }, [logout, navigate]);

  const renderMenuItem = (item: MenuItem, isSubItem = false) => {
    // For category headers with sub-items
    if (item.subItems) {
      const menuId = item.path.replace('#', '');
      const isExpanded = expandedMenus[menuId];
      const isAnySubItemActive = isAnyCategoryItemActive(item.subItems);
      
      return (
        <React.Fragment key={item.text}>
          <ListItem disablePadding sx={{ display: 'block', mb: 0.5 }}>
            <ListItemButton
              sx={{
                minHeight: 48,
                justifyContent: open ? 'initial' : 'center',
                px: open ? 2 : 1.5,
                borderRadius: 1,
                backgroundColor: isAnySubItemActive ? 'rgba(52, 152, 219, 0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(52, 152, 219, 0.05)',
                },
              }}
              onClick={() => open ? handleToggleMenu(menuId) : onToggle()}
            >
              <Tooltip title={open ? '' : item.text} placement="right" arrow>
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 2 : 'auto',
                    justifyContent: 'center',
                    color: isAnySubItemActive ? 'primary.main' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
              </Tooltip>
              {open && (
                <>
                  <ListItemText 
                    primary={item.text} 
                    sx={{ 
                      opacity: 1,
                      color: isAnySubItemActive ? 'primary.main' : 'text.primary',
                    }} 
                  />
                  {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </>
              )}
            </ListItemButton>
          </ListItem>
          
          {open && (
            <Collapse in={isExpanded} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {item.subItems.map(subItem => renderMenuItem(subItem, true))}
              </List>
            </Collapse>
          )}
        </React.Fragment>
      );
    }
    
    // For regular menu items
    return (
      <ListItem key={item.text} disablePadding sx={{ display: 'block', mb: 0.5, pl: isSubItem && open ? 2 : 0 }}>
        <ListItemButton
          sx={{
            minHeight: 48,
            justifyContent: open ? 'initial' : 'center',
            px: open ? 2 : 1.5,
            borderRadius: 1,
            backgroundColor: isActive(item.path) ? 'rgba(52, 152, 219, 0.1)' : 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(52, 152, 219, 0.05)',
            },
          }}
          onClick={() => handleNavigate(item.path)}
        >
          <Tooltip title={open ? '' : item.text} placement="right" arrow>
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: open ? 2 : 'auto',
                justifyContent: 'center',
                color: isActive(item.path) ? 'primary.main' : 'text.secondary',
              }}
            >
              {item.icon}
            </ListItemIcon>
          </Tooltip>
          {open && (
            <ListItemText 
              primary={item.text} 
              sx={{ 
                opacity: 1,
                color: isActive(item.path) ? 'primary.main' : 'text.primary',
              }} 
            />
          )}
        </ListItemButton>
      </ListItem>
    );
  };

  return (
    <Drawer
      sx={{
        width: open ? drawerWidth : miniDrawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? drawerWidth : miniDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          boxShadow: '0px 0px 15px rgba(0, 0, 0, 0.05)',
          overflowX: 'hidden',
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        },
        transition: theme.transitions.create('width', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      }}
      variant={isMobile ? "temporary" : "permanent"}
      anchor="left"
      open={isMobile ? open : true}
      onClose={onClose}
      className={open ? "" : "drawer-mini"}
      PaperProps={{
        sx: {
          width: open ? drawerWidth : miniDrawerWidth,
          overflow: 'hidden'
        }
      }}
    >
      <DrawerHeader>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {open ? (
            <img 
              src={GELogo} 
              alt="Great Eastern Logo" 
              style={{ 
                height: '32px', 
                objectFit: 'contain',
                marginLeft: '4px' 
              }} 
            />
          ) : (
            <img 
              src={GELogo} 
              alt="Great Eastern Logo" 
              style={{ 
                height: '24px', 
                objectFit: 'contain',
                margin: '0 auto'
              }} 
            />
          )}
        </Box>
        <IconButton onClick={onToggle}>
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </DrawerHeader>
      <Divider />
      
      {/* Main Menu Items */}
      <List sx={{ px: 0.5, flexGrow: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        {menuItems.map(item => renderMenuItem(item))}
      </List>
      
      <Divider />
      
      {/* Settings and Logout */}
      <List sx={{ px: 0.5 }}>
        <ListItem disablePadding>
          <ListItemButton
            sx={{
              minHeight: 48,
              justifyContent: open ? 'initial' : 'center',
              px: open ? 2 : 1.5,
              borderRadius: 1,
              backgroundColor: isActive('/settings') ? 'rgba(52, 152, 219, 0.1)' : 'transparent',
            }}
            onClick={() => handleNavigate('/settings')}
          >
            <Tooltip title={open ? '' : 'Settings'} placement="right" arrow>
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 2 : 'auto',
                  justifyContent: 'center',
                  color: isActive('/settings') ? 'primary.main' : 'text.secondary',
                }}
              >
                <SettingsIcon />
              </ListItemIcon>
            </Tooltip>
            {open && (
              <ListItemText 
                primary="Settings" 
                sx={{ 
                  opacity: 1,
                  color: isActive('/settings') ? 'primary.main' : 'text.primary',
                }}
              />
            )}
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            sx={{
              minHeight: 48,
              justifyContent: open ? 'initial' : 'center',
              px: open ? 2 : 1.5,
              borderRadius: 1,
              '&:hover': {
                backgroundColor: 'rgba(52, 152, 219, 0.05)',
              },
            }}
            onClick={handleLogout}
          >
            <Tooltip title={open ? '' : 'Logout'} placement="right" arrow>
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 2 : 'auto',
                  justifyContent: 'center',
                  color: 'text.secondary',
                }}
              >
                <LogoutIcon />
              </ListItemIcon>
            </Tooltip>
            {open && (
              <ListItemText 
                primary="Logout" 
                sx={{ 
                  opacity: 1,
                  color: 'text.primary',
                }}
              />
            )}
          </ListItemButton>
        </ListItem>
      </List>
    </Drawer>
  );
};

export default Sidebar; 
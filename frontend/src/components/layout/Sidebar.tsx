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
  useMediaQuery
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
  Facebook as FacebookIcon
} from '@mui/icons-material';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicVideoIcon from '@mui/icons-material/MusicVideo';
import { useNavigate, useLocation } from 'react-router-dom';

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

const Sidebar: React.FC<SidebarProps> = ({ open, onClose, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { logout } = useAuth();
  
  const menuItems = [
    { text: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { text: 'Track Accounts', path: '/track-accounts/folders', icon: <TrackChangesIcon /> },
    { text: 'Instagram Data', path: '/instagram-folders', icon: <InstagramIcon /> },
    { text: 'Facebook Data', path: '/facebook-folders', icon: <FacebookIcon /> },
    { text: 'LinkedIn Data', path: '/linkedin-folders', icon: <LinkedInIcon /> },
    { text: 'TikTok Data', path: '/tiktok-folders', icon: <MusicVideoIcon /> },
    { text: 'Social Analysis', path: '/social-analysis', icon: <AnalyticsIcon /> },
    { text: 'Web Presence', path: '/web-presence', icon: <LanguageIcon /> },
    { text: 'Sentiment Analysis', path: '/sentiment', icon: <MoodIcon /> },
    { text: 'Word Cloud', path: '/word-cloud', icon: <CloudQueueIcon /> },
    { text: 'NPS Reports', path: '/nps', icon: <AssessmentIcon /> },
    { text: 'Report Folders', path: '/report-folders', icon: <DescriptionIcon /> },
    { text: 'Settings', path: '/settings', icon: <SettingsIcon /> },
  ];

  // Function to check if a menu item is active based on the current path - memoized for performance
  const isActive = useCallback((itemPath: string) => {
    // Special handling for root path
    if (itemPath === '/') {
      return location.pathname === '/';
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

  const handleNavigate = useCallback((path: string) => {
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
          <CloudQueueIcon sx={{ color: 'primary.main', mr: open ? 1 : 0 }} />
          {open && (
            <Typography variant="h6" color="primary.main" fontWeight="bold">
              Track Futura
            </Typography>
          )}
        </Box>
        <IconButton onClick={onToggle}>
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </DrawerHeader>
      <Divider />
      <List sx={{ px: 0.5 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ display: 'block', mb: 0.5 }}>
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
        ))}
      </List>
      <Divider />
      <List sx={{ mt: 'auto', px: 0.5 }}>
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
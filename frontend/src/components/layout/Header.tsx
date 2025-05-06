import React, { useState } from 'react';
import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Typography,
  InputBase,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Tooltip,
  Button,
  useMediaQuery,
} from '@mui/material';
import { styled, alpha, useTheme } from '@mui/material/styles';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  AccountCircle,
  KeyboardArrowDown,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import GELogo from '../../assets/images/logos/GE-logo.png';
import GELogoFallback from './GELogoFallback';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  border: '1px solid #E0E0E0',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: '#9E9E9E',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: theme.palette.text.primary,
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    // vertical padding + font size from searchIcon
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '40ch',
    },
    [theme.breakpoints.between('sm', 'md')]: {
      width: '20ch',
    },
  },
}));

interface HeaderProps {
  open: boolean;
  onToggle: () => void;
}

const Header: React.FC<HeaderProps> = ({ open, onToggle }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isSmall = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationsAnchorEl, setNotificationsAnchorEl] = useState<null | HTMLElement>(null);
  const [mobileMenuAnchorEl, setMobileMenuAnchorEl] = useState<null | HTMLElement>(null);
  
  const isMenuOpen = Boolean(anchorEl);
  const isNotificationsOpen = Boolean(notificationsAnchorEl);
  const isMobileMenuOpen = Boolean(mobileMenuAnchorEl);

  // State to track if the image failed to load
  const [imageError, setImageError] = useState(false);
  
  // Handle image load error
  const handleImageError = () => {
    setImageError(true);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMobileMenuAnchorEl(null);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchorEl(null);
  };

  const handleMobileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMobileMenuAnchorEl(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuAnchorEl(null);
  };

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
    >
      <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
      <MenuItem onClick={handleMenuClose}>My account</MenuItem>
      <MenuItem onClick={handleMenuClose}>Sign out</MenuItem>
    </Menu>
  );

  const notificationsId = 'primary-notifications-menu';
  const renderNotifications = (
    <Menu
      anchorEl={notificationsAnchorEl}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      id={notificationsId}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isNotificationsOpen}
      onClose={handleNotificationsClose}
    >
      <MenuItem onClick={handleNotificationsClose}>
        <Box>
          <Typography variant="subtitle2">New Analysis Complete</Typography>
          <Typography variant="body2" color="text.secondary">Your social media analysis is ready</Typography>
        </Box>
      </MenuItem>
      <MenuItem onClick={handleNotificationsClose}>
        <Box>
          <Typography variant="subtitle2">Weekly Report</Typography>
          <Typography variant="body2" color="text.secondary">Your weekly sentiment report is available</Typography>
        </Box>
      </MenuItem>
    </Menu>
  );

  const mobileMenuId = 'primary-menu-mobile';
  const renderMobileMenu = (
    <Menu
      anchorEl={mobileMenuAnchorEl}
      anchorOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      id={mobileMenuId}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isMobileMenuOpen}
      onClose={handleMobileMenuClose}
    >
      <MenuItem onClick={(e) => { handleMobileMenuClose(); handleNotificationsOpen(e); }}>
        <IconButton
          size="large"
          aria-label="show new notifications"
          color="inherit"
        >
          <Badge badgeContent={2} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <Typography variant="body1" sx={{ ml: 1 }}>Notifications</Typography>
      </MenuItem>
      <MenuItem onClick={(e) => { handleMobileMenuClose(); handleProfileMenuOpen(e); }}>
        <IconButton
          size="large"
          aria-label="account of current user"
          color="inherit"
        >
          <Avatar sx={{ width: 32, height: 32, backgroundColor: 'primary.main' }}>JD</Avatar>
        </IconButton>
        <Typography variant="body1" sx={{ ml: 1 }}>Profile</Typography>
      </MenuItem>
    </Menu>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          backgroundColor: 'background.paper',
          color: 'text.primary',
          boxShadow: '0px 1px 5px rgba(0, 0, 0, 0.05)',
          backdropFilter: 'blur(8px)',
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="open drawer"
            sx={{ mr: 1 }}
            onClick={onToggle}
          >
            <MenuIcon />
          </IconButton>
          
          <Box
            sx={{
              display: { xs: 'none', sm: 'flex' },
              alignItems: 'center',
              mr: 2
            }}
          >
            {!imageError ? (
              <img 
                src={GELogo} 
                alt="Great Eastern Logo" 
                style={{ 
                  height: '36px',
                  marginRight: '8px'
                }} 
                onError={handleImageError}
              />
            ) : (
              <GELogoFallback />
            )}
          </Box>
          
          {!isSmall && (
            <Box sx={{ display: 'flex', flexGrow: { xs: 1, md: 0 } }}>
              <Search>
                <SearchIconWrapper>
                  <SearchIcon />
                </SearchIconWrapper>
                <StyledInputBase
                  placeholder={isMobile ? "Search..." : "Search topics, hashtags, websites…"}
                  inputProps={{ 'aria-label': 'search' }}
                />
              </Search>
            </Box>
          )}
          
          <Box sx={{ flexGrow: 1 }} />
          
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center' }}>
            <IconButton
              size="large"
              aria-label="show new notifications"
              aria-controls={notificationsId}
              aria-haspopup="true"
              onClick={handleNotificationsOpen}
              color="inherit"
            >
              <Badge badgeContent={2} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                ml: 2,
                cursor: 'pointer',
                borderRadius: 2,
                padding: '4px 8px',
                '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
              }}
              onClick={handleProfileMenuOpen}
            >
              <Avatar 
                sx={{ 
                  width: 32, 
                  height: 32,
                  backgroundColor: 'primary.main' 
                }}
              >
                JD
              </Avatar>
              <Box sx={{ ml: 1, display: { xs: 'none', sm: 'block' } }}>
                <Typography variant="subtitle2" sx={{ lineHeight: 1 }}>John Doe</Typography>
                <Typography variant="caption" color="text.secondary">Administrator</Typography>
              </Box>
              <KeyboardArrowDown sx={{ ml: 0.5, fontSize: 20, color: 'text.secondary' }} />
            </Box>
          </Box>

          <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
            <IconButton
              size="large"
              aria-label="show more"
              aria-controls={mobileMenuId}
              aria-haspopup="true"
              onClick={handleMobileMenuOpen}
              color="inherit"
            >
              <MoreIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      {renderMobileMenu}
      {renderMenu}
      {renderNotifications}
    </Box>
  );
};

export default Header; 
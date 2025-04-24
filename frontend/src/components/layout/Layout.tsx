import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import { Box, CssBaseline } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

const drawerWidth = 240;
const miniDrawerWidth = 65;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' && prop !== 'isMobile' })<{
  open?: boolean;
  isMobile?: boolean;
}>(({ theme, open, isMobile }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(isMobile && {
    marginLeft: 0,
    width: '100%',
    padding: theme.spacing(2),
  }),
  ...(!isMobile && {
    marginLeft: 0,
    width: `calc(100% - ${open ? drawerWidth : miniDrawerWidth}px)`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isLarge = useMediaQuery(theme.breakpoints.up('lg'));
  const [open, setOpen] = useState(isLarge);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const toggleDrawer = () => {
    setOpen(!open);
  };

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        minHeight: '100vh', 
        bgcolor: 'background.default', 
        overflow: 'hidden',
        position: 'relative'
      }}
    >
      <CssBaseline />
      <Header open={open} onToggle={toggleDrawer} />
      <Sidebar open={open} onClose={handleDrawerClose} onToggle={toggleDrawer} />
      <Main open={open} isMobile={isMobile}>
        <DrawerHeader />
        <Box
          sx={{
            borderRadius: 2,
            p: { xs: 1.5, sm: 2, md: 3 },
            height: 'calc(100% - 64px)',
            overflow: 'auto',
          }}
        >
          {children}
        </Box>
      </Main>
    </Box>
  );
};

export default Layout; 
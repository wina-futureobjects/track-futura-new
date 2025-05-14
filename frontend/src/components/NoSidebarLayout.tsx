import React from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Header from './layout/Header';

interface NoSidebarLayoutProps {
  children: React.ReactNode;
}

const NoSidebarLayout: React.FC<NoSidebarLayoutProps> = ({ children }) => {
  const theme = useTheme();
  
  // Define a dummy toggle handler since we don't have a sidebar to toggle
  const handleToggle = () => {
    // No-op since there's no sidebar
  };
  
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        width: '100%', 
        minHeight: '100vh',
        background: '#f5f5f5',
        flexDirection: 'column'
      }}
    >
      {/* Use the shared Header component */}
      <Header open={false} onToggle={handleToggle} />
      
      <Box
        component="main"
        sx={{ 
          flexGrow: 1,
          width: '100%',
          position: 'relative',
          marginTop: '64px', // Ensure content is below the fixed header
          padding: theme.spacing(3),
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default NoSidebarLayout; 
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Breadcrumbs,
  Link,
  Paper
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import TrackAccountForm from '../components/track-accounts/TrackAccountForm';

const TrackAccountCreate = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Create Track Account
        </Typography>
        
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link 
            underline="hover" 
            color="inherit" 
            sx={{ display: 'flex', alignItems: 'center' }}
            onClick={() => navigate('/')}
          >
            <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Home
          </Link>
          <Link
            underline="hover"
            color="inherit"
            sx={{ display: 'flex', alignItems: 'center' }}
            onClick={() => navigate('/track-accounts/accounts')}
          >
            <TrackChangesIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Input Collection
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
            <PersonAddIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Create Account
          </Typography>
        </Breadcrumbs>
      </Box>
      
      <TrackAccountForm />
    </Container>
  );
};

export default TrackAccountCreate; 
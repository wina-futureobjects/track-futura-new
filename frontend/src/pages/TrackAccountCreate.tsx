import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
import TrackSourceForm from '../components/track-accounts/TrackSourceForm';

const TrackAccountCreate = () => {
  const navigate = useNavigate();
  const { organizationId, projectId } = useParams<{ 
    organizationId?: string;
    projectId?: string;
  }>();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Create Track Source
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
          {organizationId && (
            <Link
              underline="hover"
              color="inherit"
              sx={{ display: 'flex', alignItems: 'center' }}
              onClick={() => navigate(`/organizations/${organizationId}/projects`)}
            >
              Organization {organizationId}
            </Link>
          )}
          {projectId && (
            <Link
              underline="hover"
              color="inherit"
              sx={{ display: 'flex', alignItems: 'center' }}
              onClick={() => navigate(`/organizations/${organizationId}/projects/${projectId}`)}
            >
              Project {projectId}
            </Link>
          )}
          <Link
            underline="hover"
            color="inherit"
            sx={{ display: 'flex', alignItems: 'center' }}
            onClick={() => {
              if (organizationId && projectId) {
                navigate(`/organizations/${organizationId}/projects/${projectId}/source-tracking/sources`);
              } else {
                navigate('/');
              }
            }}
          >
            <TrackChangesIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Source Tracking
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
            <PersonAddIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Create Source
          </Typography>
        </Breadcrumbs>
      </Box>
      
      <TrackSourceForm 
        organizationId={organizationId} 
        projectId={projectId}
      />
    </Container>
  );
};

export default TrackAccountCreate; 
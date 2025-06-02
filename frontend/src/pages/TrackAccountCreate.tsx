import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper
} from '@mui/material';
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
      </Box>
      
      <TrackSourceForm 
        organizationId={organizationId} 
        projectId={projectId}
      />
    </Container>
  );
};

export default TrackAccountCreate; 
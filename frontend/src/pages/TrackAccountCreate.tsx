import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper
} from '@mui/material';
import BulkSourceCreate from '../components/track-accounts/BulkSourceCreate';

const TrackAccountCreate = () => {
  const navigate = useNavigate();
  const { organizationId, projectId } = useParams<{ 
    organizationId?: string;
    projectId?: string;
  }>();

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <BulkSourceCreate 
        organizationId={organizationId} 
        projectId={projectId}
        onSuccess={() => {
          // Navigate back to the sources list after successful creation
          if (organizationId && projectId) {
            navigate(`/organizations/${organizationId}/projects/${projectId}/source-tracking/sources`);
          } else {
            navigate('/');
          }
        }}
      />
    </Container>
  );
};

export default TrackAccountCreate; 
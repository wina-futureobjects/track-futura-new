import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Breadcrumbs,
  Link,
  Paper
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import TrackAccountForm from '../components/track-accounts/TrackAccountForm';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  account_count: number;
  created_at: string;
  updated_at: string;
}

const TrackAccountCreate = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  const [currentFolder, setCurrentFolder] = useState<Folder | null>(null);

  // Fetch folder details if folderId is present
  useState(() => {
    if (folderId) {
      fetch(`/api/track-accounts/folders/${folderId}/`)
        .then(response => {
          if (response.ok) return response.json();
          throw new Error('Failed to load folder');
        })
        .then(data => {
          setCurrentFolder(data);
        })
        .catch(error => {
          console.error('Error loading folder:', error);
        });
    }
  });

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
            onClick={() => navigate('/track-accounts/folders')}
          >
            <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Track Account Folders
          </Link>
          {currentFolder && (
            <Link
              underline="hover"
              color="inherit"
              sx={{ display: 'flex', alignItems: 'center' }}
              onClick={() => navigate(`/track-accounts/folders/${folderId}`)}
            >
              {currentFolder.name}
            </Link>
          )}
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
            <PersonAddIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Create Account
          </Typography>
        </Breadcrumbs>
      </Box>
      
      <TrackAccountForm folderId={folderId} />
    </Container>
  );
};

export default TrackAccountCreate; 
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Breadcrumbs,
  Link,
  Paper,
  CircularProgress
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import EditIcon from '@mui/icons-material/Edit';
import TrackAccountForm from '../components/track-accounts/TrackAccountForm';

interface TrackAccount {
  id: number;
  name: string;
  folder: number | null;
}

interface Folder {
  id: number;
  name: string;
  description: string | null;
  account_count: number;
  created_at: string;
  updated_at: string;
}

const TrackAccountEdit = () => {
  const { accountId } = useParams();
  const navigate = useNavigate();
  const [account, setAccount] = useState<TrackAccount | null>(null);
  const [folder, setFolder] = useState<Folder | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch account and folder data
  useEffect(() => {
    if (!accountId) return;
    
    setLoading(true);
    
    // Fetch account data
    fetch(`/api/track-accounts/accounts/${accountId}/`)
      .then(response => {
        if (!response.ok) throw new Error('Failed to load account');
        return response.json();
      })
      .then(accountData => {
        setAccount(accountData);
        
        // If the account belongs to a folder, fetch folder details
        if (accountData.folder) {
          return fetch(`/api/track-accounts/folders/${accountData.folder}/`)
            .then(response => {
              if (!response.ok) throw new Error('Failed to load folder details');
              return response.json();
            })
            .then(folderData => {
              setFolder(folderData);
            });
        }
      })
      .catch(err => {
        console.error('Error loading data:', err);
        setError('Failed to load account data. Please try again.');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [accountId]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !accountId) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h5" color="error" align="center">
          {error || 'Account ID is missing'}
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Edit Track Account
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
          {folder && (
            <Link
              underline="hover"
              color="inherit"
              sx={{ display: 'flex', alignItems: 'center' }}
              onClick={() => navigate(`/track-accounts/folders/${folder.id}`)}
            >
              {folder.name}
            </Link>
          )}
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
            <EditIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Edit {account?.name || 'Account'}
          </Typography>
        </Breadcrumbs>
      </Box>
      
      <TrackAccountForm accountId={accountId} />
    </Container>
  );
};

export default TrackAccountEdit; 
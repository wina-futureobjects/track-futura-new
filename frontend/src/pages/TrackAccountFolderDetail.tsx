import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Breadcrumbs,
  Link,
  Snackbar,
  Alert,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import AssessmentIcon from '@mui/icons-material/Assessment';
import AddIcon from '@mui/icons-material/Add';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

interface Folder {
  id: number;
  name: string;
  description: string | null;
  account_count: number;
  created_at: string;
  updated_at: string;
}

interface Account {
  id: number;
  name: string;
  iac_no: string;
  facebook_username: string | null;
  instagram_username: string | null;
  linkedin_username: string | null;
  tiktok_username: string | null;
  risk_classification: string | null;
  close_monitoring: boolean;
  created_at: string;
}

const TrackAccountFolderDetail = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  const [folder, setFolder] = useState<Folder | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  useEffect(() => {
    if (folderId) {
      fetchFolderDetails();
    }
  }, [folderId]);

  const fetchFolderDetails = async () => {
    try {
      setLoading(true);
      
      // Fetch folder details
      const folderResponse = await api.get(`/api/track-accounts/folders/${folderId}/`);
      if (folderResponse.status === 200) {
        setFolder(folderResponse.data);
      }
      
      // Fetch accounts in the folder
      const accountsResponse = await api.get(`/api/track-accounts/accounts/?folder_id=${folderId}`);
      if (accountsResponse.status === 200) {
        setAccounts(accountsResponse.data.results || []);
      }
    } catch (error) {
      console.error('Error fetching folder details:', error);
      showSnackbar('Failed to load folder details', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleBackToFolders = () => {
    navigate('/track-accounts/folders');
  };

  const handleGenerateReport = () => {
    navigate(`/report-folders/generate?folder_id=${folderId}`);
  };

  // Calculate displayed rows based on pagination
  const displayedAccounts = accounts.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center' }}
          color="inherit"
          href="/"
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Home
        </Link>
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center' }}
          color="inherit"
          onClick={handleBackToFolders}
          style={{ cursor: 'pointer' }}
        >
          <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Track Account Folders
        </Link>
        {folder && (
          <Typography
            sx={{ display: 'flex', alignItems: 'center' }}
            color="text.primary"
          >
            <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            {folder.name}
          </Typography>
        )}
      </Breadcrumbs>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : folder ? (
        <>
          {/* Folder Header */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <Box>
                <Typography variant="h5" gutterBottom>
                  {folder.name}
                </Typography>
                {folder.description && (
                  <Typography variant="body1" color="text.secondary" paragraph>
                    {folder.description}
                  </Typography>
                )}
                <Chip 
                  label={`${folder.account_count} accounts`} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                />
              </Box>
              <Box>
                <Button
                  variant="outlined"
                  startIcon={<ArrowBackIcon />}
                  onClick={handleBackToFolders}
                  sx={{ mr: 1 }}
                >
                  Back
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AssessmentIcon />}
                  onClick={handleGenerateReport}
                >
                  Generate Report
                </Button>
              </Box>
            </Box>
          </Paper>

          {/* List of accounts */}
          <Paper sx={{ width: '100%', mb: 2 }}>
            <Box sx={{ p: 2, borderBottom: '1px solid rgba(0, 0, 0, 0.12)' }}>
              <Typography variant="h6">
                Track Accounts
              </Typography>
            </Box>
            {accounts.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary" paragraph>
                  No accounts found in this folder.
                </Typography>
                <Button 
                  variant="outlined" 
                  startIcon={<AddIcon />}
                  onClick={() => navigate(`/track-accounts/folders/${folderId}/upload`)}
                >
                  Upload Accounts
                </Button>
              </Box>
            ) : (
              <>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>IAC No.</TableCell>
                        <TableCell>Instagram</TableCell>
                        <TableCell>Facebook</TableCell>
                        <TableCell>Risk Classification</TableCell>
                        <TableCell>Close Monitoring</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {displayedAccounts.map((account) => (
                        <TableRow key={account.id}>
                          <TableCell>{account.name}</TableCell>
                          <TableCell>{account.iac_no}</TableCell>
                          <TableCell>{account.instagram_username || '-'}</TableCell>
                          <TableCell>{account.facebook_username || '-'}</TableCell>
                          <TableCell>{account.risk_classification || '-'}</TableCell>
                          <TableCell>{account.close_monitoring ? 'Yes' : 'No'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <TablePagination
                  rowsPerPageOptions={[5, 10, 25]}
                  component="div"
                  count={accounts.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                />
              </>
            )}
          </Paper>
        </>
      ) : (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Folder not found or could not be loaded.
          </Typography>
          <Button
            variant="contained"
            onClick={handleBackToFolders}
          >
            Back to Folders
          </Button>
        </Paper>
      )}

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default TrackAccountFolderDetail; 
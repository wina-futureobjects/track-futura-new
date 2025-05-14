import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Grid,
  FormControlLabel,
  Switch,
  MenuItem,
  CircularProgress,
  Alert,
  Divider,
  Card,
  CardContent,
  InputAdornment,
  Avatar,
  Tooltip,
  useTheme
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicNoteIcon from '@mui/icons-material/MusicNote'; // For TikTok
import PersonIcon from '@mui/icons-material/Person';
import FolderIcon from '@mui/icons-material/Folder';
import WarningIcon from '@mui/icons-material/Warning';
import LinkIcon from '@mui/icons-material/Link';
import InfoIcon from '@mui/icons-material/Info';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import { apiFetch } from '../../utils/api';

// Types
interface TrackAccountFormProps {
  accountId?: string; // Optional - if provided, we're editing an existing account
  folderId?: string; // Optional - if provided, pre-select this folder
  organizationId?: string; // Optional - for navigation with organization context
  projectId?: string; // Optional - for navigation with project context
  onSuccess?: (account: TrackAccount) => void;
}

interface TrackAccount {
  id: number;
  name: string;
  iac_no: string;
  facebook_username: string | null;
  instagram_username: string | null;
  linkedin_username: string | null;
  tiktok_username: string | null;
  facebook_id: string | null;
  instagram_id: string | null;
  linkedin_id: string | null;
  tiktok_id: string | null;
  other_social_media: string | null;
  risk_classification: string | null;
  close_monitoring: boolean;
  posting_frequency: string | null;
  folder: number | null;
  project?: number | null;
  created_at?: string;
  updated_at?: string;
}

interface Folder {
  id: number;
  name: string;
  description: string | null;
  account_count: number;
  created_at: string;
  updated_at: string;
}

const riskClassifications = [
  'Low',
  'Medium',
  'High',
  'Critical'
];

const postingFrequencies = [
  'Low',
  'Medium',
  'High'
];

const TrackAccountForm: React.FC<TrackAccountFormProps> = ({ 
  accountId, 
  folderId, 
  organizationId,
  projectId,
  onSuccess 
}) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [loadingAccount, setLoadingAccount] = useState(!!accountId);
  const [loadingFolders, setLoadingFolders] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [folders, setFolders] = useState<Folder[]>([]);
  
  // Form state
  const [formData, setFormData] = useState<TrackAccount>({
    id: 0,
    name: '',
    iac_no: '',
    facebook_username: '',
    instagram_username: '',
    linkedin_username: '',
    tiktok_username: '',
    facebook_id: '',
    instagram_id: '',
    linkedin_id: '',
    tiktok_id: '',
    other_social_media: '',
    risk_classification: null,
    close_monitoring: false,
    posting_frequency: null,
    folder: folderId ? parseInt(folderId) : null,
  });

  // Form errors
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Load folders
  useEffect(() => {
    const fetchFolders = async () => {
      try {
        setLoadingFolders(true);
        
        // Add project filter if available
        let endpoint = '/api/track-accounts/folders/';
        if (projectId) {
          endpoint += `?project=${projectId}`;
        }
        
        const response = await apiFetch(endpoint);
        if (!response.ok) {
          throw new Error('Failed to load folders');
        }
        
        const data = await response.json();
        console.log('Fetched folder data:', data);
        
        // Ensure folders is always set as an array
        if (data && data.results && Array.isArray(data.results)) {
          // Handle paginated response
          setFolders(data.results);
        } else if (Array.isArray(data)) {
          // Handle array response
          setFolders(data);
        } else {
          console.error('Unexpected data format from API:', data);
          setFolders([]);
        }
      } catch (error) {
        console.error('Error loading folders:', error);
        setError('Failed to load folders. Please try again.');
        setFolders([]); // Reset to empty array on error
      } finally {
        setLoadingFolders(false);
      }
    };

    fetchFolders();
  }, [projectId]);

  // Load account data if editing
  useEffect(() => {
    if (accountId) {
      const fetchAccountData = async () => {
        try {
          setLoadingAccount(true);
          const response = await apiFetch(`/api/track-accounts/accounts/${accountId}/`);
          if (!response.ok) {
            throw new Error('Failed to load account data');
          }
          const data = await response.json();
          setFormData(data);
        } catch (error) {
          console.error('Error loading account:', error);
          setError('Failed to load account. Please try again.');
        } finally {
          setLoadingAccount(false);
        }
      };

      fetchAccountData();
    }
  }, [accountId]);

  // Handle form field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear the error for this field if it exists
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Handle switch change
  const handleSwitchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  // Handle select change
  const handleSelectChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? null : value
    }));
  };

  // Validate form
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!formData.iac_no.trim()) {
      errors.iac_no = 'IAC Number is required';
    }
    
    // Validate URLs if provided
    const urlFields = [
      { field: 'facebook_id', label: 'Facebook Profile URL' },
      { field: 'instagram_id', label: 'Instagram Profile URL' },
      { field: 'linkedin_id', label: 'LinkedIn Profile URL' },
      { field: 'tiktok_id', label: 'TikTok Profile URL' }
    ];
    
    urlFields.forEach(({ field, label }) => {
      const value = formData[field as keyof TrackAccount] as string;
      if (value && value.trim() !== '') {
        try {
          new URL(value);
        } catch (e) {
          errors[field] = `${label} must be a valid URL`;
        }
      }
    });

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const url = accountId 
        ? `/api/track-accounts/accounts/${accountId}/`
        : '/api/track-accounts/accounts/';
      
      const method = accountId ? 'PUT' : 'POST';
      
      // Add project ID to request body if available
      let requestData = { ...formData };
      if (projectId && !accountId) { // Only for new accounts
        requestData.project = parseInt(projectId, 10);
      }
      
      const response = await apiFetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save account');
      }
      
      const savedAccount = await response.json();
      
      setSuccess(`Account ${accountId ? 'updated' : 'created'} successfully!`);
      
      // Callback if provided
      if (onSuccess) {
        onSuccess(savedAccount);
      } else {
        // Otherwise, navigate back after a short delay
        setTimeout(() => {
          if (formData.folder) {
            if (organizationId && projectId) {
              navigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/folders/${formData.folder}`);
            } else {
              navigate(`/track-accounts/folders/${formData.folder}`);
            }
          } else {
            if (organizationId && projectId) {
              navigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/folders`);
            } else {
              navigate('/track-accounts/folders');
            }
          }
        }, 1500);
      }
    } catch (error) {
      console.error('Error saving account:', error);
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Function to navigate back based on context
  const handleCancel = () => {
    if (formData.folder) {
      if (organizationId && projectId) {
        navigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/folders/${formData.folder}`);
      } else {
        navigate(`/track-accounts/folders/${formData.folder}`);
      }
    } else {
      if (organizationId && projectId) {
        navigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/folders`);
      } else {
        navigate('/track-accounts/folders');
      }
    }
  };

  // Get color based on risk classification
  const getRiskColor = (risk: string | null) => {
    if (!risk) return theme.palette.grey[500];
    
    switch (risk.toLowerCase()) {
      case 'high':
      case 'critical':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      case 'low':
        return theme.palette.success.main;
      default:
        return theme.palette.grey[500];
    }
  };

  if (loadingAccount) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: { xs: 2, sm: 4 },
        borderRadius: 2,
        backgroundColor: theme.palette.background.default
      }}
    >
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar
          sx={{
            bgcolor: accountId ? theme.palette.primary.main : theme.palette.secondary.main,
            width: 48,
            height: 48
          }}
        >
          <PersonIcon />
        </Avatar>
        <Box>
          <Typography variant="h5" fontWeight="bold" color="primary">
            {accountId ? 'Edit Track Account' : 'Create New Track Account'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {accountId ? 'Update account details below' : 'Fill in the details to create a new account'}
          </Typography>
        </Box>
      </Box>
      
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3, borderRadius: 1.5 }}
          variant="filled"
        >
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert 
          severity="success" 
          sx={{ mb: 3, borderRadius: 1.5 }}
          variant="filled"
        >
          {success}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Account Basic Information */}
          <Grid item xs={12}>
            <Card elevation={1} sx={{ mb: 3, borderRadius: 2, overflow: 'visible' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
                  <Typography variant="h6" fontWeight="bold" color="primary">
                    Basic Information
                  </Typography>
                </Box>
                <Divider sx={{ mb: 3 }} />
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      error={!!formErrors.name}
                      helperText={formErrors.name}
                      required
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <PersonIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="IAC Number"
                      name="iac_no"
                      value={formData.iac_no}
                      onChange={handleChange}
                      error={!!formErrors.iac_no}
                      helperText={formErrors.iac_no}
                      required
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <InfoIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      select
                      label="Risk Classification"
                      name="risk_classification"
                      value={formData.risk_classification || ''}
                      onChange={handleSelectChange}
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <WarningIcon fontSize="small" color={formData.risk_classification ? 
                              (formData.risk_classification.toLowerCase() === 'high' || formData.risk_classification.toLowerCase() === 'critical' ? 'error' : 
                              formData.risk_classification.toLowerCase() === 'medium' ? 'warning' : 'success') : 'action'} 
                            />
                          </InputAdornment>
                        ),
                      }}
                    >
                      <MenuItem value="">None</MenuItem>
                      {riskClassifications.map(option => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      select
                      label="Posting Frequency"
                      name="posting_frequency"
                      value={formData.posting_frequency || ''}
                      onChange={handleSelectChange}
                      variant="outlined"
                    >
                      <MenuItem value="">None</MenuItem>
                      {postingFrequencies.map(option => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.close_monitoring}
                          onChange={handleSwitchChange}
                          name="close_monitoring"
                          color="primary"
                        />
                      }
                      label={
                        <Box component="span" sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography sx={{ mr: 1 }}>Close Monitoring</Typography>
                          <Tooltip title="Enable to actively monitor this account">
                            <InfoIcon fontSize="small" color="action" />
                          </Tooltip>
                        </Box>
                      }
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      select
                      label="Folder"
                      name="folder"
                      value={formData.folder || ''}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData(prev => ({
                          ...prev,
                          folder: value === '' ? null : Number(value)
                        }));
                      }}
                      disabled={loadingFolders}
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <FolderIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    >
                      <MenuItem value="">None</MenuItem>
                      {Array.isArray(folders) && folders.map(folder => (
                        <MenuItem key={folder.id} value={folder.id}>
                          {folder.name}
                        </MenuItem>
                      ))}
                    </TextField>
                    {loadingFolders && (
                      <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                        <CircularProgress size={16} sx={{ mr: 1 }} />
                        <Typography variant="caption" color="text.secondary">Loading folders...</Typography>
                      </Box>
                    )}
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Social Media Information */}
          <Grid item xs={12}>
            <Card elevation={1} sx={{ mb: 3, borderRadius: 2, overflow: 'visible' }}>
              <CardContent sx={{ p: 3 }}>
                {/* Social Media Usernames */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <FacebookIcon sx={{ color: '#4267B2' }} fontSize="small" />
                    <InstagramIcon sx={{ color: '#E1306C' }} fontSize="small" />
                    <LinkedInIcon sx={{ color: '#0077B5' }} fontSize="small" />
                    <MusicNoteIcon sx={{ color: '#000000' }} fontSize="small" />
                  </Box>
                  <Typography variant="h6" fontWeight="bold" color="primary" sx={{ ml: 1 }}>
                    Social Media Information
                  </Typography>
                </Box>
                <Divider sx={{ mb: 3 }} />
                
                <Typography variant="subtitle2" gutterBottom sx={{ mb: 2, fontWeight: 'bold' }}>
                  Usernames
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Facebook Username"
                      name="facebook_username"
                      value={formData.facebook_username || ''}
                      onChange={handleChange}
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <FacebookIcon fontSize="small" sx={{ color: '#4267B2' }} />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Instagram Username"
                      name="instagram_username"
                      value={formData.instagram_username || ''}
                      onChange={handleChange}
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <InstagramIcon fontSize="small" sx={{ color: '#E1306C' }} />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="LinkedIn Username"
                      name="linkedin_username"
                      value={formData.linkedin_username || ''}
                      onChange={handleChange}
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LinkedInIcon fontSize="small" sx={{ color: '#0077B5' }} />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="TikTok Username"
                      name="tiktok_username"
                      value={formData.tiktok_username || ''}
                      onChange={handleChange}
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <MusicNoteIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                </Grid>
                
                {/* Social Media Profile URLs */}
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 4, mb: 2, fontWeight: 'bold' }}>
                  Profile URLs
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Facebook Profile URL"
                      name="facebook_id"
                      value={formData.facebook_id || ''}
                      onChange={handleChange}
                      error={!!formErrors.facebook_id}
                      helperText={formErrors.facebook_id}
                      variant="outlined"
                      placeholder="https://facebook.com/username"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LinkIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Instagram Profile URL"
                      name="instagram_id"
                      value={formData.instagram_id || ''}
                      onChange={handleChange}
                      error={!!formErrors.instagram_id}
                      helperText={formErrors.instagram_id}
                      variant="outlined"
                      placeholder="https://instagram.com/username"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LinkIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="LinkedIn Profile URL"
                      name="linkedin_id"
                      value={formData.linkedin_id || ''}
                      onChange={handleChange}
                      error={!!formErrors.linkedin_id}
                      helperText={formErrors.linkedin_id}
                      variant="outlined"
                      placeholder="https://linkedin.com/in/username"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LinkIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="TikTok Profile URL"
                      name="tiktok_id"
                      value={formData.tiktok_id || ''}
                      onChange={handleChange}
                      error={!!formErrors.tiktok_id}
                      helperText={formErrors.tiktok_id}
                      variant="outlined"
                      placeholder="https://tiktok.com/@username"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LinkIcon fontSize="small" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Other Social Media"
                      name="other_social_media"
                      value={formData.other_social_media || ''}
                      onChange={handleChange}
                      placeholder="Enter details about other social media accounts"
                      variant="outlined"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Form Actions */}
          <Grid item xs={12}>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                display: 'flex',
                justifyContent: 'flex-end',
                gap: 2,
                borderRadius: 2,
                background: theme.palette.grey[50]
              }}
            >
              <Button 
                variant="outlined"
                color="secondary"
                startIcon={<CancelIcon />}
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button 
                variant="contained" 
                color="primary"
                startIcon={<SaveIcon />}
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? 
                  <CircularProgress size={24} /> : 
                  (accountId ? 'Update Account' : 'Create Account')
                }
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default TrackAccountForm;
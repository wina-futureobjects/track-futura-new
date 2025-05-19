import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  FormControlLabel,
  Switch,
  MenuItem,
  CircularProgress,
  Alert,
  Divider,
  Stack,
  InputAdornment
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicNoteIcon from '@mui/icons-material/MusicNote'; // For TikTok
import PersonIcon from '@mui/icons-material/Person';
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
  const [loading, setLoading] = useState(false);
  const [loadingAccount, setLoadingAccount] = useState(!!accountId);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
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
    project: projectId ? parseInt(projectId) : null
  });

  // Form errors
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

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
          
          const accountData = await response.json();
          setFormData({
            ...accountData,
            folder: accountData.folder || null,
            project: accountData.project || (projectId ? parseInt(projectId, 10) : null)
          });
        } catch (error) {
          console.error('Error loading account:', error);
          setError('Failed to load account data. Please try again.');
        } finally {
          setLoadingAccount(false);
        }
      };
      
      fetchAccountData();
    }
  }, [accountId, projectId]);

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
          if (organizationId && projectId) {
            navigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/accounts`);
          } else {
            navigate('/track-accounts/accounts');
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
    if (organizationId && projectId) {
      navigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/accounts`);
    } else {
      navigate('/track-accounts/accounts');
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
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom>
        {accountId ? 'Edit Track Account' : 'Create New Track Account'}
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Stack spacing={3}>
          {/* Basic Information */}
          <Box>
            <Typography variant="h6" gutterBottom>Basic Information</Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                error={!!formErrors.name}
                helperText={formErrors.name}
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
              />
              
              <TextField
                fullWidth
                label="IAC Number"
                name="iac_no"
                value={formData.iac_no}
                onChange={handleChange}
                error={!!formErrors.iac_no}
                helperText={formErrors.iac_no}
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <InfoIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
              />
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  select
                  label="Risk Classification"
                  name="risk_classification"
                  value={formData.risk_classification || ''}
                  onChange={handleSelectChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <WarningIcon fontSize="small" />
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
                
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  select
                  label="Posting Frequency"
                  name="posting_frequency"
                  value={formData.posting_frequency || ''}
                  onChange={handleSelectChange}
                >
                  <MenuItem value="">None</MenuItem>
                  {postingFrequencies.map(option => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </TextField>
              </Box>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.close_monitoring}
                    onChange={handleSwitchChange}
                    name="close_monitoring"
                    color="primary"
                  />
                }
                label="Close Monitoring"
              />
            </Stack>
          </Box>
          
          {/* Social Media Usernames */}
          <Box>
            <Typography variant="h6" gutterBottom>Social Media Usernames</Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="Facebook Username"
                  name="facebook_username"
                  value={formData.facebook_username || ''}
                  onChange={handleChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <FacebookIcon fontSize="small" sx={{ color: '#4267B2' }} />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="Instagram Username"
                  name="instagram_username"
                  value={formData.instagram_username || ''}
                  onChange={handleChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <InstagramIcon fontSize="small" sx={{ color: '#E1306C' }} />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="LinkedIn Username"
                  name="linkedin_username"
                  value={formData.linkedin_username || ''}
                  onChange={handleChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LinkedInIcon fontSize="small" sx={{ color: '#0077B5' }} />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="TikTok Username"
                  name="tiktok_username"
                  value={formData.tiktok_username || ''}
                  onChange={handleChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <MusicNoteIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
            </Stack>
          </Box>
          
          {/* Social Media Profile URLs */}
          <Box>
            <Typography variant="h6" gutterBottom>Social Media Profile URLs</Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="Facebook Profile URL"
                  name="facebook_id"
                  value={formData.facebook_id || ''}
                  onChange={handleChange}
                  error={!!formErrors.facebook_id}
                  helperText={formErrors.facebook_id}
                  placeholder="https://facebook.com/username"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LinkIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="Instagram Profile URL"
                  name="instagram_id"
                  value={formData.instagram_id || ''}
                  onChange={handleChange}
                  error={!!formErrors.instagram_id}
                  helperText={formErrors.instagram_id}
                  placeholder="https://instagram.com/username"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LinkIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="LinkedIn Profile URL"
                  name="linkedin_id"
                  value={formData.linkedin_id || ''}
                  onChange={handleChange}
                  error={!!formErrors.linkedin_id}
                  helperText={formErrors.linkedin_id}
                  placeholder="https://linkedin.com/in/username"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LinkIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="TikTok Profile URL"
                  name="tiktok_id"
                  value={formData.tiktok_id || ''}
                  onChange={handleChange}
                  error={!!formErrors.tiktok_id}
                  helperText={formErrors.tiktok_id}
                  placeholder="https://tiktok.com/@username"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LinkIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Other Social Media"
                name="other_social_media"
                value={formData.other_social_media || ''}
                onChange={handleChange}
                placeholder="Enter details about other social media accounts"
              />
            </Stack>
          </Box>
          
          {/* Form Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
            <Button 
              variant="outlined"
              color="secondary"
              startIcon={<CancelIcon />}
              onClick={handleCancel}
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              variant="contained" 
              color="primary"
              startIcon={<SaveIcon />}
              disabled={loading}
            >
              {loading ? 
                <CircularProgress size={24} /> : 
                (accountId ? 'Update Account' : 'Create Account')
              }
            </Button>
          </Box>
        </Stack>
      </form>
    </Paper>
  );
};

export default TrackAccountForm;
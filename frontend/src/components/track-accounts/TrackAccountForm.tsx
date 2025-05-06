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
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

// Types
interface TrackAccountFormProps {
  accountId?: string; // Optional - if provided, we're editing an existing account
  folderId?: string; // Optional - if provided, pre-select this folder
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

const TrackAccountForm: React.FC<TrackAccountFormProps> = ({ accountId, folderId, onSuccess }) => {
  const navigate = useNavigate();
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
        const response = await fetch('/api/track-accounts/folders/');
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
  }, []);

  // Load account data if editing
  useEffect(() => {
    if (accountId) {
      const fetchAccountData = async () => {
        try {
          setLoadingAccount(true);
          const response = await fetch(`/api/track-accounts/accounts/${accountId}/`);
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
      const method = accountId ? 'PUT' : 'POST';
      const url = accountId 
        ? `/api/track-accounts/accounts/${accountId}/` 
        : '/api/track-accounts/accounts/';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
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
            navigate(`/track-accounts/folders/${formData.folder}`);
          } else {
            navigate('/track-accounts/folders');
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

  if (loadingAccount) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h6" mb={2}>
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
        <Grid container spacing={2}>
          {/* Account Basic Information */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" fontWeight="bold">
              Basic Information
            </Typography>
            <Divider sx={{ mb: 2, mt: 0.5 }} />
          </Grid>
          
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
              label="Close Monitoring"
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
            >
              <MenuItem value="">None</MenuItem>
              {/* Make sure folders is an array before mapping */}
              {Array.isArray(folders) && folders.map(folder => (
                <MenuItem key={folder.id} value={folder.id}>
                  {folder.name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          {/* Social Media Usernames */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" fontWeight="bold" mt={2}>
              Social Media Usernames
            </Typography>
            <Divider sx={{ mb: 2, mt: 0.5 }} />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Facebook Username"
              name="facebook_username"
              value={formData.facebook_username || ''}
              onChange={handleChange}
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Instagram Username"
              name="instagram_username"
              value={formData.instagram_username || ''}
              onChange={handleChange}
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="LinkedIn Username"
              name="linkedin_username"
              value={formData.linkedin_username || ''}
              onChange={handleChange}
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="TikTok Username"
              name="tiktok_username"
              value={formData.tiktok_username || ''}
              onChange={handleChange}
            />
          </Grid>
          
          {/* Social Media Profile URLs */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" fontWeight="bold" mt={2}>
              Social Media Profile URLs
            </Typography>
            <Divider sx={{ mb: 2, mt: 0.5 }} />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Facebook Profile URL"
              name="facebook_id"
              value={formData.facebook_id || ''}
              onChange={handleChange}
              error={!!formErrors.facebook_id}
              helperText={formErrors.facebook_id}
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
            />
          </Grid>
          
          {/* Form Actions */}
          <Grid item xs={12} sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button 
              variant="outlined"
              onClick={() => {
                if (formData.folder) {
                  navigate(`/track-accounts/folders/${formData.folder}`);
                } else {
                  navigate('/track-accounts/folders');
                }
              }}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {loading ? 'Saving...' : accountId ? 'Update Account' : 'Create Account'}
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default TrackAccountForm;
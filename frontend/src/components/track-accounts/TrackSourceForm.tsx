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
interface TrackSourceFormProps {
  sourceId?: string; // Optional - if provided, we're editing an existing source
  organizationId?: string; // Optional - for navigation with organization context
  projectId?: string; // Optional - for navigation with project context
  onSuccess?: (source: TrackSource) => void;
}

interface TrackSource {
  id: number;
  name: string;
  facebook_link: string | null;
  instagram_link: string | null;
  linkedin_link: string | null;
  tiktok_link: string | null;
  other_social_media: string | null;
  project?: number | null;
  created_at?: string;
  updated_at?: string;
}

const TrackSourceForm: React.FC<TrackSourceFormProps> = ({ 
  sourceId, 
  organizationId,
  projectId,
  onSuccess 
}) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [loadingSource, setLoadingSource] = useState(!!sourceId);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Form state
  const [formData, setFormData] = useState<TrackSource>({
    id: 0,
    name: '',
    facebook_link: '',
    instagram_link: '',
    linkedin_link: '',
    tiktok_link: '',
    other_social_media: '',
    project: projectId ? parseInt(projectId) : null
  });

  // Form errors
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Load source data if editing
  useEffect(() => {
    if (sourceId) {
      const fetchSourceData = async () => {
        try {
          setLoadingSource(true);
          const response = await apiFetch(`/api/track-accounts/sources/${sourceId}/`);
          
          if (!response.ok) {
            throw new Error('Failed to load source data');
          }
          
          const sourceData = await response.json();
          setFormData({
            ...sourceData,
            project: sourceData.project || (projectId ? parseInt(projectId, 10) : null)
          });
        } catch (error) {
          console.error('Error loading source:', error);
          setError('Failed to load source data. Please try again.');
        } finally {
          setLoadingSource(false);
        }
      };
      
      fetchSourceData();
    }
  }, [sourceId, projectId]);

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
    
    // Validate URLs if provided
    const urlFields = [
      { field: 'facebook_link', label: 'Facebook Profile URL' },
      { field: 'instagram_link', label: 'Instagram Profile URL' },
      { field: 'linkedin_link', label: 'LinkedIn Profile URL' },
      { field: 'tiktok_link', label: 'TikTok Profile URL' }
    ];
    
    urlFields.forEach(({ field, label }) => {
      const value = formData[field as keyof TrackSource] as string;
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
      const url = sourceId 
        ? `/api/track-accounts/sources/${sourceId}/`
        : '/api/track-accounts/sources/';
      
      const method = sourceId ? 'PUT' : 'POST';
      
      // Add project ID to request body if available
      let requestData = { ...formData };
      
      // Ensure project ID is set if available from props
      if (projectId) {
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
        
        // Handle field-specific validation errors
        if (errorData && typeof errorData === 'object' && !errorData.detail) {
          // This is likely a validation error with field-specific messages
          const newFormErrors: Record<string, string> = {};
          let hasFieldErrors = false;
          
          // Extract field-specific errors
          Object.keys(errorData).forEach(field => {
            const fieldError = errorData[field];
            
            // Handle both array format ["error message"] and string format "error message"
            if (Array.isArray(fieldError) && fieldError.length > 0) {
              newFormErrors[field] = fieldError[0]; // Take the first error for arrays
              hasFieldErrors = true;
            } else if (typeof fieldError === 'string' && fieldError.trim() !== '') {
              newFormErrors[field] = fieldError; // Use string directly
              hasFieldErrors = true;
            }
          });
          
          if (hasFieldErrors) {
            setFormErrors(newFormErrors);
            setError('Please correct the errors below.');
            return;
          }
        }
        
        // Handle general error messages
        throw new Error(errorData.detail || errorData.message || 'Failed to save source');
      }
      
      const savedSource = await response.json();
      
      setSuccess(`Source ${sourceId ? 'updated' : 'created'} successfully!`);
      
      // Callback if provided
      if (onSuccess) {
        onSuccess(savedSource);
      } else {
        // Otherwise, navigate back after a short delay
        setTimeout(() => {
          if (organizationId && projectId) {
            navigate(`/organizations/${organizationId}/projects/${projectId}/source-tracking/sources`);
          } else {
            // If no organization/project context, navigate to home
            navigate('/');
          }
        }, 1500);
      }
    } catch (error) {
      console.error('Error saving source:', error);
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Function to navigate back based on context
  const handleCancel = () => {
    if (organizationId && projectId) {
      navigate(`/organizations/${organizationId}/projects/${projectId}/source-tracking/sources`);
    } else {
      // If no organization/project context, navigate to home
      navigate('/');
    }
  };

  if (loadingSource) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom>
        {sourceId ? 'Edit Track Source' : 'Create New Track Source'}
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
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  sx={{ flex: 1, minWidth: 200 }}
                  label="Facebook Link"
                  name="facebook_link"
                  value={formData.facebook_link || ''}
                  onChange={handleChange}
                  error={!!formErrors.facebook_link}
                  helperText={formErrors.facebook_link}
                  placeholder="https://facebook.com/username"
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
                  label="Instagram Link"
                  name="instagram_link"
                  value={formData.instagram_link || ''}
                  onChange={handleChange}
                  error={!!formErrors.instagram_link}
                  helperText={formErrors.instagram_link}
                  placeholder="https://instagram.com/username"
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
                  label="LinkedIn Link"
                  name="linkedin_link"
                  value={formData.linkedin_link || ''}
                  onChange={handleChange}
                  error={!!formErrors.linkedin_link}
                  helperText={formErrors.linkedin_link}
                  placeholder="https://linkedin.com/in/username"
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
                  label="TikTok Link"
                  name="tiktok_link"
                  value={formData.tiktok_link || ''}
                  onChange={handleChange}
                  error={!!formErrors.tiktok_link}
                  helperText={formErrors.tiktok_link}
                  placeholder="https://tiktok.com/@username"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <MusicNoteIcon fontSize="small" />
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
                (sourceId ? 'Update Source' : 'Create Source')
              }
            </Button>
          </Box>
        </Stack>
      </form>
    </Paper>
  );
};

export default TrackSourceForm;
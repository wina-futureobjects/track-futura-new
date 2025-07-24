import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Divider,
  Stack,
  InputAdornment,
  Tooltip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicNoteIcon from '@mui/icons-material/MusicNote'; // For TikTok
import PersonIcon from '@mui/icons-material/Person';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import AddIcon from '@mui/icons-material/Add';
import { apiFetch } from '../../utils/api';

// Validation functions
const validateFacebookLink = (link: string): boolean => {
  if (!link.trim()) return true; // Empty is valid
  const facebookRegex = /^(https?:\/\/)?(www\.)?(facebook\.com|fb\.com)\/.+/i;
  return facebookRegex.test(link);
};

const validateInstagramLink = (link: string): boolean => {
  if (!link.trim()) return true; // Empty is valid
  const instagramRegex = /^(https?:\/\/)?(www\.)?(instagram\.com|instagr\.am)\/.+/i;
  return instagramRegex.test(link);
};

const validateLinkedInLink = (link: string): boolean => {
  if (!link.trim()) return true; // Empty is valid
  const linkedinRegex = /^(https?:\/\/)?(www\.)?(linkedin\.com)\/(in|company)\/.+/i;
  return linkedinRegex.test(link);
};

const validateTikTokLink = (link: string): boolean => {
  if (!link.trim()) return true; // Empty is valid
  const tiktokRegex = /^(https?:\/\/)?(www\.)?(tiktok\.com)\/@.+/i;
  return tiktokRegex.test(link);
};

const getValidationMessage = (platform: string, link: string): string => {
  if (!link.trim()) return '';
  
  let isValid = false;
  switch (platform) {
    case 'facebook':
      isValid = validateFacebookLink(link);
      break;
    case 'instagram':
      isValid = validateInstagramLink(link);
      break;
    case 'linkedin':
      isValid = validateLinkedInLink(link);
      break;
    case 'tiktok':
      isValid = validateTikTokLink(link);
      break;
    default:
      isValid = true;
  }
  
  return isValid ? '' : 'Please enter a valid social media URL.';
};

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
          const response = await apiFetch(`/track-accounts/sources/${sourceId}/`);
          
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



  // Validate form
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }
    
    // Validate social media links using our custom validation functions
    if (formData.facebook_link && !validateFacebookLink(formData.facebook_link)) {
      errors.facebook_link = getValidationMessage('facebook', formData.facebook_link);
    }
    
    if (formData.instagram_link && !validateInstagramLink(formData.instagram_link)) {
      errors.instagram_link = getValidationMessage('instagram', formData.instagram_link);
    }
    
    if (formData.linkedin_link && !validateLinkedInLink(formData.linkedin_link)) {
      errors.linkedin_link = getValidationMessage('linkedin', formData.linkedin_link);
    }
    
    if (formData.tiktok_link && !validateTikTokLink(formData.tiktok_link)) {
      errors.tiktok_link = getValidationMessage('tiktok', formData.tiktok_link);
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Check if there are any validation errors
  const hasValidationErrors = (): boolean => {
    if (!formData.name.trim()) return true;
    
    if (formData.facebook_link && !validateFacebookLink(formData.facebook_link)) return true;
    if (formData.instagram_link && !validateInstagramLink(formData.instagram_link)) return true;
    if (formData.linkedin_link && !validateLinkedInLink(formData.linkedin_link)) return true;
    if (formData.tiktok_link && !validateTikTokLink(formData.tiktok_link)) return true;
    
    return false;
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
        ? `/track-accounts/sources/${sourceId}/`
        : '/track-accounts/sources/';
      
      const method = sourceId ? 'PUT' : 'POST';
      
      // Add project ID to request body if available
      const requestData = { 
        ...formData,
        project: projectId ? parseInt(projectId, 10) : formData.project
      };
      
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
                sx={{
                  '& .MuiFormHelperText-root': {
                    color: formErrors.name ? '#d32f2f !important' : 'inherit'
                  },
                  '& .MuiOutlinedInput-root': {
                    '&.Mui-error': {
                      '& fieldset': {
                        borderColor: '#d32f2f !important'
                      }
                    },
                    '&:not(.Mui-error)': {
                      '& fieldset': {
                        borderColor: '#d0d7de !important'
                      }
                    }
                  }
                }}
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
                  sx={{ 
                    flex: 1, 
                    minWidth: 200,
                    '& .MuiFormHelperText-root': {
                      color: (formData.facebook_link && !validateFacebookLink(formData.facebook_link)) ? '#d32f2f !important' : 'inherit'
                    },
                    '& .MuiOutlinedInput-root': {
                      '&.Mui-error': {
                        '& fieldset': {
                          borderColor: '#d32f2f !important'
                        }
                      },
                      '&:not(.Mui-error)': {
                        '& fieldset': {
                          borderColor: '#d0d7de !important'
                        }
                      }
                    }
                  }}
                  label="Facebook Link"
                  name="facebook_link"
                  value={formData.facebook_link || ''}
                  onChange={handleChange}
                  error={formData.facebook_link ? !validateFacebookLink(formData.facebook_link) : false}
                  helperText={getValidationMessage('facebook', formData.facebook_link || '')}
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
                  sx={{ 
                    flex: 1, 
                    minWidth: 200,
                    '& .MuiFormHelperText-root': {
                      color: (formData.instagram_link && !validateInstagramLink(formData.instagram_link)) ? '#d32f2f !important' : 'inherit'
                    },
                    '& .MuiOutlinedInput-root': {
                      '&.Mui-error': {
                        '& fieldset': {
                          borderColor: '#d32f2f !important'
                        }
                      },
                      '&:not(.Mui-error)': {
                        '& fieldset': {
                          borderColor: '#d0d7de !important'
                        }
                      }
                    }
                  }}
                  label="Instagram Link"
                  name="instagram_link"
                  value={formData.instagram_link || ''}
                  onChange={handleChange}
                  error={formData.instagram_link ? !validateInstagramLink(formData.instagram_link) : false}
                  helperText={getValidationMessage('instagram', formData.instagram_link || '')}
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
                  sx={{ 
                    flex: 1, 
                    minWidth: 200,
                    '& .MuiFormHelperText-root': {
                      color: (formData.linkedin_link && !validateLinkedInLink(formData.linkedin_link)) ? '#d32f2f !important' : 'inherit'
                    },
                    '& .MuiOutlinedInput-root': {
                      '&.Mui-error': {
                        '& fieldset': {
                          borderColor: '#d32f2f !important'
                        }
                      },
                      '&:not(.Mui-error)': {
                        '& fieldset': {
                          borderColor: '#d0d7de !important'
                        }
                      }
                    }
                  }}
                  label="LinkedIn Link"
                  name="linkedin_link"
                  value={formData.linkedin_link || ''}
                  onChange={handleChange}
                  error={formData.linkedin_link ? !validateLinkedInLink(formData.linkedin_link) : false}
                  helperText={getValidationMessage('linkedin', formData.linkedin_link || '')}
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
                  sx={{ 
                    flex: 1, 
                    minWidth: 200,
                    '& .MuiFormHelperText-root': {
                      color: (formData.tiktok_link && !validateTikTokLink(formData.tiktok_link)) ? '#d32f2f !important' : 'inherit'
                    },
                    '& .MuiOutlinedInput-root': {
                      '&.Mui-error': {
                        '& fieldset': {
                          borderColor: '#d32f2f !important'
                        }
                      },
                      '&:not(.Mui-error)': {
                        '& fieldset': {
                          borderColor: '#d0d7de !important'
                        }
                      }
                    }
                  }}
                  label="TikTok Link"
                  name="tiktok_link"
                  value={formData.tiktok_link || ''}
                  onChange={handleChange}
                  error={formData.tiktok_link ? !validateTikTokLink(formData.tiktok_link) : false}
                  helperText={getValidationMessage('tiktok', formData.tiktok_link || '')}
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

              {/* Add Other Sources Button */}
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={() => {
                    // TODO: Implement functionality to add other sources
                    console.log('Add Other Sources clicked - functionality to be implemented');
                  }}
                  sx={{
                    borderStyle: 'dashed',
                    borderWidth: 2,
                    py: 1.5,
                    px: 3,
                    '&:hover': {
                      borderStyle: 'dashed',
                      borderWidth: 2,
                    }
                  }}
                >
                  Add Other Sources
                </Button>
              </Box>
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
            <Tooltip 
              title={hasValidationErrors() ? "Check the link errors before saving" : ""}
              open={hasValidationErrors() ? undefined : false}
            >
              <span>
                <Button 
                  type="submit"
                  variant="contained" 
                  color="primary"
                  startIcon={<SaveIcon />}
                  disabled={loading || hasValidationErrors()}
                >
                  {loading ? 
                    <CircularProgress size={24} /> : 
                    (sourceId ? 'Update Source' : 'Create Source')
                  }
                </Button>
              </span>
            </Tooltip>
          </Box>
        </Stack>
      </form>
    </Paper>
  );
};

export default TrackSourceForm;
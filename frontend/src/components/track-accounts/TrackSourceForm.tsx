import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Stack,
  Tooltip,
  IconButton,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import MusicNoteIcon from '@mui/icons-material/MusicNote'; // For TikTok
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import HelpIcon from '@mui/icons-material/Help';
import { useTheme } from '@mui/material/styles';
import { apiFetch } from '../../utils/api';

// Service-specific validation functions
const validateServiceUrl = (service: string | null | undefined, url: string | undefined | null): boolean => {
  if (!url || !url.trim()) return true; // Empty is valid
  
  switch (service) {
    case 'linkedin_posts':
      return /^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[^/?#]+(?:\/)?(?:\?.*)?$/i.test(url);
    
    case 'tiktok_posts':
      return /^(https?:\/\/)?(www\.)?tiktok\.com\/discover\/[^/?#]+/i.test(url);
    
    case 'instagram_posts':
    case 'instagram_reels':
      return /^https?:\/\/(www\.)?instagram\.com\/([a-zA-Z0-9._]{1,30})\/?$/i.test(url);

    case 'instagram_comments':
      return /^https?:\/\/(www\.)?instagram\.com\/(p|reel|tv)\/[a-zA-Z0-9_-]{5,}\/?$/i.test(url);
    
    case 'facebook_comments':
      return /^https?:\/\/(www\.)?facebook\.com\/(?:(?:[a-zA-Z0-9.-]+\/posts\/\d+)|(?:groups\/\d+\/posts\/\d+)|(?:permalink\.php\?story_fbid=\d+&id=\d+)|(?:profile\.php\?id=\d+&[^ ]*story_fbid=\d+)|(?:share\/p\/[a-zA-Z0-9]+))\/?$/i.test(url);
    
    case 'facebook_reels_profile':
      return /^https?:\/\/(www\.)?facebook\.com\/(profile\.php\?id=\d+|[a-zA-Z0-9.-]+|groups\/[a-zA-Z0-9.-]+)\/?$/i.test(url);

    case 'facebook_pages_posts':
      return /^https?:\/\/(www\.)?facebook\.com\/(profile\.php\?id=\d+|[a-zA-Z0-9.-]+|groups\/[a-zA-Z0-9.-]+)\/?$/i.test(url);
    
    default:
      return true;
  }
};

const getServiceValidationMessage = (service: string | null | undefined, url: string | undefined | null): string => {
  if (!url || !url.trim()) return '';
  
  const isValid = validateServiceUrl(service, url);
  if (isValid) return '';
  
  switch (service) {
    case 'linkedin_posts':
      return 'Please enter a valid LinkedIn profile URL';
    
    case 'tiktok_posts':
      return 'Please enter the TikTok Discover page URL';
    
    case 'instagram_posts':
    case 'instagram_reels':
      return 'Please enter a valid Instagram profile URL';
    
    case 'instagram_comments':
      return 'Please enter a valid Instagram post URL to collect comments';
    
    case 'facebook_comments':
      return 'Please enter a valid Facebook post URL to collect comments';
    
    case 'facebook_reels_profile':
      return 'Please enter a valid Facebook profile URL';
    
    case 'facebook_pages_posts':
      return 'Please enter a valid Facebook page, group or profile URL';
    
    default:
      return 'Please enter a valid URL';
  }
};

// Helper functions for the step-by-step flow
const getServicesForPlatform = (platform: string | null | undefined) => {
  switch (platform) {
    case 'linkedin':
      return [
        { key: 'linkedin_posts', label: 'Posts' },
      ];
    case 'tiktok':
      return [
        { key: 'tiktok_posts', label: 'Posts' },
      ];
    case 'instagram':
      return [
        { key: 'instagram_posts', label: 'Posts' },
        { key: 'instagram_reels', label: 'Reels' },
        { key: 'instagram_comments', label: 'Comments' },
      ];
    case 'facebook':
      return [
        { key: 'facebook_pages_posts', label: 'Posts' },
        { key: 'facebook_reels_profile', label: 'Reels' },
        { key: 'facebook_comments', label: 'Comments' },
      ];
    default:
      return [];
  }
};

const getServiceLabel = (service: string | null | undefined) => {
  switch (service) {
    case 'linkedin_posts': return 'LinkedIn Profile';
    case 'tiktok_posts': return 'TikTok Discover';
    case 'instagram_posts': return 'Instagram Profile';
    case 'instagram_reels': return 'Instagram Profile';
    case 'instagram_comments': return 'Instagram Post';
    case 'facebook_comments': return 'Facebook Post';
    case 'facebook_reels_profile': return 'Facebook Profile';
    case 'facebook_pages_posts': return 'Facebook Page/Profile';
    default: return 'Social Media';
  }
};

const getUrlPlaceholder = (platform: string | null | undefined, service: string | null | undefined) => {
  switch (service) {
    case 'linkedin_posts': return 'https://linkedin.com/in/username';
    case 'tiktok_posts': return 'https://tiktok.com/discover/...';
    case 'instagram_posts': return 'https://instagram.com/username';
    case 'instagram_reels': return 'https://instagram.com/username/';
    case 'instagram_comments': return 'https://instagram.com/p/ABC123xyz/';
    case 'facebook_comments': return 'https://facebook.com/post-url';
    case 'facebook_reels_profile': return 'https://facebook.com/profile-username';
    case 'facebook_pages_posts': return 'https://facebook.com/page-username';
    default: return 'Enter URL...';
  }
};

const getUrlFieldForService = (service: string | null | undefined) => {
  switch (service) {
    case 'linkedin_posts':
      return 'linkedin_link';
    case 'tiktok_posts':
      return 'tiktok_link';
    case 'instagram_posts':
    case 'instagram_reels':
    case 'instagram_comments':
      return 'instagram_link';
    case 'facebook_comments':
    case 'facebook_reels_profile':
    case 'facebook_pages_posts':
      return 'facebook_link';
    default:
      return 'other_social_media';
  }
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
  selectedPlatform?: string | null;
  selectedService?: string | null;
  additionalUrls?: Array<{ id: string; url: string; service: string }>;
}

const TrackSourceForm: React.FC<TrackSourceFormProps> = ({ 
  sourceId, 
  organizationId,
  projectId,
  onSuccess 
}) => {
  const navigate = useNavigate();
  const theme = useTheme();
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
    project: projectId ? parseInt(projectId) : null,
    selectedPlatform: null,
    selectedService: null,
    additionalUrls: []
  });

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
           console.log('Loaded source data:', sourceData);
          
                     // Determine platform and service based on existing data
           let selectedPlatform = null;
           let selectedService = null;
           
           // Check which social media links exist and set the appropriate platform/service
           // Priority order: LinkedIn, TikTok, Instagram, Facebook
           if (sourceData.linkedin_link && sourceData.linkedin_link.trim()) {
             selectedPlatform = 'linkedin';
             selectedService = 'linkedin_posts';
           } else if (sourceData.tiktok_link && sourceData.tiktok_link.trim()) {
             selectedPlatform = 'tiktok';
             selectedService = 'tiktok_posts';
           } else if (sourceData.instagram_link && sourceData.instagram_link.trim()) {
             selectedPlatform = 'instagram';
             // Try to determine if it's a post URL or profile URL
             if (sourceData.instagram_link.includes('/p/') || sourceData.instagram_link.includes('/reel/') || sourceData.instagram_link.includes('/tv/')) {
               selectedService = 'instagram_comments';
             } else {
               selectedService = 'instagram_posts';
             }
           } else if (sourceData.facebook_link && sourceData.facebook_link.trim()) {
             selectedPlatform = 'facebook';
             // Try to determine if it's a post URL or profile URL
             if (sourceData.facebook_link.includes('/posts/') || sourceData.facebook_link.includes('permalink.php') || sourceData.facebook_link.includes('share/p/')) {
               selectedService = 'facebook_comments';
             } else {
               selectedService = 'facebook_pages_posts';
             }
           }
          
                     // Parse additional URLs from other_social_media field if it exists
           let additionalUrls: Array<{ id: string; url: string; service: string }> = [];
           if (sourceData.other_social_media && sourceData.other_social_media.trim()) {
             const urls = sourceData.other_social_media.split(';').map((url: string) => url.trim()).filter((url: string) => url);
             additionalUrls = urls.map((url: string) => ({
               id: `url_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
               url,
               service: selectedService || ''
             }));
           }
           
           console.log('Determined platform:', selectedPlatform, 'service:', selectedService);
           console.log('Additional URLs:', additionalUrls);
           
           setFormData({
             ...sourceData,
             project: sourceData.project || (projectId ? parseInt(projectId, 10) : null),
             selectedPlatform,
             selectedService,
             additionalUrls
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
  const handleFieldChange = (field: keyof TrackSource, value: string | null) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Generate unique ID for additional URLs
  const generateId = () => `url_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Add additional URL
  const handleAddAdditionalUrl = () => {
    const newUrl = {
      id: generateId(),
      url: '',
      service: formData.selectedService || ''
    };
    setFormData(prev => ({
      ...prev,
      additionalUrls: [...(prev.additionalUrls || []), newUrl]
    }));
  };

  // Remove additional URL
  const handleRemoveAdditionalUrl = (urlId: string) => {
    setFormData(prev => ({
      ...prev,
      additionalUrls: (prev.additionalUrls || []).filter(url => url.id !== urlId)
    }));
  };

  // Update additional URL
  const handleUpdateAdditionalUrl = (urlId: string, url: string) => {
    setFormData(prev => ({
      ...prev,
      additionalUrls: (prev.additionalUrls || []).map(additionalUrl => 
        additionalUrl.id === urlId ? { ...additionalUrl, url } : additionalUrl
      )
    }));
  };

  // Helper functions for validation
  const getCurrentUrlValue = () => {
    if (!formData.selectedService) return '';
    const field = getUrlFieldForService(formData.selectedService);
    return formData[field as keyof TrackSource] as string || '';
  };

  const hasUrlValidationError = () => {
    if (!formData.selectedService) return false;
    const field = getUrlFieldForService(formData.selectedService);
    const value = formData[field as keyof TrackSource] as string;
    if (!value) return false;
    
    return !validateServiceUrl(formData.selectedService, value);
  };

  const getUrlValidationMessage = () => {
    if (!formData.selectedService) return '';
    const field = getUrlFieldForService(formData.selectedService);
    const value = formData[field as keyof TrackSource] as string;
    if (!value) return '';
    
    return getServiceValidationMessage(formData.selectedService, value);
  };

  // Check if there are any validation errors
  const hasValidationErrors = (): boolean => {
    // Check for missing name
    if (!formData.name.trim()) return true;
    
    // Check for invalid URL if service is selected and URL is provided
    if (formData.selectedService && getCurrentUrlValue()) {
      return hasUrlValidationError();
    }
    
    return false;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check for validation errors
    if (hasValidationErrors()) {
      setError('Please correct the errors before saving.');
      return;
    }

    // Validate required fields
    if (!formData.name.trim()) {
      setError('Source name is required');
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
      
      // Prepare the main social media links
      const socialMediaLinks = {
        facebook_link: formData.facebook_link?.trim() || null,
        instagram_link: formData.instagram_link?.trim() || null,
        linkedin_link: formData.linkedin_link?.trim() || null,
        tiktok_link: formData.tiktok_link?.trim() || null,
        other_social_media: formData.other_social_media?.trim() || null,
      };

      // Add additional URLs to the appropriate field
      if (formData.additionalUrls && formData.additionalUrls.length > 0) {
        const additionalUrls = formData.additionalUrls
          .filter(url => url.url.trim())
          .map(url => url.url.trim());
        
        if (additionalUrls.length > 0) {
          const existingOther = socialMediaLinks.other_social_media;
          const combinedOther = existingOther 
            ? `${existingOther}; ${additionalUrls.join('; ')}`
            : additionalUrls.join('; ');
          socialMediaLinks.other_social_media = combinedOther;
        }
      }
      
      const requestData = { 
        name: formData.name.trim(),
        project: projectId ? parseInt(projectId, 10) : formData.project,
        ...socialMediaLinks
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
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom sx={{ fontWeight: 700, color: '#1e293b', mb: 3 }}>
        {sourceId ? 'Edit Track Source' : 'Create New Track Source'}
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Stack spacing={3}>
          {/* Step 1: Source Name */}
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#374151' }}>
              Step 1: Source Name
            </Typography>
            <TextField
              fullWidth
              label="Source Name"
              placeholder="Enter source name"
              value={formData.name}
              onChange={(e) => handleFieldChange('name', e.target.value)}
              required
              error={!formData.name.trim()}
              helperText={!formData.name.trim() ? 'Name is required' : ''}
              sx={{
                '& .MuiFormHelperText-root': {
                  color: !formData.name.trim() ? '#d32f2f !important' : 'inherit'
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
            />
          </Box>

          {/* Step 2: Platform Selection */}
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#374151' }}>
              Step 2: Select Platform
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {[
                { key: 'facebook', label: 'Facebook', icon: <FacebookIcon />, color: '#4267B2' },
                { key: 'instagram', label: 'Instagram', icon: <InstagramIcon />, color: '#E1306C' },
                { key: 'linkedin', label: 'LinkedIn', icon: <LinkedInIcon />, color: '#0077B5' },
                { key: 'tiktok', label: 'TikTok', icon: <MusicNoteIcon />, color: '#000' }
              ].map((platform) => (
                <Button
                  key={platform.key}
                  variant={formData.selectedPlatform === platform.key ? "contained" : "outlined"}
                  startIcon={platform.icon}
                  onClick={() => {
                    handleFieldChange('selectedPlatform', platform.key);
                    handleFieldChange('selectedService', null);
                  }}
                  sx={{
                    minWidth: 140,
                    height: 48,
                    textTransform: 'none',
                    fontWeight: 500,
                    ...(formData.selectedPlatform === platform.key ? {
                      bgcolor: platform.color,
                      color: 'white',
                      border: 'none',
                      '&:hover': { bgcolor: platform.color, opacity: 0.9 }
                    } : {
                      borderColor: platform.color,
                      color: platform.color,
                      '&:hover': { 
                        bgcolor: platform.color,
                        color: 'white'
                      }
                    })
                  }}
                >
                  {platform.label}
                </Button>
              ))}
            </Box>
          </Box>

          {/* Step 3: Service Selection (only show if platform is selected) */}
          {formData.selectedPlatform && (
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#374151' }}>
                Step 3: Select Service Type
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                {getServicesForPlatform(formData.selectedPlatform).map((service) => (
                  <Button
                    key={service.key}
                    variant={formData.selectedService === service.key ? "contained" : "outlined"}
                    onClick={() => {
                      handleFieldChange('selectedService', service.key);
                    }}
                    sx={{
                      minWidth: 120,
                      height: 40,
                      textTransform: 'none',
                      fontWeight: 500,
                      ...(formData.selectedService === service.key ? {
                        bgcolor: theme.palette.primary.main,
                        color: 'white',
                        '&:hover': { bgcolor: theme.palette.primary.dark }
                      } : {
                        borderColor: theme.palette.primary.main,
                        color: theme.palette.primary.main,
                        '&:hover': { 
                          bgcolor: theme.palette.primary.main,
                          color: 'white'
                        }
                      })
                    }}
                  >
                    {service.label}
                  </Button>
                ))}
              </Box>
            </Box>
          )}

          {/* Step 4: URL Input (only show if service is selected) */}
          {formData.selectedPlatform && formData.selectedService && (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#374151' }}>
                  Step 4: Enter URL
                </Typography>
                <Tooltip title="Provide actual URL instead of share/app links" arrow>
                  <IconButton size="small" sx={{ ml: 0.5, color: '#6b7280', p: 0.5 }}>
                    <HelpIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </Tooltip>
                <Box sx={{ flexGrow: 1 }} />
                <Tooltip title="Add another URL for this source" arrow>
                  <IconButton 
                    size="small" 
                    sx={{ 
                      color: '#10b981', 
                      p: 0.5,
                      bgcolor: '#ecfdf5',
                      border: '1px solid #10b981',
                      '&:hover': {
                        bgcolor: '#10b981',
                        color: 'white',
                        transform: 'scale(1.05)'
                      },
                      transition: 'all 0.2s ease-in-out'
                    }}
                    onClick={handleAddAdditionalUrl}
                  >
                    <AddIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </Tooltip>
              </Box>
              <TextField
                fullWidth
                label={`${getServiceLabel(formData.selectedService)} URL`}
                placeholder={getUrlPlaceholder(formData.selectedPlatform, formData.selectedService)}
                value={getCurrentUrlValue()}
                onChange={(e) => {
                  const value = e.target.value || null;
                  const field = getUrlFieldForService(formData.selectedService);
                  handleFieldChange(field as keyof TrackSource, value);
                }}
                error={hasUrlValidationError()}
                helperText={getUrlValidationMessage()}
                sx={{
                  '& .MuiFormHelperText-root': {
                    color: hasUrlValidationError() ? '#d32f2f !important' : 'inherit'
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
              />

              {/* Additional URL inputs */}
              {formData.additionalUrls && formData.additionalUrls.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  {formData.additionalUrls.map((additionalUrl) => (
                    <Box key={additionalUrl.id} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                      <TextField
                        fullWidth
                        size="small"
                        label={`${getServiceLabel(formData.selectedService)} URL`}
                        placeholder={getUrlPlaceholder(formData.selectedPlatform, formData.selectedService)}
                        value={additionalUrl.url}
                        onChange={(e) => handleUpdateAdditionalUrl(additionalUrl.id, e.target.value)}
                        error={additionalUrl.url ? !validateServiceUrl(formData.selectedService, additionalUrl.url) : false}
                        helperText={additionalUrl.url ? getServiceValidationMessage(formData.selectedService, additionalUrl.url) : ''}
                        sx={{
                          '& .MuiFormHelperText-root': {
                            color: (additionalUrl.url && !validateServiceUrl(formData.selectedService, additionalUrl.url)) ? '#d32f2f !important' : 'inherit'
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
                      />
                      <IconButton
                        size="small"
                        onClick={() => handleRemoveAdditionalUrl(additionalUrl.id)}
                        sx={{ 
                          ml: 1,
                          color: '#dc2626',
                          bgcolor: '#fef2f2',
                          '&:hover': {
                            bgcolor: '#dc2626',
                            color: 'white',
                            transform: 'scale(1.05)'
                          },
                          transition: 'all 0.2s ease-in-out'
                        }}
                      >
                        <DeleteIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          )}


          
          {/* Form Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
            <Button 
              variant="outlined"
              color="secondary"
              startIcon={<CancelIcon />}
              onClick={handleCancel}
            >
              Cancel
            </Button>
            <Tooltip 
              title={
                !formData.name?.trim() ? "Source name is required" :
                !formData.selectedPlatform ? "Please select a platform" :
                !formData.selectedService ? "Please select a service type" :
                hasUrlValidationError() ? "Please correct the URL errors" :
                ""
              }
              open={!formData.name?.trim() || !formData.selectedPlatform || !formData.selectedService || hasUrlValidationError() ? undefined : false}
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
                    <CircularProgress size={20} color="inherit" /> : 
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
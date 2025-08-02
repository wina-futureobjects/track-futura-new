import React, { useState, useEffect, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  IconButton,
  Alert,
  Snackbar,
  Stack,
  CircularProgress,
  Card,
  CardContent,
  Tooltip,
  MenuItem,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Publish as PublishIcon,
  Clear as ClearIcon,
  ViewList as ViewListIcon,
  Person as PersonIcon,
  Facebook as FacebookIcon,
  Instagram as InstagramIcon,
  LinkedIn as LinkedInIcon,
  MusicNote as TikTokIcon,
  Help as HelpIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { apiFetch } from '../../utils/api';

interface DraftSource {
  id: string; // Temporary ID for draft
  name: string;
  facebook_link: string | null;
  instagram_link: string | null;
  linkedin_link: string | null;
  tiktok_link: string | null;
  other_social_media: string | null;
  selectedPlatform?: string | null;
  selectedService?: string | null;
  additionalUrls?: Array<{ id: string; url: string; service: string }>;
}

// Validation functions
const validateFacebookLink = (link: string | undefined | null): boolean => {
  if (!link || !link.trim()) return true; // Empty is valid
  const facebookRegex = /^(https?:\/\/)?(www\.)?(facebook\.com|fb\.com)\/.+/i;
  return facebookRegex.test(link);
};

const validateInstagramLink = (link: string | undefined | null): boolean => {
  if (!link || !link.trim()) return true; // Empty is valid
  const instagramRegex = /^(https?:\/\/)?(www\.)?(instagram\.com|instagr\.am)\/.+/i;
  return instagramRegex.test(link);
};

const validateLinkedInLink = (link: string | undefined | null): boolean => {
  if (!link || !link.trim()) return true; // Empty is valid
  const linkedinRegex = /^(https?:\/\/)?(www\.)?(linkedin\.com)\/(in|company)\/.+/i;
  return linkedinRegex.test(link);
};

const validateTikTokLink = (link: string | undefined | null): boolean => {
  if (!link || !link.trim()) return true; // Empty is valid
  const tiktokRegex = /^(https?:\/\/)?(www\.)?(tiktok\.com)\/@.+/i;
  return tiktokRegex.test(link);
};

// Service-specific validation functions
const validateServiceUrl = (service: string | null | undefined, url: string | undefined | null): boolean => {
  if (!url || !url.trim()) return true; // Empty is valid
  
  switch (service) {
    case 'linkedin_posts':
      // LinkedIn posts: Accepts profile URLs with or without trailing slash and with optional query parameters
      return /^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[^/?#]+(?:\/)?(?:\?.*)?$/i.test(url);
    
    case 'tiktok_posts':
      // TikTok posts: URL of the TikTok Discover page with something after /discover/
      return /^(https?:\/\/)?(www\.)?tiktok\.com\/discover\/[^/?#]+/i.test(url);
    
    case 'instagram_posts':
      // Instagram posts: Accepts only valid Instagram profile URLs (1-30 chars, alphanumeric, dot, underscore)
      return /^https?:\/\/(www\.)?instagram\.com\/([a-zA-Z0-9._]{1,30})\/?$/i.test(url);

    case 'instagram_reels':
      // Instagram reels: Accepts only valid Instagram profile URLs (1-30 chars, alphanumeric, dot, underscore)
      return /^https?:\/\/(www\.)?instagram\.com\/([a-zA-Z0-9._]{1,30})\/?$/i.test(url);
    case 'instagram_comments':
      // Instagram comments: specific post URL (p, reel, or tv)
      return /^https?:\/\/(www\.)?instagram\.com\/(p|reel|tv)\/[a-zA-Z0-9_-]{5,}\/?$/i.test(url);
    
    case 'facebook_comments':
      // Facebook comments: post URL (strict match for post URLs)
      return /^https?:\/\/(www\.)?facebook\.com\/(?:(?:[a-zA-Z0-9.-]+\/posts\/\d+)|(?:groups\/\d+\/posts\/\d+)|(?:permalink\.php\?story_fbid=\d+&id=\d+)|(?:profile\.php\?id=\d+&[^ ]*story_fbid=\d+)|(?:share\/p\/[a-zA-Z0-9]+))\/?$/i.test(url);
    
    case 'facebook_reels_profile':
      // Facebook reels: profile URL, profile.php?id=, or group URL
      return /^https?:\/\/(www\.)?facebook\.com\/(profile\.php\?id=\d+|[a-zA-Z0-9.-]+|groups\/[a-zA-Z0-9.-]+)\/?$/i.test(url);

    case 'facebook_pages_posts':
      // Facebook pages posts: page, group, or open profile URL
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
      return 'Please enter a valid Instagram profile URL';
    
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



// Helper functions for the new step-by-step flow
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

interface BulkSourceCreateProps {
  organizationId?: string;
  projectId?: string;
  onSuccess?: () => void;
}

const BulkSourceCreate: React.FC<BulkSourceCreateProps> = ({
  organizationId,
  projectId,
  onSuccess
}) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [draftSources, setDraftSources] = useState<DraftSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info'
  });
  const [mode, setMode] = useState<'bulk' | 'single'>('single'); // Default to quick add mode

  // Load draft from localStorage on mount
  useEffect(() => {
    const savedDraft = localStorage.getItem(`draft_sources_${projectId}`);
    if (savedDraft) {
      try {
        const parsed = JSON.parse(savedDraft);
        setDraftSources(parsed);
      } catch (error) {
        console.error('Error loading draft:', error);
      }
    }
  }, [projectId]);

  // Auto-save draft to localStorage
  useEffect(() => {
    if (draftSources.length > 0) {
      localStorage.setItem(`draft_sources_${projectId}`, JSON.stringify(draftSources));
    }
  }, [draftSources, projectId]);

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Generate unique ID for draft entries
  const generateId = () => `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Handle CSV file upload
  const handleCsvFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      
      if (!file.name.toLowerCase().endsWith('.csv')) {
        showSnackbar('Please select a CSV file', 'error');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) {
        showSnackbar('File size must be less than 10MB', 'error');
        return;
      }
      
      setCsvFile(file);
      parseCsvFile(file);
    }
  };

  // Parse CSV file and populate table
  const parseCsvFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const csv = e.target?.result as string;
        const lines = csv.split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        
        // Validate headers
        const expectedHeaders = ['Name', 'Platform', 'Service_Type', 'URL', 'Additional_URLs'];
        const hasValidHeaders = expectedHeaders.every(h => headers.includes(h));
        
        if (!hasValidHeaders) {
          showSnackbar('CSV must have headers: Name, Platform, Service_Type, URL, Additional_URLs', 'error');
          return;
        }

        // Parse data rows
        const newSources: DraftSource[] = [];
        for (let i = 1; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line) continue;
          
          const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
          
          if (values.length >= headers.length && values[0]) { // At least name is required
            const source: DraftSource = {
              id: generateId(),
              name: values[headers.indexOf('Name')] || '',
              facebook_link: null, // Initialize all fields to null
              instagram_link: null,
              linkedin_link: null,
              tiktok_link: null,
              other_social_media: null,
              selectedPlatform: values[headers.indexOf('Platform')] || null,
              selectedService: values[headers.indexOf('Service_Type')] || null,
            };

            // Parse URLs and additional URLs
            const url = values[headers.indexOf('URL')] || null;
            if (url) {
              const field = getUrlFieldForService(source.selectedService);
              if (field === 'facebook_link') {
                source.facebook_link = url;
              } else if (field === 'instagram_link') {
                source.instagram_link = url;
              } else if (field === 'linkedin_link') {
                source.linkedin_link = url;
              } else if (field === 'tiktok_link') {
                source.tiktok_link = url;
              } else if (field === 'other_social_media') {
                source.other_social_media = url;
              }
            }

            const additionalUrls = values[headers.indexOf('Additional_URLs')] || '';
            if (additionalUrls) {
              const urls = additionalUrls.split(';').map(u => u.trim()).filter(u => u);
              source.additionalUrls = urls.map(u => ({ 
                id: generateId(), 
                url: u, 
                service: source.selectedService || '' 
              }));
            } else {
              source.additionalUrls = [];
            }

            newSources.push(source);
          }
        }

        if (newSources.length > 0) {
          setDraftSources(prev => [...prev, ...newSources]);
          showSnackbar(`Loaded ${newSources.length} sources from CSV`, 'success');
        } else {
          showSnackbar('No valid data found in CSV', 'error');
        }
        
      } catch (error) {
        console.error('Error parsing CSV:', error);
        showSnackbar('Error parsing CSV file', 'error');
      }
    };
    
    reader.readAsText(file);
  };

  // Add empty row
  const handleAddRow = () => {
    const newSource: DraftSource = {
      id: generateId(),
      name: '',
      facebook_link: null,
      instagram_link: null,
      linkedin_link: null,
      tiktok_link: null,
      other_social_media: null,
      selectedPlatform: null,
      selectedService: null,
      additionalUrls: [],
    };
    setDraftSources(prev => [...prev, newSource]);
  };

  // Delete row
  const handleDeleteRow = (id: string) => {
    setDraftSources(prev => prev.filter(source => source.id !== id));
  };

  // Add additional URL
  const handleAddAdditionalUrl = (sourceId: string) => {
    setDraftSources(prev => prev.map(source => {
      if (source.id === sourceId) {
        const newUrl = {
          id: generateId(),
          url: '',
          service: source.selectedService || ''
        };
        return {
          ...source,
          additionalUrls: [...(source.additionalUrls || []), newUrl]
        };
      }
      return source;
    }));
  };

  // Remove additional URL
  const handleRemoveAdditionalUrl = (sourceId: string, urlId: string) => {
    setDraftSources(prev => prev.map(source => {
      if (source.id === sourceId) {
        return {
          ...source,
          additionalUrls: (source.additionalUrls || []).filter(url => url.id !== urlId)
        };
      }
      return source;
    }));
  };

  // Update additional URL
  const handleUpdateAdditionalUrl = (sourceId: string, urlId: string, url: string) => {
    setDraftSources(prev => prev.map(source => {
      if (source.id === sourceId) {
        return {
          ...source,
          additionalUrls: (source.additionalUrls || []).map(additionalUrl => 
            additionalUrl.id === urlId ? { ...additionalUrl, url } : additionalUrl
          )
        };
      }
      return source;
    }));
  };

  // Update field
  const handleFieldChange = (id: string, field: keyof DraftSource, value: string | null) => {
    setDraftSources(prev => prev.map(source => {
      if (source.id === id) {
        // Convert empty strings to null for social media fields
        const processedValue = (field === 'facebook_link' || field === 'instagram_link' || 
                               field === 'linkedin_link' || field === 'tiktok_link' || 
                               field === 'other_social_media') && value === '' ? null : value;
        return { ...source, [field]: processedValue };
      }
      return source;
    }));
  };

  // Clear all draft
  const handleClearDraft = () => {
    setDraftSources([]);
    localStorage.removeItem(`draft_sources_${projectId}`);
    showSnackbar('Draft cleared', 'success');
  };

  // Save as draft
  const handleSaveDraft = () => {
    localStorage.setItem(`draft_sources_${projectId}`, JSON.stringify(draftSources));
    showSnackbar('Draft saved successfully', 'success');
  };

  // Check if there are any validation errors in bulk mode
  const hasValidationErrors = (): boolean => {
    // Check for missing names
    const hasMissingNames = draftSources.some(source => !source.name.trim());
    if (hasMissingNames) return true;
    
    // Check for invalid social media links
    const hasInvalidLinks = draftSources.some(source => 
      (source.facebook_link && !validateFacebookLink(source.facebook_link)) ||
      (source.instagram_link && !validateInstagramLink(source.instagram_link)) ||
      (source.linkedin_link && !validateLinkedInLink(source.linkedin_link)) ||
      (source.tiktok_link && !validateTikTokLink(source.tiktok_link))
    );
    
    return hasInvalidLinks;
  };

  // Create all sources
  const handleCreateSources = async () => {
    if (draftSources.length === 0) {
      showSnackbar('No sources to create', 'error');
      return;
    }

    // Check for validation errors
    if (hasValidationErrors()) {
      showSnackbar('Check the link errors before creating sources', 'error');
      return;
    }

    // Validate required fields
    const invalidSources = draftSources.filter(source => !source.name.trim());
    if (invalidSources.length > 0) {
      showSnackbar('All sources must have a name', 'error');
      return;
    }

    setLoading(true);
    try {
      let created = 0;
      let errors = 0;

      for (const source of draftSources) {
        try {
          // Prepare the main social media links
          const socialMediaLinks = {
            facebook_link: source.facebook_link?.trim() || null,
            instagram_link: source.instagram_link?.trim() || null,
            linkedin_link: source.linkedin_link?.trim() || null,
            tiktok_link: source.tiktok_link?.trim() || null,
            other_social_media: source.other_social_media?.trim() || null,
          };

          // Add additional URLs to the appropriate field
          if (source.additionalUrls && source.additionalUrls.length > 0) {
            const additionalUrls = source.additionalUrls
              .filter(url => url.url.trim())
              .map(url => url.url.trim());
            
            if (additionalUrls.length > 0) {
              // For now, we'll append additional URLs to the other_social_media field
              // This could be enhanced to store them separately in the backend
              const existingOther = socialMediaLinks.other_social_media;
              const combinedOther = existingOther 
                ? `${existingOther}; ${additionalUrls.join('; ')}`
                : additionalUrls.join('; ');
              socialMediaLinks.other_social_media = combinedOther;
            }
          }

          const response = await apiFetch('/track-accounts/sources/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              name: source.name.trim(),
              project: parseInt(projectId || '0'),
              ...socialMediaLinks,
            }),
          });

          if (response.ok) {
            created++;
          } else {
            errors++;
          }
        } catch (error) {
          console.error('Error creating source:', error);
          errors++;
        }
      }

      if (errors === 0) {
        showSnackbar(`Successfully created ${created} sources`, 'success');
        // Clear draft after successful creation
        setDraftSources([]);
        localStorage.removeItem(`draft_sources_${projectId}`);
        
        // Navigate back or call success callback
        if (onSuccess) {
          onSuccess();
        } else {
          setTimeout(() => {
            navigate(getNavigationPath('/source-tracking/sources'));
          }, 1500);
        }
      } else {
        showSnackbar(`Created ${created} sources, ${errors} failed`, 'error');
      }

    } catch (error) {
      console.error('Error creating sources:', error);
      showSnackbar('Failed to create sources', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Download template
  const handleDownloadTemplate = () => {
    const csvContent = 'Name,Platform,Service_Type,URL,Additional_URLs\n' +
                      'Example Source,linkedin,linkedin_posts,https://linkedin.com/in/example,https://linkedin.com/in/example2;https://linkedin.com/in/example3\n' +
                      'Facebook Page,facebook,facebook_pages_posts,https://facebook.com/examplepage,https://facebook.com/anotherpage\n' +
                      'Instagram Profile,instagram,instagram_posts,https://instagram.com/example,https://instagram.com/example2\n' +
                      'TikTok Discover,tiktok,tiktok_posts,https://tiktok.com/discover/example,\n' +
                      'Facebook Comments,facebook,facebook_comments,https://facebook.com/example/posts/123,\n' +
                      'Instagram Reels,instagram,instagram_reels,https://instagram.com/example,https://instagram.com/example2\n' +
                      'Instagram Comments,instagram,instagram_comments,https://instagram.com/p/ABC123xyz/,https://instagram.com/reel/DEF456uvw/';
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'track_sources_template.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    showSnackbar('Template downloaded', 'success');
  };

  // Navigation helper
  const getNavigationPath = (path: string) => {
    if (organizationId && projectId) {
      return `/organizations/${organizationId}/projects/${projectId}${path}`;
    }
    return path;
  };

  // Helper functions for the step-by-step flow
  const getCurrentUrlValue = () => {
    if (!draftSources[0]?.selectedService) return '';
    const field = getUrlFieldForService(draftSources[0].selectedService);
    return draftSources[0][field as keyof DraftSource] as string || '';
  };

  const hasUrlValidationError = () => {
    if (!draftSources[0]?.selectedService) return false;
    const field = getUrlFieldForService(draftSources[0].selectedService);
    const value = draftSources[0][field as keyof DraftSource] as string;
    if (!value) return false;
    
    return !validateServiceUrl(draftSources[0].selectedService, value);
  };

  const getUrlValidationMessage = () => {
    if (!draftSources[0]?.selectedService) return '';
    const field = getUrlFieldForService(draftSources[0].selectedService);
    const value = draftSources[0][field as keyof DraftSource] as string;
    if (!value) return '';
    
    return getServiceValidationMessage(draftSources[0].selectedService, value);
  };

  // Helper functions for bulk mode table
  const getCurrentUrlValueForSource = (source: DraftSource) => {
    if (!source.selectedService) return '';
    const field = getUrlFieldForService(source.selectedService);
    return source[field as keyof DraftSource] as string || '';
  };

  const hasUrlValidationErrorForSource = (source: DraftSource) => {
    if (!source.selectedService) return false;
    const field = getUrlFieldForService(source.selectedService);
    const value = source[field as keyof DraftSource] as string;
    if (!value) return false;
    
    return !validateServiceUrl(source.selectedService, value);
  };

  const getUrlValidationMessageForSource = (source: DraftSource) => {
    if (!source.selectedService) return '';
    const field = getUrlFieldForService(source.selectedService);
    const value = source[field as keyof DraftSource] as string;
    if (!value) return '';
    
    return getServiceValidationMessage(source.selectedService, value);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b', mb: 1 }}>
              {mode === 'bulk' ? 'Bulk Source Creation' : 'Quick Add Source'}
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748b' }}>
              {mode === 'bulk' 
                ? 'Upload CSV data or manually add multiple sources, then create them all at once'
                : 'Quickly add a single source with social media links'
              }
            </Typography>
          </Box>

          {/* Mode Toggle */}
          <Stack direction="row" spacing={1}>
            <Button
              variant={mode === 'single' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<PersonIcon />}
              onClick={() => setMode('single')}
              sx={{ minWidth: 120 }}
            >
              Quick Add
            </Button>
            <Button
              variant={mode === 'bulk' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<ViewListIcon />}
              onClick={() => setMode('bulk')}
              sx={{ minWidth: 120 }}
            >
              Bulk Mode
            </Button>
          </Stack>
        </Box>
      </Box>

      {/* Quick Single Mode */}
      {mode === 'single' && (
        <Paper sx={{ p: 4, mb: 3 }}>
          
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
                value={draftSources[0]?.name || ''}
                onChange={(e) => {
                  if (draftSources.length === 0) {
                    const newId = generateId();
                    const newSource: DraftSource = {
                      id: newId,
                      name: '',
                      facebook_link: null,
                      instagram_link: null,
                      linkedin_link: null,
                      tiktok_link: null,
                      other_social_media: null,
                      selectedPlatform: null,
                      selectedService: null,
                    };
                    setDraftSources([newSource]);
                    // Update the name immediately
                    setDraftSources([{ ...newSource, name: e.target.value }]);
                  } else {
                    handleFieldChange(draftSources[0].id, 'name', e.target.value);
                  }
                }}
                required
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
                  { key: 'tiktok', label: 'TikTok', icon: <TikTokIcon />, color: '#000' }
                ].map((platform) => (
                  <Button
                    key={platform.key}
                    variant={draftSources[0]?.selectedPlatform === platform.key ? "contained" : "outlined"}
                    startIcon={platform.icon}
                    onClick={() => {
                      if (draftSources.length === 0) {
                        const newId = generateId();
                        const newSource: DraftSource = {
                          id: newId,
                          name: '',
                          facebook_link: null,
                          instagram_link: null,
                          linkedin_link: null,
                          tiktok_link: null,
                          other_social_media: null,
                          selectedPlatform: platform.key,
                          selectedService: null,
                        };
                        setDraftSources([newSource]);
                                              } else {
                          handleFieldChange(draftSources[0].id, 'selectedPlatform' as keyof DraftSource, platform.key);
                          handleFieldChange(draftSources[0].id, 'selectedService' as keyof DraftSource, null);
                        }
                    }}
                    sx={{
                      minWidth: 140,
                      height: 48,
                      textTransform: 'none',
                      fontWeight: 500,
                      ...(draftSources[0]?.selectedPlatform === platform.key ? {
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
            {draftSources[0]?.selectedPlatform && (
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#374151' }}>
                  Step 3: Select Service Type
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  {getServicesForPlatform(draftSources[0]?.selectedPlatform).map((service) => (
                    <Button
                      key={service.key}
                      variant={draftSources[0]?.selectedService === service.key ? "contained" : "outlined"}
                      onClick={() => {
                        handleFieldChange(draftSources[0].id, 'selectedService' as keyof DraftSource, service.key);
                      }}
                      sx={{
                        minWidth: 120,
                        height: 40,
                        textTransform: 'none',
                        fontWeight: 500,
                        ...(draftSources[0]?.selectedService === service.key ? {
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
            {draftSources[0]?.selectedPlatform && draftSources[0]?.selectedService && (
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
                      onClick={() => {
                        if (draftSources[0]) {
                          handleAddAdditionalUrl(draftSources[0].id);
                        }
                      }}
                    >
                      <AddIcon sx={{ fontSize: 16 }} />
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  label={`${getServiceLabel(draftSources[0]?.selectedService)} URL`}
                  placeholder={getUrlPlaceholder(draftSources[0]?.selectedPlatform, draftSources[0]?.selectedService)}
                  value={getCurrentUrlValue() || ''}
                  onChange={(e) => {
                    const value = e.target.value || null;
                    const field = getUrlFieldForService(draftSources[0]?.selectedService);
                    handleFieldChange(draftSources[0].id, field as keyof DraftSource, value);
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
                {draftSources[0]?.additionalUrls && draftSources[0].additionalUrls.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                                          {draftSources[0].additionalUrls.map((additionalUrl) => (
                        <Box key={additionalUrl.id} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                        <TextField
                          fullWidth
                          size="small"
                          label={`${getServiceLabel(draftSources[0]?.selectedService)} URL`}
                          placeholder={getUrlPlaceholder(draftSources[0]?.selectedPlatform, draftSources[0]?.selectedService)}
                          value={additionalUrl.url}
                          onChange={(e) => handleUpdateAdditionalUrl(draftSources[0].id, additionalUrl.id, e.target.value)}
                          error={additionalUrl.url ? !validateServiceUrl(draftSources[0]?.selectedService, additionalUrl.url) : false}
                          helperText={additionalUrl.url ? getServiceValidationMessage(draftSources[0]?.selectedService, additionalUrl.url) : ''}
                          sx={{
                            '& .MuiFormHelperText-root': {
                              color: (additionalUrl.url && !validateServiceUrl(draftSources[0]?.selectedService, additionalUrl.url)) ? '#d32f2f !important' : 'inherit'
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
                          onClick={() => handleRemoveAdditionalUrl(draftSources[0].id, additionalUrl.id)}
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


            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
              <Button
                variant="outlined"
                onClick={handleClearDraft}
                disabled={draftSources.length === 0}
              >
                Clear
              </Button>
              <Tooltip 
                title={
                  !draftSources[0]?.name?.trim() ? "Source name is required" :
                  !draftSources[0]?.selectedPlatform ? "Please select a platform" :
                  !draftSources[0]?.selectedService ? "Please select a service type" :
                  ""
                }
                open={!draftSources[0]?.name?.trim() || !draftSources[0]?.selectedPlatform || !draftSources[0]?.selectedService ? undefined : false}
              >
                <span>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleCreateSources}
                    disabled={
                      loading || 
                      draftSources.length === 0 || 
                      !draftSources[0]?.name?.trim() ||
                      !draftSources[0]?.selectedPlatform ||
                      !draftSources[0]?.selectedService
                    }
                  >
                    {loading ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      'Create Source'
                    )}
                  </Button>
                </span>
              </Tooltip>
            </Box>
          </Stack>
        </Paper>
      )}

      {/* Bulk Mode */}
      {mode === 'bulk' && (
        <>
          {/* Actions */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              {/* Left side - CSV operations */}
              <Stack direction="row" spacing={2}>
                {/* CSV Upload */}
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  sx={{ minWidth: 'fit-content' }}
                >
                  Upload CSV
                  <input
                    type="file"
                    hidden
                    accept=".csv"
                    onChange={handleCsvFileChange}
                  />
                </Button>

                {/* Download Template */}
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownloadTemplate}
                >
                  Download Template
                </Button>
              </Stack>

              {/* Right side - Row management */}
              <Stack direction="row" spacing={2}>
                {/* Add Row */}
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleAddRow}
                  sx={{ 
                    fontWeight: 600,
                    boxShadow: 2,
                    bgcolor: '#10b981',
                    color: 'white',
                    '&:hover': { 
                      boxShadow: 4,
                      bgcolor: '#059669'
                    }
                  }}
                >
                  Add Row
                </Button>

                {/* Clear Draft */}
                {draftSources.length > 0 && (
                  <Button
                    variant="contained"
                    startIcon={<ClearIcon />}
                    onClick={handleClearDraft}
                    sx={{ 
                      fontWeight: 600,
                      boxShadow: 2,
                      bgcolor: '#dc2626',
                      color: 'white',
                      '&:hover': { 
                        boxShadow: 4,
                        bgcolor: '#b91c1c'
                      }
                    }}
                  >
                    Clear All
                  </Button>
                )}
              </Stack>
            </Box>

            {csvFile && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Loaded file: <strong>{csvFile.name}</strong>
              </Alert>
            )}
          </Paper>

          {/* Data Table */}
          {draftSources.length > 0 ? (
            <Paper sx={{ mb: 3 }}>
              <TableContainer sx={{ maxHeight: 600 }}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600, minWidth: 200 }}>Name *</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 120 }}>Platform</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 150 }}>Service Type</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 300 }}>URL</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 200 }}>Additional URLs</TableCell>
                      <TableCell sx={{ fontWeight: 600, width: 80 }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {draftSources.map((source) => (
                      <TableRow key={source.id}>
                        <TableCell>
                          <TextField
                            fullWidth
                            size="small"
                            value={source.name}
                            onChange={(e) => handleFieldChange(source.id, 'name', e.target.value)}
                            error={!source.name.trim()}
                            helperText={!source.name.trim() ? 'Required' : ''}
                            sx={{
                              '& .MuiFormHelperText-root': {
                                color: !source.name.trim() ? '#d32f2f !important' : 'inherit'
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
                        </TableCell>
                        <TableCell>
                          <TextField
                            select
                            fullWidth
                            size="small"
                            value={source.selectedPlatform || ''}
                            onChange={(e) => {
                              handleFieldChange(source.id, 'selectedPlatform' as keyof DraftSource, e.target.value);
                              handleFieldChange(source.id, 'selectedService' as keyof DraftSource, null);
                            }}
                            placeholder="Select platform"
                          >
                            <MenuItem value="linkedin">LinkedIn</MenuItem>
                            <MenuItem value="facebook">Facebook</MenuItem>
                            <MenuItem value="instagram">Instagram</MenuItem>
                            <MenuItem value="tiktok">TikTok</MenuItem>
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <TextField
                            select
                            fullWidth
                            size="small"
                            value={source.selectedService || ''}
                            onChange={(e) => handleFieldChange(source.id, 'selectedService' as keyof DraftSource, e.target.value)}
                            disabled={!source.selectedPlatform}
                            placeholder="Select service"
                          >
                            {source.selectedPlatform && getServicesForPlatform(source.selectedPlatform).map((service) => (
                              <MenuItem key={service.key} value={service.key}>
                                {service.label}
                              </MenuItem>
                            ))}
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <TextField
                            fullWidth
                            size="small"
                            value={getCurrentUrlValueForSource(source) || ''}
                            onChange={(e) => {
                              const value = e.target.value || null;
                              const field = getUrlFieldForService(source.selectedService);
                              handleFieldChange(source.id, field as keyof DraftSource, value);
                            }}
                            placeholder={getUrlPlaceholder(source.selectedPlatform, source.selectedService)}
                            error={hasUrlValidationErrorForSource(source)}
                            helperText={getUrlValidationMessageForSource(source)}
                            disabled={!source.selectedService}
                            sx={{
                              '& .MuiFormHelperText-root': {
                                color: hasUrlValidationErrorForSource(source) ? '#d32f2f !important' : 'inherit'
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
                        </TableCell>
                        <TableCell>
                          <Box>
                            {source.additionalUrls && source.additionalUrls.length > 0 && (
                              <Stack spacing={1}>
                                {source.additionalUrls.map((additionalUrl) => (
                                  <Box key={additionalUrl.id} sx={{ display: 'flex', alignItems: 'center' }}>
                                    <TextField
                                      size="small"
                                      value={additionalUrl.url}
                                      onChange={(e) => handleUpdateAdditionalUrl(source.id, additionalUrl.id, e.target.value)}
                                      placeholder="Additional URL"
                                      sx={{ flexGrow: 1, mr: 1 }}
                                    />
                                    <IconButton
                                      size="small"
                                      onClick={() => handleRemoveAdditionalUrl(source.id, additionalUrl.id)}
                                      sx={{ 
                                        color: '#dc2626',
                                        '&:hover': {
                                          bgcolor: '#fef2f2',
                                          transform: 'scale(1.05)'
                                        },
                                        transition: 'all 0.2s ease-in-out'
                                      }}
                                    >
                                      <CloseIcon sx={{ fontSize: 16 }} />
                                    </IconButton>
                                  </Box>
                                ))}
                              </Stack>
                            )}
                            <Button
                              size="small"
                              startIcon={<AddIcon />}
                              onClick={() => handleAddAdditionalUrl(source.id)}
                              disabled={!source.selectedService}
                              sx={{ mt: 1 }}
                            >
                              More URLs
                            </Button>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteRow(source.id)}
                            sx={{
                              color: '#dc2626',
                              '&:hover': {
                                bgcolor: '#fef2f2',
                                transform: 'scale(1.05)'
                              },
                              transition: 'all 0.2s ease-in-out'
                            }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Summary and Actions */}
              <Box sx={{ p: 3, borderTop: '1px solid #e2e8f0' }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {draftSources.length} sources ready • Auto-saved as draft
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={2}>
                    <Button
                      variant="outlined"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveDraft}
                    >
                      Save Draft
                    </Button>
                    <Tooltip 
                      title={hasValidationErrors() ? "Check the link errors before creating sources" : ""}
                      open={hasValidationErrors() ? undefined : false}
                    >
                      <span>
                        <Button
                          variant="contained"
                          startIcon={<PublishIcon />}
                          onClick={handleCreateSources}
                          disabled={loading || draftSources.length === 0 || hasValidationErrors()}
                          sx={{ minWidth: 140 }}
                        >
                          {loading ? (
                            <CircularProgress size={20} color="inherit" />
                          ) : (
                            `Create ${draftSources.length} Sources`
                          )}
                        </Button>
                      </span>
                    </Tooltip>
                  </Stack>
                </Stack>
              </Box>
            </Paper>
          ) : (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <Typography variant="h6" gutterBottom color="text.secondary">
                  No sources added yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Upload a CSV file or manually add sources to get started
                </Typography>
                <Stack direction="row" spacing={2} justifyContent="center">
                  <Button
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                    component="label"
                  >
                    Upload CSV
                    <input
                      type="file"
                      hidden
                      accept=".csv"
                      onChange={handleCsvFileChange}
                    />
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<AddIcon />}
                    onClick={handleAddRow}
                  >
                    Add Manually
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default BulkSourceCreate; 
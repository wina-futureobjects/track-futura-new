import React, { useState, useEffect, ChangeEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Stack,
  Tooltip,
  CircularProgress,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Publish as PublishIcon,
  Info as InfoIcon,
  Clear as ClearIcon,
  ViewList as ViewListIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { apiFetch } from '../../utils/api';

interface DraftSource {
  id: string; // Temporary ID for draft
  name: string;
  facebook_link: string;
  instagram_link: string;
  linkedin_link: string;
  tiktok_link: string;
  other_social_media: string;
}

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
  const [draftSources, setDraftSources] = useState<DraftSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });
  const [mode, setMode] = useState<'bulk' | 'single'>('bulk'); // New mode state

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

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
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
        const expectedHeaders = ['Name', 'FACEBOOK_LINK', 'INSTAGRAM_LINK', 'LINKEDIN_LINK', 'TIKTOK_LINK', 'OTHER_SOCIAL_MEDIA'];
        const hasValidHeaders = expectedHeaders.every(h => headers.includes(h));
        
        if (!hasValidHeaders) {
          showSnackbar('CSV must have headers: Name, FACEBOOK_LINK, INSTAGRAM_LINK, LINKEDIN_LINK, TIKTOK_LINK, OTHER_SOCIAL_MEDIA', 'error');
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
              facebook_link: values[headers.indexOf('FACEBOOK_LINK')] || '',
              instagram_link: values[headers.indexOf('INSTAGRAM_LINK')] || '',
              linkedin_link: values[headers.indexOf('LINKEDIN_LINK')] || '',
              tiktok_link: values[headers.indexOf('TIKTOK_LINK')] || '',
              other_social_media: values[headers.indexOf('OTHER_SOCIAL_MEDIA')] || '',
            };
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
      facebook_link: '',
      instagram_link: '',
      linkedin_link: '',
      tiktok_link: '',
      other_social_media: '',
    };
    setDraftSources(prev => [...prev, newSource]);
  };

  // Delete row
  const handleDeleteRow = (id: string) => {
    setDraftSources(prev => prev.filter(source => source.id !== id));
  };

  // Update field
  const handleFieldChange = (id: string, field: keyof DraftSource, value: string) => {
    setDraftSources(prev => prev.map(source => 
      source.id === id ? { ...source, [field]: value } : source
    ));
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

  // Create all sources
  const handleCreateSources = async () => {
    if (draftSources.length === 0) {
      showSnackbar('No sources to create', 'error');
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
          const response = await apiFetch('/track-accounts/sources/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              name: source.name.trim(),
              facebook_link: source.facebook_link.trim() || null,
              instagram_link: source.instagram_link.trim() || null,
              linkedin_link: source.linkedin_link.trim() || null,
              tiktok_link: source.tiktok_link.trim() || null,
              other_social_media: source.other_social_media.trim() || null,
              project: parseInt(projectId || '0'),
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
    const csvContent = 'Name,FACEBOOK_LINK,INSTAGRAM_LINK,LINKEDIN_LINK,TIKTOK_LINK,OTHER_SOCIAL_MEDIA\n' +
                      'Example Source,https://facebook.com/example,https://instagram.com/example,https://linkedin.com/in/example,https://tiktok.com/@example,Other social media info';
    
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
                : 'Quickly add a single source with all social media links'
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
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            Source Information
          </Typography>
          
          <Stack spacing={3}>
            <TextField
              fullWidth
              label="Source Name"
              placeholder="Enter source name"
              value={draftSources[0]?.name || ''}
              onChange={(e) => {
                if (draftSources.length === 0) {
                  handleAddRow();
                }
                handleFieldChange(draftSources[0]?.id || generateId(), 'name', e.target.value);
              }}
              required
            />
            
            <Stack direction="row" spacing={2}>
              <TextField
                fullWidth
                label="Facebook Link"
                placeholder="https://facebook.com/..."
                value={draftSources[0]?.facebook_link || ''}
                onChange={(e) => {
                  if (draftSources.length === 0) {
                    handleAddRow();
                  }
                  handleFieldChange(draftSources[0]?.id || generateId(), 'facebook_link', e.target.value);
                }}
              />
              <TextField
                fullWidth
                label="Instagram Link"
                placeholder="https://instagram.com/..."
                value={draftSources[0]?.instagram_link || ''}
                onChange={(e) => {
                  if (draftSources.length === 0) {
                    handleAddRow();
                  }
                  handleFieldChange(draftSources[0]?.id || generateId(), 'instagram_link', e.target.value);
                }}
              />
            </Stack>
            
            <Stack direction="row" spacing={2}>
              <TextField
                fullWidth
                label="LinkedIn Link"
                placeholder="https://linkedin.com/in/..."
                value={draftSources[0]?.linkedin_link || ''}
                onChange={(e) => {
                  if (draftSources.length === 0) {
                    handleAddRow();
                  }
                  handleFieldChange(draftSources[0]?.id || generateId(), 'linkedin_link', e.target.value);
                }}
              />
              <TextField
                fullWidth
                label="TikTok Link"
                placeholder="https://tiktok.com/@..."
                value={draftSources[0]?.tiktok_link || ''}
                onChange={(e) => {
                  if (draftSources.length === 0) {
                    handleAddRow();
                  }
                  handleFieldChange(draftSources[0]?.id || generateId(), 'tiktok_link', e.target.value);
                }}
              />
            </Stack>
            
            <TextField
              fullWidth
              label="Other Social Media"
              placeholder="Other social media information..."
              multiline
              rows={2}
              value={draftSources[0]?.other_social_media || ''}
              onChange={(e) => {
                if (draftSources.length === 0) {
                  handleAddRow();
                }
                handleFieldChange(draftSources[0]?.id || generateId(), 'other_social_media', e.target.value);
              }}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
              <Button
                variant="outlined"
                onClick={handleClearDraft}
                disabled={draftSources.length === 0}
              >
                Clear
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleCreateSources}
                disabled={loading || draftSources.length === 0 || !draftSources[0]?.name?.trim()}
              >
                {loading ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  'Create Source'
                )}
              </Button>
            </Box>
          </Stack>
        </Paper>
      )}

      {/* Bulk Mode */}
      {mode === 'bulk' && (
        <>
          {/* Actions */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Stack direction="row" spacing={2} sx={{ flexWrap: 'wrap', gap: 2 }}>
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

              {/* Add Row */}
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleAddRow}
              >
                Add Row
              </Button>

              {/* Clear Draft */}
              {draftSources.length > 0 && (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<ClearIcon />}
                  onClick={handleClearDraft}
                >
                  Clear All
                </Button>
              )}
            </Stack>

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
                      <TableCell sx={{ fontWeight: 600, minWidth: 200 }}>Facebook</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 200 }}>Instagram</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 200 }}>LinkedIn</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 200 }}>TikTok</TableCell>
                      <TableCell sx={{ fontWeight: 600, minWidth: 200 }}>Other</TableCell>
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
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            fullWidth
                            size="small"
                            value={source.facebook_link}
                            onChange={(e) => handleFieldChange(source.id, 'facebook_link', e.target.value)}
                            placeholder="https://facebook.com/..."
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            fullWidth
                            size="small"
                            value={source.instagram_link}
                            onChange={(e) => handleFieldChange(source.id, 'instagram_link', e.target.value)}
                            placeholder="https://instagram.com/..."
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            fullWidth
                            size="small"
                            value={source.linkedin_link}
                            onChange={(e) => handleFieldChange(source.id, 'linkedin_link', e.target.value)}
                            placeholder="https://linkedin.com/in/..."
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            fullWidth
                            size="small"
                            value={source.tiktok_link}
                            onChange={(e) => handleFieldChange(source.id, 'tiktok_link', e.target.value)}
                            placeholder="https://tiktok.com/@..."
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            fullWidth
                            size="small"
                            value={source.other_social_media}
                            onChange={(e) => handleFieldChange(source.id, 'other_social_media', e.target.value)}
                            placeholder="Other social media info"
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteRow(source.id)}
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
                    <Button
                      variant="contained"
                      startIcon={<PublishIcon />}
                      onClick={handleCreateSources}
                      disabled={loading || draftSources.length === 0}
                      sx={{ minWidth: 140 }}
                    >
                      {loading ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : (
                        `Create ${draftSources.length} Sources`
                      )}
                    </Button>
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
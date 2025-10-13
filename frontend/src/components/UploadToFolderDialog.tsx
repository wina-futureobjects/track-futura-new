import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Autocomplete,
  Chip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as CheckIcon,
  Folder as FolderIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { apiFetch } from '../utils/api';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  folder_type: string;
  post_count?: number;
}

interface UploadToFolderDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (folderId: number, folderName: string, platform: string) => void;
  projectId: string;
}

const UploadToFolderDialog: React.FC<UploadToFolderDialogProps> = ({
  open,
  onClose,
  onSuccess,
  projectId,
}) => {
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null);
  const [platform, setPlatform] = useState('instagram');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loadingFolders, setLoadingFolders] = useState(false);

  // Create new folder option
  const [showCreateNewFolder, setShowCreateNewFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  const platforms = [
    { key: 'instagram', label: 'Instagram', color: '#E4405F' },
    { key: 'facebook', label: 'Facebook', color: '#1877F2' },
    { key: 'tiktok', label: 'TikTok', color: '#000000' },
    { key: 'linkedin', label: 'LinkedIn', color: '#0A66C2' },
  ];

  // Fetch available folders
  const fetchFolders = async () => {
    setLoadingFolders(true);
    try {
      const response = await apiFetch(`/api/track-accounts/report-folders/?project=${projectId}&folder_type=run`);
      if (response.ok) {
        const data = await response.json();
        setFolders(data.results || data || []);
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
      setError('Failed to load folders. Please try again.');
    } finally {
      setLoadingFolders(false);
    }
  };

  useEffect(() => {
    if (open && projectId) {
      fetchFolders();
    }
  }, [open, projectId]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setDragOver(false);
    
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.json') || droppedFile.name.endsWith('.csv'))) {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please select a JSON or CSV file');
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleCreateNewFolder = async () => {
    if (!newFolderName.trim()) {
      setError('Please enter a folder name');
      return;
    }

    try {
      const folderData = {
        name: newFolderName.trim(),
        description: null,
        folder_type: 'run',
        project_id: projectId
      };

      const response = await apiFetch(`/api/track-accounts/report-folders/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(folderData),
      });

      if (!response.ok) {
        throw new Error('Failed to create folder');
      }

      const newFolder = await response.json();
      setFolders(prev => [...prev, newFolder]);
      setSelectedFolder(newFolder);
      setShowCreateNewFolder(false);
      setNewFolderName('');
      
    } catch (error) {
      console.error('Error creating folder:', error);
      setError('Failed to create new folder. Please try again.');
    }
  };

  const handleUpload = async () => {
    if (!file || !selectedFolder) {
      setError('Please select a file and a folder');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder_name', selectedFolder.name);
      formData.append('platform', platform);

      const response = await fetch('/api/brightdata/upload-data/', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        onSuccess(result.main_folder_id || result.folder_id, result.hierarchy || selectedFolder.name, platform);
        handleClose();
      } else {
        setError(result.error || 'Upload failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setSelectedFolder(null);
    setPlatform('instagram');
    setFile(null);
    setError(null);
    setUploading(false);
    setShowCreateNewFolder(false);
    setNewFolderName('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <CloudUploadIcon />
          Upload Data to Folder
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {/* Step 1: Select or Create Folder */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom fontWeight={500}>
            1. Select Destination Folder
          </Typography>
          
          {loadingFolders ? (
            <Box display="flex" alignItems="center" gap={2} p={2}>
              <CircularProgress size={20} />
              <Typography>Loading folders...</Typography>
            </Box>
          ) : (
            <Box>
              {!showCreateNewFolder ? (
                <Box>
                  <FormControl fullWidth margin="normal">
                    <Autocomplete
                      options={folders}
                      getOptionLabel={(folder) => folder.name}
                      value={selectedFolder}
                      onChange={(event, newValue) => {
                        setSelectedFolder(newValue);
                      }}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Select existing folder"
                          placeholder="Choose a folder to upload data into"
                          variant="outlined"
                        />
                      )}
                      renderOption={(props, folder) => (
                        <Box component="li" {...props}>
                          <Box display="flex" alignItems="center" gap={1} width="100%">
                            <FolderIcon color="primary" />
                            <Box flexGrow={1}>
                              <Typography>{folder.name}</Typography>
                              {folder.description && (
                                <Typography variant="body2" color="text.secondary">
                                  {folder.description}
                                </Typography>
                              )}
                            </Box>
                            <Chip 
                              label={`${folder.post_count || 0} items`} 
                              size="small" 
                              variant="outlined" 
                            />
                          </Box>
                        </Box>
                      )}
                    />
                  </FormControl>
                  
                  <Box display="flex" justifyContent="center" mt={2}>
                    <Button
                      startIcon={<AddIcon />}
                      onClick={() => setShowCreateNewFolder(true)}
                      variant="outlined"
                      size="small"
                    >
                      Create New Folder
                    </Button>
                  </Box>
                </Box>
              ) : (
                <Box>
                  <TextField
                    fullWidth
                    label="New Folder Name"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    margin="normal"
                    placeholder="e.g., Nike Campaign Data"
                  />
                  <Box display="flex" gap={2} mt={2}>
                    <Button
                      onClick={handleCreateNewFolder}
                      variant="contained"
                      disabled={!newFolderName.trim()}
                    >
                      Create
                    </Button>
                    <Button
                      onClick={() => {
                        setShowCreateNewFolder(false);
                        setNewFolderName('');
                      }}
                      variant="outlined"
                    >
                      Cancel
                    </Button>
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </Box>

        {/* Step 2: Select Platform */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom fontWeight={500}>
            2. Select Platform
          </Typography>
          <FormControl fullWidth margin="normal">
            <InputLabel id="platform-select-label">Platform</InputLabel>
            <Select
              labelId="platform-select-label"
              id="platform-select"
              name="platformSelect"
              value={platform}
              label="Platform"
              onChange={(e) => setPlatform(e.target.value)}
            >
              {platforms.map((platform) => (
                <MenuItem key={platform.key} value={platform.key}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Box 
                      sx={{ 
                        width: 12, 
                        height: 12, 
                        borderRadius: '50%', 
                        bgcolor: platform.color 
                      }} 
                    />
                    {platform.label}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            A "{platform}" subfolder will be automatically created inside "{selectedFolder?.name || 'the selected folder'}"
          </Typography>
        </Box>

        {/* Step 3: Upload File */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom fontWeight={500}>
            3. Upload Data File
          </Typography>
          
          <Paper
            sx={{
              p: 3,
              border: '2px dashed',
              borderColor: dragOver ? 'primary.main' : 'grey.300',
              bgcolor: dragOver ? 'action.hover' : 'background.paper',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => document.getElementById('file-input-upload')?.click()}
          >
            <input
              id="file-input-upload"
              name="uploadDataFile"
              type="file"
              accept=".json,.csv"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            
            {file ? (
              <Box>
                <CheckIcon color="success" sx={{ fontSize: 48, mb: 1 }} />
                <Typography variant="h6" gutterBottom>
                  File Selected
                </Typography>
                <Box display="flex" alignItems="center" justifyContent="center" gap={1} mb={1}>
                  <FileIcon color="primary" />
                  <Typography>{file.name}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Size: {(file.size / 1024).toFixed(1)} KB
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Click to select a different file
                </Typography>
              </Box>
            ) : (
              <Box>
                <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                <Typography variant="h6" gutterBottom>
                  Drop your file here or click to select
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Supports JSON and CSV files from BrightData or other sources
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Preview of folder structure */}
        {selectedFolder && platform && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Your data will be organized as:</strong>
            </Typography>
            <Box sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              📁 {selectedFolder.name}/
              <br />
              &nbsp;&nbsp;└── 📁 {platform.charAt(0).toUpperCase() + platform.slice(1)}/
              <br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 📄 {file ? file.name : 'uploaded-data.json'}
            </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          Cancel
        </Button>
        <Button
          onClick={handleUpload}
          variant="contained"
          disabled={!file || !selectedFolder || uploading}
          startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
        >
          {uploading ? 'Uploading...' : 'Upload to Folder'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UploadToFolderDialog;
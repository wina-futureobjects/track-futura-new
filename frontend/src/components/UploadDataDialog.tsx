import React, { useState } from 'react';
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
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { apiFetch } from '../utils/api';

interface UploadDataDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (folderId: number, folderName: string) => void;
}

const UploadDataDialog: React.FC<UploadDataDialogProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [folderName, setFolderName] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      
      // Auto-generate folder name if empty
      if (!folderName) {
        const baseName = selectedFile.name.replace(/\.(json|csv)$/i, '');
        setFolderName(`Uploaded Data - ${baseName}`);
      }
    }
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setDragOver(false);
    
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.json') || droppedFile.name.endsWith('.csv'))) {
      setFile(droppedFile);
      setError(null);
      
      // Auto-generate folder name if empty
      if (!folderName) {
        const baseName = droppedFile.name.replace(/\.(json|csv)$/i, '');
        setFolderName(`Uploaded Data - ${baseName}`);
      }
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

  const handleUpload = async () => {
    if (!file || !folderName.trim()) {
      setError('Please select a file and enter a folder name');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('data_file', file);
      formData.append('folder_name', folderName.trim());
      formData.append('platform', platform);

      const response = await fetch('/api/brightdata/upload-data/', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        onSuccess(result.folder_id, result.folder_name);
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
    setFolderName('');
    setPlatform('instagram');
    setFile(null);
    setError(null);
    setUploading(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <CloudUploadIcon />
          Upload Data File
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="Folder Name"
            id="folder-name"
            name="folderName"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            margin="normal"
            required
            helperText="Enter a descriptive name for your data folder"
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="platform-select-label">Platform</InputLabel>
            <Select
              labelId="platform-select-label"
              id="platform-select"
              value={platform}
              label="Platform"
              onChange={(e) => setPlatform(e.target.value)}
            >
              <MenuItem value="instagram">Instagram</MenuItem>
              <MenuItem value="facebook">Facebook</MenuItem>
              <MenuItem value="tiktok">TikTok</MenuItem>
              <MenuItem value="linkedin">LinkedIn</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>
        </Box>

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
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            name="dataFile"
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

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Supported formats:</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • JSON files with post data (Instagram, Facebook, etc.)
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • CSV files with columns: post_id, user_posted, content, likes, comments, url
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          Cancel
        </Button>
        <Button
          onClick={handleUpload}
          variant="contained"
          disabled={!file || !folderName.trim() || uploading}
          startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
        >
          {uploading ? 'Uploading...' : 'Upload & Create Folder'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UploadDataDialog;
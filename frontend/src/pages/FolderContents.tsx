import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Breadcrumbs,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Tooltip,
  IconButton,
  Snackbar,
} from '@mui/material';
import {
  Folder as FolderIcon,
  Instagram as InstagramIcon,
  Facebook as FacebookIcon,
  LinkedIn as LinkedInIcon,
  MusicVideo as TikTokIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  OpenInNew as OpenInNewIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Storage as StorageIcon,
  ArrowBack as ArrowBackIcon,
  FolderOutlined as FolderOutlinedIcon,
} from '@mui/icons-material';
import { apiFetch } from '../utils/api';

interface Folder {
  id: number;
  name: string;
  description: string | null;
  category: string;
  category_display: string;
  platform: string;
  created_at?: string;
  post_count?: number;
  parent_folder?: number;
  folder_type: string;
  scraping_run?: number;
  subfolders?: Folder[];
}

const FolderContents = () => {
  const { organizationId, projectId, folderType, folderId } = useParams<{ 
    organizationId: string; 
    projectId: string; 
    folderType: string;
    folderId: string;
  }>();
  const navigate = useNavigate();
  
  const [currentFolder, setCurrentFolder] = useState<Folder | null>(null);
  const [subfolders, setSubfolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const platforms = [
    { key: 'instagram', label: 'Instagram', icon: <InstagramIcon />, color: '#E4405F' },
    { key: 'facebook', label: 'Facebook', icon: <FacebookIcon />, color: '#1877F2' },
    { key: 'linkedin', label: 'LinkedIn', icon: <LinkedInIcon />, color: '#0A66C2' },
    { key: 'tiktok', label: 'TikTok', icon: <TikTokIcon />, color: '#000000' }
  ];

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'posts', label: 'Posts' },
    { value: 'reels', label: 'Reels' },
    { value: 'comments', label: 'Comments' }
  ];

  const fetchFolderContents = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch the current folder details
      let folderResponse;
      if (folderType === 'run') {
        // For unified run folders, fetch from track_accounts
        try {
          const response = await apiFetch(`/api/track-accounts/report-folders/${folderId}/?project=${projectId}`);
          if (response.ok) {
            folderResponse = await response.json();
          }
        } catch (e) {
          console.error('Error fetching run folder:', e);
        }
      } else if (folderType === 'service') {
        // For service folders, we need to check all platforms
        const allPlatforms = ['instagram', 'facebook', 'linkedin', 'tiktok'];
        for (const platform of allPlatforms) {
          try {
            const response = await apiFetch(`/api/${platform}-data/folders/${folderId}/?project=${projectId}`);
            if (response.ok) {
              folderResponse = await response.json();
              break;
            }
          } catch (e) {
            continue;
          }
        }
      } else {
        // For content folders, use the platform from the URL
        const platform = folderType;
        const response = await apiFetch(`/api/${platform}-data/folders/${folderId}/?project=${projectId}`);
        if (response.ok) {
          folderResponse = await response.json();
        }
      }

      if (folderResponse) {
        setCurrentFolder(folderResponse);
        
        // Fetch subfolders based on folder type
        if (folderType === 'run') {
          // For run folders, fetch all service folders with the same scraping_run
          const allPlatforms = ['instagram', 'facebook', 'linkedin', 'tiktok'];
          const allSubfolders = [];
          
          for (const platform of allPlatforms) {
            try {
              const response = await apiFetch(`/api/${platform}-data/folders/?project=${projectId}&scraping_run=${folderResponse.scraping_run}&folder_type=service&include_hierarchy=true`);
              if (response.ok) {
                const data = await response.json();
                const platformSubfolders = data.results || data;
                allSubfolders.push(...platformSubfolders);
              }
            } catch (e) {
              console.error(`Error fetching ${platform} service folders:`, e);
            }
          }
          
          setSubfolders(allSubfolders);
        } else {
          // For other folder types, fetch subfolders normally
          const subfoldersResponse = await apiFetch(`/api/${folderResponse.platform}-data/folders/?project=${projectId}&parent_folder=${folderId}&include_hierarchy=true`);
          if (subfoldersResponse.ok) {
            const data = await subfoldersResponse.json();
            setSubfolders(data.results || data);
          }
        }
      } else {
        setError('Folder not found');
      }
      
    } catch (error) {
      console.error('Error fetching folder contents:', error);
      setError('Failed to load folder contents. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId && folderId) {
      fetchFolderContents();
    }
  }, [projectId, folderId, folderType]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleCategoryFilterChange = (event: SelectChangeEvent) => {
    setCategoryFilter(event.target.value);
  };

  const getFilteredSubfolders = () => {
    return subfolders.filter(folder => {
      const matchesSearch = folder.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (folder.description && folder.description.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesCategory = categoryFilter === 'all' || folder.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  };

  const handleFolderClick = (folder: Folder) => {
    if (folder.folder_type === 'content') {
      // Navigate to content folder (existing data page)
      navigate(`/organizations/${organizationId}/projects/${projectId}/data/${folder.platform}/${folder.id}`);
    } else {
      // Navigate to folder contents page
      navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/${folder.folder_type}/${folder.id}`);
    }
  };

  const handleBackClick = () => {
    if (currentFolder?.parent_folder) {
      // Navigate back to parent folder
      navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage/${currentFolder.folder_type === 'service' ? 'run' : 'service'}/${currentFolder.parent_folder}`);
    } else {
      // Navigate back to data storage main page
      navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage`);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'posts': return 'primary';
      case 'reels': return 'secondary';
      case 'comments': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Box sx={{ 
      width: '100%', 
      padding: '16px 32px',
      bgcolor: '#f5f5f5',
      minHeight: 'calc(100vh - 56px)',
    }}>
      
      {/* Header with breadcrumbs */}
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBackClick}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
          <Button
            startIcon={<HomeIcon />}
            onClick={() => navigate(`/organizations/${organizationId}/projects/${projectId}/data-storage`)}
            sx={{ textTransform: 'none' }}
          >
            Data Storage
          </Button>
          {currentFolder && (
            <Typography color="text.primary">{currentFolder.name}</Typography>
          )}
        </Breadcrumbs>
      </Box>

      {/* Folder Header */}
      {currentFolder && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Box display="flex" alignItems="center">
              {currentFolder.folder_type === 'run' && <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />}
              {currentFolder.folder_type === 'service' && <FolderOutlinedIcon sx={{ mr: 1, color: 'secondary.main' }} />}
              {currentFolder.folder_type === 'content' && <FolderIcon sx={{ mr: 1, color: 'success.main' }} />}
              <Typography variant="h5" sx={{ fontWeight: 500 }}>
                {currentFolder.name}
              </Typography>
            </Box>
            <Chip 
              label={`${currentFolder.post_count || 0} items`} 
              size="small" 
              color="primary" 
              variant="outlined"
            />
          </Box>
          {currentFolder.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {currentFolder.description}
            </Typography>
          )}
          <Typography variant="caption" color="text.secondary">
            Created: {formatDate(currentFolder.created_at || '')}
          </Typography>
        </Paper>
      )}

      {/* Search and filters */}
      <Box
        display="flex" 
        justifyContent="space-between" 
        alignItems="center" 
        sx={{ mb: 2 }}
      >
        <TextField
          placeholder="Search folders"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={handleSearchChange}
          sx={{ 
            width: '300px',
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'white',
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <FormControl size="small" sx={{ minWidth: 180, backgroundColor: 'white' }}>
          <InputLabel id="category-select-label">Category</InputLabel>
          <Select
            labelId="category-select-label"
            id="category-select"
            value={categoryFilter}
            label="Category"
            onChange={handleCategoryFilterChange}
          >
            {categories.map((category) => (
              <MenuItem key={category.value} value={category.value}>
                {category.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Folders Count */}
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Showing {getFilteredSubfolders().length} folder{getFilteredSubfolders().length !== 1 ? 's' : ''}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Subfolders Grid */}
      {getFilteredSubfolders().length > 0 ? (
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 2 }}>
          {getFilteredSubfolders().map((folder) => {
            const platformConfig = platforms.find(p => p.key === folder.platform) || 
              { key: folder.platform, label: folder.platform.charAt(0).toUpperCase() + folder.platform.slice(1), icon: <FolderIcon />, color: '#666' };
            
            return (
              <Paper 
                key={folder.id}
                sx={{ 
                  p: 2, 
                  border: '1px solid #e0e0e0',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': { 
                    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                    transform: 'translateY(-2px)'
                  }
                }}
                onClick={() => handleFolderClick(folder)}
              >
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Box display="flex" alignItems="center">
                    <Box sx={{ color: platformConfig.color, mr: 1 }}>
                      {platformConfig.icon}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 500 }}>
                      {folder.name}
                    </Typography>
                  </Box>
                  <Chip 
                    label={`${folder.post_count || 0} items`} 
                    size="small" 
                    color="primary" 
                    variant="outlined"
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Click to view contents
                </Typography>
                
                <Box display="flex" gap={1}>
                  <Chip
                    label={platformConfig.label}
                    size="small"
                    sx={{ 
                      bgcolor: platformConfig.color,
                      color: 'white',
                      fontWeight: 500
                    }}
                  />
                  <Chip
                    label={folder.category_display || folder.category}
                    color={getCategoryColor(folder.category) as any}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Paper>
            );
          })}
        </Box>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center', mt: 2, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>No folders found</Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {searchTerm || categoryFilter !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'This folder is empty.'
            }
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default FolderContents; 
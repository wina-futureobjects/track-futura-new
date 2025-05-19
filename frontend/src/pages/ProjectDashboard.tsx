import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent,
  Button,
  Grid as MuiGrid,
  Divider,
  CircularProgress,
  Paper,
  Breadcrumbs,
  Link,
  Stack,
  LinearProgress,
  Avatar,
  Chip,
  IconButton,
  Tooltip as MuiTooltip,
  Tab,
  Tabs,
  Container,
  useTheme,
  alpha,
} from '@mui/material';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import FolderOutlinedIcon from '@mui/icons-material/FolderOutlined';
import InstagramIcon from '@mui/icons-material/Instagram';
import FacebookIcon from '@mui/icons-material/Facebook';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import PersonIcon from '@mui/icons-material/Person';
import BarChartIcon from '@mui/icons-material/BarChart';
import DataUsageIcon from '@mui/icons-material/DataUsage';
import SummarizeIcon from '@mui/icons-material/Summarize';
import StorageIcon from '@mui/icons-material/Storage';
import PeopleIcon from '@mui/icons-material/People';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CreditScoreIcon from '@mui/icons-material/CreditScore';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import NotificationsNoneOutlinedIcon from '@mui/icons-material/NotificationsNoneOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import DateRangeOutlinedIcon from '@mui/icons-material/DateRangeOutlined';
import SpeedOutlinedIcon from '@mui/icons-material/SpeedOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import TuneOutlinedIcon from '@mui/icons-material/TuneOutlined';
import { apiFetch } from '../utils/api';
import StatCard from '../components/dashboard/StatCard';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from 'recharts';

// Create a Grid component that inherits from MuiGrid to fix type issues
const Grid = (props: any) => <MuiGrid {...props} />;

interface Project {
  id: number;
  name: string;
  description: string | null;
  owner: number;
  owner_name: string;
  created_at: string;
  updated_at: string;
  organization?: {
    id: number;
    name: string;
  };
  status?: 'active' | 'pending' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  progress?: number;
}

// Mock data for the dashboard
interface ProjectStats {
  totalPosts: number;
  totalAccounts: number;
  totalReports: number;
  totalStorageUsed: string;
  creditBalance: number;
  maxCredits: number;
  engagementRate: number;
  growthRate: number;
}

// Demo data for the charts
const activityData = [
  { date: 'Jun', instagram: 340, facebook: 240, linkedin: 180, tiktok: 120 },
  { date: 'Jul', instagram: 520, facebook: 320, linkedin: 220, tiktok: 180 },
  { date: 'Aug', instagram: 450, facebook: 280, linkedin: 310, tiktok: 240 },
  { date: 'Sep', instagram: 610, facebook: 380, linkedin: 340, tiktok: 320 },
  { date: 'Oct', instagram: 580, facebook: 450, linkedin: 290, tiktok: 360 },
];

const platformDistribution = [
  { name: 'Instagram', value: 45, color: '#E1306C' },
  { name: 'Facebook', value: 30, color: '#1877F2' },
  { name: 'LinkedIn', value: 15, color: '#0A66C2' },
  { name: 'TikTok', value: 10, color: '#000000' },
];

const ProjectDashboard = () => {
  const theme = useTheme();
  // Get parameters from both URL patterns
  const { projectId, organizationId } = useParams<{ 
    projectId: string;
    organizationId?: string;
  }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Mock project stats
  const [stats, setStats] = useState<ProjectStats>({
    totalPosts: 1258,
    totalAccounts: 42,
    totalReports: 15,
    totalStorageUsed: '2.8 GB',
    creditBalance: 2400,
    maxCredits: 5000,
    engagementRate: 3.2,
    growthRate: 5.8
  });
  
  // Determine which URL pattern we're using
  const isOrgProjectUrl = location.pathname.includes('/organizations/') && location.pathname.includes('/projects/');

  useEffect(() => {
    const fetchProject = async () => {
      if (!projectId) return;
      
      try {
        setLoading(true);
        const response = await apiFetch(`/api/users/projects/${projectId}/`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch project details');
        }
        
        const data = await response.json();
        setProject(data);
        
        // If we're using the old URL pattern but have organization info,
        // redirect to the new URL pattern
        if (!isOrgProjectUrl && data.organization && data.organization.id) {
          navigate(`/organizations/${data.organization.id}/projects/${projectId}`, { replace: true });
        }
      } catch (error) {
        console.error('Error fetching project:', error);
        setError('Failed to load project. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchProject();
  }, [projectId, isOrgProjectUrl]);

  // Function to get the project URL in the correct format
  const getProjectUrl = () => {
    if (organizationId && projectId) {
      return `/organizations/${organizationId}/projects/${projectId}`;
    }
    return `/dashboard/${projectId}`;
  };
  
  // Function to get the organization projects URL
  const getOrganizationProjectsUrl = () => {
    if (organizationId) {
      return `/organizations/${organizationId}/projects`;
    }
    if (project?.organization?.id) {
      return `/organizations/${project.organization.id}/projects`;
    }
    return '/organizations';
  };

  const handleNavigate = (path: string) => {
    // If we have organization and project IDs, use the new URL structure
    if (organizationId && projectId) {
      navigate(path);
    } else if (project?.organization?.id && projectId) {
      // If we have organization info in the project, use that
      const orgId = project.organization.id;
      // If the path doesn't already include organization/project IDs
      if (!path.includes('/organizations/')) {
        navigate(path.replace(/^\//, `/organizations/${orgId}/projects/${projectId}/`));
      } else {
        navigate(path);
      }
    } else {
      // Fallback to old URL structure with query parameters
      const baseUrl = path.split('?')[0];
      navigate(`${baseUrl}?project=${projectId}`);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !project) {
    return (
      <Box sx={{ p: 3 }}>
        <Paper sx={{ p: 3, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography variant="h6">{error || 'Project not found'}</Typography>
          <Button 
            variant="contained" 
            sx={{ mt: 2 }} 
            onClick={() => navigate('/')}
          >
            Back to Home
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      width: '100%', 
      backgroundColor: '#f8f9fd',
      p: { xs: 2, md: 3 },
      flexGrow: 1
    }}>
      <Container maxWidth="xl" sx={{ mx: 'auto' }}>
        {/* Project header with title and actions - simplified */}
        <Box sx={{ 
          mb: 3
        }}>
          <Typography variant="h4" component="h1" fontWeight={600}>
            Dashboard
          </Typography>
        </Box>

        {/* Credit balance and key stats row */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={9}>
            <Paper
              elevation={0}
              sx={{ 
                p: 3, 
                borderRadius: 2,
                background: `linear-gradient(135deg, ${theme.palette.primary.light} 0%, ${theme.palette.primary.main} 100%)`,
                color: 'white',
                display: 'flex',
                flexDirection: { xs: 'column', sm: 'row' },
                alignItems: 'center',
                gap: 3
              }}
            >
              <Box sx={{ flex: 1 }}>
                <Typography variant="h5" fontWeight={600} gutterBottom>
                  Project Credits
                </Typography>
                <Typography variant="body1" sx={{ mb: 2, opacity: 0.9 }}>
                  Your project has {stats.creditBalance} credits remaining out of {stats.maxCredits} total.
                </Typography>
                <Box sx={{ mb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" fontWeight={500}>Usage</Typography>
                    <Typography variant="body2" fontWeight={500}>{stats.creditBalance} / {stats.maxCredits}</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={(stats.creditBalance / stats.maxCredits) * 100} 
                    sx={{ 
                      height: 8, 
                      borderRadius: 1,
                      bgcolor: 'rgba(255,255,255,0.2)',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: 'white'
                      }
                    }}
                  />
                </Box>
              </Box>
              <Box>
                <Button
                  variant="contained"
                  sx={{ 
                    bgcolor: 'white', 
                    color: theme.palette.primary.main,
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.9)'
                    }
                  }}
                >
                  Add Credits
                </Button>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Paper
              elevation={0}
              sx={{ 
                p: 3, 
                borderRadius: 2,
                height: '100%',
                boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Project Status</Typography>
                <IconButton size="small">
                  <MoreVertIcon fontSize="small" />
                </IconButton>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>Created</Typography>
                <Typography variant="body1" fontWeight={500}>{new Date(project.created_at).toLocaleDateString()}</Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>Owner</Typography>
                <Typography variant="body1" fontWeight={500}>{project.owner_name}</Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>Organization</Typography>
                <Typography variant="body1" fontWeight={500}>{project.organization?.name || 'Personal'}</Typography>
              </Box>
              
              <Box sx={{ mt: 'auto', pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">Last Update</Typography>
                  <Typography variant="body2" fontWeight={500}>{new Date(project.updated_at).toLocaleDateString()}</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Dashboard Stats Cards */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} lg={3}>
            <Paper elevation={0} sx={{ 
              p: 2.5, 
              borderRadius: 2, 
              boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
              height: '100%' 
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle1" color="text.secondary">Total Posts</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
                  <DataUsageIcon fontSize="small" />
                </Avatar>
              </Box>
              <Typography variant="h4" fontWeight={600} gutterBottom>{stats.totalPosts}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Chip 
                  label={`+12.5%`} 
                  size="small" 
                  sx={{ 
                    bgcolor: alpha(theme.palette.success.main, 0.1), 
                    color: theme.palette.success.main,
                    mr: 1
                  }} 
                />
                <Typography variant="body2" color="text.secondary">vs last period</Typography>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} sm={6} lg={3}>
            <Paper elevation={0} sx={{ 
              p: 2.5, 
              borderRadius: 2, 
              boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
              height: '100%' 
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle1" color="text.secondary">Total Accounts</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.secondary.main, 0.1), color: theme.palette.secondary.main }}>
                  <PersonIcon fontSize="small" />
                </Avatar>
              </Box>
              <Typography variant="h4" fontWeight={600} gutterBottom>{stats.totalAccounts}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Chip 
                  label={`+5.2%`} 
                  size="small" 
                  sx={{ 
                    bgcolor: alpha(theme.palette.success.main, 0.1), 
                    color: theme.palette.success.main,
                    mr: 1
                  }} 
                />
                <Typography variant="body2" color="text.secondary">vs last period</Typography>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} sm={6} lg={3}>
            <Paper elevation={0} sx={{ 
              p: 2.5, 
              borderRadius: 2, 
              boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
              height: '100%' 
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle1" color="text.secondary">Engagement Rate</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1), color: theme.palette.success.main }}>
                  <TrendingUpIcon fontSize="small" />
                </Avatar>
              </Box>
              <Typography variant="h4" fontWeight={600} gutterBottom>{stats.engagementRate}%</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Chip 
                  label={`+0.8%`} 
                  size="small" 
                  sx={{ 
                    bgcolor: alpha(theme.palette.success.main, 0.1), 
                    color: theme.palette.success.main,
                    mr: 1
                  }} 
                />
                <Typography variant="body2" color="text.secondary">vs last period</Typography>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} sm={6} lg={3}>
            <Paper elevation={0} sx={{ 
              p: 2.5, 
              borderRadius: 2, 
              boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
              height: '100%' 
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle1" color="text.secondary">Storage Used</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.warning.main, 0.1), color: theme.palette.warning.main }}>
                  <StorageIcon fontSize="small" />
                </Avatar>
              </Box>
              <Typography variant="h4" fontWeight={600} gutterBottom>{stats.totalStorageUsed}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Chip 
                  label={`-20.3%`} 
                  size="small" 
                  sx={{ 
                    bgcolor: alpha(theme.palette.error.main, 0.1), 
                    color: theme.palette.error.main,
                    mr: 1
                  }} 
                />
                <Typography variant="body2" color="text.secondary">vs last period</Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Activity and Platform Distribution Charts */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Paper elevation={0} sx={{ p: 3, borderRadius: 2, boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box>
                  <Typography variant="h6" fontWeight={500}>Activity Overview</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Posts and engagements across platforms over time
                  </Typography>
                </Box>
                <Box>
                  <Button 
                    variant="text" 
                    endIcon={<DateRangeOutlinedIcon />}
                    sx={{ color: 'text.secondary' }}
                    size="small"
                  >
                    Last 30 Days
                  </Button>
                </Box>
              </Box>
              <Box sx={{ height: 340, width: '100%', mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={activityData}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="colorInstagram" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#E1306C" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#E1306C" stopOpacity={0.1}/>
                      </linearGradient>
                      <linearGradient id="colorFacebook" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1877F2" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#1877F2" stopOpacity={0.1}/>
                      </linearGradient>
                      <linearGradient id="colorLinkedin" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0A66C2" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#0A66C2" stopOpacity={0.1}/>
                      </linearGradient>
                      <linearGradient id="colorTiktok" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#000000" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#000000" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis dataKey="date" tick={{ fill: '#666666' }} />
                    <YAxis tick={{ fill: '#666666' }} />
                    <Tooltip 
                      contentStyle={{ 
                        borderRadius: 8, 
                        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                        border: 'none' 
                      }} 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="instagram" 
                      stroke="#E1306C" 
                      fillOpacity={1}
                      fill="url(#colorInstagram)" 
                      strokeWidth={2}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="facebook" 
                      stroke="#1877F2" 
                      fillOpacity={1}
                      fill="url(#colorFacebook)" 
                      strokeWidth={2}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="linkedin" 
                      stroke="#0A66C2" 
                      fillOpacity={1}
                      fill="url(#colorLinkedin)" 
                      strokeWidth={2}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="tiktok" 
                      stroke="#000000" 
                      fillOpacity={1}
                      fill="url(#colorTiktok)" 
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper elevation={0} sx={{ p: 3, borderRadius: 2, boxShadow: '0 2px 10px rgba(0,0,0,0.05)', height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight={500}>Platform Distribution</Typography>
                <IconButton size="small">
                  <MoreVertIcon fontSize="small" />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Breakdown of your data across platforms
              </Typography>
              
              <Box sx={{ height: 260, display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={platformDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={65}
                      outerRadius={90}
                      paddingAngle={4}
                      dataKey="value"
                      strokeWidth={1}
                      stroke="#fff"
                    >
                      {platformDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: number) => [`${value}%`, 'Percentage']}
                      contentStyle={{ 
                        borderRadius: 8, 
                        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                        border: 'none' 
                      }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      layout="horizontal"
                      iconType="circle"
                      iconSize={10}
                      formatter={(value) => <span style={{ color: '#666', fontSize: '0.875rem' }}>{value}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Quick Access Platform Buttons */}
        <Grid container spacing={2}>
          <Grid item xs={6} sm={4} md={3} lg={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              startIcon={<InstagramIcon />}
              sx={{ 
                p: 1.5,
                py: 2, 
                justifyContent: 'flex-start',
                borderColor: '#E1306C',
                color: '#E1306C',
                borderRadius: 2,
                '&:hover': {
                  borderColor: '#E1306C',
                  backgroundColor: 'rgba(225, 48, 108, 0.04)'
                }
              }}
              onClick={() => {
                handleNavigate(`/organizations/${organizationId}/projects/${projectId}/instagram-folders`);
              }}
            >
              Instagram
            </Button>
          </Grid>
          <Grid item xs={6} sm={4} md={3} lg={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              startIcon={<FacebookIcon />}
              sx={{ 
                p: 1.5,
                py: 2, 
                justifyContent: 'flex-start',
                borderColor: '#1877F2',
                color: '#1877F2',
                borderRadius: 2,
                '&:hover': {
                  borderColor: '#1877F2',
                  backgroundColor: 'rgba(24, 119, 242, 0.04)'
                }
              }}
              onClick={() => {
                handleNavigate(`/organizations/${organizationId}/projects/${projectId}/facebook-folders`);
              }}
            >
              Facebook
            </Button>
          </Grid>
          <Grid item xs={6} sm={4} md={3} lg={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              startIcon={<LinkedInIcon />}
              sx={{ 
                p: 1.5,
                py: 2, 
                justifyContent: 'flex-start',
                borderColor: '#0A66C2',
                color: '#0A66C2',
                borderRadius: 2,
                '&:hover': {
                  borderColor: '#0A66C2',
                  backgroundColor: 'rgba(10, 102, 194, 0.04)'
                }
              }}
              onClick={() => {
                handleNavigate(`/organizations/${organizationId}/projects/${projectId}/linkedin-folders`);
              }}
            >
              LinkedIn
            </Button>
          </Grid>
          <Grid item xs={6} sm={4} md={3} lg={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              startIcon={<WhatsAppIcon />}
              sx={{ 
                p: 1.5,
                py: 2, 
                justifyContent: 'flex-start',
                borderColor: '#000000',
                color: '#000000',
                borderRadius: 2,
                '&:hover': {
                  borderColor: '#000000',
                  backgroundColor: 'rgba(0, 0, 0, 0.04)'
                }
              }}
              onClick={() => {
                handleNavigate(`/organizations/${organizationId}/projects/${projectId}/tiktok-folders`);
              }}
            >
              TikTok
            </Button>
          </Grid>
          <Grid item xs={6} sm={4} md={3} lg={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              startIcon={<PersonIcon />}
              sx={{ 
                p: 1.5,
                py: 2, 
                justifyContent: 'flex-start',
                borderColor: '#6200EA',
                color: '#6200EA',
                borderRadius: 2,
                '&:hover': {
                  borderColor: '#6200EA',
                  backgroundColor: 'rgba(98, 0, 234, 0.04)'
                }
              }}
              onClick={() => {
                handleNavigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/folders`);
              }}
            >
              Accounts
            </Button>
          </Grid>
          <Grid item xs={6} sm={4} md={3} lg={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              startIcon={<BarChartIcon />}
              sx={{ 
                p: 1.5,
                py: 2, 
                justifyContent: 'flex-start',
                borderColor: '#FFA000',
                color: '#FFA000',
                borderRadius: 2,
                '&:hover': {
                  borderColor: '#FFA000',
                  backgroundColor: 'rgba(255, 160, 0, 0.04)'
                }
              }}
              onClick={() => {
                handleNavigate(`/organizations/${organizationId}/projects/${projectId}/report-folders`);
              }}
            >
              Reports
            </Button>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default ProjectDashboard; 
import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent,
  Button,
  Grid,
  Divider,
  CircularProgress,
  Paper,
  Breadcrumbs,
  Link,
  Stack,
  LinearProgress,
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
} from 'recharts';

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
      padding: { xs: '16px', md: '24px' },
      minHeight: 'calc(100vh - 56px)',
      backgroundColor: '#f5f7fa'
    }}>
      {/* Project header */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', md: 'row' }, 
        justifyContent: 'space-between',
        alignItems: { xs: 'flex-start', md: 'center' },
        mb: 4 
      }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
            {project.name}
          </Typography>
          {project.description && (
            <Typography variant="body1" color="text.secondary">
              {project.description}
            </Typography>
          )}
        </Box>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          mt: { xs: 2, md: 0 },
          backgroundColor: 'background.paper',
          borderRadius: 1,
          p: 1
        }}>
          <CreditScoreIcon color="primary" sx={{ mr: 1.5 }} />
          <Box sx={{ minWidth: 180 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2" color="text.secondary">Credits Balance</Typography>
              <Typography variant="body2" fontWeight={500}>{stats.creditBalance} / {stats.maxCredits}</Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={(stats.creditBalance / stats.maxCredits) * 100} 
              sx={{ height: 8, borderRadius: 1 }}
            />
          </Box>
        </Box>
      </Box>
      
      {/* Dashboard Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Total Posts" 
            value={stats.totalPosts} 
            icon={<DataUsageIcon />} 
            color="primary"
            change={{ value: 12.5, positive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Total Accounts" 
            value={stats.totalAccounts} 
            icon={<PersonIcon />} 
            color="secondary"
            change={{ value: 5.2, positive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Engagement Rate" 
            value={`${stats.engagementRate}%`} 
            icon={<TrendingUpIcon />} 
            color="success"
            change={{ value: 0.8, positive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Storage Used" 
            value={stats.totalStorageUsed} 
            icon={<StorageIcon />} 
            color="warning"
            change={{ value: 20.3, positive: false }}
          />
        </Grid>
      </Grid>
      
      {/* Activity Chart */}
      <Paper sx={{ p: 3, mb: 4, borderRadius: 2, boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
        <Typography variant="h6" gutterBottom>Activity Overview</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Posts and engagements across platforms over time
        </Typography>
        <Box sx={{ height: 320, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={activityData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="instagram" 
                stackId="1" 
                stroke="#E1306C" 
                fill="#E1306C" 
                fillOpacity={0.8} 
              />
              <Area 
                type="monotone" 
                dataKey="facebook" 
                stackId="1" 
                stroke="#1877F2" 
                fill="#1877F2" 
                fillOpacity={0.6} 
              />
              <Area 
                type="monotone" 
                dataKey="linkedin" 
                stackId="1" 
                stroke="#0A66C2" 
                fill="#0A66C2" 
                fillOpacity={0.4} 
              />
              <Area 
                type="monotone" 
                dataKey="tiktok" 
                stackId="1" 
                stroke="#000000" 
                fill="#000000" 
                fillOpacity={0.2} 
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
      
      {/* Platform Distribution & Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%', borderRadius: 2, boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
            <Typography variant="h6" gutterBottom>Platform Distribution</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Breakdown of your data across platforms
            </Typography>
            <Box sx={{ height: 250, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={platformDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {platformDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`${value}%`, 'Percentage']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: '100%', borderRadius: 2, boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
            <Typography variant="h6" gutterBottom>Quick Access</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Manage key aspects of your project
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={4}>
                <Button 
                  variant="outlined" 
                  fullWidth 
                  startIcon={<InstagramIcon />}
                  sx={{ 
                    p: 1.5, 
                    justifyContent: 'flex-start',
                    borderColor: '#E1306C',
                    color: '#E1306C',
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
              <Grid item xs={6} md={4}>
                <Button 
                  variant="outlined" 
                  fullWidth 
                  startIcon={<FacebookIcon />}
                  sx={{ 
                    p: 1.5, 
                    justifyContent: 'flex-start',
                    borderColor: '#1877F2',
                    color: '#1877F2',
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
              <Grid item xs={6} md={4}>
                <Button 
                  variant="outlined" 
                  fullWidth 
                  startIcon={<LinkedInIcon />}
                  sx={{ 
                    p: 1.5, 
                    justifyContent: 'flex-start',
                    borderColor: '#0A66C2',
                    color: '#0A66C2',
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
              <Grid item xs={6} md={4}>
                <Button 
                  variant="outlined" 
                  fullWidth 
                  startIcon={<WhatsAppIcon />}
                  sx={{ 
                    p: 1.5, 
                    justifyContent: 'flex-start',
                    borderColor: '#000000',
                    color: '#000000',
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
              <Grid item xs={6} md={4}>
                <Button 
                  variant="outlined" 
                  fullWidth 
                  startIcon={<PersonIcon />}
                  sx={{ 
                    p: 1.5, 
                    justifyContent: 'flex-start',
                    borderColor: '#6200EA',
                    color: '#6200EA',
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
              <Grid item xs={6} md={4}>
                <Button 
                  variant="outlined" 
                  fullWidth 
                  startIcon={<BarChartIcon />}
                  sx={{ 
                    p: 1.5, 
                    justifyContent: 'flex-start',
                    borderColor: '#FFA000',
                    color: '#FFA000',
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
          </Paper>
        </Grid>
      </Grid>
      
      {/* Project Information */}
      <Paper sx={{ p: 3, mb: 4, borderRadius: 2, boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
        <Typography variant="h6" gutterBottom>Project Information</Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Owner
            </Typography>
            <Typography variant="body1" fontWeight={500}>
              {project.owner_name}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Created
            </Typography>
            <Typography variant="body1" fontWeight={500}>
              {new Date(project.created_at).toLocaleDateString()}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Last Updated
            </Typography>
            <Typography variant="body1" fontWeight={500}>
              {new Date(project.updated_at).toLocaleDateString()}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Organization
            </Typography>
            <Typography variant="body1" fontWeight={500}>
              {project.organization?.name || 'Personal'}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ProjectDashboard; 
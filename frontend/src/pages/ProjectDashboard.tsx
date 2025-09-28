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
import { 
  Home,
  FolderOpen,
  Instagram,
  Facebook,
  Linkedin,
  Users,
  BarChart3,
  HardDrive,
  TrendingUp,
  CreditCard,
  MoreHorizontal,
  Bell,
  RefreshCw,
  Calendar,
  Gauge,
  Settings,
  Sliders,
  Activity,
  Eye,
  Target,
  Award,
  Clock,
  MessageCircle
} from 'lucide-react';
import { apiFetch } from '../utils/api';
import StatCard from '../components/dashboard/StatCard';
import { dashboardService, DashboardStats, ActivityTimelineItem, PlatformDistributionItem, RecentActivityItem, TopPerformerItem, WeeklyGoalItem } from '../services/dashboardService';
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
  LineChart,
  Line,
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

// Dashboard data types using the dashboard service interfaces
type ProjectStats = DashboardStats;

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
  
  // Dashboard data state
  const [stats, setStats] = useState<ProjectStats>({
    totalPosts: 0,
    totalAccounts: 0,
    totalReports: 0,
    totalStorageUsed: '0 MB',
    creditBalance: 0,
    maxCredits: 0,
    engagementRate: 0,
    growthRate: 0,
    platforms: {},
    totalLikes: 0,
    totalComments: 0,
    totalShares: 0,
    totalViews: 0
  });
  const [activityData, setActivityData] = useState<ActivityTimelineItem[]>([]);
  const [platformDistribution, setPlatformDistribution] = useState<PlatformDistributionItem[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivityItem[]>([]);
  const [topPerformers, setTopPerformers] = useState<TopPerformerItem[]>([]);
  const [weeklyGoals, setWeeklyGoals] = useState<WeeklyGoalItem[]>([]);
  const [statsLoading, setStatsLoading] = useState(true);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  
  // Determine which URL pattern we're using
  const isOrgProjectUrl = location.pathname.includes('/organizations/') && location.pathname.includes('/projects/');

  // Function to fetch all dashboard data
  const fetchDashboardData = async () => {
    if (!projectId) return;

    try {
      setStatsLoading(true);
      setDashboardLoading(true);

      // Fetch all dashboard data in parallel
      const [statsData, activityTimeline, platformDist, recentAct, topPerf, weeklyGoalsData] = await Promise.all([
        dashboardService.getStats(projectId),
        dashboardService.getActivityTimeline(projectId),
        dashboardService.getPlatformDistribution(projectId),
        dashboardService.getRecentActivity(projectId),
        dashboardService.getTopPerformers(projectId),
        dashboardService.getWeeklyGoals(projectId)
      ]);

      setStats(statsData);
      setActivityData(activityTimeline);
      setPlatformDistribution(platformDist);
      setRecentActivity(recentAct);
      setTopPerformers(topPerf);
      setWeeklyGoals(weeklyGoalsData);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Don't set error state - just log it and keep using default values
    } finally {
      setStatsLoading(false);
      setDashboardLoading(false);
    }
  };

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
    fetchDashboardData();
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
      p: { xs: 2, md: 3, lg: 4 },
      flexGrow: 1,
      minHeight: '100vh'
    }}>
      <Box sx={{ mx: 'auto', maxWidth: 'none', width: '100%' }}>
        {/* Dashboard Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h4" fontWeight={600} gutterBottom>
                {project?.name || 'Project Dashboard'}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Track your social media performance and manage your content across platforms
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={<RefreshCw size={16} />}
              onClick={fetchDashboardData}
              disabled={statsLoading}
              sx={{ 
                borderColor: 'divider',
                color: 'text.secondary',
                '&:hover': { borderColor: 'primary.main' }
              }}
            >
              {statsLoading ? 'Refreshing...' : 'Refresh Stats'}
            </Button>
          </Box>
        </Box>

        {/* Dashboard Stats Cards */}
        <Grid container columns={12} spacing={4} sx={{ mb: 4 }}>
          <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3', xl: 'span 3' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="subtitle1" color="text.secondary" fontWeight={500}>Total Posts</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main, width: 48, height: 48 }}>
                  <BarChart3 size={22} />
                </Avatar>
              </Box>
              {statsLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CircularProgress size={24} color="primary" />
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    Loading...
                  </Typography>
                </Box>
              ) : (
                <>
                  <Typography variant="h3" fontWeight={700} gutterBottom sx={{ color: 'text.primary' }}>
                    {stats.totalPosts.toLocaleString()}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={`+12.5%`} 
                      size="small" 
                      sx={{ 
                        bgcolor: alpha(theme.palette.success.main, 0.1), 
                        color: theme.palette.success.main,
                        mr: 1,
                        fontWeight: 600
                      }} 
                    />
                    <Typography variant="body2" color="text.secondary">vs last period</Typography>
                  </Box>
                </>
              )}
            </Paper>
          </Grid>
          <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3', xl: 'span 3' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="subtitle1" color="text.secondary" fontWeight={500}>Total Accounts</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.secondary.main, 0.1), color: theme.palette.secondary.main, width: 48, height: 48 }}>
                  <Users size={22} />
                </Avatar>
              </Box>
              {statsLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CircularProgress size={24} color="secondary" />
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    Loading...
                  </Typography>
                </Box>
              ) : (
                <>
                  <Typography variant="h3" fontWeight={700} gutterBottom sx={{ color: 'text.primary' }}>
                    {stats.totalAccounts.toLocaleString()}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={`+5.2%`} 
                      size="small" 
                      sx={{ 
                        bgcolor: alpha(theme.palette.success.main, 0.1), 
                        color: theme.palette.success.main,
                        mr: 1,
                        fontWeight: 600
                      }} 
                    />
                    <Typography variant="body2" color="text.secondary">vs last period</Typography>
                  </Box>
                </>
              )}
            </Paper>
          </Grid>
          <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3', xl: 'span 3' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="subtitle1" color="text.secondary" fontWeight={500}>Engagement Rate</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1), color: theme.palette.success.main, width: 48, height: 48 }}>
                  <TrendingUp size={22} />
                </Avatar>
              </Box>
              {statsLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CircularProgress size={24} color="success" />
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    Loading...
                  </Typography>
                </Box>
              ) : (
                <>
                  <Typography variant="h3" fontWeight={700} gutterBottom sx={{ color: 'text.primary' }}>
                    {stats.engagementRate}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={`+0.8%`} 
                      size="small" 
                      sx={{ 
                        bgcolor: alpha(theme.palette.success.main, 0.1), 
                        color: theme.palette.success.main,
                        mr: 1,
                        fontWeight: 600
                      }} 
                    />
                    <Typography variant="body2" color="text.secondary">vs last period</Typography>
                  </Box>
                </>
              )}
            </Paper>
          </Grid>
          <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3', xl: 'span 3' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="subtitle1" color="text.secondary" fontWeight={500}>Storage Used</Typography>
                <Avatar sx={{ bgcolor: alpha(theme.palette.warning.main, 0.1), color: theme.palette.warning.main, width: 48, height: 48 }}>
                  <HardDrive size={22} />
                </Avatar>
              </Box>
              {statsLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CircularProgress size={24} color="warning" />
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    Loading...
                  </Typography>
                </Box>
              ) : (
                <>
                  <Typography variant="h3" fontWeight={700} gutterBottom sx={{ color: 'text.primary' }}>
                    {stats.totalStorageUsed}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={`${Math.round((stats.creditBalance / stats.maxCredits) * 100)}%`} 
                      size="small" 
                      sx={{ 
                        bgcolor: alpha(theme.palette.info.main, 0.1), 
                        color: theme.palette.info.main,
                        mr: 1,
                        fontWeight: 600
                      }} 
                    />
                    <Typography variant="body2" color="text.secondary">of quota used</Typography>
                  </Box>
                </>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Activity and Platform Distribution Charts */}
        <Grid container columns={12} spacing={4} sx={{ mb: 4 }}>
          <Grid gridColumn={{ xs: 'span 12', lg: 'span 7', xl: 'span 8' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box>
                  <Typography variant="h6" fontWeight={600}>Activity Overview</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Posts and engagements across platforms over time
                  </Typography>
                </Box>
                <Box>
                  <Button 
                    variant="text" 
                    endIcon={<Calendar size={16} />}
                    sx={{ color: 'text.secondary' }}
                    size="small"
                  >
                    Last 30 Days
                  </Button>
                </Box>
              </Box>
              <Box sx={{ height: { xs: 320, lg: 420, xl: 480 }, width: '100%', mt: 2 }}>
                {dashboardLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={activityData.length > 0 ? activityData : [{ date: 'No Data', instagram: 0, facebook: 0, linkedin: 0, tiktok: 0 }]}
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
                )}
              </Box>
            </Paper>
          </Grid>
          
          <Grid gridColumn={{ xs: 'span 12', lg: 'span 5', xl: 'span 4' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" fontWeight={600}>Platform Distribution</Typography>
                <IconButton size="small">
                  <MoreHorizontal size={16} />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Breakdown of your data across platforms
              </Typography>
              
              <Box sx={{ height: { xs: 240, lg: 340, xl: 400 }, display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 2 }}>
                {dashboardLoading ? (
                  <CircularProgress />
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={platformDistribution.length > 0 ? platformDistribution : [
                          { name: 'No Data', value: 100, color: '#e0e0e0' }
                        ]}
                        cx="50%"
                        cy="50%"
                        innerRadius={80}
                        outerRadius={120}
                        paddingAngle={4}
                        dataKey="value"
                        strokeWidth={1}
                        stroke="#fff"
                      >
                        {(platformDistribution.length > 0 ? platformDistribution : [
                          { name: 'No Data', value: 100, color: '#e0e0e0' }
                        ]).map((entry, index) => (
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
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Additional Dashboard Content */}
        <Grid container columns={12} spacing={4} sx={{ mb: 4 }}>
          {/* Recent Activity */}
          <Grid gridColumn={{ xs: 'span 12', md: 'span 6', lg: 'span 4' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" fontWeight={600}>Recent Activity</Typography>
                <IconButton size="small">
                  <RefreshCw size={16} />
                </IconButton>
              </Box>
              {dashboardLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                <Stack spacing={2.5}>
                  {recentActivity.length > 0 ? recentActivity.map((activity) => (
                    <Box key={activity.id} sx={{ display: 'flex', alignItems: 'center', gap: 2.5 }}>
                      <Avatar sx={{
                        bgcolor: activity.type === 'upload' ? alpha(theme.palette.primary.main, 0.1) :
                                  activity.type === 'analysis' ? alpha(theme.palette.success.main, 0.1) :
                                  activity.type === 'report' ? alpha(theme.palette.warning.main, 0.1) :
                                  alpha(theme.palette.info.main, 0.1),
                        color: activity.type === 'upload' ? theme.palette.primary.main :
                               activity.type === 'analysis' ? theme.palette.success.main :
                               activity.type === 'report' ? theme.palette.warning.main :
                               theme.palette.info.main,
                        width: 40,
                        height: 40
                      }}>
                        {activity.type === 'upload' && <Activity size={18} />}
                        {activity.type === 'analysis' && <Target size={18} />}
                        {activity.type === 'report' && <BarChart3 size={18} />}
                        {activity.type === 'import' && <HardDrive size={18} />}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="body2" fontWeight={500}>{activity.action}</Typography>
                        <Typography variant="caption" color="text.secondary">{activity.time}</Typography>
                      </Box>
                    </Box>
                  )) : (
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                      No recent activity
                    </Typography>
                  )}
                </Stack>
              )}
            </Paper>
          </Grid>

          {/* Top Performers */}
          <Grid gridColumn={{ xs: 'span 12', md: 'span 6', lg: 'span 4' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" fontWeight={600}>Top Performers</Typography>
                <IconButton size="small">
                  <Award size={16} />
                </IconButton>
              </Box>
              {dashboardLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                <Stack spacing={3.5}>
                  {topPerformers.length > 0 ? topPerformers.map((performer, index) => (
                    <Box key={index}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar sx={{
                            bgcolor: performer.platform === 'Instagram' ? '#E1306C' :
                                     performer.platform === 'Facebook' ? '#1877F2' :
                                     '#0A66C2',
                            width: 36,
                            height: 36
                          }}>
                            {performer.platform === 'Instagram' && <Instagram size={16} />}
                            {performer.platform === 'Facebook' && <Facebook size={16} />}
                            {performer.platform === 'LinkedIn' && <Linkedin size={16} />}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>{performer.account}</Typography>
                            <Typography variant="caption" color="text.secondary">{performer.platform}</Typography>
                          </Box>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="body2" fontWeight={600}>{performer.engagement}</Typography>
                          <Typography variant="caption" color="success.main">{performer.growth}</Typography>
                        </Box>
                      </Box>
                      {index < topPerformers.length - 1 && <Divider />}
                    </Box>
                  )) : (
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                      No top performers data
                    </Typography>
                  )}
                </Stack>
              )}
            </Paper>
          </Grid>

          {/* Weekly Goals */}
          <Grid gridColumn={{ xs: 'span 12', md: 'span 12', lg: 'span 4' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', height: '100%', border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" fontWeight={600}>Weekly Goals</Typography>
                <IconButton size="small">
                  <Target size={16} />
                </IconButton>
              </Box>
              {dashboardLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                <Stack spacing={3.5}>
                  {weeklyGoals.length > 0 ? weeklyGoals.map((goal, index) => (
                    <Box key={index}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                        <Typography variant="body2" fontWeight={500}>{goal.goal}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {goal.goal === 'Engagement Rate' ? `${goal.current}% / ${goal.target}%` : `${goal.current} / ${goal.target}`}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={goal.percentage}
                        sx={{
                          height: 10,
                          borderRadius: 5,
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 5
                          }
                        }}
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        {goal.percentage}% complete
                      </Typography>
                    </Box>
                  )) : (
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                      No weekly goals data
                    </Typography>
                  )}
                </Stack>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Quick Access Platform Buttons */}
        <Grid container columns={12} spacing={4}>
          <Grid gridColumn={{ xs: 'span 12' }}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 3, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Quick Access</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                Navigate to different platform data and tools
              </Typography>
              <Grid container columns={12} spacing={3}>
                <Grid gridColumn={{ xs: 'span 6', sm: 'span 4', md: 'span 3', lg: 'span 2', xl: 'span 2' }}>
                  <Button 
                    variant="outlined" 
                    fullWidth 
                    startIcon={<Instagram size={20} />}
                    sx={{ 
                      p: 3,
                      py: 3, 
                      justifyContent: 'flex-start',
                      borderColor: '#E1306C',
                      color: '#E1306C',
                      borderRadius: 3,
                      fontWeight: 600,
                      fontSize: '0.95rem',
                      '&:hover': {
                        borderColor: '#E1306C',
                        backgroundColor: 'rgba(225, 48, 108, 0.06)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 16px rgba(225, 48, 108, 0.25)'
                      },
                      transition: 'all 0.2s ease-in-out'
                    }}
                    onClick={() => {
                      handleNavigate(`/organizations/${organizationId}/projects/${projectId}/instagram-folders`);
                    }}
                  >
                    Instagram
                  </Button>
                </Grid>
                <Grid gridColumn={{ xs: 'span 6', sm: 'span 4', md: 'span 3', lg: 'span 2', xl: 'span 2' }}>
                  <Button 
                    variant="outlined" 
                    fullWidth 
                    startIcon={<Facebook size={20} />}
                    sx={{ 
                      p: 3,
                      py: 3, 
                      justifyContent: 'flex-start',
                      borderColor: '#1877F2',
                      color: '#1877F2',
                      borderRadius: 3,
                      fontWeight: 600,
                      fontSize: '0.95rem',
                      '&:hover': {
                        borderColor: '#1877F2',
                        backgroundColor: 'rgba(24, 119, 242, 0.06)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 16px rgba(24, 119, 242, 0.25)'
                      },
                      transition: 'all 0.2s ease-in-out'
                    }}
                    onClick={() => {
                      handleNavigate(`/organizations/${organizationId}/projects/${projectId}/facebook-folders`);
                    }}
                  >
                    Facebook
                  </Button>
                </Grid>
                <Grid gridColumn={{ xs: 'span 6', sm: 'span 4', md: 'span 3', lg: 'span 2', xl: 'span 2' }}>
                  <Button 
                    variant="outlined" 
                    fullWidth 
                    startIcon={<Linkedin size={20} />}
                    sx={{ 
                      p: 3,
                      py: 3, 
                      justifyContent: 'flex-start',
                      borderColor: '#0A66C2',
                      color: '#0A66C2',
                      borderRadius: 3,
                      fontWeight: 600,
                      fontSize: '0.95rem',
                      '&:hover': {
                        borderColor: '#0A66C2',
                        backgroundColor: 'rgba(10, 102, 194, 0.06)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 16px rgba(10, 102, 194, 0.25)'
                      },
                      transition: 'all 0.2s ease-in-out'
                    }}
                    onClick={() => {
                      handleNavigate(`/organizations/${organizationId}/projects/${projectId}/linkedin-folders`);
                    }}
                  >
                    LinkedIn
                  </Button>
                </Grid>
                <Grid gridColumn={{ xs: 'span 6', sm: 'span 4', md: 'span 3', lg: 'span 2', xl: 'span 2' }}>
                  <Button 
                    variant="outlined" 
                    fullWidth 
                    startIcon={<MessageCircle size={20} />}
                    sx={{ 
                      p: 3,
                      py: 3, 
                      justifyContent: 'flex-start',
                      borderColor: '#000000',
                      color: '#000000',
                      borderRadius: 3,
                      fontWeight: 600,
                      fontSize: '0.95rem',
                      '&:hover': {
                        borderColor: '#000000',
                        backgroundColor: 'rgba(0, 0, 0, 0.06)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 16px rgba(0, 0, 0, 0.25)'
                      },
                      transition: 'all 0.2s ease-in-out'
                    }}
                    onClick={() => {
                      handleNavigate(`/organizations/${organizationId}/projects/${projectId}/tiktok-folders`);
                    }}
                  >
                    TikTok
                  </Button>
                </Grid>
                <Grid gridColumn={{ xs: 'span 6', sm: 'span 4', md: 'span 3', lg: 'span 2', xl: 'span 2' }}>
                  <Button 
                    variant="outlined" 
                    fullWidth 
                    startIcon={<Users size={20} />}
                    sx={{ 
                      p: 3,
                      py: 3, 
                      justifyContent: 'flex-start',
                      borderColor: '#6200EA',
                      color: '#6200EA',
                      borderRadius: 3,
                      fontWeight: 600,
                      fontSize: '0.95rem',
                      '&:hover': {
                        borderColor: '#6200EA',
                        backgroundColor: 'rgba(98, 0, 234, 0.06)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 16px rgba(98, 0, 234, 0.25)'
                      },
                      transition: 'all 0.2s ease-in-out'
                    }}
                    onClick={() => {
                      handleNavigate(`/organizations/${organizationId}/projects/${projectId}/track-accounts/accounts`);
                    }}
                  >
                    Accounts
                  </Button>
                </Grid>
                <Grid gridColumn={{ xs: 'span 6', sm: 'span 4', md: 'span 3', lg: 'span 2', xl: 'span 2' }}>
                  <Button 
                    variant="outlined" 
                    fullWidth 
                    startIcon={<BarChart3 size={20} />}
                    sx={{ 
                      p: 3,
                      py: 3, 
                      justifyContent: 'flex-start',
                      borderColor: '#FFA000',
                      color: '#FFA000',
                      borderRadius: 3,
                      fontWeight: 600,
                      fontSize: '0.95rem',
                      '&:hover': {
                        borderColor: '#FFA000',
                        backgroundColor: 'rgba(255, 160, 0, 0.06)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 16px rgba(255, 160, 0, 0.25)'
                      },
                      transition: 'all 0.2s ease-in-out'
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
      </Box>
    </Box>
  );
};

export default ProjectDashboard; 
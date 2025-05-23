import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid as MuiGrid,
  Card,
  CardContent,
  Divider,
  Stack,
  Button,
  useTheme,
  alpha,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import {
  IconTrendingUp,
  IconTrendingDown,
  IconUsers,
  IconEye,
  IconMouse,
  IconClock,
  IconWorldWww,
  IconDeviceMobile,
  IconDeviceDesktop,
  IconArrowUpRight,
  IconArrowDownRight,
  IconDots,
  IconRefresh,
  IconDownload,
  IconFilter,
  IconCalendar,
  IconMapPin,
  IconChartLine,
  IconChartArea,
  IconChartBar,
  IconInfoCircle,
} from '@tabler/icons-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { apiFetch } from '../utils/api';

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
}

// Web analytics data structure
interface WebAnalytics {
  visitors: number;
  pageViews: number;
  bounceRate: number;
  avgSessionDuration: string;
  newUsers: number;
  returningUsers: number;
  visitorsChange: number;
  pageViewsChange: number;
  bounceRateChange: number;
  newUsersChange: number;
}

// Sample web analytics data with multiple metrics
const dailyTrafficData = [
  { date: 'May 16', visitors: 7500, pageViews: 12800, bounceRate: 2.1, sessions: 6200 },
  { date: 'May 17', visitors: 2800, pageViews: 8200, bounceRate: 2.3, sessions: 2400 },
  { date: 'May 18', visitors: 2400, pageViews: 7900, bounceRate: 2.0, sessions: 2100 },
  { date: 'May 19', visitors: 6200, pageViews: 15400, bounceRate: 1.8, sessions: 5800 },
  { date: 'May 20', visitors: 5800, pageViews: 14200, bounceRate: 1.9, sessions: 5400 },
  { date: 'May 21', visitors: 5900, pageViews: 14800, bounceRate: 2.2, sessions: 5600 },
  { date: 'May 22', visitors: 5900, pageViews: 14800, bounceRate: 2.0, sessions: 5600 },
  { date: 'May 23', visitors: 5600, pageViews: 13900, bounceRate: 1.7, sessions: 5200 },
];

const sessionData = [
  { name: 'New Users', value: 452, color: '#1976d2' },
  { name: 'Returning Users', value: 21248, color: '#e3f2fd' },
];

const countryData = [
  { country: 'United States', users: 8420, percentage: 35.2 },
  { country: 'United Kingdom', users: 3210, percentage: 13.4 },
  { country: 'Germany', users: 2890, percentage: 12.1 },
  { country: 'France', users: 2340, percentage: 9.8 },
  { country: 'Canada', users: 1980, percentage: 8.3 },
  { country: 'Others', users: 5160, percentage: 21.2 },
];

const Dashboard3 = () => {
  const theme = useTheme();
  const { projectId, organizationId } = useParams<{ 
    projectId: string;
    organizationId?: string;
  }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState(0);
  const [chartType, setChartType] = useState('area');
  
  // Web analytics metrics
  const [analytics, setAnalytics] = useState<WebAnalytics>({
    visitors: 37600,
    pageViews: 41000,
    bounceRate: 0.0,
    avgSessionDuration: '2m 56s',
    newUsers: 452,
    returningUsers: 21248,
    visitorsChange: 0.31,
    pageViewsChange: 0.35,
    bounceRateChange: -2.1,
    newUsersChange: 12.3,
  });

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
      } catch (error) {
        console.error('Error fetching project:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProject();
  }, [projectId]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const getMetricByTab = () => {
    switch (selectedTab) {
      case 0: return { key: 'visitors', label: 'Visitors', value: analytics.visitors, change: analytics.visitorsChange };
      case 1: return { key: 'pageViews', label: 'Page Views', value: analytics.pageViews, change: analytics.pageViewsChange };
      case 2: return { key: 'bounceRate', label: 'Bounce Rate', value: analytics.bounceRate, change: analytics.bounceRateChange, suffix: '%' };
      case 3: return { key: 'sessions', label: 'Sessions', value: 0, change: 0 };
      default: return { key: 'visitors', label: 'Visitors', value: analytics.visitors, change: analytics.visitorsChange };
    }
  };

  const getCurrentDataKey = () => {
    switch (selectedTab) {
      case 0: return 'visitors';
      case 1: return 'pageViews';
      case 2: return 'bounceRate';
      case 3: return 'sessions';
      default: return 'visitors';
    }
  };

  const renderChart = () => {
    const dataKey = getCurrentDataKey();
    const commonProps = {
      data: dailyTrafficData,
      children: [
        <CartesianGrid key="grid" strokeDasharray="3 3" stroke="#f0f0f0" />,
        <XAxis 
          key="xaxis"
          dataKey="date" 
          tick={{ fill: '#666', fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />,
        <YAxis 
          key="yaxis"
          tick={{ fill: '#666', fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />,
        <Tooltip 
          key="tooltip"
          contentStyle={{ 
            borderRadius: 8, 
            border: '1px solid #e0e0e0',
            boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
            background: '#fff'
          }}
        />
      ]
    };

    switch (chartType) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            {commonProps.children}
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke="#1976d2" 
              strokeWidth={2}
              dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        );
      case 'bar':
        return (
          <BarChart {...commonProps}>
            {commonProps.children}
            <Bar 
              dataKey={dataKey} 
              fill="rgba(25, 118, 210, 0.8)" 
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        );
      default: // area
        return (
          <AreaChart {...commonProps}>
            {commonProps.children}
            <Area 
              type="monotone" 
              dataKey={dataKey} 
              stroke="#1976d2" 
              fill="rgba(25, 118, 210, 0.1)" 
              strokeWidth={2}
              dot={false}
            />
          </AreaChart>
        );
    }
  };

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '50vh' 
      }}>
        <Typography variant="h6" color="text.secondary">
          Loading...
        </Typography>
      </Box>
    );
  }

  const currentMetric = getMetricByTab();
  const lastUpdated = new Date().toLocaleString();

  return (
    <Box sx={{ 
      p: 3, 
      bgcolor: '#f8f9fa',
      minHeight: '100vh',
      width: '100%'
    }}>
      {/* Header with Last Updated */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 3,
        flexWrap: 'wrap',
        gap: 2
      }}>
        <Box>
          <Typography 
            variant="h4" 
            fontWeight={600} 
            sx={{ mb: 0.5, color: 'text.primary' }}
          >
            Web Analytics
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body1" color="text.secondary">
              {project?.name || 'Nike'} • Real-time insights
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 2 }}>
              <IconInfoCircle size={16} color={theme.palette.text.secondary} />
              <Typography variant="body2" color="text.secondary">
                Last updated: {lastUpdated}
              </Typography>
            </Box>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<IconCalendar size={16} />}
            sx={{ 
              borderColor: 'divider',
              color: 'text.secondary',
              bgcolor: 'background.paper'
            }}
          >
            Last 7 days
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<IconRefresh size={16} />}
            sx={{ 
              borderColor: 'divider',
              color: 'text.secondary',
              bgcolor: 'background.paper'
            }}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Web Engagement Section with Tabs and Integrated Metrics */}
      <Card 
        elevation={0} 
        sx={{ 
          p: 0, 
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 2,
          bgcolor: 'background.paper',
          mb: 4
        }}
      >
        {/* Tabs Header */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 3, pt: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Web Engagement
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <Select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value)}
                  displayEmpty
                  sx={{ fontSize: '0.875rem' }}
                >
                  <MenuItem value="area">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <IconChartArea size={16} />
                      Area Chart
                    </Box>
                  </MenuItem>
                  <MenuItem value="line">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <IconChartLine size={16} />
                      Line Chart
                    </Box>
                  </MenuItem>
                  <MenuItem value="bar">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <IconChartBar size={16} />
                      Bar Chart
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
              <Button 
                size="small"
                variant="text"
                endIcon={<IconArrowUpRight size={14} />}
                sx={{ color: 'primary.main', fontWeight: 500 }}
              >
                Open Analysis
              </Button>
              <Button 
                size="small"
                variant="text"
                sx={{ color: 'text.secondary', minWidth: 'auto', p: 1 }}
              >
                <IconDots size={16} />
              </Button>
            </Box>
          </Box>
          <Tabs 
            value={selectedTab} 
            onChange={handleTabChange}
            sx={{ 
              px: 3,
              '& .MuiTab-root': {
                textTransform: 'none',
                fontWeight: 500,
                minWidth: 'auto',
                px: 2
              }
            }}
          >
            <Tab label="Visitors" />
            <Tab label="Page Views" />
            <Tab label="Bounce Rate" />
            <Tab label="Page Views Per Session" />
          </Tabs>
        </Box>

        {/* Metric Display and Chart */}
        <Box sx={{ p: 3 }}>
          {/* Current Metric Display */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {currentMetric.label}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 2 }}>
              <Typography variant="h3" fontWeight={700} color="text.primary">
                {typeof currentMetric.value === 'number' ? currentMetric.value.toLocaleString() : currentMetric.value}
                {currentMetric.suffix || ''}
              </Typography>
              {currentMetric.change !== 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {currentMetric.change > 0 ? (
                    <IconArrowUpRight size={16} color={theme.palette.success.main} />
                  ) : (
                    <IconArrowDownRight size={16} color={theme.palette.error.main} />
                  )}
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: 600,
                      color: currentMetric.change > 0 ? 'success.main' : 'error.main'
                    }}
                  >
                    {Math.abs(currentMetric.change)}%
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>

          {/* Chart */}
          <Box sx={{ height: 300, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              {renderChart()}
            </ResponsiveContainer>
          </Box>
        </Box>
      </Card>

      {/* Main Charts - CSS Grid */}
      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          lg: '2fr 1fr'
        },
        gap: 3,
        mb: 4
      }}>
        {/* Current Live Users */}
        <Card 
          elevation={0} 
          sx={{ 
            p: 3, 
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            bgcolor: 'background.paper',
          }}
        >
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Current live users
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Box 
              sx={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                bgcolor: 'success.main',
                mr: 1,
                animation: 'pulse 1.5s infinite'
              }} 
            />
            <Typography variant="body2" color="text.secondary">
              Realtime
            </Typography>
          </Box>
          
          {/* Donut Chart */}
          <Box sx={{ position: 'relative', height: 180, mb: 3 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sessionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {sessionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <Box sx={{ 
              position: 'absolute', 
              top: '50%', 
              left: '50%', 
              transform: 'translate(-50%, -50%)',
              textAlign: 'center'
            }}>
              <Typography variant="h4" fontWeight={700} color="primary.main">
                21.7k
              </Typography>
            </Box>
          </Box>

          {/* Session Metrics */}
          <Stack spacing={2}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                New Users
              </Typography>
              <Typography variant="h6" fontWeight={600}>
                {analytics.newUsers}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Avg session duration
              </Typography>
              <Typography variant="h6" fontWeight={600}>
                {analytics.avgSessionDuration}
              </Typography>
            </Box>
          </Stack>
        </Card>

        {/* Placeholder for second chart */}
        <Card 
          elevation={0} 
          sx={{ 
            p: 3, 
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            bgcolor: 'background.paper',
          }}
        >
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Additional Metrics
          </Typography>
          <Box sx={{ 
            height: 200, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            bgcolor: '#f8f9fa',
            borderRadius: 2,
            border: '1px dashed',
            borderColor: 'divider'
          }}>
            <Typography variant="body2" color="text.secondary">
              Additional chart content
            </Typography>
          </Box>
        </Card>
      </Box>

      {/* Bottom Section - CSS Grid */}
      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          lg: 'repeat(2, 1fr)'
        },
        gap: 3,
        mb: 4
      }}>
        {/* Country Breakdown */}
        <Card 
          elevation={0} 
          sx={{ 
            p: 3, 
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            bgcolor: 'background.paper',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" fontWeight={600}>
              Breakdown of users by country
            </Typography>
            <Box sx={{ ml: 1, color: 'text.secondary' }}>
              <IconMapPin size={16} />
            </Box>
          </Box>
          <Stack spacing={2}>
            {countryData.map((country, index) => (
              <Box key={country.country} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" fontWeight={500}>
                      {country.country}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {country.percentage}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={country.percentage}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: '#f0f0f0',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 3,
                        backgroundColor: '#1976d2'
                      }
                    }}
                  />
                </Box>
                <Typography variant="body2" fontWeight={600} sx={{ minWidth: 60, textAlign: 'right' }}>
                  {country.users.toLocaleString()}
                </Typography>
              </Box>
            ))}
          </Stack>
        </Card>

        {/* Realtime Map */}
        <Card 
          elevation={0} 
          sx={{ 
            p: 3, 
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            bgcolor: 'background.paper',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Box 
              sx={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                bgcolor: 'success.main',
                mr: 1,
                animation: 'pulse 1.5s infinite'
              }} 
            />
            <Typography variant="h6" fontWeight={600} color="primary.main">
              Realtime users by location
            </Typography>
          </Box>
          <Box sx={{ 
            height: 200, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            bgcolor: '#f8f9fa',
            borderRadius: 2,
            border: '1px dashed',
            borderColor: 'divider'
          }}>
            <Typography variant="body2" color="text.secondary">
              Interactive map visualization
            </Typography>
          </Box>
        </Card>
      </Box>

      {/* Templates Section */}
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" fontWeight={600}>
            Templates
          </Typography>
          <Button 
            size="small"
            variant="text"
            sx={{ color: 'primary.main', fontWeight: 500 }}
          >
            See All
          </Button>
        </Box>
        <Box sx={{ 
          display: 'grid',
          gridTemplateColumns: {
            xs: 'repeat(2, 1fr)',
            sm: 'repeat(3, 1fr)',
            md: 'repeat(6, 1fr)'
          },
          gap: 2
        }}>
          {[
            { name: 'User Activity', icon: '👤', charts: '10 Charts' },
            { name: 'Marketing Analytics', icon: '📊', charts: '14 Charts' },
            { name: 'Session Engagement', icon: '📈', charts: '6 Charts' },
            { name: 'Product KPIs', icon: '📋', charts: '9 Charts' },
            { name: 'Media', icon: '🎬', charts: '12 Charts' },
            { name: 'Feature Adoption', icon: '⚡', charts: '8 Charts' },
          ].map((template, index) => (
            <Card 
              key={template.name}
              elevation={0} 
              sx={{ 
                p: 2, 
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                bgcolor: 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                textAlign: 'center',
                '&:hover': {
                  borderColor: 'primary.main',
                  boxShadow: '0 4px 20px rgba(25, 118, 210, 0.1)',
                }
              }}
            >
              <Typography variant="h5" sx={{ mb: 1 }}>
                {template.icon}
              </Typography>
              <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>
                {template.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Dashboard • {template.charts}
              </Typography>
            </Card>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard3; 
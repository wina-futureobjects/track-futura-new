import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  Alert,
  Button,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  CheckCircle,
  Schedule,
  Error,
  Refresh,
  TrendingUp,
  DataUsage
} from '@mui/icons-material';
import { format } from 'date-fns';
import { apifyMonitorService, ApifyScraperRequest, ApifyPollingStatus } from '../services/apifyMonitorService';

const ApifyMonitorDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [pollingStatus, setPollingStatus] = useState<ApifyPollingStatus | null>(null);
  const [recentRequests, setRecentRequests] = useState<ApifyScraperRequest[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchData = async () => {
    try {
      setError(null);
      const [status, requests, statistics] = await Promise.all([
        apifyMonitorService.getPollingStatus(),
        apifyMonitorService.getScraperRequests(10),
        apifyMonitorService.getStats()
      ]);

      setPollingStatus(status);
      setRecentRequests(requests);
      setStats(statistics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch Apify data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Auto-refresh every 30 seconds to match polling interval
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchData, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'pending': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle color="success" />;
      case 'processing': return <CircularProgress size={20} />;
      case 'pending': return <Schedule color="info" />;
      case 'failed': return <Error color="error" />;
      default: return <DataUsage />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
        <Typography variant="body2" sx={{ ml: 2 }}>
          Loading Apify status...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h2">
          🔄 Apify Integration Monitor
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            size="small"
            variant={autoRefresh ? "contained" : "outlined"}
            startIcon={autoRefresh ? <Pause /> : <PlayArrow />}
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? 'Stop' : 'Start'} Auto-refresh
          </Button>
          <Button
            size="small"
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchData}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        {/* Polling Status Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📡 Polling Status
              </Typography>
              {pollingStatus && (
                <Box>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <Chip
                      icon={pollingStatus.is_polling ? <PlayArrow /> : <Pause />}
                      label={pollingStatus.is_polling ? 'Active' : 'Inactive'}
                      color={pollingStatus.is_polling ? 'success' : 'error'}
                      size="small"
                    />
                    <Typography variant="body2" color="text.secondary">
                      Every {pollingStatus.polling_interval}s
                    </Typography>
                  </Box>
                  <Typography variant="body2">
                    Active Requests: <strong>{pollingStatus.active_requests}</strong>
                  </Typography>
                  {pollingStatus.last_poll_time && (
                    <Typography variant="body2" color="text.secondary">
                      Last Poll: {format(new Date(pollingStatus.last_poll_time), 'HH:mm:ss')}
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Statistics
              </Typography>
              {stats && (
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Total Requests
                    </Typography>
                    <Typography variant="h6">{stats.total_requests}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Success Rate
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      {stats.success_rate.toFixed(1)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Active
                    </Typography>
                    <Typography variant="h6" color="warning.main">
                      {stats.active_requests}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Recent (24h)
                    </Typography>
                    <Typography variant="h6" color="info.main">
                      {stats.recent_requests_24h}
                    </Typography>
                  </Grid>
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Requests */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🔄 Recent Scraper Requests
              </Typography>
              {recentRequests.length > 0 ? (
                <List dense>
                  {recentRequests.slice(0, 5).map((request, index) => (
                    <React.Fragment key={request.id}>
                      <ListItem>
                        <ListItemIcon>
                          {getStatusIcon(request.status)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="body2">
                                {request.platform.replace('_posts', '').toUpperCase()}
                              </Typography>
                              <Chip
                                label={request.status}
                                color={getStatusColor(request.status) as any}
                                size="small"
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="caption" display="block">
                                ID: {request.request_id}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Created: {format(new Date(request.created_at), 'MMM dd, HH:mm')}
                              </Typography>
                              {request.completed_at && (
                                <Typography variant="caption" color="text.secondary" display="block">
                                  Completed: {format(new Date(request.completed_at), 'MMM dd, HH:mm')}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < recentRequests.slice(0, 5).length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No recent scraper requests found
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {pollingStatus?.is_polling && (
        <Box mt={2}>
          <Alert severity="success" icon={<TrendingUp />}>
            <strong>Apify Polling Active!</strong> The system is automatically checking for completed scraping jobs every {pollingStatus.polling_interval} seconds.
          </Alert>
        </Box>
      )}
    </Box>
  );
};

export default ApifyMonitorDashboard;
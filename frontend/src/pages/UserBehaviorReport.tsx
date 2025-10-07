import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider
} from '@mui/material';
import { ArrowBack, Person, Insights, Lightbulb, Download } from '@mui/icons-material';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { FUTUREOBJECTS_COLORS } from '../constants/colors';
import { generateEnhancedPDF } from '../utils/enhancedPdfGenerator';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { fetchUserBehaviorReport } from '../services/templateReportService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const UserBehaviorReport: React.FC = () => {
  const { id, organizationId, projectId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfGenerating, setPdfGenerating] = useState(false);

  useEffect(() => {
    loadReport();
  }, [id]);

  const loadReport = async () => {
    try {
      setLoading(true);
      console.log('🚀 FRONTEND: Fetching User Behavior Report ID:', id);

      const data = await fetchUserBehaviorReport(Number(id));
      console.log('✅ FRONTEND: USER BEHAVIOR DATA RECEIVED:', data);
      setReport(data);
    } catch (err: any) {
      console.error('❌ FRONTEND ERROR:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (organizationId && projectId) {
      navigate(`/organizations/${organizationId}/projects/${projectId}/reports/generated`);
    } else {
      navigate('/reports/generated');
    }
  };

  const handleDownloadPDF = async () => {
    try {
      setPdfGenerating(true);
      console.log('Generating enhanced PDF with AI analysis...');

      const reportType = report?.template_type || 'User Behavior';

      await generateEnhancedPDF(
        Number(id),
        report?.title || 'User Behavior Report',
        reportType,
        results
      );
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setPdfGenerating(false);
    }
  };

  const COLORS = FUTUREOBJECTS_COLORS;

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !report) {
    return (
      <Container>
        <Typography color="error">Error loading report: {error}</Typography>
        <Button onClick={handleBack}>Go Back</Button>
      </Container>
    );
  }

  const results = report.results || {};

  return (
    <Box sx={{ bgcolor: COLORS.background, minHeight: '100vh', width: '100%' }}>
    <Container maxWidth="xl" sx={{ py: 4 }} id="report-content">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={handleBack}
          sx={{
            mb: 3,
            color: COLORS.dark,
            fontWeight: 500,
            '&:hover': { bgcolor: 'rgba(79, 209, 197, 0.08)' }
          }}
        >
          Back to Reports
        </Button>

        <Paper elevation={0} sx={{ p: 4, border: `1px solid ${COLORS.border}`, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <Box sx={{
              bgcolor: COLORS.primary,
              p: 2,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Person sx={{ fontSize: 36, color: 'white' }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" fontWeight={700} color={COLORS.dark} sx={{ mb: 1.5 }}>
                {report.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Chip
                  label="User Behavior Analysis"
                  sx={{
                    bgcolor: `${COLORS.primary}20`,
                    color: COLORS.primaryDark,
                    fontWeight: 600,
                    border: `1px solid ${COLORS.primary}40`,
                    fontSize: '0.875rem'
                  }}
                />
                <Chip
                  label={report.status}
                  sx={{
                    bgcolor: `${COLORS.accent}20`,
                    color: COLORS.accent,
                    fontWeight: 600,
                    border: `1px solid ${COLORS.accent}40`,
                    textTransform: 'capitalize',
                    fontSize: '0.875rem'
                  }}
                />
              </Box>
            </Box>
            <Button
              variant="contained"
              startIcon={pdfGenerating ? <CircularProgress size={20} color="inherit" /> : <Download />}
              onClick={handleDownloadPDF}
              disabled={pdfGenerating}
              sx={{
                bgcolor: COLORS.primary,
                color: 'white',
                fontWeight: 600,
                px: 3,
                py: 1.5,
                '&:hover': {
                  bgcolor: COLORS.primaryDark
                },
                '&:disabled': {
                  bgcolor: COLORS.lightGray,
                  color: 'white'
                },
                '@media print': {
                  display: 'none'
                }
              }}
            >
              {pdfGenerating ? 'Generating...' : 'Download PDF'}
            </Button>
          </Box>
        </Paper>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <Card elevation={0} sx={{
            height: '100%',
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            transition: 'all 0.3s',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: `0 12px 24px -10px ${COLORS.primary}40`,
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color={COLORS.lightGray} sx={{ mb: 2, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.75rem' }}>
                Total Users
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                {results.total_users?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                All users tracked
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <Card elevation={0} sx={{
            height: '100%',
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            transition: 'all 0.3s',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: `0 12px 24px -10px ${COLORS.primary}40`,
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color={COLORS.lightGray} sx={{ mb: 2, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.75rem' }}>
                Active Users
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                {results.active_users?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                {results.active_user_percentage?.toFixed(1) || 0}% of total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <Card elevation={0} sx={{
            height: '100%',
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            transition: 'all 0.3s',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: `0 12px 24px -10px ${COLORS.primary}40`,
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color={COLORS.lightGray} sx={{ mb: 2, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.75rem' }}>
                Avg. Session Time
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.primary} sx={{ mb: 1 }}>
                {results.avg_session_time?.toFixed(1) || 0}m
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                Average duration
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <Card elevation={0} sx={{
            height: '100%',
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            transition: 'all 0.3s',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: `0 12px 24px -10px ${COLORS.primary}40`,
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" color={COLORS.lightGray} sx={{ mb: 2, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.75rem' }}>
                Engagement Rate
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.primary} sx={{ mb: 1 }}>
                {results.engagement_rate?.toFixed(1) || 0}%
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                User interaction rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* User Activity Over Time Line Chart */}
        {results.visualizations?.user_activity_timeline && (
          <Grid item xs={12}>
            <Paper elevation={0} sx={{ p: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                User Activity Timeline
              </Typography>
              <Box sx={{ height: 450 }}>
                <Line
                  data={results.visualizations.user_activity_timeline.data}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top' as const,
                        align: 'end'
                      },
                      title: { display: false }
                    },
                    scales: {
                      y: { beginAtZero: true }
                    }
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Device Distribution */}
        {results.visualizations?.device_distribution && (
          <Grid item xs={12} lg={6}>
            <Paper elevation={0} sx={{ p: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Device Distribution
              </Typography>
              <Box sx={{ height: 450, display: 'flex', justifyContent: 'center' }}>
                <Doughnut
                  data={results.visualizations.device_distribution.data}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom' as const,
                        align: 'center'
                      },
                      title: { display: false }
                    }
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Peak Activity Hours */}
        {results.visualizations?.peak_hours && (
          <Grid item xs={12} lg={6}>
            <Paper elevation={0} sx={{ p: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Peak Activity Hours
              </Typography>
              <Box sx={{ height: 450 }}>
                <Bar
                  data={results.visualizations.peak_hours.data}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top' as const,
                        align: 'end'
                      },
                      title: { display: false }
                    },
                    scales: {
                      y: { beginAtZero: true }
                    }
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* AI Insights */}
      {results.insights && results.insights.length > 0 && (
        <Paper elevation={0} sx={{ p: 4, mb: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Box sx={{
              bgcolor: `${COLORS.primary}15`,
              p: 1.5,
              borderRadius: 1.5,
              display: 'flex'
            }}>
              <Insights sx={{ fontSize: 24, color: COLORS.primary }} />
            </Box>
            <Typography variant="h6" fontWeight={600} color={COLORS.dark}>
              AI-Powered Insights
            </Typography>
          </Box>
          <Divider sx={{ mb: 2.5 }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            {results.insights.map((insight: string, index: number) => (
              <Box key={index} sx={{ display: 'flex', gap: 2.5 }}>
                <Box sx={{
                  minWidth: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: COLORS.primary,
                  mt: 1
                }} />
                <Typography variant="body1" color={COLORS.neutral} sx={{ lineHeight: 1.8, fontSize: '1rem' }}>
                  {insight}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}

      {/* AI Recommendations */}
      {results.recommendations && results.recommendations.length > 0 && (
        <Paper elevation={0} sx={{ p: 4, mb: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Box sx={{
              bgcolor: `${COLORS.warning}15`,
              p: 1.5,
              borderRadius: 1.5,
              display: 'flex'
            }}>
              <Lightbulb sx={{ fontSize: 24, color: COLORS.warning }} />
            </Box>
            <Typography variant="h6" fontWeight={600} color={COLORS.dark}>
              Strategic Recommendations
            </Typography>
          </Box>
          <Divider sx={{ mb: 2.5 }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            {results.recommendations.map((rec: string, index: number) => (
              <Box key={index} sx={{ display: 'flex', gap: 2.5 }}>
                <Typography variant="body1" fontWeight={700} color={COLORS.warning} sx={{ minWidth: 28, fontSize: '1rem' }}>
                  {index + 1}.
                </Typography>
                <Typography variant="body1" color={COLORS.neutral} sx={{ lineHeight: 1.8, fontSize: '1rem' }}>
                  {rec}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}

      {/* User Segments */}
      {results.user_segments && results.user_segments.length > 0 && (
        <Paper sx={{ p: 3, mb: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            User Segments
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            {results.user_segments.map((segment: any, index: number) => (
              <Grid item xs={12} md={4} key={index}>
                <Card sx={{ bgcolor: 'white', border: `2px solid ${COLORS.primary}`, boxShadow: 2 }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" sx={{ color: COLORS.dark }}>
                      {segment.name}
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" sx={{ mt: 1, color: COLORS.primary }}>
                      {segment.count?.toLocaleString() || 0}
                    </Typography>
                    <Typography variant="body2" sx={{ color: COLORS.lightGray }}>
                      {segment.percentage?.toFixed(1) || 0}% of users
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" sx={{ color: COLORS.neutral }}>
                        {segment.description || 'User segment'}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* User Journey */}
      {results.user_journey && results.user_journey.length > 0 && (
        <Paper sx={{ p: 3, mb: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            User Journey Steps
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            {results.user_journey.map((step: any, index: number) => (
              <Grid item xs={12} key={index}>
                <Card sx={{ background: index % 2 === 0 ? '#e3f2fd' : '#f3e5f5' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Chip label={`Step ${index + 1}`} color="primary" />
                      <Typography variant="h6" fontWeight="bold">
                        {step.action}
                      </Typography>
                      <Box sx={{ ml: 'auto' }}>
                        <Chip label={`${step.users?.toLocaleString() || 0} users`} variant="outlined" />
                        <Chip label={`${step.conversion_rate?.toFixed(1) || 0}%`} color="success" sx={{ ml: 1 }} />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Most Engaged Users */}
      {results.most_engaged_users && results.most_engaged_users.length > 0 && (
        <Paper sx={{ p: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            Most Engaged Users
          </Typography>
          <Divider sx={{ mb: 2 }} />
          {results.most_engaged_users.map((user: any, index: number) => (
            <Card key={index} sx={{ mb: 2, border: `2px solid ${COLORS.primary}`, boxShadow: 1 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h6" fontWeight="bold" sx={{ color: COLORS.dark }}>
                      {user.username || `User ${index + 1}`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {user.platform && <Chip label={user.platform} size="small" sx={{ mr: 1, bgcolor: COLORS.background }} />}
                      {user.user_type && <Chip label={user.user_type} size="small" sx={{ bgcolor: COLORS.primary, color: 'white' }} />}
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="h5" fontWeight="bold" sx={{ color: COLORS.primary }}>
                      {user.engagement_score?.toFixed(0) || 0}
                    </Typography>
                    <Typography variant="body2" sx={{ color: COLORS.lightGray }}>
                      engagement score
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                  {user.total_interactions && (
                    <Chip label={`${user.total_interactions} interactions`} size="small" variant="outlined" />
                  )}
                  {user.avg_session_time && (
                    <Chip label={`${user.avg_session_time}m avg session`} size="small" variant="outlined" />
                  )}
                  {user.content_created && (
                    <Chip label={`${user.content_created} posts`} size="small" variant="outlined" color="success" />
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Paper>
      )}
    </Container>
    </Box>
  );
};

export default UserBehaviorReport;

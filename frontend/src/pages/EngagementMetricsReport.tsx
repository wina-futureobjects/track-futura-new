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
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { ArrowBack, TrendingUp, Insights, Lightbulb, Download } from '@mui/icons-material';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { fetchEngagementMetricsReport } from '../services/templateReportService';
import { FUTUREOBJECTS_COLORS } from '../constants/colors';
import { generateEnhancedPDF } from '../utils/enhancedPdfGenerator';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const COLORS = FUTUREOBJECTS_COLORS;

const EngagementMetricsReport: React.FC = () => {
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
      const data = await fetchEngagementMetricsReport(Number(id));
      setReport(data);
    } catch (err: any) {
      console.error('Error loading report:', err);
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

      const reportType = report?.template_type || 'Engagement Metrics';

      await generateEnhancedPDF(
        Number(id),
        report?.title || 'Engagement Metrics Report',
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

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress sx={{ color: COLORS.primary }} />
      </Container>
    );
  }

  if (error || !report) {
    return (
      <Container>
        <Typography color="error">Error loading report: {error}</Typography>
        <Button onClick={handleBack} sx={{ bgcolor: COLORS.primary, color: 'white', '&:hover': { bgcolor: COLORS.primaryDark } }}>
          Go Back
        </Button>
      </Container>
    );
  }

  const results = report.results || {};

  return (
    <Box sx={{ bgcolor: COLORS.background, minHeight: '100vh', width: '100%' }}>
    <Box sx={{ py: 3, px: 3, width: '100%' }} id="report-content">
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
              <TrendingUp sx={{ fontSize: 36, color: 'white' }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" fontWeight={700} color={COLORS.dark} sx={{ mb: 1.5 }}>
                {report.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Chip
                  label="Engagement Metrics"
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
              boxShadow: '0 8px 24px rgba(79, 209, 197, 0.15)',
              transform: 'translateY(-4px)',
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="body2" color={COLORS.lightGray} fontWeight={600} sx={{ mb: 2, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Total Posts
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark}>
                {results.total_posts?.toLocaleString() || 0}
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
              boxShadow: '0 8px 24px rgba(79, 209, 197, 0.15)',
              transform: 'translateY(-4px)',
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="body2" color={COLORS.lightGray} fontWeight={600} sx={{ mb: 2, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Total Likes
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark}>
                {results.total_likes?.toLocaleString() || 0}
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
              boxShadow: '0 8px 24px rgba(79, 209, 197, 0.15)',
              transform: 'translateY(-4px)',
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="body2" color={COLORS.lightGray} fontWeight={600} sx={{ mb: 2, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Total Comments
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark}>
                {results.total_comments?.toLocaleString() || 0}
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
              boxShadow: '0 8px 24px rgba(79, 209, 197, 0.15)',
              transform: 'translateY(-4px)',
              borderColor: COLORS.primary
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="body2" color={COLORS.lightGray} fontWeight={600} sx={{ mb: 2, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Engagement Rate
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.primary}>
                {results.engagement_rate?.toFixed(2) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Visualizations - Full Width Side by Side */}
      <Grid container spacing={2} sx={{ mb: 4, width: '100%' }}>
        {results.visualizations?.engagement_trend && (
          <Grid item xs={12} lg={6} sx={{ width: '100%' }}>
            <Paper elevation={0} sx={{ p: 4, border: `1px solid ${COLORS.border}`, borderRadius: 2, height: '100%' }}>
              <Typography variant="h6" fontWeight={700} color={COLORS.dark} sx={{ mb: 4 }}>
                Engagement Trend Over Time
              </Typography>
              <Box sx={{ height: 450 }}>
                <Line
                  data={results.visualizations.engagement_trend.data}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top' as const,
                        align: 'start',
                        labels: {
                          font: { size: 13, weight: '600' },
                          color: COLORS.neutral,
                          padding: 20,
                          usePointStyle: true,
                          boxWidth: 8,
                          boxHeight: 8
                        }
                      },
                      title: { display: false }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        grid: {
                          color: COLORS.border,
                          drawBorder: false
                        },
                        ticks: {
                          color: COLORS.neutral,
                          font: { size: 12 },
                          padding: 10
                        },
                        border: { display: false }
                      },
                      x: {
                        grid: { display: false },
                        ticks: {
                          color: COLORS.neutral,
                          font: { size: 12 },
                          padding: 10
                        },
                        border: { display: false }
                      }
                    },
                    layout: {
                      padding: {
                        top: 10,
                        bottom: 10,
                        left: 10,
                        right: 10
                      }
                    }
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        )}

        {results.visualizations?.platform_performance && (
          <Grid item xs={12} lg={6} sx={{ width: '100%' }}>
            <Paper elevation={0} sx={{ p: 4, border: `1px solid ${COLORS.border}`, borderRadius: 2, height: '100%' }}>
              <Typography variant="h6" fontWeight={700} color={COLORS.dark} sx={{ mb: 4 }}>
                Platform Performance Comparison
              </Typography>
              <Box sx={{ height: 450 }}>
                <Bar
                  data={results.visualizations.platform_performance.data}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top' as const,
                        align: 'start',
                        labels: {
                          font: { size: 13, weight: '600' },
                          color: COLORS.neutral,
                          padding: 20,
                          usePointStyle: true,
                          boxWidth: 8,
                          boxHeight: 8
                        }
                      },
                      title: { display: false }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        grid: {
                          color: COLORS.border,
                          drawBorder: false
                        },
                        ticks: {
                          color: COLORS.neutral,
                          font: { size: 12 },
                          padding: 10
                        },
                        border: { display: false }
                      },
                      x: {
                        grid: { display: false },
                        ticks: {
                          color: COLORS.neutral,
                          font: { size: 12 },
                          padding: 10
                        },
                        border: { display: false }
                      }
                    },
                    layout: {
                      padding: {
                        top: 10,
                        bottom: 10,
                        left: 10,
                        right: 10
                      }
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
            <Insights sx={{ color: COLORS.primary, fontSize: 32 }} />
            <Typography variant="h6" fontWeight={700} color={COLORS.dark}>
              AI-Powered Insights
            </Typography>
          </Box>
          <Divider sx={{ mb: 3, borderColor: COLORS.border }} />
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
            <Lightbulb sx={{ color: COLORS.warning, fontSize: 32 }} />
            <Typography variant="h6" fontWeight={700} color={COLORS.dark}>
              Strategic Recommendations
            </Typography>
          </Box>
          <Divider sx={{ mb: 3, borderColor: COLORS.border }} />
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

      {/* Top Posts */}
      {results.top_posts && results.top_posts.length > 0 && (
        <Paper elevation={0} sx={{ p: 4, border: `1px solid ${COLORS.border}`, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight={700} color={COLORS.dark} sx={{ mb: 3 }}>
            Top 5 Performing Posts
          </Typography>
          <Divider sx={{ mb: 3, borderColor: COLORS.border }} />
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: COLORS.background }}>
                  <TableCell sx={{ fontWeight: 700, color: COLORS.dark, fontSize: '0.875rem' }}>Rank</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: COLORS.dark, fontSize: '0.875rem' }}>Content</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: COLORS.dark, fontSize: '0.875rem' }}>Likes</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: COLORS.dark, fontSize: '0.875rem' }}>Comments</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: COLORS.dark, fontSize: '0.875rem' }}>Views</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: COLORS.dark, fontSize: '0.875rem' }}>Platform</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.top_posts.map((post: any, index: number) => (
                  <TableRow
                    key={index}
                    sx={{
                      '&:hover': { bgcolor: COLORS.background },
                      '&:last-child td': { border: 0 }
                    }}
                  >
                    <TableCell>
                      <Chip
                        label={`#${index + 1}`}
                        size="small"
                        sx={{
                          bgcolor: index === 0 ? COLORS.primary : `${COLORS.primary}25`,
                          color: index === 0 ? 'white' : COLORS.primaryDark,
                          fontWeight: 700,
                          minWidth: 45,
                          fontSize: '0.875rem'
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ maxWidth: 500 }}>
                      <Typography variant="body2" color={COLORS.neutral} sx={{ lineHeight: 1.6 }}>
                        {post.content?.substring(0, 120)}{post.content?.length > 120 ? '...' : ''}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={600} color={COLORS.dark}>
                        {post.likes?.toLocaleString() || 0}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={600} color={COLORS.dark}>
                        {post.comments?.toLocaleString() || 0}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={600} color={COLORS.dark}>
                        {post.views?.toLocaleString() || 0}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={post.platform}
                        size="small"
                        sx={{
                          textTransform: 'capitalize',
                          bgcolor: `${COLORS.secondary}20`,
                          color: COLORS.secondary,
                          border: `1px solid ${COLORS.secondary}40`,
                          fontWeight: 600
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
    </Box>
  );
};

export default EngagementMetricsReport;

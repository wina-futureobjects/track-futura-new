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
import { ArrowBack, Article, Insights, Lightbulb, Download } from '@mui/icons-material';
import { Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { fetchContentAnalysisReport } from '../services/templateReportService';
import { FUTUREOBJECTS_COLORS } from '../constants/colors';
import { generateEnhancedPDF } from '../utils/enhancedPdfGenerator';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const ContentAnalysisReport: React.FC = () => {
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
      console.log('🚀 FRONTEND: Fetching Content Analysis Report ID:', id);

      const data = await fetchContentAnalysisReport(Number(id));
      console.log('✅ FRONTEND: CONTENT ANALYSIS DATA RECEIVED:', data);
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

      const reportType = report?.template_type || 'Content Analysis';

      await generateEnhancedPDF(
        Number(id),
        report?.title || 'Content Analysis Report',
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
              bgcolor: COLORS.secondary,
              p: 2,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Article sx={{ fontSize: 36, color: 'white' }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" fontWeight={700} color={COLORS.dark} sx={{ mb: 1.5 }}>
                {report.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Chip
                  label="Content Analysis"
                  sx={{
                    bgcolor: `${COLORS.secondary}20`,
                    color: COLORS.secondary,
                    fontWeight: 600,
                    border: `1px solid ${COLORS.secondary}40`,
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
                Total Posts
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                {results.total_posts?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                Content analyzed
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
                Avg. Post Length
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                {results.avg_post_length?.toFixed(0) || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                characters
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
                Content Types
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.primary} sx={{ mb: 1 }}>
                {results.content_type_counts ? Object.keys(results.content_type_counts).length : 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                different types
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
                Top Hashtags
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.primary} sx={{ mb: 1 }}>
                {results.top_hashtags?.length || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                identified
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Content Type Distribution */}
        {results.visualizations?.content_type_distribution && (
          <Grid item xs={12} lg={6}>
            <Paper elevation={0} sx={{ p: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Content Type Distribution
              </Typography>
              <Box sx={{ height: 450, display: 'flex', justifyContent: 'center' }}>
                <Doughnut
                  data={results.visualizations.content_type_distribution.data}
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

        {/* Post Length Distribution */}
        {results.visualizations?.post_length_distribution && (
          <Grid item xs={12} lg={6}>
            <Paper elevation={0} sx={{ p: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Post Length Distribution
              </Typography>
              <Box sx={{ height: 450 }}>
                <Bar
                  data={results.visualizations.post_length_distribution.data}
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

      {/* Top Hashtags */}
      {results.top_hashtags && results.top_hashtags.length > 0 && (
        <Paper sx={{ p: 3, mb: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            Top Hashtags
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {results.top_hashtags.map((hashtag: any, index: number) => (
              <Chip
                key={index}
                label={`${hashtag.tag} (${hashtag.count})`}
                sx={{
                  bgcolor: COLORS.secondary,
                  color: 'white',
                  fontSize: '0.95rem',
                  '&:hover': {
                    bgcolor: COLORS.secondary
                  }
                }}
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Best Performing Content */}
      {results.best_performing_content && results.best_performing_content.length > 0 && (
        <Paper sx={{ p: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            Best Performing Content
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Content</strong></TableCell>
                  <TableCell align="right"><strong>Type</strong></TableCell>
                  <TableCell align="right"><strong>Engagement</strong></TableCell>
                  <TableCell align="right"><strong>Platform</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.best_performing_content.slice(0, 10).map((content: any, index: number) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ maxWidth: 400 }}>
                        {content.content || 'No content'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip label={content.content_type || 'Unknown'} size="small" sx={{ bgcolor: COLORS.background }} />
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold" sx={{ color: COLORS.primary }}>
                        {content.engagement?.toLocaleString() || 0}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip label={content.platform || 'Unknown'} size="small" sx={{ bgcolor: COLORS.primary, color: 'white' }} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Container>
    </Box>
  );
};

export default ContentAnalysisReport;

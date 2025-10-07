// Full width sentiment analysis report
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid
} from '@mui/material';
import { ArrowBack, SentimentSatisfiedAlt, Insights, Lightbulb, Download } from '@mui/icons-material';
import { Doughnut } from 'react-chartjs-2';
import { FUTUREOBJECTS_COLORS } from '../constants/colors';
import { generateEnhancedPDF } from '../utils/enhancedPdfGenerator';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import { fetchSentimentAnalysisReport } from '../services/templateReportService';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

const SentimentAnalysisReport: React.FC = () => {
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
      console.log('🚀 FRONTEND: Fetching Sentiment Analysis Report ID:', id);

      const data = await fetchSentimentAnalysisReport(Number(id));
      console.log('✅ FRONTEND: SENTIMENT ANALYSIS DATA RECEIVED:', data);
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

      const reportType = report?.template_type || 'Sentiment Analysis';

      await generateEnhancedPDF(
        Number(id),
        report?.title || 'Sentiment Analysis Report',
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
      <Box sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={3}>
          <CircularProgress size={48} />
          <Typography variant="h6">
            Loading sentiment analysis report...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error || !report) {
    return (
      <Box sx={{ minHeight: '100vh', p: 4 }}>
        <Typography color="error">Error loading report: {error}</Typography>
        <Button
          onClick={handleBack}
          variant="contained"
        >
          Go Back
        </Button>
      </Box>
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
              <SentimentSatisfiedAlt sx={{ fontSize: 36, color: 'white' }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" fontWeight={700} color={COLORS.dark} sx={{ mb: 1.5 }}>
                {report.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Chip
                  label="Sentiment Analysis"
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
      <Grid container spacing={2} sx={{ mb: 4, width: '100%' }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
                Positive
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.accent} sx={{ mb: 1 }}>
                {results.sentiment_counts?.positive?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                {results.sentiment_percentages?.positive?.toFixed(1) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
                Neutral
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                {results.sentiment_counts?.neutral?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                {results.sentiment_percentages?.neutral?.toFixed(1) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
                Negative
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.error} sx={{ mb: 1 }}>
                {results.sentiment_counts?.negative?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                {results.sentiment_percentages?.negative?.toFixed(1) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
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
                Total Analyzed
              </Typography>
              <Typography variant="h3" fontWeight={700} color={COLORS.primary} sx={{ mb: 1 }}>
                {results.total_comments?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                Comments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Visualizations */}
      <Grid container spacing={2} sx={{ mb: 4, width: '100%' }}>
        {/* Sentiment Distribution Doughnut Chart */}
        {results.visualizations?.sentiment_distribution?.data?.labels && results.visualizations?.sentiment_distribution?.data?.datasets && (
          <Grid size={{ xs: 12, md: 6 }} sx={{ width: '100%' }}>
            <Paper elevation={0} sx={{ p: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white', height: '100%' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Sentiment Distribution
              </Typography>
              <Box sx={{ height: 420, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Doughnut
                  data={results.visualizations.sentiment_distribution.data}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' as const },
                      title: { display: false }
                    }
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Top 10 Common Words with Sentiment */}
        {results.word_sentiment_details && results.word_sentiment_details.length > 0 && (
          <Grid size={{ xs: 12, md: 6 }} sx={{ width: '100%' }}>
            <Paper elevation={0} sx={{ p: 3, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white', height: '100%' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Top 10 Common Words & Hashtags
              </Typography>
              <Box sx={{ maxHeight: 420, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 2, pr: 1 }}>
                {results.word_sentiment_details.map((word: any, index: number) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="body1" sx={{ minWidth: 90, fontWeight: 600, color: COLORS.dark, fontSize: '0.85rem' }}>
                      #{word.word}
                    </Typography>
                    <Box sx={{ flex: 1, display: 'flex', gap: 0.5 }}>
                      {word.positive_count > 0 && (
                        <Box sx={{
                          flex: word.positive_count,
                          bgcolor: COLORS.accent,
                          height: 28,
                          borderRadius: 1,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontSize: '0.7rem',
                          fontWeight: 600,
                          minWidth: 35
                        }}>
                          +{word.positive_count}
                        </Box>
                      )}
                      {word.neutral_count > 0 && (
                        <Box sx={{
                          flex: word.neutral_count,
                          bgcolor: COLORS.warning,
                          height: 28,
                          borderRadius: 1,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontSize: '0.7rem',
                          fontWeight: 600,
                          minWidth: 35
                        }}>
                          {word.neutral_count}
                        </Box>
                      )}
                      {word.negative_count > 0 && (
                        <Box sx={{
                          flex: word.negative_count,
                          bgcolor: COLORS.error,
                          height: 28,
                          borderRadius: 1,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontSize: '0.7rem',
                          fontWeight: 600,
                          minWidth: 35
                        }}>
                          -{word.negative_count}
                        </Box>
                      )}
                    </Box>
                    <Typography variant="body2" sx={{ minWidth: 60, color: COLORS.neutral, textAlign: 'right', fontSize: '0.75rem' }}>
                      {word.total_count} uses
                    </Typography>
                  </Box>
                ))}
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

      {/* Sample Comments */}
      {results.sample_comments && (
        <Paper sx={{ p: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            Sample Comments by Sentiment
          </Typography>
          <Divider sx={{ mb: 2 }} />

          {/* Positive Comments */}
          {results.sample_comments.positive && results.sample_comments.positive.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1, color: COLORS.accent }}>
                Positive Comments
              </Typography>
              {results.sample_comments.positive.map((comment: string, index: number) => (
                <Card key={index} sx={{ mb: 1, bgcolor: '#e8f5e9', border: `1px solid ${COLORS.accent}` }}>
                  <CardContent>
                    <Typography variant="body2">{comment}</Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}

          {/* Neutral Comments */}
          {results.sample_comments.neutral && results.sample_comments.neutral.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1, color: COLORS.neutral }}>
                Neutral Comments
              </Typography>
              {results.sample_comments.neutral.map((comment: string, index: number) => (
                <Card key={index} sx={{ mb: 1, bgcolor: '#f5f5f5', border: `1px solid ${COLORS.lightGray}` }}>
                  <CardContent>
                    <Typography variant="body2">{comment}</Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}

          {/* Negative Comments */}
          {results.sample_comments.negative && results.sample_comments.negative.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1, color: COLORS.error }}>
                Negative Comments
              </Typography>
              {results.sample_comments.negative.map((comment: string, index: number) => (
                <Card key={index} sx={{ mb: 1, bgcolor: '#ffebee', border: `1px solid ${COLORS.error}` }}>
                  <CardContent>
                    <Typography variant="body2">{comment}</Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Paper>
      )}
    </Box>
    </Box>
  );
};

export default SentimentAnalysisReport;

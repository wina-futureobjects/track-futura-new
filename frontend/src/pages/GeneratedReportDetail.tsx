import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Chip,
  Breadcrumbs,
  Link,
  Snackbar,
  Alert,
  Grid,
  Card,
  CardContent,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  ArrowBack,
  Download,
  PictureAsPdf,
  TableChart,
  CheckCircle,
  Schedule,
  Error as ErrorIcon,
  Psychology,
  TrendingUp,
  Description,
  Assessment
} from '@mui/icons-material';
import { format } from 'date-fns';
import { reportService, GeneratedReport } from '../services/reportService';

const GeneratedReportDetail: React.FC = () => {
  const { organizationId, projectId, reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState<GeneratedReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  useEffect(() => {
    const loadReport = async () => {
      try {
        setLoading(true);
        const reportData = await reportService.getReport(Number(reportId));
        setReport(reportData);
      } catch (error) {
        console.error('Error loading report:', error);
        showSnackbar('Failed to load report details', 'error');
      } finally {
        setLoading(false);
      }
    };

    if (reportId) {
      loadReport();
    }
  }, [reportId]);

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleDownloadPDF = async () => {
    if (!report) return;

    try {
      setDownloading(true);
      await reportService.downloadPDF(report.id);
      showSnackbar('PDF downloaded successfully!', 'success');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      showSnackbar('Failed to download PDF', 'error');
    } finally {
      setDownloading(false);
    }
  };

  const handleDownloadCSV = async () => {
    if (!report) return;

    try {
      setDownloading(true);
      await reportService.downloadCSV(report.id);
      showSnackbar('CSV downloaded successfully!', 'success');
    } catch (error) {
      console.error('Error downloading CSV:', error);
      showSnackbar('Failed to download CSV', 'error');
    } finally {
      setDownloading(false);
    }
  };

  const handleBack = () => {
    if (organizationId && projectId) {
      navigate(`/organizations/${organizationId}/projects/${projectId}/report`);
    } else {
      navigate('/report');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'processing':
        return <Schedule color="warning" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <Schedule color="warning" />;
    }
  };

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const renderInsights = (insights: string[]) => {
    if (!insights || insights.length === 0) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Key Insights
          </Typography>
          {insights.map((insight, index) => (
            <Typography key={index} variant="body2" sx={{ mb: 1, pl: 2 }}>
              • {insight}
            </Typography>
          ))}
        </CardContent>
      </Card>
    );
  };

  const renderRecommendations = (recommendations: string[]) => {
    if (!recommendations || recommendations.length === 0) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          {recommendations.map((recommendation, index) => (
            <Typography key={index} variant="body2" sx={{ mb: 1, pl: 2 }}>
              • {recommendation}
            </Typography>
          ))}
        </CardContent>
      </Card>
    );
  };

  const renderSentimentAnalysis = (results: any) => {
    const summary = results.summary || {};
    const distribution = summary.sentiment_distribution || {};

    return (
      <>
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sentiment Distribution
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Positive:</Typography>
                    <Chip label={`${distribution.positive || 0}%`} color="success" size="small" />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Negative:</Typography>
                    <Chip label={`${distribution.negative || 0}%`} color="error" size="small" />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Neutral:</Typography>
                    <Chip label={`${distribution.neutral || 0}%`} color="default" size="small" />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Summary
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Total Comments: {summary.total_comments_analyzed || 0}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Overall Sentiment: <Chip
                    label={summary.overall_sentiment || 'N/A'}
                    size="small"
                    color={summary.overall_sentiment === 'positive' ? 'success' :
                           summary.overall_sentiment === 'negative' ? 'error' : 'default'}
                  />
                </Typography>
                <Typography variant="body2">
                  Average Confidence: {summary.confidence_average || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {results.trending_keywords && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Trending Keywords
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Keyword</TableCell>
                      <TableCell align="right">Count</TableCell>
                      <TableCell align="center">Sentiment</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.trending_keywords.slice(0, 10).map((keyword: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{keyword.keyword}</TableCell>
                        <TableCell align="right">{keyword.count}</TableCell>
                        <TableCell align="center">
                          <Chip
                            label={keyword.sentiment}
                            size="small"
                            color={keyword.sentiment === 'positive' ? 'success' :
                                   keyword.sentiment === 'negative' ? 'error' : 'default'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}
      </>
    );
  };

  const renderEngagementMetrics = (results: any) => {
    const summary = results.summary || {};

    return (
      <>
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Engagement Overview
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Total Posts:</Typography>
                    <Typography variant="body2" fontWeight="bold">{summary.total_posts || 0}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Total Likes:</Typography>
                    <Typography variant="body2" fontWeight="bold">{summary.total_likes || 0}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Total Comments:</Typography>
                    <Typography variant="body2" fontWeight="bold">{summary.total_comments || 0}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Total Shares:</Typography>
                    <Typography variant="body2" fontWeight="bold">{summary.total_shares || 0}</Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Avg. Engagement Rate:</Typography>
                    <Chip label={`${summary.average_engagement_rate || 0}%`} color="primary" size="small" />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {results.performance_analysis && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Performing Content
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Content Title</TableCell>
                      <TableCell align="right">Likes</TableCell>
                      <TableCell align="right">Comments</TableCell>
                      <TableCell align="right">Shares</TableCell>
                      <TableCell align="right">Engagement Rate</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.performance_analysis.map((item: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{item.title}</TableCell>
                        <TableCell align="right">{item.likes}</TableCell>
                        <TableCell align="right">{item.comments}</TableCell>
                        <TableCell align="right">{item.shares}</TableCell>
                        <TableCell align="right">{item.engagement_rate}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}
      </>
    );
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!report) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h6">Report not found</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link color="inherit" onClick={handleBack} sx={{ cursor: 'pointer' }}>
          Report Marketplace
        </Link>
        <Typography color="text.primary">{report.title}</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            {report.title}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {getStatusIcon(report.status)}
            <Chip label={report.status.charAt(0).toUpperCase() + report.status.slice(1)} color={getStatusColor(report.status)} />
            <Typography variant="body2" color="text.secondary">
              Created: {format(new Date(report.created_at), 'MMM dd, yyyy HH:mm')}
            </Typography>
            {report.completed_at && (
              <Typography variant="body2" color="text.secondary">
                Completed: {format(new Date(report.completed_at), 'MMM dd, yyyy HH:mm')}
              </Typography>
            )}
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={handleBack}
            variant="outlined"
          >
            Back
          </Button>
          {report.status === 'completed' && (
            <>
              <Button
                startIcon={<PictureAsPdf />}
                onClick={handleDownloadPDF}
                variant="contained"
                disabled={downloading}
                color="error"
              >
                {downloading ? <CircularProgress size={20} /> : 'Download PDF'}
              </Button>
              <Button
                startIcon={<TableChart />}
                onClick={handleDownloadCSV}
                variant="contained"
                disabled={downloading}
                color="success"
              >
                {downloading ? <CircularProgress size={20} /> : 'Download CSV'}
              </Button>
            </>
          )}
        </Box>
      </Box>

      {/* Report Content */}
      {report.status === 'completed' && report.results && (
        <Box>
          {/* Render based on template type */}
          {report.template_type === 'sentiment_analysis' && renderSentimentAnalysis(report.results)}
          {report.template_type === 'engagement_metrics' && renderEngagementMetrics(report.results)}

          {/* Generic insights and recommendations */}
          {report.results.insights && renderInsights(report.results.insights)}
          {report.results.recommendations && renderRecommendations(report.results.recommendations)}

          {/* Metadata */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Report Metadata
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Template Type: {report.template_type?.replace('_', ' ')?.toUpperCase()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Data Points Analyzed: {report.data_source_count}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  {report.processing_time && (
                    <Typography variant="body2" color="text.secondary">
                      Processing Time: {report.processing_time.toFixed(2)}s
                    </Typography>
                  )}
                  {report.results.ai_generated && (
                    <Chip label="AI Generated" size="small" color="primary" variant="outlined" />
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Error state */}
      {report.status === 'failed' && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6">Report Generation Failed</Typography>
          <Typography variant="body2">
            {report.error_message || 'An unknown error occurred during report generation.'}
          </Typography>
        </Alert>
      )}

      {/* Processing state */}
      {report.status === 'processing' && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="h6">Report is being generated...</Typography>
          <Typography variant="body2">
            This may take a few minutes. Please check back shortly.
          </Typography>
        </Alert>
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default GeneratedReportDetail;
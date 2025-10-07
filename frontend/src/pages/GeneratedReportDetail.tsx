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
import ChartRenderer from '../components/charts/ChartRenderer';

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
        console.log('📊 Loaded Report Data:', {
          id: reportData.id,
          template_type: reportData.template_type,
          title: reportData.title,
          has_visualizations: !!reportData.results?.visualizations,
          visualization_keys: Object.keys(reportData.results?.visualizations || {})
        });
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

  const renderVisualizations = (visualizations: any) => {
    if (!visualizations || Object.keys(visualizations).length === 0) {
      console.log('⚠️  No visualizations to render');
      return null;
    }

    console.log('📊 renderVisualizations called with:', Object.keys(visualizations));

    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          📊 Visualizations
        </Typography>
        <Grid container spacing={3}>
          {Object.entries(visualizations).map(([key, viz]: [string, any]) => {
            console.log(`  ➡️  Rendering visualization: ${key}`, { type: viz.type, title: viz.title });
            return (
              <Grid item xs={12} md={6} key={key}>
                <ChartRenderer visualization={viz} />
              </Grid>
            );
          })}
        </Grid>
      </Box>
    );
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
    // Use new enhanced data structure
    const sentimentBreakdown = results.sentiment_breakdown || {};
    const sentimentPercentages = results.sentiment_percentages || {};
    const overallSentiment = results.overall_sentiment || 'neutral';

    return (
      <>
        {/* Render Visualizations First */}
        {results.visualizations && renderVisualizations(results.visualizations)}

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
                    <Chip label={`${sentimentPercentages.positive?.toFixed(1) || 0}% (${sentimentBreakdown.positive || 0})`} color="success" size="small" />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Negative:</Typography>
                    <Chip label={`${sentimentPercentages.negative?.toFixed(1) || 0}% (${sentimentBreakdown.negative || 0})`} color="error" size="small" />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Neutral:</Typography>
                    <Chip label={`${sentimentPercentages.neutral?.toFixed(1) || 0}% (${sentimentBreakdown.neutral || 0})`} color="default" size="small" />
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
                  Total Posts Analyzed: {results.data_source_count || 0}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Overall Sentiment: <Chip
                    label={overallSentiment}
                    size="small"
                    color={overallSentiment === 'positive' ? 'success' :
                           overallSentiment === 'negative' ? 'error' : 'default'}
                  />
                </Typography>
                <Typography variant="body2">
                  Processing Time: {results.processing_time || 0}s
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Enhanced Performance Metrics Dashboard */}
        {results.performance_metrics && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Nike Brand Performance Dashboard
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#f5f5f5', borderRadius: 2 }}>
                    <Typography variant="h4" color="primary" fontWeight="bold">
                      {results.performance_metrics.brand_strength_score}/10
                    </Typography>
                    <Typography variant="body2">Brand Strength Score</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={8}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Typography variant="body2">
                      <strong>Campaign Effectiveness:</strong> {results.performance_metrics.campaign_effectiveness}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Partnership Impact:</strong> {results.performance_metrics.partnership_impact}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Enhanced Visualization Data */}
        {results.visualization_data && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Brand Theme Analysis
                  </Typography>
                  {Object.entries(results.visualization_data.brand_theme_analysis || {}).map(([theme, count]: [string, any]) => (
                    <Box key={theme} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {theme.replace('_', ' ')}:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{
                          width: `${(count / 7) * 100}px`,
                          height: 20,
                          backgroundColor: '#2196f3',
                          borderRadius: 1,
                          mr: 1
                        }} />
                        <Typography variant="body2" fontWeight="bold">{count}</Typography>
                      </Box>
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Engagement Breakdown
                  </Typography>
                  {Object.entries(results.visualization_data.engagement_breakdown || {}).map(([level, count]: [string, any]) => (
                    <Box key={level} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {level} Engagement:
                      </Typography>
                      <Chip
                        label={`${count} posts`}
                        color={level === 'high' ? 'success' : level === 'medium' ? 'warning' : 'default'}
                        size="small"
                      />
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Enhanced Trending Keywords */}
        {results.trending_keywords && results.trending_keywords.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Trending Keywords & Themes
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Keyword</TableCell>
                      <TableCell align="right">Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.trending_keywords.slice(0, 15).map((keyword: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {keyword.word || keyword.keyword || keyword}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={keyword.count || 0}
                            size="small"
                            color="primary"
                            variant="outlined"
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

        {/* Enhanced Strategic Insights with Business Impact */}
        {results.insights && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Strategic Nike Brand Insights
              </Typography>
              {results.insights.map((insight: any, index: number) => (
                <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <Typography variant="body1" sx={{ mb: 1, fontWeight: 'medium' }}>
                    {typeof insight === 'object' ? insight.insight : insight}
                  </Typography>
                  {insight.business_impact && (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                      <strong>Business Impact:</strong> {insight.business_impact}
                    </Typography>
                  )}
                </Box>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Enhanced Strategic Recommendations with Priority */}
        {results.recommendations && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Strategic Recommendations
              </Typography>
              {results.recommendations.map((rec: any, index: number) => (
                <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="body1" sx={{ fontWeight: 'medium', flex: 1 }}>
                      {typeof rec === 'object' ? rec.recommendation : rec}
                    </Typography>
                    {rec.implementation_priority && (
                      <Chip
                        label={`${rec.implementation_priority} priority`}
                        size="small"
                        color={rec.implementation_priority === 'high' ? 'error' :
                               rec.implementation_priority === 'medium' ? 'warning' : 'default'}
                      />
                    )}
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        )}
      </>
    );
  };

  const renderCompetitiveAnalysis = (results: any) => {
    return (
      <>
        {/* Render Visualizations First */}
        {results.visualizations && renderVisualizations(results.visualizations)}

        {/* Competitor Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Competitors
                </Typography>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {results.competitors?.length || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Performer
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {results.top_performer?.name || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {results.top_performer?.avg_engagement?.toLocaleString() || 0} avg engagement
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Leader
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {results.market_leader?.name || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {results.market_leader?.market_share?.toFixed(1) || 0}% market share
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Competitor Details Table */}
        {results.competitors && results.competitors.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Competitor Performance Details
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Competitor</TableCell>
                      <TableCell align="right">Posts</TableCell>
                      <TableCell align="right">Avg Likes</TableCell>
                      <TableCell align="right">Avg Comments</TableCell>
                      <TableCell align="right">Engagement Rate</TableCell>
                      <TableCell align="right">Market Share</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.competitors.map((competitor: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {competitor.name}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{competitor.post_count}</TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="success.main">
                            {competitor.avg_likes?.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="info.main">
                            {competitor.avg_comments?.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={`${competitor.engagement_rate || 0}%`}
                            size="small"
                            color={competitor.engagement_rate > 5 ? 'success' : 'warning'}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={`${competitor.market_share?.toFixed(1) || 0}%`}
                            size="small"
                            color="primary"
                            variant="outlined"
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
    return (
      <>
        {/* Render Visualizations First */}
        {results.visualizations && renderVisualizations(results.visualizations)}

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
                    <Typography variant="body2" fontWeight="bold" color="primary">
                      {results.total_posts?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Total Likes:</Typography>
                    <Typography variant="body2" fontWeight="bold" color="success.main">
                      {results.total_likes?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Total Comments:</Typography>
                    <Typography variant="body2" fontWeight="bold" color="info.main">
                      {results.total_comments?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Total Views:</Typography>
                    <Typography variant="body2" fontWeight="bold" color="warning.main">
                      {results.total_views?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Engagement Rate:</Typography>
                    <Chip
                      label={`${results.engagement_rate || 0}%`}
                      color={results.engagement_rate > 5 ? "success" : results.engagement_rate > 2 ? "warning" : "error"}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Avg Likes/Post:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {results.avg_likes_per_post?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Real Visualization Data */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Real Content Performance
                </Typography>
                {results.visualization_data?.content_performance_breakdown && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {results.visualization_data.content_performance_breakdown.map((content: any, index: number) => (
                      <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2">{content.type}:</Typography>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                          <Chip label={`${content.count} posts`} size="small" />
                          <Typography variant="body2" fontWeight="bold">
                            {content.total_likes?.toLocaleString()} likes
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Real Top Performing Posts - Support both top_posts and top_performing_posts */}
        {(results.top_posts || results.top_performing_posts) && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Performing Posts
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Content</TableCell>
                      <TableCell align="right">Likes</TableCell>
                      <TableCell align="right">Comments</TableCell>
                      <TableCell align="right">Views</TableCell>
                      <TableCell align="right">Platform</TableCell>
                      <TableCell align="right">Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(results.top_posts || results.top_performing_posts || []).slice(0, 5).map((post: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Box sx={{ maxWidth: 300 }}>
                            <Typography variant="body2" sx={{
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden'
                            }}>
                              {post.content || 'No content'}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="success.main" fontWeight="bold">
                            {post.likes?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="info.main" fontWeight="bold">
                            {post.comments?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="warning.main">
                            {post.views?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={post.platform || 'N/A'}
                            size="small"
                            sx={{ textTransform: 'capitalize' }}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="caption">
                            {post.date || 'N/A'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}

        {/* Real Engagement Trend Visualization */}
        {results.visualization_data?.engagement_trend && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Real Engagement Trend (Daily Performance)
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {results.visualization_data.engagement_trend.slice(0, 5).map((day: any, index: number) => (
                  <Box key={index} sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" fontWeight="bold">Day {day.day}</Typography>
                      <Typography variant="h6" color="primary">
                        {day.engagement?.toLocaleString()} total engagement
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      "{day.content}"
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Chip label={`${day.likes?.toLocaleString()} likes`} color="success" size="small" />
                      <Chip label={`${day.comments?.toLocaleString()} comments`} color="info" size="small" />
                      <Chip label={`${day.views?.toLocaleString()} views`} color="warning" size="small" />
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        )}
      </>
    );
  };

  const renderContentAnalysis = (results: any) => {
    return (
      <>
        {/* Render Visualizations First */}
        {results.visualizations && renderVisualizations(results.visualizations)}

        {/* Content Overview */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Posts
                </Typography>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {results.total_posts || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Unique Hashtags
                </Typography>
                <Typography variant="h3" color="success.main" fontWeight="bold">
                  {results.unique_hashtags || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Avg Content Length
                </Typography>
                <Typography variant="h3" color="info.main" fontWeight="bold">
                  {results.avg_content_length || 0}
                </Typography>
                <Typography variant="caption">characters</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Top Hashtags */}
        {results.top_hashtags && results.top_hashtags.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Performing Hashtags
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Hashtag</TableCell>
                      <TableCell align="right">Usage Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.top_hashtags.slice(0, 10).map((hashtag: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            #{Array.isArray(hashtag) ? hashtag[0] : hashtag.hashtag || hashtag}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={Array.isArray(hashtag) ? hashtag[1] : hashtag.posts || hashtag.count || 0}
                            size="small"
                            color="primary"
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

        {/* Content Type Breakdown */}
        {results.content_type_breakdown && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Content Type Distribution
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {Object.entries(results.content_type_breakdown).map(([type, data]: [string, any]) => (
                  <Box key={type} sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body1" fontWeight="bold" sx={{ textTransform: 'capitalize' }}>
                        {type}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip label={`${data.count} posts`} size="small" />
                        <Chip label={`${data.total_likes?.toLocaleString() || 0} likes`} size="small" color="success" />
                      </Box>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        )}
      </>
    );
  };

  const renderTrendAnalysis = (results: any) => {
    return (
      <>
        {/* Render Visualizations First */}
        {results.visualizations && renderVisualizations(results.visualizations)}

        {/* Trend Summary */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Posts
                </Typography>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {results.total_posts || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Growth Rate
                </Typography>
                <Typography variant="h3" color={results.growth_rate >= 0 ? 'success.main' : 'error.main'} fontWeight="bold">
                  {results.growth_rate >= 0 ? '+' : ''}{results.growth_rate?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Time Periods
                </Typography>
                <Typography variant="h3" color="info.main" fontWeight="bold">
                  {results.trend_data?.length || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Trend Data Table */}
        {results.trend_data && results.trend_data.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Engagement Trends Over Time
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Period</TableCell>
                      <TableCell align="right">Posts</TableCell>
                      <TableCell align="right">Avg Likes</TableCell>
                      <TableCell align="right">Avg Comments</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.trend_data.map((period: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {period.period}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{period.post_count}</TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="success.main">
                            {period.avg_likes?.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="info.main">
                            {period.avg_comments?.toLocaleString()}
                          </Typography>
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

  const renderUserBehavior = (results: any) => {
    return (
      <>
        {/* Render Visualizations First */}
        {results.visualizations && renderVisualizations(results.visualizations)}

        {/* User Behavior Summary */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {results.total_users || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Posts
                </Typography>
                <Typography variant="h3" color="success.main" fontWeight="bold">
                  {results.total_posts || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Top Users Table */}
        {results.top_users && results.top_users.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Users by Engagement
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell align="right">Posts</TableCell>
                      <TableCell align="right">Total Likes</TableCell>
                      <TableCell align="right">Total Comments</TableCell>
                      <TableCell align="right">Avg Engagement</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.top_users.map((user: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {user.user}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{user.posts}</TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="success.main">
                            {user.total_likes?.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="info.main">
                            {user.total_comments?.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={user.avg_engagement?.toLocaleString()}
                            size="small"
                            color="primary"
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
          {/* Debug logging */}
          {console.log('🎨 Rendering report type:', report.template_type)}

          {/* Render based on template type */}
          {report.template_type === 'sentiment_analysis' && (
            <>
              {console.log('✅ Rendering Sentiment Analysis')}
              {renderSentimentAnalysis(report.results)}
            </>
          )}
          {report.template_type === 'competitive_analysis' && (
            <>
              {console.log('✅ Rendering Competitive Analysis')}
              {renderCompetitiveAnalysis(report.results)}
            </>
          )}
          {report.template_type === 'engagement_metrics' && (
            <>
              {console.log('✅ Rendering Engagement Metrics')}
              {renderEngagementMetrics(report.results)}
            </>
          )}
          {report.template_type === 'content_analysis' && (
            <>
              {console.log('✅ Rendering Content Analysis')}
              {renderContentAnalysis(report.results)}
            </>
          )}
          {report.template_type === 'trend_analysis' && (
            <>
              {console.log('✅ Rendering Trend Analysis')}
              {renderTrendAnalysis(report.results)}
            </>
          )}
          {report.template_type === 'user_behavior' && (
            <>
              {console.log('✅ Rendering User Behavior')}
              {renderUserBehavior(report.results)}
            </>
          )}

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
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
import { ArrowBack, CompareArrows, Insights, Lightbulb, Download, SentimentSatisfiedAlt } from '@mui/icons-material';
import { FUTUREOBJECTS_COLORS } from '../constants/colors';
import { generateEnhancedPDF } from '../utils/enhancedPdfGenerator';
import { Bar, Radar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { fetchCompetitiveAnalysisReport } from '../services/templateReportService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const CompetitiveAnalysisReport: React.FC = () => {
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
      console.log('🚀 FRONTEND: Fetching Competitive Analysis Report ID:', id);

      const data = await fetchCompetitiveAnalysisReport(Number(id));
      console.log('✅ FRONTEND: COMPETITIVE ANALYSIS DATA RECEIVED:', data);
      console.log('📊 FRONTEND: Competitor Metrics:', data.results?.competitor_metrics);
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

      const reportType = report?.template_type || 'Competitive Analysis';

      await generateEnhancedPDF(
        Number(id),
        report?.title || 'Competitive Analysis Report',
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

  // Helper function to safely extract string content from objects or strings
  const extractStringContent = (item: any): string => {
    if (typeof item === 'string') {
      return item;
    }
    if (typeof item === 'object' && item !== null) {
      // If it's an object, try to extract meaningful text
      if (item.text || item.content || item.insight || item.recommendation || item.opportunity) {
        return item.text || item.content || item.insight || item.recommendation || item.opportunity;
      }
      // Handle specific object structures from AI responses
      if (item.Insight) {
        return item.Insight;
      }
      if (item.Recommendation) {
        return item.Recommendation;
      }
      if (item.Opportunity) {
        return item.Opportunity;
      }
      // If it has keys like Nike, Adidas, etc., try to extract meaningful content
      if (item.Nike || item.Adidas) {
        const parts = [];
        if (item.Nike) parts.push(`Nike: ${item.Nike}`);
        if (item.Adidas) parts.push(`Adidas: ${item.Adidas}`);
        if (item.Insight) parts.push(item.Insight);
        return parts.join(' | ');
      }
      // Skip rendering objects that look like debug info
      if (Object.keys(item).length === 1 && Object.keys(item)[0].toLowerCase().includes('object')) {
        return '';
      }
      // Convert simple objects to readable text
      const entries = Object.entries(item);
      if (entries.length === 1 && typeof entries[0][1] === 'string') {
        return entries[0][1];
      }
      // As last resort, convert to JSON but make it readable
      try {
        return JSON.stringify(item, null, 2).replace(/[{}"\[\]]/g, '').replace(/,/g, ', ').trim();
      } catch {
        return String(item);
      }
    }
    return String(item || '');
  };

  // Process arrays to ensure they contain strings and filter out empty ones
  const processedInsights = (results.insights || [])
    .map(extractStringContent)
    .filter(insight => insight && insight.trim() && !insight.includes('[object Object]'));
  
  const processedRecommendations = (results.recommendations || [])
    .map(extractStringContent)
    .filter(rec => rec && rec.trim() && !rec.includes('[object Object]'));
  
  const processedOpportunities = (results.opportunities || [])
    .map(extractStringContent)
    .filter(opp => opp && opp.trim() && !opp.includes('[object Object]'));
  
  const processedStrengths = (results.strengths || [])
    .map(extractStringContent)
    .filter(strength => strength && strength.trim());
  
  const processedWeaknesses = (results.weaknesses || [])
    .map(extractStringContent)
    .filter(weakness => weakness && weakness.trim());

  // Calculate real metrics from competitor data
  const competitorMetrics = results.competitor_metrics || [];
  const nikeData = competitorMetrics.find((comp: any) => comp.name === 'Nike') || {};
  const adidasData = competitorMetrics.find((comp: any) => comp.name === 'Adidas') || {};
  
  console.log('📊 METRICS CALCULATION:');
  console.log('Nike Data:', nikeData);
  console.log('Adidas Data:', adidasData);
  
  // Calculate totals
  const nikeTotalEngagement = (nikeData.total_likes || 0) + (nikeData.total_comments || 0);
  const adidasTotalEngagement = (adidasData.total_likes || 0) + (adidasData.total_comments || 0);
  const totalEngagements = nikeTotalEngagement + adidasTotalEngagement;
  
  const nikeAvgEngagement = nikeData.avg_engagement || 0;
  const adidasAvgEngagement = adidasData.avg_engagement || 0;
  
  const nikePotentialImpressions = (nikeData.total_views || 0) + (nikeData.total_followers || 0);
  const adidasPotentialImpressions = (adidasData.total_views || 0) + (adidasData.total_followers || 0);
  const totalPotentialImpressions = nikePotentialImpressions + adidasPotentialImpressions;
  
  const nikeUniqueAuthors = nikeData.post_count || 0;
  const adidasUniqueAuthors = adidasData.post_count || 0;
  const totalUniqueAuthors = nikeUniqueAuthors + adidasUniqueAuthors;
  
  console.log('Calculated Metrics:');
  console.log('Nike Total Engagement:', nikeTotalEngagement);
  console.log('Adidas Total Engagement:', adidasTotalEngagement);
  console.log('Total Engagements:', totalEngagements);
  
  // Share of Engagement (Doughnut Chart Data)
  const shareOfEngagementData = {
    labels: ['Nike', 'Adidas'],
    datasets: [{
      data: [nikeTotalEngagement, adidasTotalEngagement],
      backgroundColor: [COLORS.primary, COLORS.secondary], // Teal for Nike, Purple for Adidas
      borderWidth: 2,
      borderColor: '#fff'
    }]
  };

  // Competitive Comparison (Bar Chart Data)
  const competitiveComparisonData = {
    labels: ['Nike', 'Adidas'],
    datasets: [
      {
        label: 'Avg Likes',
        data: [nikeData.avg_likes || 0, adidasData.avg_likes || 0],
        backgroundColor: [COLORS.primary, COLORS.secondary]
      },
      {
        label: 'Avg Comments',
        data: [nikeData.avg_comments || 0, adidasData.avg_comments || 0],
        backgroundColor: [COLORS.primaryLight, COLORS.accent]
      }
    ]
  };

  // Horizontal bar data for metrics with both Nike and Adidas
  const createHorizontalBarData = (nikeValue: number, adidasValue: number) => {
    const total = nikeValue + adidasValue;
    if (total === 0) {
      return {
        labels: [''],
        datasets: [{
          data: [0],
          backgroundColor: [COLORS.border],
          barThickness: 20,
          categoryPercentage: 1.0,
          barPercentage: 1.0
        }]
      };
    }
    
    return {
      labels: [''],
      datasets: [{
        label: 'Nike',
        data: [nikeValue],
        backgroundColor: COLORS.primary,
        barThickness: 20,
        categoryPercentage: 1.0,
        barPercentage: 1.0,
        stack: 'combined'
      }, {
        label: 'Adidas',
        data: [adidasValue],
        backgroundColor: COLORS.secondary,
        barThickness: 20,
        categoryPercentage: 1.0,
        barPercentage: 1.0,
        stack: 'combined'
      }]
    };
  };

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
              <CompareArrows sx={{ fontSize: 36, color: 'white' }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" fontWeight={700} color={COLORS.dark} sx={{ mb: 1.5 }}>
                {report.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Chip
                  label="Competitive Analysis"
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

      {/* Top Metrics Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Total Engagements */}
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={0} sx={{
            height: 180,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            bgcolor: 'white'
          }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Box sx={{
                    bgcolor: COLORS.primary,
                    p: 0.5,
                    borderRadius: 1,
                    display: 'flex'
                  }}>
                    <Insights sx={{ fontSize: 16, color: 'white' }} />
                  </Box>
                  <Typography variant="body2" color={COLORS.neutral} fontWeight={500} fontSize="0.75rem">
                    Total Engagements
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                  {totalEngagements.toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ height: 20 }}>
                <Bar
                  data={createHorizontalBarData(nikeTotalEngagement, adidasTotalEngagement)}
                  options={{
                    indexAxis: 'y' as const,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                      legend: { display: false },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const brand = context.dataset.label;
                            const value = context.parsed.x;
                            return `${brand}: ${value.toLocaleString()}`;
                          }
                        }
                      }
                    },
                    scales: {
                      x: { 
                        display: false,
                        stacked: true
                      },
                      y: { 
                        display: false,
                        stacked: true
                      }
                    },
                    interaction: {
                      intersect: false
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Avg Engagements Per Message */}
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={0} sx={{
            height: 180,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            bgcolor: 'white'
          }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Box sx={{
                    bgcolor: COLORS.error,
                    p: 0.5,
                    borderRadius: 1,
                    display: 'flex'
                  }}>
                    <ArrowBack sx={{ fontSize: 16, color: 'white', transform: 'rotate(-45deg)' }} />
                  </Box>
                  <Typography variant="body2" color={COLORS.neutral} fontWeight={500} fontSize="0.75rem">
                    Avg. Engagements Per Msg
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                  {Math.round((nikeAvgEngagement + adidasAvgEngagement) / 2)}
                </Typography>
              </Box>
              <Box sx={{ height: 20 }}>
                <Bar
                  data={createHorizontalBarData(nikeAvgEngagement, adidasAvgEngagement)}
                  options={{
                    indexAxis: 'y' as const,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                      legend: { display: false },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const brand = context.dataset.label;
                            const value = context.parsed.x;
                            return `${brand}: ${value.toLocaleString()}`;
                          }
                        }
                      }
                    },
                    scales: {
                      x: { 
                        display: false,
                        stacked: true
                      },
                      y: { 
                        display: false,
                        stacked: true
                      }
                    },
                    interaction: {
                      intersect: false
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Total Potential Impressions */}
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={0} sx={{
            height: 180,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            bgcolor: 'white'
          }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Box sx={{
                    bgcolor: COLORS.warning,
                    p: 0.5,
                    borderRadius: 1,
                    display: 'flex'
                  }}>
                    <Lightbulb sx={{ fontSize: 16, color: 'white' }} />
                  </Box>
                  <Typography variant="body2" color={COLORS.neutral} fontWeight={500} fontSize="0.75rem">
                    Total Potential Impressions
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                  {totalPotentialImpressions.toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ height: 20 }}>
                <Bar
                  data={createHorizontalBarData(nikePotentialImpressions, adidasPotentialImpressions)}
                  options={{
                    indexAxis: 'y' as const,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                      legend: { display: false },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const brand = context.dataset.label;
                            const value = context.parsed.x;
                            return `${brand}: ${value.toLocaleString()}`;
                          }
                        }
                      }
                    },
                    scales: {
                      x: { 
                        display: false,
                        stacked: true
                      },
                      y: { 
                        display: false,
                        stacked: true
                      }
                    },
                    interaction: {
                      intersect: false
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Total Unique Authors */}
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={0} sx={{
            height: 180,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            bgcolor: 'white'
          }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Box sx={{
                    bgcolor: COLORS.primaryDark,
                    p: 0.5,
                    borderRadius: 1,
                    display: 'flex'
                  }}>
                    <CompareArrows sx={{ fontSize: 16, color: 'white' }} />
                  </Box>
                  <Typography variant="body2" color={COLORS.neutral} fontWeight={500} fontSize="0.75rem">
                    Total Unique Authors
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                  {totalUniqueAuthors}
                </Typography>
              </Box>
              <Box sx={{ height: 20 }}>
                <Bar
                  data={createHorizontalBarData(nikeUniqueAuthors, adidasUniqueAuthors)}
                  options={{
                    indexAxis: 'y' as const,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                      legend: { display: false },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const brand = context.dataset.label;
                            const value = context.parsed.x;
                            return `${brand}: ${value.toLocaleString()}`;
                          }
                        }
                      }
                    },
                    scales: {
                      x: { 
                        display: false,
                        stacked: true
                      },
                      y: { 
                        display: false,
                        stacked: true
                      }
                    },
                    interaction: {
                      intersect: false
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Avg Positive Sentiment */}
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={0} sx={{
            height: 180,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            bgcolor: 'white'
          }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Box sx={{
                    bgcolor: COLORS.accent,
                    p: 0.5,
                    borderRadius: 1,
                    display: 'flex'
                  }}>
                    <SentimentSatisfiedAlt sx={{ fontSize: 16, color: 'white' }} />
                  </Box>
                  <Typography variant="body2" color={COLORS.neutral} fontWeight={500} fontSize="0.75rem">
                    Avg. Positive Sentiment
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight={700} color={COLORS.dark} sx={{ mb: 1 }}>
                  {Math.round(((nikeData.engagement_rate || 0) + (adidasData.engagement_rate || 0)) / 2)}%
                </Typography>
              </Box>
              <Box sx={{ height: 20 }}>
                <Bar
                  data={createHorizontalBarData(nikeData.engagement_rate || 0, adidasData.engagement_rate || 0)}
                  options={{
                    indexAxis: 'y' as const,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                      legend: { display: false },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const brand = context.dataset.label;
                            const value = context.parsed.x;
                            return `${brand}: ${value.toFixed(1)}%`;
                          }
                        }
                      }
                    },
                    scales: {
                      x: { 
                        display: false,
                        stacked: true
                      },
                      y: { 
                        display: false,
                        stacked: true
                      }
                    },
                    interaction: {
                      intersect: false
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Share of Engagement (Doughnut Chart) */}
        <Grid item xs={12} md={6}>
          <Card elevation={0} sx={{
            height: 400,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            bgcolor: 'white'
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Share of Engagement
              </Typography>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Doughnut
                  data={shareOfEngagementData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom' as const,
                        labels: {
                          padding: 20,
                          usePointStyle: true
                        }
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = nikeTotalEngagement + adidasTotalEngagement;
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value.toLocaleString()} (${percentage}%)`;
                          }
                        }
                      }
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Competitive Comparison (Bar Chart) */}
        <Grid item xs={12} md={6}>
          <Card elevation={0} sx={{
            height: 400,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 2,
            bgcolor: 'white'
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 3 }}>
                Competitive Comparison
              </Typography>
              <Box sx={{ height: 300 }}>
                <Bar
                  data={competitiveComparisonData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top' as const
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
                          }
                        }
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          callback: function(value) {
                            return value.toLocaleString();
                          }
                        }
                      }
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Comprehensive Analysis Overview */}
      <Paper elevation={0} sx={{ p: 4, mb: 4, border: `1px solid ${COLORS.border}`, borderRadius: 2, bgcolor: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box sx={{
            bgcolor: COLORS.primary,
            p: 1.5,
            borderRadius: 1.5,
            display: 'flex'
          }}>
            <CompareArrows sx={{ fontSize: 24, color: 'white' }} />
          </Box>
          <Typography variant="h6" fontWeight={600} color={COLORS.dark}>
            Comprehensive Competitive Analysis
          </Typography>
        </Box>
        <Divider sx={{ mb: 3 }} />
        
        <Typography variant="body1" color={COLORS.neutral} sx={{ mb: 3, lineHeight: 1.8 }}>
          This report provides a comprehensive competitive analysis of Nike vs Adidas performance, covering key strategic areas for competitive advantage.
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box sx={{ 
              p: 3, 
              border: `1px solid ${COLORS.border}`, 
              borderRadius: 2,
              bgcolor: `${COLORS.primary}05`
            }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 2 }}>
                🏆 Competitor Performance Comparison
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                Side-by-side analysis of Nike vs Adidas engagement metrics, follower growth, and content performance to identify market leaders and performance gaps.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Box sx={{ 
              p: 3, 
              border: `1px solid ${COLORS.border}`, 
              borderRadius: 2,
              bgcolor: `${COLORS.accent}05`
            }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 2 }}>
                📊 Market Share Analysis
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                Detailed breakdown of market share by engagement volume, brand visibility, and competitive positioning in the athletic footwear market.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Box sx={{ 
              p: 3, 
              border: `1px solid ${COLORS.border}`, 
              borderRadius: 2,
              bgcolor: `${COLORS.warning}05`
            }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 2 }}>
                🎯 Content Strategy Gaps
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                Identification of content themes, messaging strategies, and engagement tactics where opportunities exist to outperform competitors.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Box sx={{ 
              p: 3, 
              border: `1px solid ${COLORS.border}`, 
              borderRadius: 2,
              bgcolor: `${COLORS.error}05`
            }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 2 }}>
                📈 Engagement Rate Benchmarking
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                Benchmark analysis of like-to-follower ratios, comment engagement rates, and viral content patterns for strategic optimization.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ 
              p: 3, 
              border: `2px solid ${COLORS.primary}`, 
              borderRadius: 2,
              bgcolor: `${COLORS.primary}10`
            }}>
              <Typography variant="h6" fontWeight={600} color={COLORS.dark} sx={{ mb: 2 }}>
                🚀 Growth Opportunity Identification
              </Typography>
              <Typography variant="body2" color={COLORS.neutral}>
                AI-powered analysis identifying untapped market segments, emerging trends, and strategic opportunities where Nike can gain competitive advantage over Adidas through targeted campaigns and audience development.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* AI Insights */}
      {processedInsights && processedInsights.length > 0 && (
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
            {processedInsights.map((insight: string, index: number) => (
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
      {processedRecommendations && processedRecommendations.length > 0 && (
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
            {processedRecommendations.map((rec: string, index: number) => (
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

      {/* Competitor Comparison Table */}
      {results.competitor_metrics && results.competitor_metrics.length > 0 && (
        <Paper sx={{ p: 3, mb: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            Competitor Metrics Comparison
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Competitor</strong></TableCell>
                  <TableCell align="right"><strong>Followers</strong></TableCell>
                  <TableCell align="right"><strong>Avg. Engagement</strong></TableCell>
                  <TableCell align="right"><strong>Post Frequency</strong></TableCell>
                  <TableCell align="right"><strong>Score</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.competitor_metrics.map((competitor: any, index: number) => (
                  <TableRow key={index} sx={{ background: competitor.is_you ? '#e3f2fd' : 'inherit' }}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography fontWeight={competitor.is_you ? 'bold' : 'normal'}>
                          {competitor.name}
                        </Typography>
                        {competitor.is_you && <Chip label="You" color="primary" size="small" />}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      {competitor.followers?.toLocaleString() || 0}
                    </TableCell>
                    <TableCell align="right">
                      {competitor.avg_engagement?.toLocaleString() || 0}
                    </TableCell>
                    <TableCell align="right">
                      {competitor.post_frequency || 'N/A'}
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={competitor.score?.toFixed(0) || 0}
                        color={competitor.is_you ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Strengths and Weaknesses */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {processedStrengths && processedStrengths.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, bgcolor: 'white', border: `2px solid ${COLORS.accent}`, boxShadow: 2 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
                Competitive Strengths
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {processedStrengths.map((strength: string, index: number) => (
                <Typography key={index} variant="body1" sx={{ mb: 1.5, pl: 2, color: COLORS.neutral }}>
                  • {strength}
                </Typography>
              ))}
            </Paper>
          </Grid>
        )}

        {processedWeaknesses && processedWeaknesses.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, bgcolor: 'white', border: `2px solid ${COLORS.error}`, boxShadow: 2 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
                Areas for Improvement
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {processedWeaknesses.map((weakness: string, index: number) => (
                <Typography key={index} variant="body1" sx={{ mb: 1.5, pl: 2, color: COLORS.neutral }}>
                  • {weakness}
                </Typography>
              ))}
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Opportunities */}
      {processedOpportunities && processedOpportunities.length > 0 && (
        <Paper sx={{ p: 3, border: `1px solid ${COLORS.border}` }}>
          <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: COLORS.dark }}>
            Market Opportunities
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            {processedOpportunities.map((opportunity: string, index: number) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ bgcolor: 'white', border: `2px solid ${COLORS.primary}`, boxShadow: 2 }}>
                  <CardContent>
                    <Typography variant="body1" sx={{ color: COLORS.neutral }}>
                      • {opportunity}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Container>
    </Box>
  );
};

export default CompetitiveAnalysisReport;

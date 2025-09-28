import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  CircularProgress,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Fade,
  Grow
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Description,
  People,
  Assessment,
  CompareArrows,
  CheckCircle,
  Schedule,
  Error as ErrorIcon,
  AutoAwesome,
  DataUsage,
  Insights,
  BarChart,
  Timeline,
  Analytics
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { reportService, ReportTemplate, GeneratedReport } from '../services/reportService';


const Report: React.FC = () => {
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [generateDialog, setGenerateDialog] = useState({ open: false, template: null as ReportTemplate | null });
  const [reportTitle, setReportTitle] = useState('');
  const [generating, setGenerating] = useState(false);
  const navigate = useNavigate();
  const { organizationId, projectId } = useParams();

  // API functions
  const fetchTemplates = useCallback(async () => {
    try {
      const templatesData = await reportService.getTemplates();
      setTemplates(templatesData);
    } catch (error) {
      console.error('Error fetching templates:', error);
      showSnackbar('Failed to load report templates', 'error');
    }
  }, []);

  const fetchReports = useCallback(async () => {
    try {
      const reportsData = await reportService.getReports();
      setReports(reportsData);
    } catch (error) {
      console.error('Error fetching reports:', error);
      showSnackbar('Failed to load recent reports', 'error');
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchTemplates(), fetchReports()]);
      setLoading(false);
    };
    loadData();
  }, [fetchTemplates, fetchReports]);

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const getTemplateIcon = (iconName: string) => {
    const iconMap: { [key: string]: React.ReactNode } = {
      psychology: <Psychology />,
      trending_up: <TrendingUp />,
      article: <Description />,
      description: <Description />,
      people: <People />,
      assessment: <Assessment />,
      show_chart: <Timeline />,
      compare_arrows: <CompareArrows />,
      analytics: <Analytics />,
      bar_chart: <BarChart />,
      data_usage: <DataUsage />
    };
    return iconMap[iconName] || <AutoAwesome />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle />;
      case 'processing':
        return <Schedule />;
      case 'failed':
        return <ErrorIcon />;
      default:
        return <Schedule />;
    }
  };

  const getStatusColor = (status: string) => {
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

  const handleGenerateReport = (template: ReportTemplate) => {
    setGenerateDialog({ open: true, template });
    setReportTitle(`${template.name} - ${new Date().toLocaleDateString()}`);
  };

  const handleConfirmGenerate = async () => {
    if (!generateDialog.template) return;

    setGenerating(true);
    try {
      // Generate report using the API (with project context)
      const newReport = await reportService.generateReport(
        generateDialog.template.id,
        reportTitle,
        {}, // configuration can be expanded later
        projectId // Pass project ID for real data analysis
      );

      setReports(prev => [newReport, ...prev]);
      setGenerateDialog({ open: false, template: null });
      showSnackbar(`Report "${reportTitle}" generated successfully!`, 'success');

      // Navigate to the generated report with proper context
      if (organizationId && projectId) {
        navigate(`/organizations/${organizationId}/projects/${projectId}/report/generated/${newReport.id}`);
      } else {
        navigate(`/report/generated/${newReport.id}`);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      showSnackbar('Failed to generate report. Please try again.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleViewReport = (reportId: number) => {
    if (organizationId && projectId) {
      navigate(`/organizations/${organizationId}/projects/${projectId}/report/generated/${reportId}`);
    } else {
      navigate(`/report/generated/${reportId}`);
    }
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

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>        
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          Report Marketplace
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Select from our pre-built analytics templates to generate insights from your social media data
        </Typography>
      </Box>

      {/* Template Marketplace */}
      <Box mb={6}>
        <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ mb: 3 }}>
          Available Templates
        </Typography>
        
        <Grid container spacing={3}>
          {templates.map((template, index) => (
            <Grid size={{ xs: 12, md: 6, lg: 4 }} key={template.id}>
              <Grow in={true} timeout={300 + index * 100}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    transition: 'transform 0.2s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                    }
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Avatar 
                        sx={{ 
                          bgcolor: `${template.color}.main`, 
                          mr: 2,
                          width: 48,
                          height: 48
                        }}
                      >
                        {getTemplateIcon(template.icon)}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" fontWeight="bold">
                          {template.name}
                        </Typography>
                        <Chip 
                          label={template.estimated_time} 
                          size="small" 
                          color="primary" 
                          variant="outlined" 
                        />
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      {template.description}
                    </Typography>
                    
                    <Box mb={2}>
                      <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                        Key Features:
                      </Typography>
                      {template.features.slice(0, 3).map((feature, idx) => (
                        <Typography key={idx} variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                          • {feature}
                        </Typography>
                      ))}
                    </Box>
                    
                    <Box>
                      <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                        Required Data:
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {template.required_data_types.map((type) => (
                          <Chip 
                            key={type} 
                            label={type} 
                            size="small" 
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  </CardContent>
                  
                  <CardActions sx={{ p: 2 }}>
                    <Button 
                      variant="contained" 
                      fullWidth
                      onClick={() => handleGenerateReport(template)}
                      startIcon={<Insights />}
                    >
                      Generate Report
                    </Button>
                  </CardActions>
                </Card>
              </Grow>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Generate Report Dialog */}
      <Dialog 
        open={generateDialog.open} 
        onClose={() => setGenerateDialog({ open: false, template: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Generate New Report</DialogTitle>
        <DialogContent>
          {generateDialog.template && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {generateDialog.template.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {generateDialog.template.description}
              </Typography>
              
              <TextField
                autoFocus
                margin="dense"
                label="Report Title"
                fullWidth
                variant="outlined"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                sx={{ mt: 2 }}
              />
              
              <Box mt={2}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  This report will include:
                </Typography>
                {generateDialog.template.features.map((feature, idx) => (
                  <Typography key={idx} variant="body2" color="text.secondary">
                    • {feature}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialog({ open: false, template: null })}>
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmGenerate} 
            variant="contained"
            disabled={generating || !reportTitle.trim()}
          >
            {generating ? <CircularProgress size={20} /> : 'Generate Report'}
          </Button>
        </DialogActions>
      </Dialog>

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

export default Report; 
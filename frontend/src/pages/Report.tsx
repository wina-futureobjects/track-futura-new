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
  Grow,
  Tabs,
  Tab,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Checkbox,
  ListItemText,
  SelectChangeEvent
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
  Analytics,
  TableChart,
  Storefront
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { reportService, ReportTemplate, GeneratedReport } from '../services/reportService';
import UniversalDataDisplay from '../components/UniversalDataDisplay';


interface DataSource {
  id: number;
  name: string;
  type: 'folder' | 'batch_job';
  created_at: string;
  post_count?: number;
  platform?: string;
}

const Report: React.FC = () => {
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [generateDialog, setGenerateDialog] = useState({ open: false, template: null as ReportTemplate | null });
  const [reportTitle, setReportTitle] = useState('');
  const [generating, setGenerating] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [selectedDataSources, setSelectedDataSources] = useState<number[]>([]);
  const [loadingDataSources, setLoadingDataSources] = useState(false);

  // Source Folders for Competitive Analysis
  const [sourceFolders, setSourceFolders] = useState<any[]>([]);
  const [selectedBrandFolders, setSelectedBrandFolders] = useState<number[]>([]);
  const [selectedCompetitorFolders, setSelectedCompetitorFolders] = useState<number[]>([]);
  const [loadingSourceFolders, setLoadingSourceFolders] = useState(false);

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

  const fetchDataSources = useCallback(async () => {
    setLoadingDataSources(true);
    try {
      // Fetch folders from all platforms
      const platforms = ['instagram', 'facebook', 'tiktok', 'linkedin'];
      const allSources: DataSource[] = [];

      for (const platform of platforms) {
        try {
          // Build URL with optional project filter
          const url = projectId
            ? `/api/${platform}-data/folders/?project=${projectId}`
            : `/api/${platform}-data/folders/`;

          const response = await fetch(url);
          if (response.ok) {
            const data = await response.json();
            const sources: DataSource[] = data.results.map((folder: any) => ({
              id: folder.id,
              name: folder.name,
              type: 'folder' as const,
              created_at: folder.created_at,
              post_count: folder.post_count || folder.reel_count || folder.comment_count || 0,
              platform: platform
            }));
            allSources.push(...sources);
          }
        } catch (error) {
          console.error(`Error fetching ${platform} folders:`, error);
        }
      }

      // Sort by created_at descending (newest first)
      allSources.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setDataSources(allSources);
    } catch (error) {
      console.error('Error fetching data sources:', error);
      showSnackbar('Failed to load sources. Please try again.', 'error');
    } finally {
      setLoadingDataSources(false);
    }
  }, [projectId]);

  const fetchSourceFolders = useCallback(async () => {
    if (!projectId) return;

    setLoadingSourceFolders(true);
    try {
      const response = await fetch(`/api/track-accounts/source-folders/?project=${projectId}&for_reports=true`);
      if (response.ok) {
        const data = await response.json();
        setSourceFolders(data.results || data || []);
      } else {
        console.error('Failed to fetch source folders');
        showSnackbar('Failed to load source folders', 'error');
      }
    } catch (error) {
      console.error('Error fetching source folders:', error);
      showSnackbar('Failed to load source folders', 'error');
    } finally {
      setLoadingSourceFolders(false);
    }
  }, [projectId]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchTemplates(), fetchReports()]);
      setLoading(false);
    };
    loadData();
  }, [fetchTemplates, fetchReports]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

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

  const handleGenerateReport = async (template: ReportTemplate) => {
    setGenerateDialog({ open: true, template });
    setReportTitle(`${template.name} - ${new Date().toLocaleDateString()}`);
    setSelectedDataSources([]);
    setSelectedBrandFolders([]);
    setSelectedCompetitorFolders([]);

    // For Competitive Analysis and Sentiment Analysis, fetch source folders instead of data sources
    if (template.name === 'Competitive Analysis' || template.name === 'Sentiment Analysis') {
      await fetchSourceFolders();
    } else {
      // Fetch available data sources when dialog opens
      await fetchDataSources();
    }
  };

  const handleDataSourceChange = (event: SelectChangeEvent<number[]>) => {
    const value = event.target.value;
    setSelectedDataSources(typeof value === 'string' ? value.split(',').map(Number) : value);
  };

  const handleBrandFolderChange = (event: SelectChangeEvent<number[]>) => {
    const value = event.target.value;
    setSelectedBrandFolders(typeof value === 'string' ? value.split(',').map(Number) : value);
  };

  const handleCompetitorFolderChange = (event: SelectChangeEvent<number[]>) => {
    const value = event.target.value;
    setSelectedCompetitorFolders(typeof value === 'string' ? value.split(',').map(Number) : value);
  };

  const handleConfirmGenerate = async () => {
    if (!generateDialog.template) return;

    setGenerating(true);
    try {
      // Prepare configuration based on template type
      let configuration: any;

      if (generateDialog.template.name === 'Competitive Analysis' || generateDialog.template.name === 'Sentiment Analysis') {
        // For Competitive Analysis and Sentiment Analysis, use brand and competitor source folders
        configuration = {
          brand_folder_ids: selectedBrandFolders,
          competitor_folder_ids: selectedCompetitorFolders
        };
      } else {
        // For other templates, use regular data sources
        configuration = {
          batch_job_ids: selectedDataSources.filter(id => {
            const source = dataSources.find(s => s.id === id);
            return source?.type === 'batch_job';
          }),
          folder_ids: selectedDataSources.filter(id => {
            const source = dataSources.find(s => s.id === id);
            return source?.type === 'folder';
          })
        };
      }

      // Generate report using the API (with project context and data sources)
      const newReport = await reportService.generateReport(
        generateDialog.template.id,
        reportTitle,
        configuration,
        projectId // Pass project ID for real data analysis
      );

      setReports(prev => [newReport, ...prev]);
      setGenerateDialog({ open: false, template: null });
      showSnackbar(`Report "${reportTitle}" generated successfully!`, 'success');

      // Navigate to template-specific report page
      const templateType = generateDialog.template.template_type;
      let templatePath = '';

      switch (templateType) {
        case 'engagement_metrics':
          templatePath = 'engagement-metrics';
          break;
        case 'sentiment_analysis':
          templatePath = 'sentiment-analysis';
          break;
        case 'content_analysis':
          templatePath = 'content-analysis';
          break;
        case 'trend_analysis':
          templatePath = 'trend-analysis';
          break;
        case 'competitive_analysis':
          templatePath = 'competitive-analysis';
          break;
        case 'user_behavior':
          templatePath = 'user-behavior';
          break;
        default:
          templatePath = 'generated';
      }

      if (organizationId && projectId) {
        navigate(`/organizations/${organizationId}/projects/${projectId}/reports/${templatePath}/${newReport.id}`);
      } else {
        navigate(`/reports/${templatePath}/${newReport.id}`);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      showSnackbar('Failed to generate report. Please try again.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleViewReport = (reportId: number) => {
    // Find the report to get its template type
    const report = reports.find(r => r.id === reportId);
    const templateType = report?.template_type;

    let templatePath = '';
    switch (templateType) {
      case 'engagement_metrics':
        templatePath = 'engagement-metrics';
        break;
      case 'sentiment_analysis':
        templatePath = 'sentiment-analysis';
        break;
      case 'content_analysis':
        templatePath = 'content-analysis';
        break;
      case 'trend_analysis':
        templatePath = 'trend-analysis';
        break;
      case 'competitive_analysis':
        templatePath = 'competitive-analysis';
        break;
      case 'user_behavior':
        templatePath = 'user-behavior';
        break;
      default:
        templatePath = 'generated';
    }

    if (organizationId && projectId) {
      navigate(`/organizations/${organizationId}/projects/${projectId}/reports/${templatePath}/${reportId}`);
    } else {
      navigate(`/reports/${templatePath}/${reportId}`);
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
          Generate insights from templates or view and edit your scraped data
        </Typography>
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab 
            icon={<Storefront />} 
            label="Report Templates" 
            iconPosition="start"
          />
          <Tab 
            icon={<TableChart />} 
            label="Data View & Edit" 
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {currentTab === 0 && (
        <Box>
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
        </Box>
      )}

      {currentTab === 1 && (
        <Box>
          {/* Data View & Edit Section */}
          <Box mb={3}>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Scraped Data - View & Edit
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              View and edit your scraped social media data directly. Click the edit button to modify any incorrect data.
            </Typography>
          </Box>
          
          {/* Universal Data Display Component */}
          <Paper sx={{ p: 3, borderRadius: 2, boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
            <UniversalDataDisplay 
              folder={{
                id: 8, // Using batch job 8 which has sample data
                name: "Sample Data for Editing",
                description: "Sample Instagram data for testing inline editing functionality",
                category: "posts",
                category_display: "Posts",
                platform: "instagram",
                action_type: "collect_posts"
              }}
              platform="instagram"
            />
          </Paper>
        </Box>
      )}

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

              {/* Data Source Selection - Different for Competitive Analysis and Sentiment Analysis */}
              {(generateDialog.template.name === 'Competitive Analysis' || generateDialog.template.name === 'Sentiment Analysis') ? (
                <>
                  {/* Brand Sources Selection */}
                  <FormControl fullWidth sx={{ mt: 2 }}>
                    <InputLabel id="brand-folder-label">
                      {generateDialog.template.name === 'Sentiment Analysis' ? 'Select Nike Data Sources' : 'Select Brand Sources'}
                    </InputLabel>
                    <Select
                      labelId="brand-folder-label"
                      multiple
                      value={selectedBrandFolders}
                      onChange={handleBrandFolderChange}
                      input={<OutlinedInput label={generateDialog.template.name === 'Sentiment Analysis' ? 'Select Nike Data Sources' : 'Select Brand Sources'} />}
                      renderValue={(selected) => 
                        generateDialog.template.name === 'Sentiment Analysis' 
                          ? `${selected.length} Nike data source(s) selected`
                          : `${selected.length} brand source(s) selected`
                      }
                      disabled={loadingSourceFolders}
                    >
                      {loadingSourceFolders ? (
                        <MenuItem disabled>
                          <CircularProgress size={20} sx={{ mr: 1 }} />
                          Loading source folders...
                        </MenuItem>
                      ) : sourceFolders.filter(f => f.folder_type === 'company').length === 0 ? (
                        <MenuItem disabled>
                          {generateDialog.template.name === 'Sentiment Analysis' 
                            ? 'No Nike data sources available. Please create Nike source folders first.'
                            : 'No brand sources available. Please create brand source folders first.'
                          }
                        </MenuItem>
                      ) : (
                        sourceFolders
                          .filter(folder => folder.folder_type === 'company')
                          .map((folder) => (
                            <MenuItem key={folder.id} value={folder.id}>
                              <Checkbox checked={selectedBrandFolders.indexOf(folder.id) > -1} />
                              <ListItemText
                                primary={folder.name}
                                secondary={`${folder.source_count || 0} sources`}
                              />
                            </MenuItem>
                          ))
                      )}
                    </Select>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      {selectedBrandFolders.length === 0
                        ? (generateDialog.template.name === 'Sentiment Analysis' 
                            ? 'Select at least one Nike data source folder'
                            : 'Select at least one brand source folder')
                        : (generateDialog.template.name === 'Sentiment Analysis'
                            ? `${selectedBrandFolders.length} Nike folder(s) selected`
                            : `${selectedBrandFolders.length} brand folder(s) selected`)
                      }
                    </Typography>
                  </FormControl>

                  {/* Competitor Sources Selection */}
                  <FormControl fullWidth sx={{ mt: 2 }}>
                    <InputLabel id="competitor-folder-label">
                      {generateDialog.template.name === 'Sentiment Analysis' ? 'Select Adidas Data Sources (Optional)' : 'Select Competitor Sources'}
                    </InputLabel>
                    <Select
                      labelId="competitor-folder-label"
                      multiple
                      value={selectedCompetitorFolders}
                      onChange={handleCompetitorFolderChange}
                      input={<OutlinedInput label={generateDialog.template.name === 'Sentiment Analysis' ? 'Select Adidas Data Sources (Optional)' : 'Select Competitor Sources'} />}
                      renderValue={(selected) => 
                        generateDialog.template.name === 'Sentiment Analysis'
                          ? `${selected.length} Adidas data source(s) selected`
                          : `${selected.length} competitor source(s) selected`
                      }
                      disabled={loadingSourceFolders}
                    >
                      {loadingSourceFolders ? (
                        <MenuItem disabled>
                          <CircularProgress size={20} sx={{ mr: 1 }} />
                          Loading source folders...
                        </MenuItem>
                      ) : sourceFolders.filter(f => f.folder_type === 'competitor').length === 0 ? (
                        <MenuItem disabled>
                          {generateDialog.template.name === 'Sentiment Analysis'
                            ? 'No Adidas data sources available. You can still analyze Nike sentiment data alone.'
                            : 'No competitor sources available. Please create competitor source folders first.'
                          }
                        </MenuItem>
                      ) : (
                        sourceFolders
                          .filter(folder => folder.folder_type === 'competitor')
                          .map((folder) => (
                            <MenuItem key={folder.id} value={folder.id}>
                              <Checkbox checked={selectedCompetitorFolders.indexOf(folder.id) > -1} />
                              <ListItemText
                                primary={folder.name}
                                secondary={`${folder.source_count || 0} sources`}
                              />
                            </MenuItem>
                          ))
                      )}
                    </Select>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      {generateDialog.template.name === 'Sentiment Analysis' ? (
                        selectedCompetitorFolders.length === 0
                          ? 'Optional: Select Adidas data sources for comparative sentiment analysis'
                          : `${selectedCompetitorFolders.length} Adidas folder(s) selected for comparison`
                      ) : (
                        selectedCompetitorFolders.length === 0
                          ? 'Select at least one competitor source folder'
                          : `${selectedCompetitorFolders.length} competitor folder(s) selected`
                      )}
                    </Typography>
                  </FormControl>
                </>
              ) : (
                /* Regular Data Source Selection for Other Templates */
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel id="data-source-label">Select Data Sources</InputLabel>
                  <Select
                    labelId="data-source-label"
                    multiple
                    value={selectedDataSources}
                    onChange={handleDataSourceChange}
                    input={<OutlinedInput label="Select Data Sources" />}
                    renderValue={(selected) => `${selected.length} data source(s) selected`}
                    disabled={loadingDataSources}
                  >
                    {loadingDataSources ? (
                      <MenuItem disabled>
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                        Loading data sources...
                      </MenuItem>
                    ) : dataSources.length === 0 ? (
                      <MenuItem disabled>
                        No data sources available. Please scrape some data first.
                      </MenuItem>
                    ) : (
                      dataSources.map((source) => (
                        <MenuItem key={source.id} value={source.id}>
                          <Checkbox checked={selectedDataSources.indexOf(source.id) > -1} />
                          <ListItemText
                            primary={source.name}
                            secondary={`${source.post_count || 0} posts • ${new Date(source.created_at).toLocaleDateString()}`}
                          />
                        </MenuItem>
                      ))
                    )}
                  </Select>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                    {selectedDataSources.length === 0
                      ? 'Select at least one data source to generate the report'
                      : `Report will analyze ${dataSources.filter(s => selectedDataSources.includes(s.id)).reduce((sum, s) => sum + (s.post_count || 0), 0)} posts`
                    }
                  </Typography>
                </FormControl>
              )}

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
            disabled={
              generating ||
              !reportTitle.trim() ||
              ((generateDialog.template?.name === 'Competitive Analysis' || generateDialog.template?.name === 'Sentiment Analysis')
                ? (selectedBrandFolders.length === 0 || (generateDialog.template?.name === 'Competitive Analysis' && selectedCompetitorFolders.length === 0))
                : selectedDataSources.length === 0
              )
            }
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
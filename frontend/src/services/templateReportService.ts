/**
 * Template-Specific Report Service
 * Handles fetching reports with template-specific visualizations
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

// Helper function for API calls
const apiFetch = async (endpoint: string) => {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
};

/**
 * Fetch Engagement Metrics Report
 */
export const fetchEngagementMetricsReport = async (reportId: number) => {
  console.log(`📊 Fetching Engagement Metrics Report #${reportId}`);
  const data = await apiFetch(`/api/reports/engagement-metrics/${reportId}/`);
  console.log('✅ Engagement Metrics Data:', data);
  return data;
};

/**
 * Fetch Sentiment Analysis Report
 */
export const fetchSentimentAnalysisReport = async (reportId: number) => {
  console.log(`📊 Fetching Sentiment Analysis Report #${reportId}`);
  const data = await apiFetch(`/api/reports/sentiment-analysis/${reportId}/`);
  console.log('✅ Sentiment Analysis Data:', data);
  return data;
};

/**
 * Fetch Content Analysis Report
 */
export const fetchContentAnalysisReport = async (reportId: number) => {
  console.log(`📊 Fetching Content Analysis Report #${reportId}`);
  const data = await apiFetch(`/api/reports/content-analysis/${reportId}/`);
  console.log('✅ Content Analysis Data:', data);
  return data;
};

/**
 * Fetch Trend Analysis Report
 */
export const fetchTrendAnalysisReport = async (reportId: number) => {
  console.log(`📊 Fetching Trend Analysis Report #${reportId}`);
  const data = await apiFetch(`/api/reports/trend-analysis/${reportId}/`);
  console.log('✅ Trend Analysis Data:', data);
  return data;
};

/**
 * Fetch Competitive Analysis Report
 */
export const fetchCompetitiveAnalysisReport = async (reportId: number) => {
  console.log(`📊 Fetching Competitive Analysis Report #${reportId}`);
  const data = await apiFetch(`/api/reports/competitive-analysis/${reportId}/`);
  console.log('✅ Competitive Analysis Data:', data);
  return data;
};

/**
 * Fetch User Behavior Report
 */
export const fetchUserBehaviorReport = async (reportId: number) => {
  console.log(`📊 Fetching User Behavior Report #${reportId}`);
  const data = await apiFetch(`/api/reports/user-behavior/${reportId}/`);
  console.log('✅ User Behavior Data:', data);
  return data;
};

/**
 * Auto-detect template type and fetch appropriate report
 */
export const fetchReportByTemplate = async (reportId: number, templateType: string) => {
  console.log(`🔍 Auto-fetching report #${reportId} with template type: ${templateType}`);

  switch (templateType) {
    case 'engagement_metrics':
      return fetchEngagementMetricsReport(reportId);
    case 'sentiment_analysis':
      return fetchSentimentAnalysisReport(reportId);
    case 'content_analysis':
      return fetchContentAnalysisReport(reportId);
    case 'trend_analysis':
      return fetchTrendAnalysisReport(reportId);
    case 'competitive_analysis':
      return fetchCompetitiveAnalysisReport(reportId);
    case 'user_behavior':
      return fetchUserBehaviorReport(reportId);
    default:
      throw new Error(`Unknown template type: ${templateType}`);
  }
};

export default {
  fetchEngagementMetricsReport,
  fetchSentimentAnalysisReport,
  fetchContentAnalysisReport,
  fetchTrendAnalysisReport,
  fetchCompetitiveAnalysisReport,
  fetchUserBehaviorReport,
  fetchReportByTemplate,
};

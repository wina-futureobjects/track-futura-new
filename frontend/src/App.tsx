import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import React from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

// Component imports
import Layout from './components/layout/Layout';
import NoSidebarLayout from './components/NoSidebarLayout';
import Analysis from './pages/Analysis';
import Dashboard3 from './pages/Dashboard3';
import Settings from './pages/Settings';
import TrackAccountCreate from './pages/TrackAccountCreate';
import TrackAccountEdit from './pages/TrackAccountEdit';
import TrackAccountsList from './pages/TrackAccountsList';
import TrackAccountUpload from './pages/TrackAccountUpload';

// Folder imports
import DataStorage from './pages/DataStorage';
import FolderContents from './pages/FolderContents';
import JobFolderView from './pages/JobFolderView';

// Data upload imports
import UniversalDataPage from './pages/UniversalDataPage';

// Report imports
import GeneratedReports from './pages/GeneratedReports';
import MultiPlatformReportGeneration from './pages/MultiPlatformReportGeneration';
import Report from './pages/Report';
import ReportDetail from './pages/ReportDetail';
import ReportFolders from './pages/ReportFolders';
import ReportView from './pages/ReportView';
import GeneratedReportDetail from './pages/GeneratedReportDetail';
import EngagementMetricsReport from './pages/EngagementMetricsReport';
import SentimentAnalysisReport from './pages/SentimentAnalysisReport';
import ContentAnalysisReport from './pages/ContentAnalysisReport';
import TrendAnalysisReport from './pages/TrendAnalysisReport';
import CompetitiveAnalysisReport from './pages/CompetitiveAnalysisReport';
import UserBehaviorReport from './pages/UserBehaviorReport';

// Admin and auth imports
import SuperAdminDashboard from './pages/admin/SuperAdminDashboard';
import TenantAdminDashboard from './pages/admin/TenantAdminDashboard';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import OrganizationProjects from './pages/OrganizationProjects';
import OrganizationsList from './pages/OrganizationsList';

// Scraper and comment imports
import AutomatedBatchScraper from './pages/AutomatedBatchScraper';
import CommentsScraper from './pages/CommentsScraper';
import FacebookCommentScraper from './pages/FacebookCommentScraper';

// Theme and auth imports
import AdminRoute from './components/auth/AdminRoute';
import { AuthProvider } from './components/auth/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import RouteGuard from './components/auth/RouteGuard';
import ProjectSelectionHandler from './components/ProjectSelectionHandler';
import RoleBasedRedirect from './components/RoleBasedRedirect';
import theme from './theme/index';

// Webhook monitoring
import WebhookMonitorDashboard from './components/webhook/WebhookMonitorDashboard';

// BrightData notifications
import BrightDataNotifications from './pages/BrightDataNotifications';

// Additional pages
import InstagramFolderSelector from './FolderSelectionReportGenerator';

// Auth utility
import { isAuthenticated } from './utils/auth';

// Legacy route redirect component
const LegacyRouteRedirect: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <RouteGuard requireOrgProject={true}>
      <Layout>
        {children}
      </Layout>
    </RouteGuard>
  );
};

// Project dashboard with selection handler
const ProjectDashboardWithHandler: React.FC = () => {
  return (
    <ProtectedRoute>
      <Layout>
        <ProjectSelectionHandler />
        <Dashboard3 />
      </Layout>
    </ProtectedRoute>
  );
};

function App() {

  return (
    <AuthProvider>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Root route - redirect based on role if authenticated */}
              <Route path="/" element={
                isAuthenticated() ? (
                  <RoleBasedRedirect />
                ) : (
                  <Navigate to="/login" />
                )
              } />

              {/* Admin routes */}
              <Route path="/admin/super" element={
                <AdminRoute requiredRole="super_admin">
                  <NoSidebarLayout>
                    <SuperAdminDashboard />
                  </NoSidebarLayout>
                </AdminRoute>
              } />
              <Route path="/admin/tenant" element={
                <AdminRoute requiredRole="tenant_admin">
                  <NoSidebarLayout>
                    <TenantAdminDashboard />
                  </NoSidebarLayout>
                </AdminRoute>
              } />

              {/* Organizations routes - no sidebar */}
              <Route path="/organizations" element={
                <ProtectedRoute>
                  <NoSidebarLayout>
                    <OrganizationsList />
                  </NoSidebarLayout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects" element={
                <ProtectedRoute>
                  <NoSidebarLayout>
                    <OrganizationProjects />
                  </NoSidebarLayout>
                </ProtectedRoute>
              } />

              {/* MAIN PROJECT DASHBOARD - with organization context */}
              <Route path="/organizations/:organizationId/projects/:projectId" element={<ProjectDashboardWithHandler />} />

              {/* =========================== */}
              {/* LEGACY ROUTE REDIRECTS */}
              {/* =========================== */}

              {/* Legacy dashboard routes - redirect to org selection */}
              <Route path="/dashboard" element={<LegacyRouteRedirect><Dashboard3 /></LegacyRouteRedirect>} />
              <Route path="/dashboard/:projectId" element={<LegacyRouteRedirect><Dashboard3 /></LegacyRouteRedirect>} />

              {/* Legacy track accounts routes - redirect to org selection */}
              <Route path="/track-accounts" element={<LegacyRouteRedirect><TrackAccountsList /></LegacyRouteRedirect>} />
              <Route path="/track-accounts/accounts" element={<LegacyRouteRedirect><TrackAccountsList /></LegacyRouteRedirect>} />
              <Route path="/track-accounts/upload" element={<LegacyRouteRedirect><TrackAccountUpload /></LegacyRouteRedirect>} />
              <Route path="/track-accounts/create" element={<LegacyRouteRedirect><TrackAccountCreate /></LegacyRouteRedirect>} />
              <Route path="/track-accounts/edit/:accountId" element={<LegacyRouteRedirect><TrackAccountEdit /></LegacyRouteRedirect>} />

                             {/* Legacy social media folder routes - redirect to org selection */}
               <Route path="/data-storage" element={<LegacyRouteRedirect><DataStorage /></LegacyRouteRedirect>} />
               <Route path="/data/:platform/:folderId" element={<LegacyRouteRedirect><UniversalDataPage /></LegacyRouteRedirect>} />

              {/* Legacy analysis routes */}
              <Route path="/analysis" element={<LegacyRouteRedirect><Analysis /></LegacyRouteRedirect>} />
              <Route path="/social-analysis" element={<Navigate to="/analysis" replace />} />
              <Route path="/web-presence" element={<Navigate to="/analysis" replace />} />
              <Route path="/sentiment" element={<Navigate to="/analysis" replace />} />
              <Route path="/wordcloud" element={<Navigate to="/analysis" replace />} />
              <Route path="/nps-reports" element={<Navigate to="/analysis" replace />} />

              {/* Legacy report routes */}
              <Route path="/report" element={<LegacyRouteRedirect><Report /></LegacyRouteRedirect>} />
              <Route path="/report/:id" element={<LegacyRouteRedirect><ReportView /></LegacyRouteRedirect>} />
              <Route path="/report/generated/:id" element={<LegacyRouteRedirect><GeneratedReportDetail /></LegacyRouteRedirect>} />
              <Route path="/reports/generated" element={<LegacyRouteRedirect><GeneratedReports /></LegacyRouteRedirect>} />
              <Route path="/report-folders" element={<LegacyRouteRedirect><ReportFolders /></LegacyRouteRedirect>} />
              <Route path="/report-folders/:reportId" element={<LegacyRouteRedirect><ReportDetail /></LegacyRouteRedirect>} />
              <Route path="/report-folders/:reportId/instagram-data" element={<LegacyRouteRedirect><InstagramFolderSelector /></LegacyRouteRedirect>} />
              <Route path="/report-folders/create/multi-platform" element={<LegacyRouteRedirect><MultiPlatformReportGeneration /></LegacyRouteRedirect>} />
              <Route path="/report-folders/:reportId/edit-multi-platform" element={<LegacyRouteRedirect><MultiPlatformReportGeneration /></LegacyRouteRedirect>} />

              {/* Legacy scraper routes */}
              <Route path="/comments-scraper" element={<LegacyRouteRedirect><CommentsScraper /></LegacyRouteRedirect>} />
              <Route path="/facebook-comment-scraper" element={<LegacyRouteRedirect><FacebookCommentScraper /></LegacyRouteRedirect>} />
              <Route path="/brightdata-scraper" element={<LegacyRouteRedirect><AutomatedBatchScraper /></LegacyRouteRedirect>} />
              <Route path="/automated-batch-scraper" element={<LegacyRouteRedirect><AutomatedBatchScraper /></LegacyRouteRedirect>} />
              <Route path="/workflow-management" element={<LegacyRouteRedirect><AutomatedBatchScraper /></LegacyRouteRedirect>} />

                             {/* Legacy redirects */}
               <Route path="/projects" element={<Navigate to="/organizations" replace />} />
               <Route path="/instagram-data" element={<Navigate to="/data-storage" replace />} />
               <Route path="/facebook-data" element={<Navigate to="/data-storage" replace />} />
               <Route path="/linkedin-data" element={<Navigate to="/data-storage" replace />} />
               <Route path="/tiktok-data" element={<Navigate to="/data-storage" replace />} />
               <Route path="/reports" element={<Navigate to="/report-folders" replace />} />

              {/* =========================== */}
              {/* PROPER ORGANIZATION/PROJECT ROUTES */}
              {/* =========================== */}

              {/* Source Tracking (Track Accounts) */}
              <Route path="/organizations/:organizationId/projects/:projectId/source-tracking" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountsList />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/source-tracking/sources" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountsList />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/source-tracking/upload" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountUpload />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/source-tracking/create" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountCreate />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/source-tracking/edit/:accountId" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountEdit />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Analysis routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/analysis" element={
                <ProtectedRoute>
                  <Layout>
                    <Analysis />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Social Media Data Routes */}
              {/* Data Storage - All Platforms */}
              <Route path="/organizations/:organizationId/projects/:projectId/data-storage" element={
                <ProtectedRoute>
                  <Layout>
                    <DataStorage />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Folder Contents - File Explorer Style */}
              <Route path="/organizations/:organizationId/projects/:projectId/data-storage/:folderType/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <FolderContents />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Job Folder View - Special handling for job folders */}
              <Route path="/organizations/:organizationId/projects/:projectId/data-storage/job/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <JobFolderView />
                  </Layout>
                </ProtectedRoute>
              } />
              
              <Route path="/organizations/:organizationId/projects/:projectId/data/:platform/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <UniversalDataPage />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Comments Scraper routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/comments-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <CommentsScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/facebook-comment-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <FacebookCommentScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Report Marketplace routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/report" element={
                <ProtectedRoute>
                  <Layout>
                    <Report />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/report/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <ReportView />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/report/generated/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <GeneratedReportDetail />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Template-Specific Report Routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/reports/engagement-metrics/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <EngagementMetricsReport />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/reports/engagement-metrics/:id" element={
                <LegacyRouteRedirect>
                  <EngagementMetricsReport />
                </LegacyRouteRedirect>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/reports/sentiment-analysis/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <SentimentAnalysisReport />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/reports/sentiment-analysis/:id" element={
                <LegacyRouteRedirect>
                  <SentimentAnalysisReport />
                </LegacyRouteRedirect>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/reports/content-analysis/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <ContentAnalysisReport />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/reports/content-analysis/:id" element={
                <LegacyRouteRedirect>
                  <ContentAnalysisReport />
                </LegacyRouteRedirect>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/reports/trend-analysis/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <TrendAnalysisReport />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/reports/trend-analysis/:id" element={
                <LegacyRouteRedirect>
                  <TrendAnalysisReport />
                </LegacyRouteRedirect>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/reports/competitive-analysis/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <CompetitiveAnalysisReport />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/reports/competitive-analysis/:id" element={
                <LegacyRouteRedirect>
                  <CompetitiveAnalysisReport />
                </LegacyRouteRedirect>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/reports/user-behavior/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <UserBehaviorReport />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/reports/user-behavior/:id" element={
                <LegacyRouteRedirect>
                  <UserBehaviorReport />
                </LegacyRouteRedirect>
              } />

              {/* Generated Reports routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/reports/generated" element={
                <ProtectedRoute>
                  <Layout>
                    <GeneratedReports />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Report Folder routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/report-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <ReportFolders />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/report-folders/:reportId" element={
                <ProtectedRoute>
                  <Layout>
                    <ReportDetail />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/report-folders/:reportId/instagram-data" element={
                <ProtectedRoute>
                  <Layout>
                    <InstagramFolderSelector />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Multi-Platform Report Generation routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/report-folders/create/multi-platform" element={
                <ProtectedRoute>
                  <Layout>
                    <MultiPlatformReportGeneration />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/report-folders/:reportId/edit-multi-platform" element={
                <ProtectedRoute>
                  <Layout>
                    <MultiPlatformReportGeneration />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Brightdata routes */}


              <Route path="/organizations/:organizationId/projects/:projectId/brightdata-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <AutomatedBatchScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              <Route path="/organizations/:organizationId/projects/:projectId/automated-batch-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <AutomatedBatchScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Workflow Management route - separate from scraper */}
              <Route path="/organizations/:organizationId/projects/:projectId/workflow-management" element={
                <ProtectedRoute>
                  <Layout>
                    <AutomatedBatchScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Settings route - available at project level */}
              <Route path="/organizations/:organizationId/projects/:projectId/settings" element={
                <ProtectedRoute>
                  <Layout>
                    <Settings />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Webhook Monitor - project level route */}
              <Route path="/organizations/:organizationId/projects/:projectId/webhook-monitor" element={
                <ProtectedRoute>
                  <Layout>
                    <WebhookMonitorDashboard />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* BrightData Notifications Monitor - project level route */}
              <Route path="/organizations/:organizationId/projects/:projectId/brightdata-notifications" element={
                <ProtectedRoute>
                  <Layout>
                    <BrightDataNotifications />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Webhook Monitor - standalone for development/admin use */}
              <Route path="/webhook-monitor" element={
                <ProtectedRoute>
                  <Layout>
                    <WebhookMonitorDashboard />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* BrightData Notifications - standalone for development/admin use */}
              <Route path="/brightdata-notifications" element={
                <ProtectedRoute>
                  <Layout>
                    <BrightDataNotifications />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Global settings route (legacy) */}
              <Route path="/settings" element={<LegacyRouteRedirect><Settings /></LegacyRouteRedirect>} />

              {/* Catch-all route for invalid paths - redirect to organizations */}
              <Route path="*" element={<Navigate to="/organizations" replace />} />
            </Routes>
          </Router>
        </ThemeProvider>
      </LocalizationProvider>
    </AuthProvider>
  )
}

export default App

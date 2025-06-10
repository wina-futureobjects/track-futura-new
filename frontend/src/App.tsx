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
import FacebookFolders from './pages/FacebookFolders';
import InstagramFolders from './pages/InstagramFolders';
import LinkedInFolders from './pages/LinkedInFolders';
import TikTokFolders from './pages/TikTokFolders';

// Data upload imports
import FacebookDataUpload from './pages/FacebookDataUpload';
import InstagramDataUpload from './pages/InstagramDataUpload';
import LinkedInDataUpload from './pages/LinkedInDataUpload';
import TikTokDataUpload from './pages/TikTokDataUpload';

// Report imports
import GeneratedReports from './pages/GeneratedReports';
import MultiPlatformReportGeneration from './pages/MultiPlatformReportGeneration';
import Report from './pages/Report';
import ReportDetail from './pages/ReportDetail';
import ReportFolders from './pages/ReportFolders';
import ReportView from './pages/ReportView';

// Admin and auth imports
import SuperAdminDashboard from './pages/admin/SuperAdminDashboard';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import OrganizationProjects from './pages/OrganizationProjects';
import OrganizationsList from './pages/OrganizationsList';

// Scraper and comment imports
import AutomatedBatchScraper from './pages/AutomatedBatchScraper';
import BrightdataSettings from './pages/BrightdataSettings';
import CommentsScraper from './pages/CommentsScraper';
import FacebookCommentScraper from './pages/FacebookCommentScraper';

// Theme and auth imports
import AdminRoute from './components/auth/AdminRoute';
import { AuthProvider } from './components/auth/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import RouteGuard from './components/auth/RouteGuard';
import ProjectSelectionHandler from './components/ProjectSelectionHandler';
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

              {/* Root route - redirect to login if not authenticated */}
              <Route path="/" element={
                isAuthenticated() ? (
                  <NoSidebarLayout>
                    <OrganizationsList />
                  </NoSidebarLayout>
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
              <Route path="/instagram-folders" element={<LegacyRouteRedirect><InstagramFolders /></LegacyRouteRedirect>} />
              <Route path="/instagram-data/:folderId" element={<LegacyRouteRedirect><InstagramDataUpload /></LegacyRouteRedirect>} />
              <Route path="/facebook-folders" element={<LegacyRouteRedirect><FacebookFolders /></LegacyRouteRedirect>} />
              <Route path="/facebook-data/:folderId" element={<LegacyRouteRedirect><FacebookDataUpload /></LegacyRouteRedirect>} />
              <Route path="/linkedin-folders" element={<LegacyRouteRedirect><LinkedInFolders /></LegacyRouteRedirect>} />
              <Route path="/linkedin-data/:folderId" element={<LegacyRouteRedirect><LinkedInDataUpload /></LegacyRouteRedirect>} />
              <Route path="/tiktok-folders" element={<LegacyRouteRedirect><TikTokFolders /></LegacyRouteRedirect>} />
              <Route path="/tiktok-data/:folderId" element={<LegacyRouteRedirect><TikTokDataUpload /></LegacyRouteRedirect>} />

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
              <Route path="/report/generated/:id" element={<LegacyRouteRedirect><ReportView /></LegacyRouteRedirect>} />
              <Route path="/reports/generated" element={<LegacyRouteRedirect><GeneratedReports /></LegacyRouteRedirect>} />
              <Route path="/report-folders" element={<LegacyRouteRedirect><ReportFolders /></LegacyRouteRedirect>} />
              <Route path="/report-folders/:reportId" element={<LegacyRouteRedirect><ReportDetail /></LegacyRouteRedirect>} />
              <Route path="/report-folders/:reportId/instagram-data" element={<LegacyRouteRedirect><InstagramFolderSelector /></LegacyRouteRedirect>} />
              <Route path="/report-folders/create/multi-platform" element={<LegacyRouteRedirect><MultiPlatformReportGeneration /></LegacyRouteRedirect>} />
              <Route path="/report-folders/:reportId/edit-multi-platform" element={<LegacyRouteRedirect><MultiPlatformReportGeneration /></LegacyRouteRedirect>} />

              {/* Legacy scraper routes */}
              <Route path="/comments-scraper" element={<LegacyRouteRedirect><CommentsScraper /></LegacyRouteRedirect>} />
              <Route path="/facebook-comment-scraper" element={<LegacyRouteRedirect><FacebookCommentScraper /></LegacyRouteRedirect>} />
              <Route path="/brightdata-settings" element={<LegacyRouteRedirect><BrightdataSettings /></LegacyRouteRedirect>} />
              <Route path="/brightdata-scraper" element={<LegacyRouteRedirect><AutomatedBatchScraper /></LegacyRouteRedirect>} />
              <Route path="/automated-batch-scraper" element={<LegacyRouteRedirect><AutomatedBatchScraper /></LegacyRouteRedirect>} />

              {/* Legacy redirects */}
              <Route path="/projects" element={<Navigate to="/organizations" replace />} />
              <Route path="/instagram-data" element={<Navigate to="/instagram-folders" replace />} />
              <Route path="/facebook-data" element={<Navigate to="/facebook-folders" replace />} />
              <Route path="/linkedin-data" element={<Navigate to="/linkedin-folders" replace />} />
              <Route path="/tiktok-data" element={<Navigate to="/tiktok-folders" replace />} />
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
              {/* Instagram routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/instagram-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <InstagramFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/instagram-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <InstagramDataUpload />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Facebook routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/facebook-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <FacebookFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/facebook-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <FacebookDataUpload />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* LinkedIn routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/linkedin-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <LinkedInFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/linkedin-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <LinkedInDataUpload />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* TikTok routes */}
              <Route path="/organizations/:organizationId/projects/:projectId/tiktok-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <TikTokFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/organizations/:organizationId/projects/:projectId/tiktok-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <TikTokDataUpload />
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
                    <ReportView />
                  </Layout>
                </ProtectedRoute>
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
              <Route path="/organizations/:organizationId/projects/:projectId/brightdata-settings" element={
                <ProtectedRoute>
                  <Layout>
                    <BrightdataSettings />
                  </Layout>
                </ProtectedRoute>
              } />

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

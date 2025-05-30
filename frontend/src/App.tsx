import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, useParams } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';

// Component imports
import Layout from './components/layout/Layout';
import NoSidebarLayout from './components/NoSidebarLayout';
import Dashboard from './pages/Dashboard';
import Dashboard2 from './pages/Dashboard2';
import Dashboard3 from './pages/Dashboard3';
import ProjectDashboard from './pages/ProjectDashboard';
import Analysis from './pages/Analysis';
import Settings from './pages/Settings';
import TrackAccountsList from './pages/TrackAccountsList';
import TrackAccountUpload from './pages/TrackAccountUpload';
import TrackAccountCreate from './pages/TrackAccountCreate';
import TrackAccountEdit from './pages/TrackAccountEdit';

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
import ReportFolders from './pages/ReportFolders';
import ReportDetail from './pages/ReportDetail';
import ReportGeneration from './pages/ReportGeneration';
import MultiPlatformReportGeneration from './pages/MultiPlatformReportGeneration';
import FolderReportGeneration from './pages/FolderReportGeneration';

// Admin and auth imports
import OrganizationsList from './pages/OrganizationsList';
import OrganizationProjects from './pages/OrganizationProjects';
import ProjectsList from './pages/ProjectsList';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import AdminDashboard from './pages/admin/AdminDashboard';
import SuperAdminDashboard from './pages/admin/SuperAdminDashboard';

// Scraper and comment imports
import CommentsScraper from './pages/CommentsScraper';
import FacebookCommentScraper from './pages/FacebookCommentScraper';
import BrightdataSettings from './pages/BrightdataSettings';
import AutomatedBatchScraper from './pages/AutomatedBatchScraper';

// Theme and auth imports
import theme from './theme/index';
import { AuthProvider } from './components/auth/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminRoute from './components/auth/AdminRoute';

// Additional pages
import FolderSelectionReportGenerator from './FolderSelectionReportGenerator';
import InstagramFolderSelector from './FolderSelectionReportGenerator';

// Auth utility
import { isAuthenticated } from './utils/auth';

// Redirect component for dynamic route redirects
const TrackAccountsRedirect = () => {
  const { organizationId, projectId } = useParams();
  return <Navigate to={`/organizations/${organizationId}/projects/${projectId}/source-tracking`} replace />;
};

const TrackAccountsAccountsRedirect = () => {
  const { organizationId, projectId } = useParams();
  return <Navigate to={`/organizations/${organizationId}/projects/${projectId}/source-tracking/sources`} replace />;
};

const TrackSourcesRedirect = () => {
  const { organizationId, projectId } = useParams();
  return <Navigate to={`/organizations/${organizationId}/projects/${projectId}/source-tracking`} replace />;
};

const TrackSourcesCreateRedirect = () => {
  const { organizationId, projectId } = useParams();
  return <Navigate to={`/organizations/${organizationId}/projects/${projectId}/source-tracking/create`} replace />;
};

const TrackSourcesUploadRedirect = () => {
  const { organizationId, projectId } = useParams();
  return <Navigate to={`/organizations/${organizationId}/projects/${projectId}/source-tracking/upload`} replace />;
};

const TrackSourcesEditRedirect = () => {
  const { organizationId, projectId, accountId } = useParams();
  return <Navigate to={`/organizations/${organizationId}/projects/${projectId}/source-tracking/edit/${accountId}`} replace />;
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
              
              {/* New project view route within organization context */}
              <Route path="/organizations/:organizationId/projects/:projectId" element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard3 />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Projects routes - no sidebar, now redirects to organization projects */}
              <Route path="/projects" element={
                <ProtectedRoute>
                  <Navigate to="/organizations" replace />
                </ProtectedRoute>
              } />
              
              {/* Project Dashboard and all other routes - with sidebar */}
              <Route path="/dashboard/:projectId" element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard3 />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Main dashboard for backward compatibility */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard3 />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Instagram routes */}
              <Route path="/instagram-data" element={
                <ProtectedRoute>
                  <Navigate to="/instagram-folders" replace />
                </ProtectedRoute>
              } />
              <Route path="/instagram-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <InstagramFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/instagram-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <InstagramDataUpload />
                  </Layout>
                </ProtectedRoute>
              } />

              
              <Route path="/facebook-data" element={
                <ProtectedRoute>
                  <Navigate to="/facebook-folders" replace />
                </ProtectedRoute>
              } />
              <Route path="/facebook-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <FacebookFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/facebook-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <FacebookDataUpload />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Comments Scraper - Cross-platform */}
              <Route path="/comments-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <CommentsScraper />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Comments Scraper with organization and project IDs */}
              <Route path="/organizations/:organizationId/projects/:projectId/comments-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <CommentsScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Facebook Comment Scraper */}
              <Route path="/facebook-comment-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <FacebookCommentScraper />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Facebook Comment Scraper with organization and project IDs */}
              <Route path="/organizations/:organizationId/projects/:projectId/facebook-comment-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <FacebookCommentScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* LinkedIn routes */}
              <Route path="/linkedin-data" element={
                <ProtectedRoute>
                  <Navigate to="/linkedin-folders" replace />
                </ProtectedRoute>
              } />
              <Route path="/linkedin-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <LinkedInFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/linkedin-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <LinkedInDataUpload />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* TikTok routes */}
              <Route path="/tiktok-data" element={
                <ProtectedRoute>
                  <Navigate to="/tiktok-folders" replace />
                </ProtectedRoute>
              } />
              <Route path="/tiktok-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <TikTokFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/tiktok-data/:folderId" element={
                <ProtectedRoute>
                  <Layout>
                    <TikTokDataUpload />
                  </Layout>
                </ProtectedRoute>
              } />

              
              <Route path="/track-accounts" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountsList />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/track-accounts/accounts" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountsList />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/track-accounts/upload" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountUpload />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/track-accounts/create" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountCreate />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/track-accounts/edit/:accountId" element={
                <ProtectedRoute>
                  <Layout>
                    <TrackAccountEdit />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* New routes with organization and project IDs */}
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
              
              {/* Legacy track-accounts routes for backward compatibility */}
              <Route path="/organizations/:organizationId/projects/:projectId/track-accounts" element={<TrackAccountsRedirect />} />
              <Route path="/organizations/:organizationId/projects/:projectId/track-accounts/accounts" element={<TrackAccountsAccountsRedirect />} />
              
              {/* Legacy track-sources routes for backward compatibility */}
              <Route path="/organizations/:organizationId/projects/:projectId/track-sources" element={<TrackSourcesRedirect />} />
              <Route path="/organizations/:organizationId/projects/:projectId/track-sources/create" element={<TrackSourcesCreateRedirect />} />
              <Route path="/organizations/:organizationId/projects/:projectId/track-sources/upload" element={<TrackSourcesUploadRedirect />} />
              <Route path="/organizations/:organizationId/projects/:projectId/track-sources/edit/:accountId" element={<TrackSourcesEditRedirect />} />
              
              <Route path="/social-analysis" element={
                <ProtectedRoute>
                  <Navigate to="/analysis" replace />
                </ProtectedRoute>
              } />
              <Route path="/web-presence" element={
                <ProtectedRoute>
                  <Navigate to="/analysis" replace />
                </ProtectedRoute>
              } />
              <Route path="/sentiment" element={
                <ProtectedRoute>
                  <Navigate to="/analysis" replace />
                </ProtectedRoute>
              } />
              <Route path="/wordcloud" element={
                <ProtectedRoute>
                  <Navigate to="/analysis" replace />
                </ProtectedRoute>
              } />
              <Route path="/nps-reports" element={
                <ProtectedRoute>
                  <Navigate to="/analysis" replace />
                </ProtectedRoute>
              } />
              
              {/* New unified Analysis route */}
              <Route path="/analysis" element={
                <ProtectedRoute>
                  <Layout>
                    <Analysis />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Analysis route with organization and project IDs */}
              <Route path="/organizations/:organizationId/projects/:projectId/analysis" element={
                <ProtectedRoute>
                  <Layout>
                    <Analysis />
                  </Layout>
                </ProtectedRoute>
              } />
              
              <Route path="/settings" element={
                <ProtectedRoute>
                  <Layout>
                    <Settings />
                  </Layout>
                </ProtectedRoute>
              } />
              {/* Report Folder Routes */}
              <Route path="/reports" element={
                <ProtectedRoute>
                  <Navigate to="/report-folders" replace />
                </ProtectedRoute>
              } />
              
              <Route path="/report-folders" element={
                <ProtectedRoute>
                  <Layout>
                    <ReportFolders />
                  </Layout>
                </ProtectedRoute>
              } />
              
              <Route path="/report-folders/:reportId" element={
                <ProtectedRoute>
                  <Layout>
                    <ReportDetail />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/report-folders/:reportId/instagram-data" element={
                <ProtectedRoute>
                  <Layout>
                    <InstagramFolderSelector />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/instagram-folder-selector/:reportId" element={
                <ProtectedRoute>
                  <Layout>
                    <InstagramFolderSelector />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Multi-Platform Report Generation Routes */}
              <Route path="/report-folders/create/multi-platform" element={
                <ProtectedRoute>
                  <Layout>
                    <MultiPlatformReportGeneration />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/report-folders/:reportId/edit-multi-platform" element={
                <ProtectedRoute>
                  <Layout>
                    <MultiPlatformReportGeneration />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/brightdata-settings" element={
                <ProtectedRoute>
                  <Layout>
                    <BrightdataSettings />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/brightdata-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <AutomatedBatchScraper />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/automated-batch-scraper" element={
                <ProtectedRoute>
                  <Layout>
                    <AutomatedBatchScraper />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* Social Media Data with organization and project IDs */}
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
              
              {/* Report Folder Routes with organization and project IDs */}
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
              
              {/* Multi-Platform Report Generation Routes with organization and project IDs */}
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
              
              {/* Brightdata routes with organization and project IDs */}
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
            </Routes>
          </Router>
        </ThemeProvider>
      </LocalizationProvider>
    </AuthProvider>
  )
}

export default App 
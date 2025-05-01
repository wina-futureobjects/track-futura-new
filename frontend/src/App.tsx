import { useState } from 'react'
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import InstagramDataUpload from './pages/InstagramDataUpload';
import InstagramFolders from './pages/InstagramFolders';
import FacebookDataUpload from './pages/FacebookDataUpload';
import FacebookFolders from './pages/FacebookFolders';
import LinkedInDataUpload from './pages/LinkedInDataUpload';
import LinkedInFolders from './pages/LinkedInFolders';
import TikTokDataUpload from './pages/TikTokDataUpload';
import TikTokFolders from './pages/TikTokFolders';
import TrackAccountFolders from './pages/TrackAccountFolders';
import TrackAccountFolderDetail from './pages/TrackAccountFolderDetail';
import TrackAccountUpload from './pages/TrackAccountUpload';
import ReportFolders from './pages/ReportFolders';
import ReportDetail from './pages/ReportDetail';
import FolderReportGeneration from './pages/FolderReportGeneration';
import MultiPlatformReportGeneration from './pages/MultiPlatformReportGeneration';
import theme from './theme';
import CssBaseline from '@mui/material/CssBaseline';
import InstagramFolderSelector from './FolderSelectionReportGenerator';

// Local auth implementation to avoid import issues
const isAuthenticated = () => {
  // For development, always return true
  return true;
  // In production, uncomment:
  // return !!localStorage.getItem('authToken');
};

// Route guard component for protected routes
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const auth = isAuthenticated();
  return auth ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
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

          {/* Facebook routes */}
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

          {/* Track Account routes */}
          <Route path="/track-accounts" element={
            <ProtectedRoute>
              <Navigate to="/track-accounts/folders" replace />
            </ProtectedRoute>
          } />
          <Route path="/track-accounts/folders" element={
            <ProtectedRoute>
              <Layout>
                <TrackAccountFolders />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/track-accounts/folders/:folderId" element={
            <ProtectedRoute>
              <Layout>
                <TrackAccountFolderDetail />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/track-accounts/folders/:folderId/upload" element={
            <ProtectedRoute>
              <Layout>
                <TrackAccountUpload />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/social-analysis" element={
            <ProtectedRoute>
              <Layout>
                <div>Social Analysis Page (Coming Soon)</div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/web-presence" element={
            <ProtectedRoute>
              <Layout>
                <div>Web Presence Page (Coming Soon)</div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/sentiment" element={
            <ProtectedRoute>
              <Layout>
                <div>Sentiment Analysis Page (Coming Soon)</div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/wordcloud" element={
            <ProtectedRoute>
              <Layout>
                <div>Word Cloud Page (Coming Soon)</div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/nps-reports" element={
            <ProtectedRoute>
              <Layout>
                <div>NPS Reports Page (Coming Soon)</div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Layout>
                <div>Settings Page (Coming Soon)</div>
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/reports" element={
            <ProtectedRoute>
              <Navigate to="/report-folders" replace />
            </ProtectedRoute>
          } />
          
          {/* Report Folder Routes */}
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
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App

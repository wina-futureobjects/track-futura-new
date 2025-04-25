import { useState } from 'react'
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import InstagramDataUpload from './pages/InstagramDataUpload';
import InstagramFolders from './pages/InstagramFolders';
import TrackAccountFolders from './pages/TrackAccountFolders';
import TrackAccountFolderDetail from './pages/TrackAccountFolderDetail';
import TrackAccountUpload from './pages/TrackAccountUpload';
import ReportFolders from './pages/ReportFolders';
import ReportDetail from './pages/ReportDetail';
import FolderReportGeneration from './pages/FolderReportGeneration';
import theme from './theme';
import CssBaseline from '@mui/material/CssBaseline';
import { isAuthenticated } from './lib/auth';
import InstagramFolderSelector from './FolderSelectionReportGenerator';

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
          
          <Route path="*" element={<div>404 - Page Not Found</div>} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App

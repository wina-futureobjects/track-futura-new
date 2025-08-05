import { CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Declare API_BASE_URL on Window interface to fix TypeScript error
declare global {
  interface Window {
    API_BASE_URL: string;
  }
}

// Set the API base URL based on environment
window.API_BASE_URL = import.meta.env.PROD
  ? `https://${window.location.hostname}` // Use same domain in production
  : 'http://127.0.0.1:8000'; // Use direct backend URL in development

const theme = createTheme({
  palette: {
    primary: {
      main: '#1a237e',
    },
    secondary: {
      main: '#f50057',
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { ThemeProvider, createTheme } from '@mui/material'
import { CssBaseline } from '@mui/material'

// Declare API_BASE_URL on Window interface to fix TypeScript error
declare global {
  interface Window {
    API_BASE_URL: string;
  }
}

// Set the API base URL based on environment
window.API_BASE_URL = import.meta.env.PROD 
  ? `https://api.${window.location.hostname}` // Use api subdomain in production (Upsun/Platform.sh)
  : '';

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

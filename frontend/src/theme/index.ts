import { createTheme, responsiveFontSizes } from '@mui/material/styles';

// Create a theme instance with the company red color scheme
const baseTheme = createTheme({
  // Add spacing scale reduction for more compact UI
  spacing: 7, // Reduced from default 8 to 7 for more compact spacing
  palette: {
    primary: {
      main: '#E1251B', // Company red
      light: '#E85A52', 
      dark: '#B31D15',
      contrastText: '#fff',
    },
    secondary: {
      main: '#2C3E50', // Dark blue-gray for contrast
      light: '#34495E',
      dark: '#1B2631',
      contrastText: '#fff',
    },
    background: {
      default: '#FAFAFA', // Very light gray
      paper: '#FFFFFF',
    },
    error: {
      main: '#E74C3C',
    },
    warning: {
      main: '#F39C12',
    },
    info: {
      main: '#E1251B', // Use company red for info as well
      light: '#E85A52',
      dark: '#B31D15',
    },
    success: {
      main: '#27AE60',
    },
    text: {
      primary: '#2C3E50', // Dark blue-gray for primary text
      secondary: '#7F8C8D', // Gray for secondary text
    },
    // Custom grays that complement the red theme
    grey: {
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#EEEEEE', 
      300: '#E0E0E0',
      400: '#BDBDBD',
      500: '#9E9E9E',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    // Reduce font sizes slightly for more compact UI while maintaining readability
    h1: {
      fontWeight: 700,
      fontSize: '2.2rem', // Reduced from 2.5rem
      color: '#2C3E50',
    },
    h2: {
      fontWeight: 600,
      fontSize: '1.8rem', // Reduced from 2rem
      color: '#2C3E50',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem', // Reduced from 1.75rem
      color: '#2C3E50',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.3rem', // Reduced from 1.5rem
      color: '#2C3E50',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.1rem', // Reduced from 1.25rem
      color: '#2C3E50',
    },
    h6: {
      fontWeight: 500,
      fontSize: '0.95rem', // Reduced from 1rem
      color: '#2C3E50',
    },
    subtitle1: {
      fontSize: '0.95rem', // Reduced from 1rem
      fontWeight: 400,
      color: '#2C3E50',
    },
    subtitle2: {
      fontSize: '0.825rem', // Reduced from 0.875rem
      fontWeight: 500,
      color: '#7F8C8D',
    },
    body1: {
      fontSize: '0.9rem', // Reduced from 1rem
      color: '#2C3E50',
    },
    body2: {
      fontSize: '0.8rem', // Reduced from 0.875rem
      color: '#7F8C8D',
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
      fontSize: '0.85rem', // Make buttons slightly smaller
    },
  },
  shape: {
    borderRadius: 6, // Reduced from 8 for more compact look
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
          boxShadow: 'none',
          minHeight: '36px',
          border: '1px solid transparent',
          '&:hover': {
            boxShadow: 'none',
            borderColor: '#e8eaed',
          },
        },
        containedPrimary: {
          backgroundColor: '#E1251B',
          border: '1px solid #E1251B',
          '&:hover': {
            backgroundColor: '#B31D15',
            borderColor: '#B31D15',
            boxShadow: 'none',
          },
        },
        containedSecondary: {
          backgroundColor: '#2C3E50',
          border: '1px solid #2C3E50',
          '&:hover': {
            backgroundColor: '#1B2631',
            borderColor: '#1B2631',
            boxShadow: 'none',
          },
        },
        outlined: {
          borderColor: '#e8eaed',
          '&:hover': {
            borderColor: '#E1251B',
            backgroundColor: 'rgba(225, 37, 27, 0.04)',
            boxShadow: 'none',
          },
        },
        sizeSmall: {
          padding: '6px 12px',
          fontSize: '0.8rem',
        },
        sizeLarge: {
          padding: '10px 20px',
          fontSize: '0.95rem',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          borderRadius: 12,
          border: '1px solid #e8eaed',
          '&:hover': {
            borderColor: '#d0d0d0',
          },
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: '16px',
          '&:last-child': {
            paddingBottom: '16px',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          border: '1px solid #e8eaed',
          borderRadius: 12,
        },
        elevation1: {
          boxShadow: 'none',
          border: '1px solid #e8eaed',
        },
        elevation2: {
          boxShadow: 'none',
          border: '1px solid #d0d0d0',
        },
        elevation3: {
          boxShadow: 'none',
          border: '1px solid #c0c0c0',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          color: '#2c3e50',
          boxShadow: 'none',
          borderBottom: '1px solid #e8eaed',
          minHeight: '60px',
        },
      },
    },
    MuiToolbar: {
      styleOverrides: {
        root: {
          minHeight: '60px !important',
          padding: '0 24px !important',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          height: '28px', // Reduced from default 32px
          fontSize: '0.8rem',
          '&.MuiChip-colorPrimary': {
            backgroundColor: '#E1251B',
            color: '#FFFFFF',
          },
        },
        sizeSmall: {
          height: '24px',
          fontSize: '0.75rem',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          padding: '6px 14px', // Reduced from default padding
          minHeight: '40px', // Reduced from default
          '&:hover': {
            backgroundColor: 'rgba(225, 37, 27, 0.04)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(225, 37, 27, 0.08)',
            '&:hover': {
              backgroundColor: 'rgba(225, 37, 27, 0.12)',
            },
          },
        },
      },
    },
    MuiListItemText: {
      styleOverrides: {
        root: {
          margin: '4px 0', // Reduced from default
        },
        primary: {
          fontSize: '0.9rem', // Reduced font size
        },
        secondary: {
          fontSize: '0.8rem', // Reduced font size
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: '8px 12px', // Reduced from default 16px
          fontSize: '0.85rem',
        },
        head: {
          fontSize: '0.8rem',
          fontWeight: 600,
        },
      },
    },
    MuiFormControl: {
      styleOverrides: {
        root: {
          marginBottom: '12px', // Reduced from default spacing
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiInputBase-root': {
            fontSize: '0.9rem',
          },
          '& .MuiInputLabel-root': {
            fontSize: '0.9rem',
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 8, // Reduced from default
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          padding: '16px 20px', // Reduced padding
          fontSize: '1.2rem', // Reduced font size
        },
      },
    },
    MuiDialogContent: {
      styleOverrides: {
        root: {
          padding: '12px 20px', // Reduced padding
        },
      },
    },
    MuiDialogActions: {
      styleOverrides: {
        root: {
          padding: '12px 20px 16px', // Reduced padding
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          boxShadow: 'none',
          border: '1px solid #e8eaed',
          borderRadius: 12,
          minWidth: '200px',
        },
      },
    },
    MuiPopover: {
      styleOverrides: {
        paper: {
          boxShadow: 'none',
          border: '1px solid #e8eaed',
          borderRadius: 12,
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          fontSize: '14px',
          padding: '8px 16px',
          borderRadius: '8px',
          margin: '0 8px',
          '&:hover': {
            backgroundColor: '#f8f9fa',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(225, 37, 27, 0.08)',
            '&:hover': {
              backgroundColor: 'rgba(225, 37, 27, 0.12)',
            },
          },
        },
      },
    },
  },
});

// Create responsive theme
const theme = responsiveFontSizes(baseTheme);

export default theme; 
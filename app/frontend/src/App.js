import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Dashboard Components
import ClientDashboard from './components/dashboards/ClientDashboard';
import PMDashboard from './components/dashboards/PMDashboard';
import ForecastDashboard from './components/dashboards/ForecastDashboard';

// Setup Components
import SetupPage from './components/setup/SetupPage';

// Layout Components
import Navbar from './components/layout/Navbar';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              mt: '64px',
              width: '100%',
              maxWidth: '100%',
              overflowX: 'hidden'
            }}
          >
            <Routes>
              <Route path="/" element={<ClientDashboard />} />
              <Route path="/pm" element={<PMDashboard />} />
              <Route path="/forecast" element={<ForecastDashboard />} />
              <Route path="/setup" element={<SetupPage />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App; 
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  CircularProgress, 
  Alert,
  LinearProgress,
  Chip
} from '@mui/material';

function ClientDashboard() {
  const [summary, setSummary] = useState(null);
  const [settings, setSettings] = useState({ client_name: 'Client', currency: 'USD' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([fetchSummary(), fetchSettings()]);
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      }
    } catch (err) {
      console.error('Error fetching settings:', err);
    }
  };

  const getCurrencySymbol = (currency) => {
    const symbols = {
      'USD': '$',
      'EUR': '€',
      'GBP': '£',
      'JPY': '¥',
      'AUD': 'A$',
      'CAD': 'C$',
      'CHF': 'CHF',
      'CNY': '¥',
      'INR': '₹'
    };
    return symbols[currency] || currency;
  };

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/dashboard/client/summary');
      
      if (!response.ok) {
        throw new Error('Failed to fetch summary data');
      }

      const data = await response.json();
      setSummary(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching summary:', err);
      setError('Failed to load project summary');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Project Summary
      </Typography>
      
      <Grid container spacing={3}>
        {/* Project Status and Budget Overview */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Project Status</Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" color="text.secondary">Status</Typography>
              <Chip 
                label={summary?.status || 'Not Set'} 
                color={summary?.status === 'In Progress' ? 'primary' : 'default'}
                sx={{ mt: 1 }}
              />
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" color="text.secondary">Budget Overview</Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body1">
                  Total Budget: {getCurrencySymbol(settings.currency)}
                  {summary?.budget?.total?.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </Typography>
                <Typography variant="body1">
                  Spent: {getCurrencySymbol(settings.currency)}
                  {summary?.budget?.spent?.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </Typography>
                <Typography variant="body1">
                  Remaining: {getCurrencySymbol(settings.currency)}
                  {summary?.budget?.remaining?.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" color="text.secondary">Budget Utilization</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={summary?.budget?.percentage || 0} 
                    sx={{ mt: 1, height: 10, borderRadius: 5 }}
                  />
                </Box>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Project Health */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Project Health</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" color="text.secondary">Budget</Typography>
                  <Chip 
                    label={summary?.health?.budget || 'Not Set'} 
                    color={summary?.health?.budget === 'On Track' ? 'success' : 'error'}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" color="text.secondary">Timeline</Typography>
                  <Chip 
                    label={summary?.health?.timeline || 'Not Set'} 
                    color={summary?.health?.timeline === 'On Track' ? 'success' : 'error'}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" color="text.secondary">Resources</Typography>
                  <Chip 
                    label={summary?.health?.resources || 'Not Set'} 
                    color={summary?.health?.resources === 'On Track' ? 'success' : 'error'}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" color="text.secondary">Scope</Typography>
                  <Chip 
                    label={summary?.health?.scope || 'Not Set'} 
                    color={summary?.health?.scope === 'Stable' ? 'success' : 'error'}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Workstream Progress */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Workstream Progress</Typography>
            <TableContainer>
              <Table size="medium">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Workstream</TableCell>
                    <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Status</TableCell>
                    <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Progress</TableCell>
                    <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Budget Utilization</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {summary?.workstreams?.map((workstream) => (
                    <TableRow key={workstream.id} hover>
                      <TableCell sx={{ fontSize: '1rem' }}>{workstream.name}</TableCell>
                      <TableCell sx={{ fontSize: '1rem' }}>
                        <Chip 
                          label={workstream.status} 
                          color={workstream.status === 'active' ? 'primary' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ fontSize: '1rem', width: '30%' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Box sx={{ width: '100%', mr: 1 }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={workstream.progress} 
                              sx={{ height: 10, borderRadius: 5 }}
                            />
                          </Box>
                          <Box sx={{ minWidth: 35 }}>
                            <Typography variant="body2" color="text.secondary">
                              {Math.round(workstream.progress)}%
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell sx={{ fontSize: '1rem', width: '40%' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            {getCurrencySymbol(settings.currency)}{workstream.spent?.toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            }) || '0.00'}
                          </Typography>
                          <Box sx={{ flexGrow: 1, position: 'relative' }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={(workstream.spent || 0) / workstream.budget * 100} 
                              sx={{ 
                                height: 10, 
                                borderRadius: 5,
                                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: (workstream.spent || 0) / workstream.budget > 0.9 ? '#f44336' : '#4caf50'
                                }
                              }}
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {getCurrencySymbol(settings.currency)}{workstream.budget?.toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            }) || '0.00'}
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ClientDashboard; 
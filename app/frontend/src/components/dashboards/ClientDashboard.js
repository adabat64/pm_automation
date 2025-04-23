import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, Alert } from '@mui/material';

function ClientDashboard() {
  const [workstreamBudgets, setWorkstreamBudgets] = useState([]);
  const [settings, setSettings] = useState({ client_name: 'Client', currency: 'USD' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([fetchWorkstreamBudgets(), fetchSettings()]);
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

  const fetchWorkstreamBudgets = async () => {
    try {
      setLoading(true);
      const [profilesRes, workstreamsRes] = await Promise.all([
        fetch('/api/profiles'),
        fetch('/api/workstreams')
      ]);

      if (!profilesRes.ok || !workstreamsRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [profiles, workstreams] = await Promise.all([
        profilesRes.json(),
        workstreamsRes.json()
      ]);

      console.log('Fetched profiles:', profiles);
      console.log('Fetched workstreams:', workstreams);

      // Calculate budgets for each workstream
      const budgets = workstreams.map(workstream => {
        const workstreamAllocations = profiles.flatMap(profile => 
          profile.workstreams
            .filter(ws => ws.workstream_id === workstream.id)
            .map(ws => ({
              ...ws,
              daily_rate: profile.daily_rate
            }))
        );

        console.log(`Calculating budget for workstream ${workstream.name}:`, workstreamAllocations);

        const totalBudget = workstreamAllocations.reduce((sum, allocation) => {
          const budget = allocation.days_allocated * allocation.daily_rate;
          console.log(`  Allocation: ${allocation.days_allocated} days * ${allocation.daily_rate} rate = ${budget}`);
          return sum + budget;
        }, 0);

        console.log(`Total budget for ${workstream.name}: ${totalBudget}`);

        return {
          id: workstream.id,
          name: workstream.name,
          totalBudget,
          status: workstream.status
        };
      });

      console.log('Calculated budgets:', budgets);
      setWorkstreamBudgets(budgets);
      setError(null);
    } catch (err) {
      console.error('Error fetching workstream budgets:', err);
      setError('Failed to load workstream budgets');
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
        {settings.client_name} Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, width: '100%' }}>
            <Typography variant="h6" gutterBottom>Workstream Budgets</Typography>
            <TableContainer>
              <Table size="medium">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Workstream</TableCell>
                    <TableCell align="right" sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Total Budget</TableCell>
                    <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {workstreamBudgets.map((workstream) => (
                    <TableRow key={workstream.id} hover>
                      <TableCell sx={{ fontSize: '1rem' }}>{workstream.name}</TableCell>
                      <TableCell align="right" sx={{ fontSize: '1rem' }}>
                        {getCurrencySymbol(settings.currency)}{workstream.totalBudget.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2
                        })}
                      </TableCell>
                      <TableCell sx={{ fontSize: '1rem' }}>{workstream.status}</TableCell>
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
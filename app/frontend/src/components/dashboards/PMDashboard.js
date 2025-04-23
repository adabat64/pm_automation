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
  Tabs,
  Tab
} from '@mui/material';

function PMDashboard() {
  const [workstreams, setWorkstreams] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [settings, setSettings] = useState({ client_name: '', currency: 'USD' });
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

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

  const fetchData = async () => {
    try {
      setLoading(true);
      const [profilesRes, workstreamsRes, settingsRes] = await Promise.all([
        fetch('/api/profiles'),
        fetch('/api/workstreams'),
        fetch('/api/settings')
      ]);

      if (!profilesRes.ok || !workstreamsRes.ok || !settingsRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [profilesData, workstreamsData, settingsData] = await Promise.all([
        profilesRes.json(),
        workstreamsRes.json(),
        settingsRes.json()
      ]);

      setProfiles(profilesData);
      setWorkstreams(workstreamsData);
      setSettings(settingsData);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
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
        {settings.client_name || 'Project'} Dashboard
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Team Overview" />
        <Tab label="Workstream Status" />
      </Tabs>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, width: '100%' }}>
              <Typography variant="h6" gutterBottom>Team Members</Typography>
              <TableContainer>
                <Table size="medium">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Name</TableCell>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Daily Rate</TableCell>
                      {workstreams.map(workstream => (
                        <TableCell 
                          key={workstream.id} 
                          align="right" 
                          sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}
                        >
                          {workstream.name} (days)
                        </TableCell>
                      ))}
                      <TableCell align="right" sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Total Days</TableCell>
                      <TableCell align="right" sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Total Price</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {profiles.map((profile) => {
                      const totalDays = profile.workstreams.reduce((sum, ws) => sum + ws.days_allocated, 0);
                      const totalPrice = totalDays * profile.daily_rate;

                      return (
                        <TableRow key={profile.id} hover>
                          <TableCell sx={{ fontSize: '1rem' }}>{profile.name}</TableCell>
                          <TableCell sx={{ fontSize: '1rem' }}>
                            {getCurrencySymbol(settings.currency)}{profile.daily_rate.toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            })}
                          </TableCell>
                          {workstreams.map(workstream => {
                            const allocation = profile.workstreams.find(
                              ws => ws.workstream_id === workstream.id
                            );
                            return (
                              <TableCell 
                                key={workstream.id} 
                                align="right" 
                                sx={{ fontSize: '1rem' }}
                              >
                                {allocation ? allocation.days_allocated : '-'}
                              </TableCell>
                            );
                          })}
                          <TableCell align="right" sx={{ fontSize: '1rem' }}>{totalDays}</TableCell>
                          <TableCell align="right" sx={{ fontSize: '1rem' }}>
                            {getCurrencySymbol(settings.currency)}{totalPrice.toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            })}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                    <TableRow>
                      <TableCell colSpan={2} sx={{ fontSize: '1rem', fontWeight: 'bold' }}>Totals</TableCell>
                      {workstreams.map(workstream => {
                        const totalDays = profiles.reduce((sum, profile) => {
                          const allocation = profile.workstreams.find(
                            ws => ws.workstream_id === workstream.id
                          );
                          return sum + (allocation ? allocation.days_allocated : 0);
                        }, 0);
                        return (
                          <TableCell 
                            key={workstream.id} 
                            align="right" 
                            sx={{ fontSize: '1rem', fontWeight: 'bold' }}
                          >
                            {totalDays}
                          </TableCell>
                        );
                      })}
                      <TableCell align="right" sx={{ fontSize: '1rem', fontWeight: 'bold' }}>
                        {profiles.reduce((sum, profile) => 
                          sum + profile.workstreams.reduce((days, ws) => days + ws.days_allocated, 0)
                        , 0)}
                      </TableCell>
                      <TableCell align="right" sx={{ fontSize: '1rem', fontWeight: 'bold' }}>
                        {getCurrencySymbol(settings.currency)}
                        {profiles.reduce((sum, profile) => 
                          sum + (profile.workstreams.reduce((days, ws) => days + ws.days_allocated, 0) * profile.daily_rate)
                        , 0).toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2
                        })}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, width: '100%' }}>
              <Typography variant="h6" gutterBottom>Workstream Overview</Typography>
              <TableContainer>
                <Table size="medium">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Workstream</TableCell>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Status</TableCell>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Assigned Team Members</TableCell>
                      <TableCell align="right" sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Total Days</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {workstreams.map((workstream) => {
                      const assignedProfiles = profiles.filter(profile => 
                        profile.workstreams.some(ws => ws.workstream_id === workstream.id)
                      );
                      const totalDays = assignedProfiles.reduce((sum, profile) => {
                        const allocation = profile.workstreams.find(ws => ws.workstream_id === workstream.id);
                        return sum + (allocation ? allocation.days_allocated : 0);
                      }, 0);
                      const profileNames = assignedProfiles.map(p => p.name).join(', ');

                      return (
                        <TableRow key={workstream.id} hover>
                          <TableCell sx={{ fontSize: '1rem' }}>{workstream.name}</TableCell>
                          <TableCell sx={{ fontSize: '1rem' }}>{workstream.status}</TableCell>
                          <TableCell sx={{ fontSize: '1rem' }}>{profileNames}</TableCell>
                          <TableCell align="right" sx={{ fontSize: '1rem' }}>{totalDays}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default PMDashboard; 
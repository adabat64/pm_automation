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

function ProjectDashboard() {
  const [workstreamBudgets, setWorkstreamBudgets] = useState([]);
  const [profileBudgets, setProfileBudgets] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
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

      // Calculate workstream budgets
      const workstreamBudgets = workstreams.map(workstream => {
        const workstreamAllocations = profiles.flatMap(profile => 
          profile.workstreams
            .filter(ws => ws.workstream_id === workstream.id)
            .map(ws => ({
              ...ws,
              daily_rate: profile.daily_rate
            }))
        );

        const totalBudget = workstreamAllocations.reduce((sum, allocation) => 
          sum + (allocation.days_allocated * allocation.daily_rate)
        , 0);

        return {
          id: workstream.id,
          name: workstream.name,
          totalBudget,
          status: workstream.status
        };
      });

      // Calculate profile budgets
      const profileBudgets = profiles.map(profile => {
        const workstreamAllocations = profile.workstreams.map(allocation => {
          const workstream = workstreams.find(ws => ws.id === allocation.workstream_id);
          return {
            workstreamName: workstream.name,
            daysAllocated: allocation.days_allocated,
            budget: allocation.days_allocated * profile.daily_rate
          };
        });

        const totalBudget = workstreamAllocations.reduce((sum, allocation) => 
          sum + allocation.budget, 0
        );

        return {
          id: profile.id,
          name: profile.name,
          dailyRate: profile.daily_rate,
          workstreamAllocations,
          totalBudget
        };
      });

      setWorkstreamBudgets(workstreamBudgets);
      setProfileBudgets(profileBudgets);
      setError(null);
    } catch (err) {
      console.error('Error fetching budgets:', err);
      setError('Failed to load budget data');
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
        Project Dashboard
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Workstream Budgets" />
        <Tab label="Profile Budgets" />
      </Tabs>

      {activeTab === 0 && (
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
                          ${workstream.totalBudget.toLocaleString(undefined, {
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
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, width: '100%' }}>
              <Typography variant="h6" gutterBottom>Profile Budgets</Typography>
              <TableContainer>
                <Table size="medium">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Profile</TableCell>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Daily Rate</TableCell>
                      <TableCell sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Workstream</TableCell>
                      <TableCell align="right" sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Days Allocated</TableCell>
                      <TableCell align="right" sx={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Budget</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {profileBudgets.map((profile) => (
                      profile.workstreamAllocations.map((allocation, index) => (
                        <TableRow key={`${profile.id}-${index}`} hover>
                          {index === 0 && (
                            <TableCell rowSpan={profile.workstreamAllocations.length} sx={{ fontSize: '1rem' }}>
                              {profile.name}
                            </TableCell>
                          )}
                          {index === 0 && (
                            <TableCell rowSpan={profile.workstreamAllocations.length} sx={{ fontSize: '1rem' }}>
                              ${profile.dailyRate.toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                              })}
                            </TableCell>
                          )}
                          <TableCell sx={{ fontSize: '1rem' }}>{allocation.workstreamName}</TableCell>
                          <TableCell align="right" sx={{ fontSize: '1rem' }}>{allocation.daysAllocated}</TableCell>
                          <TableCell align="right" sx={{ fontSize: '1rem' }}>
                            ${allocation.budget.toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            })}
                          </TableCell>
                        </TableRow>
                      ))
                    ))}
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

export default ProjectDashboard; 
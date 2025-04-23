import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';

function ClientDashboard() {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Client Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Project Overview</Typography>
            <Typography>Project status and key metrics will be displayed here.</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Budget Status</Typography>
            <Typography>Budget information and tracking will be shown here.</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ClientDashboard; 
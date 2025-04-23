import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';

function PMDashboard() {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Project Manager Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Team Overview</Typography>
            <Typography>Team member status and assignments will be displayed here.</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Workstream Status</Typography>
            <Typography>Workstream progress and status will be shown here.</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default PMDashboard; 
import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';

function ForecastDashboard() {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Forecast Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Resource Forecast</Typography>
            <Typography>Resource allocation and forecasting will be displayed here.</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Timeline Forecast</Typography>
            <Typography>Project timeline and milestone forecasts will be shown here.</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ForecastDashboard; 
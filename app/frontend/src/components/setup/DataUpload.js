import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Grid, 
  TextField, 
  CircularProgress,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  MenuItem
} from '@mui/material';
import { Upload as UploadIcon, ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import axios from 'axios';

function DataUpload({ onUploadComplete }) {
  const [timesheetFile, setTimesheetFile] = useState(null);
  const [projectDataFile, setProjectDataFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', severity: 'info' });
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [clientName, setClientName] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [error, setError] = useState('');

  const currencies = [
    { value: 'USD', label: 'US Dollar ($)' },
    { value: 'EUR', label: 'Euro (€)' },
    { value: 'GBP', label: 'British Pound (£)' },
    { value: 'JPY', label: 'Japanese Yen (¥)' },
    { value: 'AUD', label: 'Australian Dollar (A$)' },
    { value: 'CAD', label: 'Canadian Dollar (C$)' },
    { value: 'CHF', label: 'Swiss Franc (CHF)' },
    { value: 'CNY', label: 'Chinese Yuan (¥)' },
    { value: 'INR', label: 'Indian Rupee (₹)' }
  ];

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      if (response.ok) {
        const settings = await response.json();
        setClientName(settings.client_name);
        setCurrency(settings.currency);
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const saveSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/settings?client_name=${encodeURIComponent(clientName)}&currency=${currency}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to save settings');
      }
      
      setMessage('Settings saved successfully');
      setError('');
    } catch (err) {
      setError('Failed to save settings');
      setMessage('');
    } finally {
      setLoading(false);
    }
  };

  const handleTimesheetChange = (event) => {
    setTimesheetFile(event.target.files[0]);
  };

  const handleProjectDataChange = (event) => {
    setProjectDataFile(event.target.files[0]);
  };

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  const showMessage = (text, severity = 'info') => {
    setMessage({ text, severity });
    setOpenSnackbar(true);
  };

  const uploadFiles = async () => {
    if (!timesheetFile && !projectDataFile) {
      showMessage('Please select at least one file to upload', 'error');
      return;
    }

    setLoading(true);
    
    try {
      const formData = new FormData();
      
      if (timesheetFile) {
        formData.append('timesheet', timesheetFile);
      }
      
      if (projectDataFile) {
        formData.append('project_data', projectDataFile);
      }
      
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (response.data.message) {
        // Process the data after successful upload
        await fetch('/api/process', { method: 'POST' });
        showMessage('Files uploaded and processed successfully', 'success');
      }
      
      setTimesheetFile(null);
      setProjectDataFile(null);
      
      // Reset file inputs
      document.getElementById('timesheet-upload').value = '';
      document.getElementById('project-data-upload').value = '';
      
      // Call the callback to notify parent component
      if (onUploadComplete) {
        onUploadComplete();
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      showMessage(error.response?.data?.detail || 'Error uploading files', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Data Setup
      </Typography>
      <Typography variant="body1" paragraph>
        Upload your project data and timesheet files to get started with the dashboard.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Project Settings
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Client Name"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              margin="normal"
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Currency"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              margin="normal"
            >
              {currencies.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
        <Button
          variant="contained"
          onClick={saveSettings}
          disabled={loading || !clientName.trim()}
          sx={{ mt: 2 }}
        >
          Save Settings
        </Button>
      </Paper>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Upload Files
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Timesheet Data (CSV)
              </Typography>
              <TextField
                id="timesheet-upload"
                type="file"
                accept=".csv"
                onChange={handleTimesheetChange}
                fullWidth
                variant="outlined"
                InputProps={{
                  startAdornment: <UploadIcon sx={{ mr: 1 }} />,
                }}
              />
              {timesheetFile && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Selected: {timesheetFile.name}
                </Typography>
              )}
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Project Data (CSV)
              </Typography>
              <TextField
                id="project-data-upload"
                type="file"
                accept=".csv"
                onChange={handleProjectDataChange}
                fullWidth
                variant="outlined"
                InputProps={{
                  startAdornment: <UploadIcon sx={{ mr: 1 }} />,
                }}
              />
              {projectDataFile && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Selected: {projectDataFile.name}
                </Typography>
              )}
            </Box>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={uploadFiles}
            disabled={loading || (!timesheetFile && !projectDataFile) || !clientName.trim()}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <UploadIcon />}
          >
            {loading ? 'Uploading...' : 'Upload Files'}
          </Button>
        </Box>
      </Paper>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          File Format Requirements
        </Typography>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Timesheet CSV Format</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" paragraph>
              The timesheet CSV file should contain the following columns:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="Date - The date of the timesheet entry (YYYY-MM-DD)" />
              </ListItem>
              <ListItem>
                <ListItemText primary="UserID - The ID of the user submitting the timesheet" />
              </ListItem>
              <ListItem>
                <ListItemText primary="WorkstreamID - The ID of the workstream" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Hours - Number of hours worked" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Notes - Description of work done" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Status - Approval status of the timesheet" />
              </ListItem>
            </List>
          </AccordionDetails>
        </Accordion>

        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Project Data CSV Format</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" paragraph>
              The project data CSV file should contain the following columns:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="ProfileID - Unique identifier for the profile" />
              </ListItem>
              <ListItem>
                <ListItemText primary="ProfileName - Name of the person" />
              </ListItem>
              <ListItem>
                <ListItemText primary="WorkstreamID - ID of the workstream" />
              </ListItem>
              <ListItem>
                <ListItemText primary="WorkstreamName - Name of the workstream" />
              </ListItem>
              <ListItem>
                <ListItemText primary="DaysAllocated - Number of days allocated to this profile for this workstream" />
              </ListItem>
              <ListItem>
                <ListItemText primary="StartDate - Start date of allocation (YYYY-MM-DD)" />
              </ListItem>
              <ListItem>
                <ListItemText primary="EndDate - End date of allocation (YYYY-MM-DD)" />
              </ListItem>
            </List>
            <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic' }}>
              Note: This format focuses on days allocated per profile per workstream, which is used to calculate budget hours.
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Paper>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Data Privacy Notice
        </Typography>
        <Typography variant="body2" paragraph>
          All uploaded data will be processed according to our data privacy policy:
        </Typography>
        <ul>
          <li>
            <Typography variant="body2">
              Sensitive information will be anonymized before being displayed in the dashboard
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Original data is stored securely and is only accessible to authorized users
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              No data is shared with third parties without explicit consent
            </Typography>
          </li>
        </ul>
      </Paper>
      
      {message && (
        <Alert severity={message.severity} sx={{ mt: 2 }}>
          {message.text}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={message.severity} sx={{ width: '100%' }}>
          {message.text}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default DataUpload; 
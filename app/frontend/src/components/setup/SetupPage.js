import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
  Stepper, 
  Step, 
  StepLabel, 
  Button,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';
import DataUpload from './DataUpload';
import ReviewData from './DataConfiguration';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`setup-tabpanel-${index}`}
      aria-labelledby={`setup-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `setup-tab-${index}`,
    'aria-controls': `setup-tabpanel-${index}`,
  };
}

function SetupPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processComplete, setProcessComplete] = useState(false);
  const [message, setMessage] = useState({ text: '', severity: 'info' });
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleUploadComplete = () => {
    setUploadComplete(true);
    setActiveStep(1); // Move to the Review step
    setActiveTab(1);  // Switch to the Review tab
  };

  const handleProcessData = async () => {
    setProcessing(true);
    try {
      const response = await fetch('/api/setup/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to process data');
      }

      const result = await response.json();
      setMessage({
        text: 'Data processed successfully! Redirecting to dashboard...',
        severity: 'success'
      });
      setProcessComplete(true);
      setOpenSnackbar(true);
      
      // Wait a short moment to show the success message, then redirect
      setTimeout(() => {
        navigate('/');  // Redirect to root (main dashboard)
      }, 1500);  // 1.5 second delay to show the success message
    } catch (error) {
      console.error('Error processing data:', error);
      setMessage({
        text: 'Failed to process data. Please try again.',
        severity: 'error'
      });
      setOpenSnackbar(true);
    } finally {
      setProcessing(false);
    }
  };

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  const steps = ['Data Upload', 'Review'];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Project Setup
      </Typography>
      <Typography variant="body1" paragraph>
        Complete the following steps to set up your project management dashboard.
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Data Upload" {...a11yProps(0)} />
          <Tab label="Review" {...a11yProps(1)} />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          <DataUpload onUploadComplete={handleUploadComplete} />
        </TabPanel>
        
        <TabPanel value={activeTab} index={1}>
          {!uploadComplete ? (
            <>
              <Typography variant="h6" gutterBottom>
                Review & Complete
              </Typography>
              <Typography variant="body1" paragraph>
                Review your uploaded data before finalizing the setup.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Review options will be available after data upload.
              </Typography>
            </>
          ) : (
            <>
              <ReviewData />
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleProcessData}
                  disabled={processing || processComplete}
                >
                  {processing ? 'Processing...' : processComplete ? 'Processing Complete' : 'Process Data'}
                </Button>
              </Box>
              {processComplete && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  Data has been processed successfully. You can now proceed to create visualizations.
                </Alert>
              )}
            </>
          )}
        </TabPanel>
      </Paper>

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

export default SetupPage; 
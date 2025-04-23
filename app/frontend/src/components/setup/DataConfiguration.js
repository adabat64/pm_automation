import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
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
  Tab,
} from '@mui/material';

const DataConfiguration = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [profiles, setProfiles] = useState([]);
  const [workstreams, setWorkstreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [profilesRes, workstreamsRes] = await Promise.all([
        fetch('/api/profiles'),
        fetch('/api/workstreams'),
      ]);

      if (!profilesRes.ok || !workstreamsRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [profilesData, workstreamsData] = await Promise.all([
        profilesRes.json(),
        workstreamsRes.json(),
      ]);

      setProfiles(profilesData);
      setWorkstreams(workstreamsData);
      setError(null);
    } catch (err) {
      setError('Failed to load data. Please try again later.');
      console.error('Error fetching data:', err);
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
    <Box p={3}>
      <Typography variant="h5" gutterBottom>
        Data Review
      </Typography>
      
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Profiles & Allocations" />
        <Tab label="Workstreams" />
      </Tabs>

      {activeTab === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Daily Rate</TableCell>
                <TableCell>Workstream</TableCell>
                <TableCell>Days Allocated</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {profiles.map((profile) => (
                profile.workstreams.length > 0 ? (
                  profile.workstreams.map((allocation) => {
                    const workstream = workstreams.find(ws => ws.id === allocation.workstream_id);
                    return (
                      <TableRow key={`${profile.id}-${allocation.workstream_id}`}>
                        <TableCell>{profile.name}</TableCell>
                        <TableCell>{profile.daily_rate}</TableCell>
                        <TableCell>{workstream ? workstream.name : 'Unknown'}</TableCell>
                        <TableCell>{allocation.days_allocated}</TableCell>
                      </TableRow>
                    );
                  })
                ) : (
                  <TableRow key={profile.id}>
                    <TableCell>{profile.name}</TableCell>
                    <TableCell>{profile.daily_rate}</TableCell>
                    <TableCell>-</TableCell>
                    <TableCell>-</TableCell>
                  </TableRow>
                )
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {activeTab === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {workstreams.map((workstream) => (
                <TableRow key={workstream.id}>
                  <TableCell>{workstream.name}</TableCell>
                  <TableCell>{workstream.description}</TableCell>
                  <TableCell>{workstream.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default DataConfiguration; 
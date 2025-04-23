import React from 'react';
import { 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Divider,
  Box,
  Typography
} from '@mui/material';
import { 
  Dashboard as DashboardIcon, 
  Assessment as AssessmentIcon, 
  Timeline as TimelineIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';

const drawerWidth = 240;

function Sidebar() {
  const location = useLocation();
  
  const menuItems = [
    { text: 'Client Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'PM Dashboard', icon: <AssessmentIcon />, path: '/pm' },
    { text: 'Forecast', icon: <TimelineIcon />, path: '/forecast' },
    { text: 'Setup', icon: <SettingsIcon />, path: '/setup' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          top: '64px', // Height of the navbar
          height: 'calc(100% - 64px)',
        },
      }}
    >
      <Box sx={{ overflow: 'auto', mt: 2 }}>
        <List>
          {menuItems.map((item) => (
            <ListItem 
              button 
              key={item.text} 
              component={Link} 
              to={item.path}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'rgba(25, 118, 210, 0.08)',
                  '&:hover': {
                    backgroundColor: 'rgba(25, 118, 210, 0.12)',
                  },
                },
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
        <Divider />
      </Box>
    </Drawer>
  );
}

export default Sidebar; 
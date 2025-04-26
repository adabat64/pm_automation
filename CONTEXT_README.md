# Project Context Guide

## Overview
This document provides context about the project structure, file purposes, and interactions for the PM Automation system. It's designed to help LLMs quickly understand the project architecture and relationships between components.

## Core Architecture

### Backend (FastAPI)
- Entry Point: `app/api/main.py`
  - Main FastAPI application
  - Handles API routing and server configuration

### Frontend (React)
- Entry Point: `app/frontend/src/App.js`
  - React application root
  - Manages routing and main layout

## File Context

### Data Processing and Privacy
```
app/utils/data_processor.py
├─ Purpose: Central data processing hub
├─ Key Functions: 
│  ├─ process_timesheet(): Processes and anonymizes timesheet data
│  ├─ process_project_data(): Handles CSV data with French locale support
│  └─ init(): Sets up secure storage and privacy management
├─ Features:
│  ├─ French decimal format support (uses comma as decimal separator)
│  ├─ Preserves full workstream names including commas
│  ├─ Secure data storage
│  └─ Data anonymization
├─ Interactions:
│  ├─ Uses SecureStorage for sensitive data
│  ├─ Uses DataPrivacyManager for anonymization
│  └─ Called by frontend DataUpload component during project setup
```

### Data Models
```
app/models/
├─ profile.py
│  ├─ Purpose: Defines team member profiles and their attributes
│  ├─ Key Fields: id, name, role, workstreams, hourly_rate, skills
│  └─ Used by: ProjectDashboard, PMDashboard for team management
├─ workstream.py
│  ├─ Purpose: Defines project workstreams and their budgets
│  └─ Used by: Budget calculations, dashboard displays
├─ timesheet.py
│  ├─ Purpose: Handles time tracking and reporting
│  └─ Interactions: Processed by data_processor.py
├─ budget.py
│  ├─ Purpose: Manages financial tracking and forecasting
│  └─ Used by: ForecastDashboard, budget calculations
```

### Frontend Components
```
app/frontend/src/components/
├─ dashboards/
│  ├─ ProjectDashboard.js
│  │  ├─ Purpose: Main project overview dashboard
│  │  ├─ Shows: Profiles, workstreams, budget summaries
│  │  └─ Data Source: Fetches from /api/profiles and /api/workstreams
│  ├─ PMDashboard.js
│  │  ├─ Purpose: Detailed project management view
│  │  └─ Shows: Complex metrics and detailed analytics
│  ├─ ClientDashboard.js
│  │  ├─ Purpose: Client-facing view
│  │  └─ Shows: Simplified project status and progress
│  └─ ForecastDashboard.js
│     ├─ Purpose: Future projections and planning
│     └─ Uses: Budget data and resource allocation
├─ setup/
│  ├─ DataUpload.js
│  │  ├─ Purpose: Handles initial project setup
│  │  ├─ Features: File upload, project configuration
│  │  └─ Interactions: Sends data to data_processor.py
│  ├─ DataConfiguration.js
│  │  ├─ Purpose: Project settings configuration
│  │  └─ Manages: Client name, currency, other settings
│  └─ SetupPage.js
│     └─ Purpose: Container for setup components
```

### Data Flow
1. Initial Setup:
   ```
   DataUpload.js → API → data_processor.py → SecureStorage
                                          └→ Anonymized Data → Database
   ```

2. Dashboard Data:
   ```
   Database → API → React Components → User Interface
   ```

3. Privacy Layer:
   ```
   Raw Data → DataPrivacyManager → Anonymized Data → Public API
   ```

## Key Interactions

### Project Setup Flow
1. User uploads project data through DataUpload.js
2. data_processor.py processes and anonymizes data
3. Data is stored securely with privacy measures
4. Dashboards are populated with anonymized data

### Dashboard Updates
1. ProjectDashboard fetches data from multiple endpoints
2. PMDashboard shows detailed analytics
3. All sensitive data is pre-anonymized before reaching frontend

## Security Notes
- Client data is never committed to git
- System is designed for multi-client support
- No hardcoded client information
- All sensitive data is processed through privacy layer

## Update History
- Initial version: 2025-04-26

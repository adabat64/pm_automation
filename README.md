# Project Management Automation with LLM

This project implements a Project Management Automation system using Large Language Models (LLM) with a Model Context Protocol (MCP) server. The system helps project managers query and analyze project data, including profiles, workstreams, and timesheets.

## Features

- Profile management (skills, roles, workstream assignments)
- Workstream tracking and analysis
- Timesheet data integration
- Budget tracking and forecasting
- Natural language querying for project status
- Budget and resource allocation analysis
- Data privacy with anonymization

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file with necessary configurations (see `.env.example`)

## Running the Application

### Using Sample Data
To run the application with sample data:
```bash
python -m app.utils.load_test_data --sample
```

### Using Real Test Data
To run the application with your real test data:
```bash
python -m app.utils.load_test_data --timesheet path/to/timesheets.csv --project-data path/to/project_data.xlsx
```

### Running the API Server
After loading the data (either sample or real):
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
pm_automation/
├── app/
│   ├── models/        # Data models
│   ├── core/          # Core functionality and MCP
│   ├── api/           # API endpoints
│   └── utils/         # Utility functions
├── sample_data/       # Sample data for testing
├── requirements.txt   # Project dependencies
└── README.md         # This file
```

## Data Privacy

The system includes robust data privacy features:

- All data is stored locally in a SQLite database
- Data is automatically anonymized before being exposed through the API
- Original data is only accessible through specific endpoints with proper authentication
- CSV imports are processed locally and immediately anonymized
- Sensitive information is stored in a secure location with restricted access
- All examples and sample data use anonymized values

## Usage

The API provides endpoints for:
- Querying project status
- Managing profiles and workstreams
- Analyzing timesheet data
- Tracking budgets and forecasts
- Generating reports

Documentation available at `/docs` when the server is running.

## Testing

### Sample Data
The project includes utilities to generate and load sample data:
```python
from app.utils.sample_data import generate_sample_data
generate_sample_data()
```

### Real Test Data
To use your real test data:
1. Place your data files in a secure location (not in the repository)
2. Use the `load_test_data.py` script to load them:
```bash
python -m app.utils.load_test_data --timesheet path/to/timesheets.csv --project-data path/to/project_data.xlsx
```

## Budget Tracking

The project includes a script to manage budget relations:

```python
from app.utils.update_timesheets import TimesheetManager

manager = TimesheetManager()

# Set budget for a workstream (with anonymized values)
manager.set_budget_relation("Workstream_123", {
    "budget_hours": 100,
    "hourly_rate": 150,
    "description": "Workstream budget description"
})

# Get budget status
status = manager.get_budget_status()
print(status)
```

## Future Enhancements

- Web interface for easier interaction
- Enhanced LLM integration for more sophisticated queries
- Advanced visualization of project data
- Export functionality with proper anonymization

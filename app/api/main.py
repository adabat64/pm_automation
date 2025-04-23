from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import pandas as pd
import tempfile

from app.core.mcp import get_mcp, MCPContext
from app.models.profile import Profile
from app.models.workstream import Workstream, WorkstreamStatus
from app.models.timesheet import TimesheetEntry, TimesheetSummary
from app.models.budget import BudgetEntry, BudgetForecast, BudgetSummary, BudgetType, BudgetPeriod, BudgetStatus

app = FastAPI(
    title="Project Management Dashboard API",
    description="API for the Project Management Dashboard",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the frontend
frontend_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

# API Routes

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/context")
async def get_context(mcp: MCPContext = Depends(get_mcp)):
    """Get the current MCP context."""
    return mcp.to_dict()

# Profile endpoints
@app.post("/api/profiles/")
async def create_profile(profile: Profile, mcp: MCPContext = Depends(get_mcp)):
    """Create a new profile."""
    profile_data = profile.dict()
    anonymized_id = mcp.data_store.store_profile(profile_data)
    return {"anonymized_id": anonymized_id, "profile": profile_data}

@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific profile."""
    profile_data = mcp.data_store.get_original_data(profile_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_data

# Workstream endpoints
@app.post("/api/workstreams/")
async def create_workstream(workstream: Workstream, mcp: MCPContext = Depends(get_mcp)):
    """Create a new workstream."""
    workstream_data = workstream.dict()
    anonymized_id = mcp.data_store.store_workstream(workstream_data)
    return {"anonymized_id": anonymized_id, "workstream": workstream_data}

@app.get("/api/workstreams/{workstream_id}")
async def get_workstream(workstream_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific workstream."""
    workstream_data = mcp.data_store.get_original_data(workstream_id)
    if not workstream_data:
        raise HTTPException(status_code=404, detail="Workstream not found")
    return workstream_data

# Timesheet endpoints
@app.post("/api/timesheets/")
async def create_timesheet_entry(entry: TimesheetEntry, mcp: MCPContext = Depends(get_mcp)):
    """Create a new timesheet entry."""
    entry_data = entry.dict()
    anonymized_id = mcp.data_store.store_timesheet(entry_data)
    return {"anonymized_id": anonymized_id, "entry": entry_data}

@app.post("/api/timesheets/import-csv")
async def import_timesheet_csv(
    file: UploadFile = File(...),
    mcp: MCPContext = Depends(get_mcp)
):
    """Import timesheet data from a CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Create a temporary file to store the uploaded CSV
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        
        try:
            # Import the CSV using the data store
            anonymized_ids = mcp.data_store.import_timesheet_csv(temp_file.name)
            return {
                "message": f"Successfully imported {len(anonymized_ids)} timesheet entries",
                "anonymized_ids": anonymized_ids
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)

@app.get("/api/timesheets/summary")
async def get_timesheet_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    mcp: MCPContext = Depends(get_mcp)
):
    """Get a summary of timesheet entries."""
    anonymized_data = mcp.data_store.get_anonymized_data()
    entries = anonymized_data["timesheets"]
    
    # Filter by date range if provided
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        entries = [e for e in entries if start <= datetime.fromisoformat(e["date"]) <= end]
    
    # Calculate summary
    total_hours = sum(e["hours"] for e in entries)
    approved_hours = sum(e["hours"] for e in entries if e["approval_status"] == "approved")
    pending_hours = total_hours - approved_hours
    
    # Group by workstream and user
    by_workstream = {}
    by_user = {}
    
    for entry in entries:
        ws_id = entry["workstream_id"]
        user_id = entry["user_id"]
        hours = entry["hours"]
        
        by_workstream[ws_id] = by_workstream.get(ws_id, 0) + hours
        by_user[user_id] = by_user.get(user_id, 0) + hours
    
    summary = TimesheetSummary(
        total_hours=total_hours,
        approved_hours=approved_hours,
        pending_hours=pending_hours,
        by_workstream=by_workstream,
        by_user=by_user,
        date_range=(start_date or "all", end_date or "all")
    )
    
    return summary.dict()

# Budget endpoints
@app.post("/api/budgets/")
async def create_budget_entry(budget: BudgetEntry, mcp: MCPContext = Depends(get_mcp)):
    """Create a new budget entry."""
    budget_data = budget.dict()
    anonymized_id = mcp.data_store.store_budget(budget_data)
    return {"anonymized_id": anonymized_id, "budget": budget_data}

@app.get("/api/budgets/{budget_id}")
async def get_budget(budget_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific budget entry."""
    budget_data = mcp.data_store.get_original_data(budget_id)
    if not budget_data:
        raise HTTPException(status_code=404, detail="Budget entry not found")
    return budget_data

@app.post("/api/budgets/forecast")
async def create_budget_forecast(forecast: BudgetForecast, mcp: MCPContext = Depends(get_mcp)):
    """Create a new budget forecast."""
    forecast_data = forecast.dict()
    anonymized_id = mcp.data_store.store_budget_forecast(forecast_data)
    return {"anonymized_id": anonymized_id, "forecast": forecast_data}

@app.get("/api/budgets/forecast/{forecast_id}")
async def get_budget_forecast(forecast_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific budget forecast."""
    forecast_data = mcp.data_store.get_original_data(forecast_id)
    if not forecast_data:
        raise HTTPException(status_code=404, detail="Budget forecast not found")
    return forecast_data

@app.get("/api/budgets/summary/{workstream_id}")
async def get_budget_summary(workstream_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a summary of budget data for a workstream."""
    summary = mcp.data_store.get_budget_summary(workstream_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Budget summary not found")
    return summary

# Dashboard endpoints
@app.get("/api/dashboard/client/summary")
async def get_client_summary(mcp: MCPContext = Depends(get_mcp)):
    """Get client-facing dashboard summary."""
    # This will be expanded to include all client dashboard data
    return {
        "project_name": "Project Dashboard",
        "status": "In Progress",
        "budget": {
            "total": 100000,
            "spent": 45000,
            "remaining": 55000,
            "percentage": 45
        },
        "workstreams": [
            {"id": "WS001", "name": "Project Planning", "status": "active", "progress": 75},
            {"id": "WS002", "name": "Development", "status": "active", "progress": 30},
            {"id": "WS003", "name": "Testing", "status": "planned", "progress": 0}
        ],
        "health": {
            "budget": "On Track",
            "timeline": "On Track",
            "resources": "At Risk",
            "scope": "Stable"
        },
        "blockers": [
            {"id": "B001", "description": "Resource constraint in Development team", "severity": "Medium"}
        ],
        "next_milestones": [
            {"id": "M001", "name": "Phase 1 Completion", "date": "2024-06-15", "status": "On Track"}
        ]
    }

@app.get("/api/dashboard/pm/project")
async def get_pm_project_data(mcp: MCPContext = Depends(get_mcp)):
    """Get project manager dashboard data."""
    # This will be expanded to include all PM dashboard data
    return {
        "profiles": [
            {"id": "P001", "name": "User_1", "role": "Developer", "availability": 80},
            {"id": "P002", "name": "User_2", "role": "Designer", "availability": 90}
        ],
        "workstreams": [
            {"id": "WS001", "name": "Project Planning", "status": "active", "progress": 75},
            {"id": "WS002", "name": "Development", "status": "active", "progress": 30},
            {"id": "WS003", "name": "Testing", "status": "planned", "progress": 0}
        ],
        "timesheets": {
            "last_updated": "2024-04-15",
            "total_hours": 450,
            "by_workstream": {
                "WS001": 150,
                "WS002": 250,
                "WS003": 50
            }
        }
    }

@app.get("/api/dashboard/forecast")
async def get_forecast_data(mcp: MCPContext = Depends(get_mcp)):
    """Get forecasting dashboard data."""
    # This will be expanded to include all forecasting data
    return {
        "revenue_forecast": {
            "current_month": 50000,
            "next_month": 55000,
            "total_forecast": 300000
        },
        "resource_forecast": {
            "by_profile": {
                "P001": {"forecast": 160, "actual": 120},
                "P002": {"forecast": 120, "actual": 100}
            },
            "by_workstream": {
                "WS001": {"forecast": 200, "actual": 150},
                "WS002": {"forecast": 300, "actual": 250},
                "WS003": {"forecast": 100, "actual": 50}
            }
        }
    }

# File upload endpoints
@app.post("/api/upload/timesheet")
async def upload_timesheet(file_path: str, mcp: MCPContext = Depends(get_mcp)):
    """Upload a timesheet file."""
    # This will be expanded to handle file uploads
    return {"status": "success", "message": f"Timesheet uploaded from {file_path}"}

@app.post("/api/upload/project-data")
async def upload_project_data(file_path: str, mcp: MCPContext = Depends(get_mcp)):
    """Upload project data file."""
    # This will be expanded to handle file uploads
    return {"status": "success", "message": f"Project data uploaded from {file_path}"}

# Query endpoint
@app.post("/api/query")
async def process_query(
    query: str,
    focus_areas: Optional[List[str]] = None,
    timeframe: Optional[str] = None,
    mcp: MCPContext = Depends(get_mcp)
):
    """Process a natural language query about the project."""
    # Update query context
    mcp.set_query_context(
        timeframe=timeframe,
        focus_areas=focus_areas
    )
    
    # TODO: Implement LLM query processing
    # This is where we'll integrate with an LLM to process the query
    # For now, return a placeholder response
    return {
        "query": query,
        "context": mcp.get_context(focus_areas),
        "response": "LLM query processing to be implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True) 
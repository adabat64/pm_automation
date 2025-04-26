from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import pandas as pd
import tempfile
import shutil

from app.core.mcp import get_mcp, MCPContext
from app.models.profile import Profile
from app.models.workstream import Workstream, WorkstreamStatus
from app.models.timesheet import TimesheetEntry, TimesheetSummary
from app.models.budget import BudgetEntry, BudgetForecast, BudgetSummary, BudgetType, BudgetPeriod, BudgetStatus
from app.utils.process_timesheets import parse_openair_timesheet
from app.utils.data_privacy import SecureStorage
from app.utils.data_processor import DataProcessor

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

# Settings router
settings_router = APIRouter()
REAL_DATA_DIR = "real_data"
SETTINGS_FILE = os.path.join(REAL_DATA_DIR, "project_settings.json")

@settings_router.post("/settings")
async def save_settings(client_name: str, currency: str):
    try:
        os.makedirs(REAL_DATA_DIR, exist_ok=True)
        settings = {
            "client_name": client_name,
            "currency": currency
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
        return {"message": "Settings saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@settings_router.get("/settings")
async def get_settings():
    try:
        if not os.path.exists(SETTINGS_FILE):
            return {"client_name": "", "currency": "USD"}
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Setup router
setup_router = APIRouter()

@setup_router.post("/process")
async def process_setup():
    """Process the uploaded data files."""
    try:
        data_processor = DataProcessor()
        # Process project data
        data_processor.process_project_data(os.path.join(REAL_DATA_DIR, "project_data.csv"))
        return {"message": "Data processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include routers
app.include_router(settings_router, prefix="/api", tags=["settings"])
app.include_router(setup_router, prefix="/api/setup", tags=["setup"])

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
@app.get("/api/profiles")
async def get_all_profiles(mcp: MCPContext = Depends(get_mcp)):
    """Get all profiles."""
    try:
        # Load profiles from the real_data directory
        profiles_file = Path("real_data") / "profiles.json"
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                profiles = json.load(f)
            return profiles
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profiles: {str(e)}")

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
@app.get("/api/workstreams")
async def get_all_workstreams(mcp: MCPContext = Depends(get_mcp)):
    """Get all workstreams."""
    try:
        # Load workstreams from the real_data directory
        workstreams_file = Path("real_data") / "workstreams.json"
        if workstreams_file.exists():
            with open(workstreams_file, 'r') as f:
                workstreams = json.load(f)
            return workstreams
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching workstreams: {str(e)}")

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
    data_store = mcp.data_store
    anonymized_data = data_store.get_anonymized_data()
    
    # Calculate budget summary
    total_budget = sum(budget.get('budget_hours', 0) * budget.get('hourly_rate', 0) 
                      for budget in anonymized_data['budgets'])
    spent_budget = sum(timesheet.get('hours', 0) * 
                      next((b.get('hourly_rate', 0) for b in anonymized_data['budgets'] 
                           if b.get('id') == timesheet.get('workstream_id')), 0)
                      for timesheet in anonymized_data['timesheets'])
    
    # Prepare per-workstream budget and spent data
    budgets = anonymized_data['budgets']
    timesheets = anonymized_data['timesheets']
    budget_map = {b.get('id'): b for b in budgets}
    workstreams_list = []
    for ws in anonymized_data['workstreams']:
        ws_id = ws.get('id')
        b_entry = budget_map.get(ws_id, {})
        ws_budget = b_entry.get('budget_hours', 0) * b_entry.get('hourly_rate', 0)
        ws_spent = sum(ts.get('hours', 0) * budget_map.get(ts.get('workstream_id'), {}).get('hourly_rate', 0)
                       for ts in timesheets if ts.get('workstream_id') == ws_id)
        ws_progress = (sum(ts.get('hours', 0) for ts in timesheets if ts.get('workstream_id') == ws_id) / 
                       ws.get('estimated_hours', 1) * 100) if ws.get('estimated_hours', 0) > 0 else 0
        workstreams_list.append({
            "id": ws.get('anonymized_id'),
            "name": ws.get('name'),
            "status": ws.get('status', 'active'),
            "progress": ws_progress,
            "budget": ws_budget,
            "spent": ws_spent
        })
    
    return {
        "project_name": "Project Dashboard",
        "status": "In Progress",
        "budget": {
            "total": total_budget,
            "spent": spent_budget,
            "remaining": total_budget - spent_budget,
            "percentage": (spent_budget / total_budget * 100) if total_budget > 0 else 0
        },
        "workstreams": workstreams_list,
        "health": {
            "budget": "On Track" if spent_budget <= total_budget else "At Risk",
            "timeline": "On Track",
            "resources": "At Risk" if any(p.get('utilization_target', 1) > 0.9 
                                       for p in anonymized_data['profiles']) else "On Track",
            "scope": "Stable"
        },
        "blockers": [],  # This should be populated from a separate table in the database
        "next_milestones": []  # This should be populated from a separate table in the database
    }

@app.get("/api/dashboard/pm/project")
async def get_pm_project_data(mcp: MCPContext = Depends(get_mcp)):
    """Get project manager dashboard data."""
    data_store = mcp.data_store
    anonymized_data = data_store.get_anonymized_data()
    
    # Calculate timesheet summary
    timesheet_summary = {
        "last_updated": max(t.get('date') for t in anonymized_data['timesheets']) 
                       if anonymized_data['timesheets'] else None,
        "total_hours": sum(t.get('hours', 0) for t in anonymized_data['timesheets']),
        "by_workstream": {}
    }
    
    for ws in anonymized_data['workstreams']:
        ws_id = ws.get('id')
        timesheet_summary['by_workstream'][ws.get('anonymized_id')] = sum(
            t.get('hours', 0) for t in anonymized_data['timesheets'] 
            if t.get('workstream_id') == ws_id
        )
    
    return {
        "profiles": [
            {
                "id": p.get('anonymized_id'),
                "name": p.get('name'),
                "role": p.get('role'),
                "availability": 100 - (sum(t.get('hours', 0) for t in anonymized_data['timesheets'] 
                                        if t.get('user_id') == p.get('id')) / 
                                    (p.get('utilization_target', 1) * 40) * 100)  # Assuming 40-hour work week
            }
            for p in anonymized_data['profiles']
        ],
        "workstreams": [
            {
                "id": ws.get('anonymized_id'),
                "name": ws.get('name'),
                "status": ws.get('status', 'active'),
                "progress": (sum(t.get('hours', 0) for t in anonymized_data['timesheets'] 
                               if t.get('workstream_id') == ws.get('id')) / 
                           ws.get('estimated_hours', 1) * 100) if ws.get('estimated_hours', 0) > 0 else 0
            }
            for ws in anonymized_data['workstreams']
        ],
        "timesheets": timesheet_summary
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

# Setup endpoints
@app.post("/api/upload")
async def upload_files(
    timesheet: Optional[UploadFile] = File(None),
    project_data: Optional[UploadFile] = File(None)
):
    """Upload and process setup files (timesheet and project data)."""
    if not timesheet and not project_data:
        raise HTTPException(status_code=400, detail="At least one file must be uploaded")
        
    try:
        results = {}
        os.makedirs(REAL_DATA_DIR, exist_ok=True)
        
        # Process project data if provided
        if project_data:
            if not project_data.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type for project data: {project_data.filename}. Must be a CSV file."
                )
            
            # Save project data to file
            project_data_path = os.path.join(REAL_DATA_DIR, "project_data.csv")
            with open(project_data_path, "wb") as buffer:
                shutil.copyfileobj(project_data.file, buffer)
            
            # Process the data using DataProcessor
            processor = DataProcessor(REAL_DATA_DIR)
            results['project_data'] = processor.process_project_data(project_data_path)
        
        # Process timesheet if provided
        if timesheet:
            if not timesheet.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type for timesheet: {timesheet.filename}. Must be a CSV file."
                )
            
            # Save timesheet to file
            timesheet_path = os.path.join(REAL_DATA_DIR, "timesheet.csv")
            with open(timesheet_path, "wb") as buffer:
                shutil.copyfileobj(timesheet.file, buffer)
            
            # Process the timesheet using DataProcessor
            processor = DataProcessor(REAL_DATA_DIR)
            results['timesheet'] = processor.process_timesheet(timesheet_path)
        
        return {
            "message": "Files processed successfully",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error processing files: {str(e)}"
        )

@app.post("/api/process")
async def process_data():
    try:
        processor = DataProcessor(REAL_DATA_DIR)
        csv_path = os.path.join(REAL_DATA_DIR, "project_data.csv")
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=400, detail="No data file found. Please upload data first.")
        
        result = processor.process_project_data(csv_path)
        return {"message": "Data processed successfully", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True) 
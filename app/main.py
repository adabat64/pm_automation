from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import json
from datetime import datetime
import pandas as pd
from pathlib import Path
import tempfile
import os

from app.core.mcp import MCPContext
from app.models.profile import Profile
from app.models.workstream import Workstream, WorkstreamStatus
from app.models.timesheet import TimesheetEntry, TimesheetSummary
from app.models.budget import BudgetEntry, BudgetForecast, BudgetSummary, BudgetType, BudgetPeriod, BudgetStatus

app = FastAPI(
    title="Project Management Automation",
    description="LLM-powered project management automation system",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP context
mcp = MCPContext("Project X")

# Dependency to get MCP context
async def get_mcp():
    return mcp

@app.get("/")
async def root():
    return {"message": "Project Management Automation API"}

@app.get("/context")
async def get_context(mcp: MCPContext = Depends(get_mcp)):
    """Get the current MCP context."""
    return mcp.to_dict()

@app.post("/profiles/")
async def create_profile(profile: Profile, mcp: MCPContext = Depends(get_mcp)):
    """Create a new profile."""
    profile_data = profile.dict()
    anonymized_id = mcp.data_store.store_profile(profile_data)
    return {"anonymized_id": anonymized_id, "profile": profile_data}

@app.get("/profiles/{profile_id}")
async def get_profile(profile_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific profile."""
    profile_data = mcp.data_store.get_original_data(profile_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_data

@app.post("/workstreams/")
async def create_workstream(workstream: Workstream, mcp: MCPContext = Depends(get_mcp)):
    """Create a new workstream."""
    workstream_data = workstream.dict()
    anonymized_id = mcp.data_store.store_workstream(workstream_data)
    return {"anonymized_id": anonymized_id, "workstream": workstream_data}

@app.get("/workstreams/{workstream_id}")
async def get_workstream(workstream_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific workstream."""
    workstream_data = mcp.data_store.get_original_data(workstream_id)
    if not workstream_data:
        raise HTTPException(status_code=404, detail="Workstream not found")
    return workstream_data

@app.post("/timesheets/")
async def create_timesheet_entry(entry: TimesheetEntry, mcp: MCPContext = Depends(get_mcp)):
    """Create a new timesheet entry."""
    entry_data = entry.dict()
    anonymized_id = mcp.data_store.store_timesheet(entry_data)
    return {"anonymized_id": anonymized_id, "entry": entry_data}

@app.post("/timesheets/import-csv")
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

@app.get("/timesheets/summary")
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

@app.post("/budgets/")
async def create_budget_entry(budget: BudgetEntry, mcp: MCPContext = Depends(get_mcp)):
    """Create a new budget entry."""
    budget_data = budget.dict()
    anonymized_id = mcp.data_store.store_budget(budget_data)
    return {"anonymized_id": anonymized_id, "budget": budget_data}

@app.get("/budgets/{budget_id}")
async def get_budget(budget_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific budget entry."""
    budget_data = mcp.data_store.get_original_data(budget_id)
    if not budget_data:
        raise HTTPException(status_code=404, detail="Budget entry not found")
    return budget_data

@app.post("/budgets/forecast")
async def create_budget_forecast(forecast: BudgetForecast, mcp: MCPContext = Depends(get_mcp)):
    """Create a new budget forecast."""
    forecast_data = forecast.dict()
    anonymized_id = mcp.data_store.store_budget_forecast(forecast_data)
    return {"anonymized_id": anonymized_id, "forecast": forecast_data}

@app.get("/budgets/forecast/{forecast_id}")
async def get_budget_forecast(forecast_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a specific budget forecast."""
    forecast_data = mcp.data_store.get_original_data(forecast_id)
    if not forecast_data:
        raise HTTPException(status_code=404, detail="Budget forecast not found")
    return forecast_data

@app.get("/budgets/summary/{workstream_id}")
async def get_budget_summary(workstream_id: str, mcp: MCPContext = Depends(get_mcp)):
    """Get a summary of budget data for a workstream."""
    summary = mcp.data_store.get_budget_summary(workstream_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Budget summary not found")
    return summary

@app.post("/query")
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
    uvicorn.run(app, host="0.0.0.0", port=8000) 
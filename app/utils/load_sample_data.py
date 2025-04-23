import json
import os
from pathlib import Path
from typing import Dict, List, Any

from app.core.mcp import MCPContext
from app.models.profile import Profile
from app.models.workstream import Workstream
from app.models.timesheet import TimesheetEntry
from app.models.budget import BudgetEntry, BudgetForecast

def load_sample_data(mcp: MCPContext, data_dir: str = "sample_data") -> None:
    """Load sample data into the MCP context."""
    # Load profiles
    with open(os.path.join(data_dir, "profiles.json"), "r") as f:
        profiles_data = json.load(f)
        for profile_data in profiles_data:
            profile = Profile(**profile_data)
            mcp.update_context("profiles", {profile.id: profile.dict()})
    
    # Load workstreams
    with open(os.path.join(data_dir, "workstreams.json"), "r") as f:
        workstreams_data = json.load(f)
        for workstream_data in workstreams_data:
            workstream = Workstream(**workstream_data)
            mcp.update_context("workstreams", {workstream.id: workstream.dict()})
    
    # Load timesheets
    with open(os.path.join(data_dir, "timesheets.json"), "r") as f:
        timesheets_data = json.load(f)
        for timesheet_data in timesheets_data:
            timesheet = TimesheetEntry(**timesheet_data)
            mcp.update_context("timesheet_entries", {timesheet.id: timesheet.dict()})
    
    # Load budgets
    with open(os.path.join(data_dir, "budgets.json"), "r") as f:
        budgets_data = json.load(f)
        for budget_data in budgets_data:
            budget = BudgetEntry(**budget_data)
            mcp.data_store.store_budget(budget.dict())
    
    # Load forecasts
    with open(os.path.join(data_dir, "forecasts.json"), "r") as f:
        forecasts_data = json.load(f)
        for forecast_data in forecasts_data:
            forecast = BudgetForecast(**forecast_data)
            mcp.data_store.store_budget_forecast(forecast.dict())
    
    print("Sample data loaded successfully!")

if __name__ == "__main__":
    # Initialize MCP context
    mcp = MCPContext("Sample Project")
    
    # Load sample data
    load_sample_data(mcp)
    
    # Print summary
    context = mcp.to_dict()
    print(f"Loaded {len(context['context']['profiles'])} profiles")
    print(f"Loaded {len(context['context']['workstreams'])} workstreams")
    print(f"Loaded {len(context['context'].get('timesheet_entries', {}))} timesheets")
    print(f"Loaded {len(context['anonymized_data']['budgets'])} budgets")
    print(f"Loaded {len(context['anonymized_data']['forecasts'])} forecasts") 
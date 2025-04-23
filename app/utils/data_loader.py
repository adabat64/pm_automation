import json
import uuid
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any, Optional

from app.core.mcp import MCPContext, get_mcp
from app.models.profile import Profile
from app.models.workstream import Workstream
from app.models.timesheet import TimesheetEntry
from app.models.budget import BudgetEntry, BudgetForecast
from app.utils.process_timesheets import process_timesheet
from app.utils.excel_to_json import excel_to_profiles_and_workstreams

def generate_sample_data() -> None:
    """Generate anonymized sample data for testing."""
    # Create sample data directory
    data_dir = Path("sample_data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate anonymized profiles
    profiles = [
        {
            "id": str(uuid.uuid4()),
            "name": f"User_{i}",
            "role": f"Role_{i}",
            "rate": random.randint(100, 200)
        }
        for i in range(1, 6)
    ]
    
    # Generate anonymized workstreams
    workstreams = [
        {
            "id": str(uuid.uuid4()),
            "name": f"Workstream_{i}",
            "description": f"Description for Workstream_{i}",
            "estimated_hours": random.randint(50, 200),
            "status": random.choice(["active", "completed", "pending"])
        }
        for i in range(1, 4)
    ]
    
    # Generate anonymized timesheets
    timesheets = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(20):
        date = start_date + timedelta(days=i)
        if date.weekday() < 5:  # Only weekdays
            for _ in range(random.randint(1, 3)):
                timesheet = {
                    "id": str(uuid.uuid4()),
                    "date": date.strftime("%Y-%m-%d"),
                    "user": random.choice(profiles)["name"],
                    "workstream": random.choice(workstreams)["name"],
                    "hours": round(random.uniform(0.5, 8.0), 1),
                    "notes": "[REDACTED]",
                    "approval_status": random.choice(["approved", "pending", "rejected"]),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                timesheets.append(timesheet)
    
    # Generate anonymized budget relations
    budget_relations = {}
    for workstream in workstreams:
        budget_relations[workstream["name"]] = {
            "budget_hours": workstream["estimated_hours"],
            "hourly_rate": random.randint(100, 200),
            "description": "[REDACTED]",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    # Save sample data
    with open(data_dir / "profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)
    
    with open(data_dir / "workstreams.json", "w") as f:
        json.dump(workstreams, f, indent=2)
    
    with open(data_dir / "timesheets.json", "w") as f:
        json.dump(timesheets, f, indent=2)
    
    with open(data_dir / "budget_relations.json", "w") as f:
        json.dump(budget_relations, f, indent=2)
    
    print("Sample data generated successfully in the 'sample_data' directory.")
    print("All data has been anonymized for privacy.")

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
    
    # Load budget relations
    with open(os.path.join(data_dir, "budget_relations.json"), "r") as f:
        budget_relations = json.load(f)
        for workstream_name, budget_data in budget_relations.items():
            # Find the workstream ID
            workstream_id = None
            for ws in workstreams_data:
                if ws["name"] == workstream_name:
                    workstream_id = ws["id"]
                    break
            
            if workstream_id:
                budget_entry = BudgetEntry(
                    id=str(uuid.uuid4()),
                    workstream_id=workstream_id,
                    budget_type="hours",
                    amount=budget_data["budget_hours"],
                    period="total",
                    description=budget_data["description"],
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    last_updated=budget_data["last_updated"]
                )
                mcp.data_store.store_budget(budget_entry.dict())
    
    print("Sample data loaded successfully!")

def load_test_data(
    timesheet_path: Optional[str] = None,
    project_data_path: Optional[str] = None,
    use_sample_data: bool = False
):
    """
    Load test data into the system.
    
    Args:
        timesheet_path: Path to timesheet CSV file (e.g., 'timesheets.csv')
        project_data_path: Path to project data Excel file (e.g., 'project_data.xlsx')
        use_sample_data: If True, use sample data instead of real data
    """
    mcp = get_mcp()
    
    if use_sample_data:
        print("Loading sample data...")
        generate_sample_data()
        load_sample_data(mcp)
        return
    
    # Load real test data if provided
    if timesheet_path and os.path.exists(timesheet_path):
        print(f"\nProcessing timesheet data from {timesheet_path}...")
        process_timesheet(timesheet_path)
    
    if project_data_path and os.path.exists(project_data_path):
        print(f"\nProcessing project data from {project_data_path}...")
        profiles, workstreams = excel_to_profiles_and_workstreams(project_data_path)
        
        # Update MCP context with the data
        for profile in profiles:
            mcp.update_context("profiles", {profile["id"]: profile})
        for workstream in workstreams:
            mcp.update_context("workstreams", {workstream["id"]: workstream})
    
    print("\nTest data loaded successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data loader for the Project Management Dashboard")
    parser.add_argument("--generate", action="store_true", help="Generate sample data")
    parser.add_argument("--load", action="store_true", help="Load sample data into MCP context")
    parser.add_argument("--timesheet", help="Path to timesheet CSV file")
    parser.add_argument("--project-data", help="Path to project data Excel file")
    parser.add_argument("--sample", action="store_true", help="Use sample data instead of real data")
    
    args = parser.parse_args()
    
    if args.generate:
        generate_sample_data()
    
    if args.load or args.sample:
        mcp = MCPContext("Sample Project")
        if args.sample:
            load_test_data(use_sample_data=True)
        else:
            load_sample_data(mcp)
            
            # Print summary
            context = mcp.to_dict()
            print(f"Loaded {len(context['context']['profiles'])} profiles")
            print(f"Loaded {len(context['context']['workstreams'])} workstreams")
            print(f"Loaded {len(context['context'].get('timesheet_entries', {}))} timesheets")
    
    if args.timesheet or args.project_data:
        load_test_data(
            timesheet_path=args.timesheet,
            project_data_path=args.project_data,
            use_sample_data=args.sample
        ) 
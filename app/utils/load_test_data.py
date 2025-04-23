import os
from pathlib import Path
from typing import Optional
from app.core.mcp import get_mcp
from app.utils.process_timesheets import process_timesheet
from app.utils.excel_to_json import excel_to_profiles_and_workstreams

def load_test_data(
    timesheet_path: Optional[str] = None,
    project_data_path: Optional[str] = None,
    use_sample_data: bool = False
):
    """
    Load test data into the system.
    
    Args:
        timesheet_path: Path to timesheet CSV file (e.g., 'Lucrin_Timesheets.csv')
        project_data_path: Path to project data Excel file (e.g., 'Lucrin_Project_Data.xlsx')
        use_sample_data: If True, use sample data instead of real data
    """
    mcp = get_mcp()
    
    if use_sample_data:
        print("Loading sample data...")
        from app.utils.sample_data import generate_sample_data
        generate_sample_data()
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Load test data into the system")
    parser.add_argument("--timesheet", help="Path to timesheet CSV file")
    parser.add_argument("--project-data", help="Path to project data Excel file")
    parser.add_argument("--sample", action="store_true", help="Use sample data instead of real data")
    
    args = parser.parse_args()
    
    load_test_data(
        timesheet_path=args.timesheet,
        project_data_path=args.project_data,
        use_sample_data=args.sample
    ) 
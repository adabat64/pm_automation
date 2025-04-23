import pandas as pd
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def parse_openair_timesheet(csv_path: str) -> Dict[str, Any]:
    """Process OpenAir timesheet CSV format."""
    # Read the CSV file, skipping the header row
    df = pd.read_csv(csv_path, skiprows=1)
    
    # Get the report generation date from the last line (if it exists)
    generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Default to current time
    with open(csv_path, 'r') as f:
        lines = f.readlines()
        for line in reversed(lines):
            if line.startswith('Generated on:'):
                generated_date = line.replace('Generated on:', '').strip()
                break
    
    # Clean up the dataframe
    df = df.dropna(subset=['Date', 'Time (Hours)'])  # Remove rows with empty dates or hours
    
    # Remove the summary row (last row) if it has no date
    df = df[df['Date'].notna()]
    
    # Print data validation information
    print("\nData Validation:")
    print(f"Total rows in CSV: {len(df)}")
    print("\nSample of first few rows:")
    print(df[['Date', 'User', 'Task', 'Time (Hours)']].head())
    print("\nChecking for empty or invalid dates...")
    
    # Convert data types with error handling
    try:
        df['Time (Hours)'] = pd.to_numeric(df['Time (Hours)'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%y', errors='coerce')
        
        # Remove rows where date conversion failed
        invalid_dates = df[df['Date'].isna()]
        if not invalid_dates.empty:
            print("\nRows with invalid dates:")
            print(invalid_dates[['Date', 'User', 'Task', 'Time (Hours)']])
            df = df.dropna(subset=['Date'])
    except Exception as e:
        print(f"\nError processing dates: {e}")
        print("Please check your CSV file format.")
        raise
    
    # Create timesheet entries
    timesheets = []
    for _, row in df.iterrows():
        timesheet = {
            "id": str(uuid.uuid4()),
            "date": row['Date'].strftime("%Y-%m-%d"),
            "user": row['User'].strip(),
            "workstream": row['Task'].strip(),
            "hours": float(row['Time (Hours)']),
            "notes": row['Notes'].strip() if pd.notna(row['Notes']) else "",
            "approval_status": row['Approval status'].strip().lower() if pd.notna(row['Approval status']) else "pending"
        }
        timesheets.append(timesheet)
    
    # Calculate summary statistics
    total_hours = df['Time (Hours)'].sum()
    hours_by_workstream = df.groupby('Task')['Time (Hours)'].sum().to_dict()
    hours_by_user = df.groupby('User')['Time (Hours)'].sum().to_dict()
    hours_by_status = df.groupby('Approval status')['Time (Hours)'].sum().to_dict() if 'Approval status' in df.columns else {}
    
    # Create summary
    summary = {
        "total_hours": total_hours,
        "hours_by_workstream": hours_by_workstream,
        "hours_by_user": hours_by_user,
        "hours_by_status": hours_by_status,
        "last_updated": generated_date,
        "date_range": {
            "start": df['Date'].min().strftime("%Y-%m-%d"),
            "end": df['Date'].max().strftime("%Y-%m-%d")
        }
    }
    
    return {
        "timesheets": timesheets,
        "summary": summary
    }

def save_timesheet_data(data: Dict[str, Any], output_dir: str = "real_data") -> None:
    """Save timesheet data to JSON and CSV files."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save timesheets as JSON
    with open(Path(output_dir) / "timesheets.json", "w") as f:
        json.dump(data["timesheets"], f, indent=2)
    
    # Save summary as JSON
    with open(Path(output_dir) / "timesheet_summary.json", "w") as f:
        json.dump(data["summary"], f, indent=2)
    
    # Save timesheets as CSV
    pd.DataFrame(data["timesheets"]).to_csv(
        Path(output_dir) / "timesheets.csv",
        index=False
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python process_timesheets.py <timesheet_csv_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    data = parse_openair_timesheet(csv_path)
    save_timesheet_data(data)
    
    # Print summary
    print("\nTimesheet Processing Summary:")
    print(f"Total hours: {data['summary']['total_hours']:.2f}")
    print(f"Date range: {data['summary']['date_range']['start']} to {data['summary']['date_range']['end']}")
    print(f"Last updated: {data['summary']['last_updated']}")
    print("\nHours by workstream:")
    for workstream, hours in data['summary']['hours_by_workstream'].items():
        print(f"  {workstream}: {hours:.2f}")
    print("\nHours by approval status:")
    for status, hours in data['summary']['hours_by_status'].items():
        print(f"  {status}: {hours:.2f}") 
import pandas as pd
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import os
from app.utils.data_privacy import SecureStorage, DataPrivacyManager

class TimesheetManager:
    def __init__(self, data_dir: str = "real_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.timesheets_file = self.data_dir / "timesheets.json"
        self.summary_file = self.data_dir / "timesheet_summary.json"
        self.budget_file = self.data_dir / "budget_relations.json"
        
        # Initialize privacy and storage managers
        self.privacy_manager = DataPrivacyManager()
        self.secure_storage = SecureStorage()
        
        # Load existing data if available
        self.timesheets = self._load_json(self.timesheets_file) or []
        self.summary = self._load_json(self.summary_file) or {}
        self.budget_relations = self._load_json(self.budget_file) or {}
        
        # Track the last processed date
        self.last_processed_date = self.summary.get("last_processed_date")
    
    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file if it exists."""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def _save_json(self, data: Dict, file_path: Path) -> None:
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def process_new_timesheet(self, csv_path: str) -> Dict[str, Any]:
        """Process new timesheet data and update existing records."""
        # Read and process the new CSV file
        df = pd.read_csv(csv_path, skiprows=1)
        df = df.dropna(subset=['Date', 'Time (Hours)'])
        df = df[df['Date'].notna()]
        
        # Convert dates
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%y')
        
        # Create new timesheet entries
        new_timesheets = []
        for _, row in df.iterrows():
            # Create the timesheet entry
            timesheet = {
                "id": str(uuid.uuid4()),
                "date": row['Date'].strftime("%Y-%m-%d"),
                "user": row['User'].strip(),
                "workstream": row['Task'].strip(),
                "hours": float(row['Time (Hours)']),
                "notes": row['Notes'].strip() if pd.notna(row['Notes']) else "",
                "approval_status": row['Approval status'].strip().lower() if pd.notna(row['Approval status']) else "pending",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save the timesheet securely
            self.secure_storage.save_timesheet(timesheet)
            new_timesheets.append(timesheet)
        
        # Update summary statistics
        self._update_summary()
        
        return {
            "new_entries": len(new_timesheets),
            "updated_entries": 0,  # We now handle updates through the secure storage
            "summary": self.summary
        }
    
    def _update_summary(self) -> None:
        """Update summary statistics."""
        # Load the latest data from secure storage
        secure_timesheets = self.secure_storage._load_secure_data(
            self.secure_storage.data_dir / "secure_timesheets.json"
        )
        df = pd.DataFrame(secure_timesheets)
        
        # Create anonymized summary
        self.summary = {
            "total_hours": df['hours'].sum(),
            "hours_by_workstream": {
                self.privacy_manager.anonymize_workstream(ws): hours 
                for ws, hours in df.groupby('workstream')['hours'].sum().to_dict().items()
            },
            "hours_by_user": {
                self.privacy_manager.anonymize_user(user): hours 
                for user, hours in df.groupby('user')['hours'].sum().to_dict().items()
            },
            "hours_by_status": df.groupby('approval_status')['hours'].sum().to_dict(),
            "last_processed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_range": {
                "start": df['date'].min(),
                "end": df['date'].max()
            }
        }
        
        # Save the anonymized summary
        self._save_json(self.summary, self.summary_file)
    
    def set_budget_relation(self, workstream: str, budget_info: Dict) -> None:
        """Set budget information for a workstream."""
        # Save the budget securely
        self.secure_storage.save_budget(workstream, budget_info)
    
    def get_budget_status(self, workstream: str = None) -> Dict:
        """Get budget status for workstream(s)."""
        # Load the latest data from secure storage
        secure_budgets = self.secure_storage._load_secure_data(
            self.secure_storage.data_dir / "secure_budgets.json"
        )
        
        if workstream:
            return secure_budgets.get(workstream, {})
        
        # Calculate budget status for all workstreams
        status = {}
        for ws, budget in secure_budgets.items():
            hours = self.summary['hours_by_workstream'].get(
                self.privacy_manager.anonymize_workstream(ws), 0
            )
            rate = budget.get('hourly_rate', 0)
            budget_hours = budget.get('budget_hours', 0)
            
            status[ws] = {
                "hours_spent": hours,
                "hours_remaining": budget_hours - hours,
                "budget_spent": hours * rate,
                "budget_remaining": (budget_hours - hours) * rate,
                "budget_info": budget
            }
        
        return status

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python update_timesheets.py <timesheet_csv_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    manager = TimesheetManager()
    result = manager.process_new_timesheet(csv_path)
    
    # Print summary
    print("\nTimesheet Update Summary:")
    print(f"New entries added: {result['new_entries']}")
    print(f"Existing entries updated: {result['updated_entries']}")
    print(f"\nTotal hours: {result['summary']['total_hours']:.2f}")
    print(f"Date range: {result['summary']['date_range']['start']} to {result['summary']['date_range']['end']}")
    print(f"Last processed: {result['summary']['last_processed_date']}")
    
    print("\nHours by workstream:")
    for workstream, hours in result['summary']['hours_by_workstream'].items():
        print(f"  {workstream}: {hours:.2f}")
    
    print("\nHours by approval status:")
    for status, hours in result['summary']['hours_by_status'].items():
        print(f"  {status}: {hours:.2f}")

if __name__ == "__main__":
    main() 
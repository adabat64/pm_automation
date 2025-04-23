import os
import sys
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import uuid

from app.utils.update_timesheets import TimesheetManager
from app.utils.data_privacy import SecureStorage, DataPrivacyManager
from .process_timesheets import parse_openair_timesheet

class DataProcessor:
    """Unified data processor for handling all data operations."""
    
    def __init__(self, output_dir: str = "real_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.privacy_manager = DataPrivacyManager()
        self.secure_storage = SecureStorage()
        
    def process_timesheet(self, csv_path: str) -> List[Dict[str, Any]]:
        """Process a timesheet CSV file."""
        try:
            # Check if file exists
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Timesheet file not found: {csv_path}")
                
            # Check if file is readable
            if not os.access(csv_path, os.R_OK):
                raise PermissionError(f"Cannot read timesheet file: {csv_path}")
                
            # Use existing OpenAir parser
            timesheet_data = parse_openair_timesheet(csv_path)
            
            if not timesheet_data:
                raise ValueError("No valid timesheet data found in the file")
            
            # Save original data securely
            self.secure_storage.save_timesheet(timesheet_data)
            
            # Anonymize and save public data
            anonymized_data = []
            for entry in timesheet_data:
                anonymized_entry = self.privacy_manager.anonymize_timesheet(entry)
                anonymized_data.append(anonymized_entry)
            
            # Save anonymized data
            with open(self.output_dir / "timesheets.json", "w") as f:
                json.dump(anonymized_data, f, indent=2)
            
            return anonymized_data
            
        except Exception as e:
            error_msg = f"Error processing timesheet: {str(e)}"
            print(error_msg)  # For logging
            raise ValueError(error_msg)  # Re-raise with context
            
    def process_budget(self, excel_path: str) -> List[Dict[str, Any]]:
        """Process a budget Excel file."""
        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            
            # Convert to list of dictionaries
            budget_data = df.to_dict('records')
            
            # Save original data securely
            self.secure_storage.save_budget(budget_data)
            
            # Anonymize and save public data
            anonymized_data = []
            for entry in budget_data:
                anonymized_entry = self.privacy_manager.anonymize_budget(entry)
                anonymized_data.append(anonymized_entry)
            
            # Save anonymized data
            with open(self.output_dir / "budget_relations.json", "w") as f:
                json.dump(anonymized_data, f, indent=2)
            
            return anonymized_data
            
        except Exception as e:
            print(f"Error processing budget: {e}")
            return []
            
    def process_project_data(self, csv_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Process project data (profiles and workstreams) from CSV."""
        try:
            # Check if file exists
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Project data file not found: {csv_path}")
                
            # Check if file is readable
            if not os.access(csv_path, os.R_OK):
                raise PermissionError(f"Cannot read project data file: {csv_path}")
                
            # Try reading CSV with different separators
            try:
                # First try with semicolon separator
                df = pd.read_csv(csv_path, sep=';', thousands=',')
            except:
                try:
                    # Then try with comma separator
                    df = pd.read_csv(csv_path, sep=',', thousands=',')
                except:
                    raise ValueError("Could not read CSV file with either semicolon or comma separator")
            
            print(f"Columns found in CSV: {df.columns.tolist()}")
            
            # Get workstream names from columns (excluding Profile and Daily Rate)
            workstream_columns = [col for col in df.columns if col not in ['Profile', 'Daily Rate']]
            print(f"Workstream columns: {workstream_columns}")
            
            # Create unique workstreams first
            workstreams = []
            workstream_map = {}  # Map workstream names to their IDs
            
            for workstream_name in workstream_columns:
                # Clean workstream name - take first part if comma-separated
                clean_name = workstream_name.split(',')[0].strip()
                workstream_id = str(uuid.uuid4())
                workstream = {
                    "id": workstream_id,
                    "name": clean_name,
                    "description": "",  # Empty description as requested
                    "status": "active"  # lowercase to match frontend
                }
                workstreams.append(workstream)
                workstream_map[workstream_name] = workstream_id
            
            print(f"Created workstreams: {json.dumps(workstreams, indent=2)}")
            
            # Process profiles and their workstream allocations
            profiles = []
            
            for _, row in df.iterrows():
                # Handle daily rate
                daily_rate = row['Daily Rate']
                if pd.isna(daily_rate):
                    daily_rate = 0
                else:
                    # Convert to float, handling both string and numeric inputs
                    daily_rate = float(str(daily_rate).replace(',', '.'))
                
                profile = {
                    "id": str(uuid.uuid4()),
                    "name": row['Profile'],
                    "daily_rate": daily_rate,
                    "workstreams": []
                }
                
                print(f"Processing profile: {profile['name']} with daily rate: {daily_rate}")
                
                # Process each workstream allocation
                for workstream_name in workstream_columns:
                    days = row[workstream_name]
                    if pd.isna(days):
                        days = 0
                    else:
                        # Convert to float, handling both string and numeric inputs
                        days = float(str(days).replace(',', '.'))
                    
                    if days > 0:
                        # Add allocation to profile using the workstream ID from the map
                        allocation = {
                            "workstream_id": workstream_map[workstream_name],
                            "days_allocated": days
                        }
                        profile["workstreams"].append(allocation)
                        print(f"  Added allocation: {workstream_name} - {days} days")
                
                profiles.append(profile)
            
            print(f"\nFinal data to save:")
            print(f"Profiles: {json.dumps(profiles, indent=2)}")
            print(f"Workstreams: {json.dumps(workstreams, indent=2)}")
            
            # Save data
            with open(self.output_dir / "profiles.json", "w") as f:
                json.dump(profiles, f, indent=2)
            
            with open(self.output_dir / "workstreams.json", "w") as f:
                json.dump(workstreams, f, indent=2)
            
            return {
                "profiles": profiles,
                "workstreams": workstreams
            }
            
        except Exception as e:
            error_msg = f"Error processing project data: {str(e)}"
            print(error_msg)  # For logging
            raise ValueError(error_msg)  # Re-raise with context
            
    def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of project data."""
        try:
            # Load anonymized data
            with open(self.output_dir / "timesheets.json", "r") as f:
                timesheets = json.load(f)
            
            with open(self.output_dir / "budget_relations.json", "r") as f:
                budget_relations = json.load(f)
            
            # Calculate summary statistics
            total_hours = sum(float(entry.get("Hours", 0)) for entry in timesheets)
            total_budget = sum(float(entry.get("BudgetHours", 0)) for entry in budget_relations)
            
            return {
                "total_hours": total_hours,
                "total_budget": total_budget,
                "remaining_budget": total_budget - total_hours,
                "timesheet_count": len(timesheets),
                "budget_relation_count": len(budget_relations)
            }
            
        except Exception as e:
            print(f"Error getting project summary: {e}")
            return {
                "total_hours": 0,
                "total_budget": 0,
                "remaining_budget": 0,
                "timesheet_count": 0,
                "budget_relation_count": 0
            }

def main():
    """
    Command-line interface for the data processor.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Process project data files")
    parser.add_argument("--timesheet", help="Path to timesheet CSV file")
    parser.add_argument("--budget", help="Path to budget Excel file")
    parser.add_argument("--project", help="Path to project data CSV file")
    parser.add_argument("--output", default="real_data", help="Output directory")
    
    args = parser.parse_args()
    
    processor = DataProcessor(args.output)
    
    if args.timesheet:
        processor.process_timesheet(args.timesheet)
    
    if args.budget:
        processor.process_budget(args.budget)
    
    if args.project:
        processor.process_project_data(args.project)
    
    # Print summary
    summary = processor.get_project_summary()
    print("\nProject Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main() 
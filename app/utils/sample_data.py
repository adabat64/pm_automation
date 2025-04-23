import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any

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

if __name__ == "__main__":
    generate_sample_data() 
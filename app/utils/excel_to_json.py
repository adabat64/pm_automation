import pandas as pd
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any
import re

def parse_profile_name(name: str) -> tuple[str, str]:
    """Parse 'Last Name, First Name' format into first and last name."""
    parts = name.split(',')
    if len(parts) == 2:
        return parts[1].strip(), parts[0].strip()
    return name.strip(), ""

def parse_decimal(value: str) -> float:
    """Convert French decimal format (comma) to standard decimal (point)."""
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(',', '.'))

def excel_to_profiles_and_workstreams(excel_path: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Convert Excel data to profiles and workstreams JSON format."""
    df = pd.read_excel(excel_path)
    profiles = []
    workstreams = []
    workstream_map = {}  # To track workstream IDs
    
    # First pass: Create workstreams
    workstream_names = ["UX, UI & Design", "Composable & Headless", "SEO, Analytics & Strategy"]
    for name in workstream_names:
        workstream = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": f"Description for {name}",
            "estimated_hours": 0.0,  # Will be calculated based on days
            "status": "active"
        }
        workstreams.append(workstream)
        workstream_map[name] = workstream["id"]
    
    # Second pass: Create profiles
    for _, row in df.iterrows():
        # Parse profile name
        last_name, first_name = parse_profile_name(str(row["Profile"]))
        full_name = f"{first_name} {last_name}".strip()
        
        # Get daily rate (already numeric)
        daily_rate = float(row["Daily Rate"])
        
        # Create profile
        profile = {
            "id": str(uuid.uuid4()),
            "name": full_name,
            "role": "Team Member",  # Default role
            "rate": daily_rate
        }
        profiles.append(profile)
        
        # Update workstream estimated hours
        for workstream_name in workstream_names:
            days = parse_decimal(row[workstream_name])
            if days > 0:
                workstream = next(ws for ws in workstreams if ws["name"] == workstream_name)
                workstream["estimated_hours"] += days * 8  # Assuming 8 hours per day
    
    return profiles, workstreams

def convert_excel_to_json(excel_path: str, output_dir: str = "real_data") -> Dict[str, List[Dict[str, Any]]]:
    """Convert Excel data to JSON format and save to files."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Convert Excel data
    profiles, workstreams = excel_to_profiles_and_workstreams(excel_path)
    
    data = {
        "profiles": profiles,
        "workstreams": workstreams
    }
    
    # Save to files
    for key, value in data.items():
        with open(Path(output_dir) / f"{key}.json", "w") as f:
            json.dump(value, f, indent=2)
    
    return data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python excel_to_json.py <excel_file_path>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    data = convert_excel_to_json(excel_path)
    
    # Print summary
    print("\nConversion Summary:")
    for key, value in data.items():
        print(f"{key}: {len(value)} records converted") 
import pandas as pd
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any
import re

def parse_profile_name(name: str) -> tuple[str, str]:
    """Parse a profile name into last name and first name."""
    parts = name.strip().split(',')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
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
    
    # First pass: Create workstreams
    workstream_names = ["Design", "Development", "Strategy"]
    
    for name in workstream_names:
        workstream = {
            "id": f"WS{len(workstreams) + 1:03d}",
            "name": name,
            "description": f"Generic {name} workstream",
            "status": "active",
            "estimated_hours": 100,
            "tags": [name.lower()]
        }
        workstreams.append(workstream)
    
    # Second pass: Create profiles
    for _, row in df.iterrows():
        if pd.isna(row["Profile"]):
            continue
            
        # Parse profile name
        last_name, first_name = parse_profile_name(str(row["Profile"]))
        
        # Create profile
        profile = {
            "id": f"P{len(profiles) + 1:03d}",
            "name": f"{first_name} {last_name}".strip(),
            "role": "Team Member",  # Default role
            "rate": 100,  # Default rate
            "workstreams": []
        }
        profiles.append(profile)
    
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

def main():
    excel_path = "project_data.xlsx"
    profiles, workstreams = excel_to_profiles_and_workstreams(excel_path)
    
    data = {
        "profiles": profiles,
        "workstreams": workstreams
    }
    
    output_dir = Path("real_data")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "project_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Processed {len(profiles)} profiles and {len(workstreams)} workstreams")
    print(f"Data saved to {output_dir / 'project_data.json'}")

if __name__ == "__main__":
    main() 
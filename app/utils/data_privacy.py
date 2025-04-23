import hashlib
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Union
from datetime import datetime

class DataPrivacyManager:
    """Manages data privacy and anonymization."""
    
    def __init__(self, data_dir: str = "real_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.mapping_file = self.data_dir / "anonymization_mapping.json"
        
        # Load or create anonymization mapping
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load anonymization mapping from file."""
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r') as f:
                return json.load(f)
        return {
            "users": {},
            "workstreams": {},
            "notes": {}
        }
    
    def _save_mapping(self) -> None:
        """Save anonymization mapping to file."""
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mapping, f, indent=2)
    
    def _hash_value(self, value: str) -> str:
        """Create a consistent hash for a value."""
        if not value:
            return ""
        return hashlib.sha256(value.encode()).hexdigest()[:8]
    
    def anonymize_user(self, user: Union[str, Dict[str, Any]]) -> str:
        """Anonymize a user name."""
        if not user:
            return ""
        
        # Extract name if user is a dictionary
        user_name = user if isinstance(user, str) else user.get("name", "")
        
        if user_name not in self.mapping["users"]:
            self.mapping["users"][user_name] = f"User_{self._hash_value(user_name)}"
            self._save_mapping()
        
        return self.mapping["users"][user_name]
    
    def anonymize_workstream(self, workstream: Union[str, Dict[str, Any]]) -> str:
        """Anonymize a workstream name."""
        if not workstream:
            return ""
        
        # Extract name if workstream is a dictionary
        workstream_name = workstream if isinstance(workstream, str) else workstream.get("name", "")
        
        if workstream_name not in self.mapping["workstreams"]:
            self.mapping["workstreams"][workstream_name] = f"Workstream_{self._hash_value(workstream_name)}"
            self._save_mapping()
        
        return self.mapping["workstreams"][workstream_name]
    
    def anonymize_notes(self, notes: str) -> str:
        """Anonymize notes content."""
        if not notes:
            return ""
        
        # For notes, we just remove them entirely for privacy
        return "[REDACTED]"
    
    def anonymize_timesheet(self, timesheet: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize a timesheet entry."""
        return {
            "id": timesheet["id"],
            "date": timesheet["date"],
            "user": self.anonymize_user(timesheet["user"]),
            "workstream": self.anonymize_workstream(timesheet["workstream"]),
            "hours": timesheet["hours"],
            "notes": self.anonymize_notes(timesheet["notes"]),
            "approval_status": timesheet["approval_status"],
            "created_at": timesheet["created_at"],
            "last_updated": timesheet["last_updated"]
        }
    
    def anonymize_budget(self, budget: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize budget information."""
        return {
            "budget_hours": budget["budget_hours"],
            "hourly_rate": budget["hourly_rate"],
            "description": self.anonymize_notes(budget["description"]),
            "last_updated": budget["last_updated"]
        }
    
    def get_original_value(self, category: str, anonymized_value: str) -> str:
        """Get the original value for an anonymized value (if authorized)."""
        if category not in self.mapping:
            return anonymized_value
        
        for original, anonymized in self.mapping[category].items():
            if anonymized == anonymized_value:
                return original
        
        return anonymized_value

class SecureStorage:
    """Handles secure storage of sensitive data."""
    
    def __init__(self, data_dir: str = "secure_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.privacy_manager = DataPrivacyManager()
    
    def save_timesheet(self, timesheet: Dict[str, Any]) -> None:
        """Save a timesheet entry securely."""
        # Save original data in secure storage
        secure_file = self.data_dir / "secure_timesheets.json"
        secure_data = self._load_secure_data(secure_file)
        secure_data.append(timesheet)
        self._save_secure_data(secure_file, secure_data)
        
        # Save anonymized data in public storage
        public_file = Path("real_data") / "timesheets.json"
        public_data = self._load_secure_data(public_file)
        public_data.append(self.privacy_manager.anonymize_timesheet(timesheet))
        self._save_secure_data(public_file, public_data)
    
    def save_budget(self, workstream: Union[str, Dict[str, Any]], budget: Dict[str, Any]) -> None:
        """Save budget information securely."""
        # Extract workstream ID if workstream is a dictionary
        workstream_id = workstream if isinstance(workstream, str) else workstream.get("id", "")
        
        # Save original data in secure storage
        secure_file = self.data_dir / "secure_budgets.json"
        secure_data = self._load_secure_data(secure_file)
        secure_data[workstream_id] = budget
        self._save_secure_data(secure_file, secure_data)
        
        # Save anonymized data in public storage
        public_file = Path("real_data") / "budget_relations.json"
        public_data = self._load_secure_data(public_file)
        public_data[self.privacy_manager.anonymize_workstream(workstream_id)] = self.privacy_manager.anonymize_budget(budget)
        self._save_secure_data(public_file, public_data)
    
    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Save a profile securely."""
        # Save original data in secure storage
        secure_file = self.data_dir / "secure_profiles.json"
        secure_data = self._load_secure_data(secure_file)
        
        # Check if profile already exists
        profile_id = profile.get("id")
        if profile_id:
            # Update existing profile
            for i, p in enumerate(secure_data):
                if p.get("id") == profile_id:
                    secure_data[i] = profile
                    break
            else:
                # Add new profile
                secure_data.append(profile)
        else:
            # Add new profile with generated ID
            profile["id"] = str(uuid.uuid4())
            secure_data.append(profile)
        
        self._save_secure_data(secure_file, secure_data)
        
        # Save anonymized data in public storage
        public_file = Path("real_data") / "profiles.json"
        public_data = self._load_secure_data(public_file)
        
        # Create anonymized profile
        anonymized_profile = {
            "id": self.privacy_manager.anonymize_user(profile.get("id", "")),
            "name": self.privacy_manager.anonymize_user(profile.get("name", "")),
            "role": self.privacy_manager.anonymize_notes(profile.get("role", "")),
            "workstreams": [self.privacy_manager.anonymize_workstream(ws) for ws in profile.get("workstreams", [])],
            "hourly_rate": profile.get("hourly_rate", 0),
            "allocated_hours": {
                self.privacy_manager.anonymize_workstream(k): v 
                for k, v in profile.get("allocated_hours", {}).items()
            },
            "skills": [self.privacy_manager.anonymize_notes(skill) for skill in profile.get("skills", [])],
            "start_date": profile.get("start_date"),
            "end_date": profile.get("end_date"),
            "utilization_target": profile.get("utilization_target", 1.0)
        }
        
        # Update or add anonymized profile
        profile_id = profile.get("id")
        if profile_id:
            anonymized_id = self.privacy_manager.anonymize_user(profile_id)
            for i, p in enumerate(public_data):
                if p.get("id") == anonymized_id:
                    public_data[i] = anonymized_profile
                    break
            else:
                public_data.append(anonymized_profile)
        else:
            public_data.append(anonymized_profile)
        
        self._save_secure_data(public_file, public_data)
    
    def save_workstream(self, workstream: Dict[str, Any]) -> None:
        """Save a workstream securely."""
        # Save original data in secure storage
        secure_file = self.data_dir / "secure_workstreams.json"
        secure_data = self._load_secure_data(secure_file)
        
        # Check if workstream already exists
        workstream_id = workstream.get("id")
        if workstream_id:
            # Update existing workstream
            for i, w in enumerate(secure_data):
                if w.get("id") == workstream_id:
                    secure_data[i] = workstream
                    break
            else:
                # Add new workstream
                secure_data.append(workstream)
        else:
            # Add new workstream with generated ID
            workstream["id"] = str(uuid.uuid4())
            secure_data.append(workstream)
        
        self._save_secure_data(secure_file, secure_data)
        
        # Save anonymized data in public storage
        public_file = Path("real_data") / "workstreams.json"
        public_data = self._load_secure_data(public_file)
        
        # Create anonymized workstream
        anonymized_workstream = {
            "id": self.privacy_manager.anonymize_workstream(workstream.get("id", "")),
            "name": self.privacy_manager.anonymize_workstream(workstream.get("name", "")),
            "description": self.privacy_manager.anonymize_notes(workstream.get("description", "")),
            "estimated_hours": workstream.get("estimated_hours", 0),
            "status": workstream.get("status", "active")
        }
        
        # Update or add anonymized workstream
        workstream_id = workstream.get("id")
        if workstream_id:
            anonymized_id = self.privacy_manager.anonymize_workstream(workstream_id)
            for i, w in enumerate(public_data):
                if w.get("id") == anonymized_id:
                    public_data[i] = anonymized_workstream
                    break
            else:
                public_data.append(anonymized_workstream)
        else:
            public_data.append(anonymized_workstream)
        
        self._save_secure_data(public_file, public_data)
    
    def _load_secure_data(self, file_path: Path) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Load data from a JSON file."""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        
        # Return empty list for collection files, empty dict for mapping files
        if "timesheets" in str(file_path) or "profiles" in str(file_path) or "workstreams" in str(file_path):
            return []
        elif "budgets" in str(file_path):
            return {}
        else:
            # Default to empty list for safety
            return []
    
    def _save_secure_data(self, file_path: Path, data: Any) -> None:
        """Save data to a JSON file."""
        # Ensure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2) 
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
    
    def anonymize_user(self, user: str) -> str:
        """Anonymize a user name."""
        if not user:
            return ""
        
        if user not in self.mapping["users"]:
            self.mapping["users"][user] = f"User_{self._hash_value(user)}"
            self._save_mapping()
        
        return self.mapping["users"][user]
    
    def anonymize_workstream(self, workstream: str) -> str:
        """Anonymize a workstream name."""
        if not workstream:
            return ""
        
        if workstream not in self.mapping["workstreams"]:
            self.mapping["workstreams"][workstream] = f"Workstream_{self._hash_value(workstream)}"
            self._save_mapping()
        
        return self.mapping["workstreams"][workstream]
    
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
    
    def save_budget(self, workstream: str, budget: Dict[str, Any]) -> None:
        """Save budget information securely."""
        # Save original data in secure storage
        secure_file = self.data_dir / "secure_budgets.json"
        secure_data = self._load_secure_data(secure_file)
        secure_data[workstream] = budget
        self._save_secure_data(secure_file, secure_data)
        
        # Save anonymized data in public storage
        public_file = Path("real_data") / "budget_relations.json"
        public_data = self._load_secure_data(public_file)
        public_data[self.privacy_manager.anonymize_workstream(workstream)] = self.privacy_manager.anonymize_budget(budget)
        self._save_secure_data(public_file, public_data)
    
    def _load_secure_data(self, file_path: Path) -> Union[List, Dict]:
        """Load data from a secure file."""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return [] if "timesheets" in str(file_path) else {}
    
    def _save_secure_data(self, file_path: Path, data: Union[List, Dict]) -> None:
        """Save data to a secure file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2) 
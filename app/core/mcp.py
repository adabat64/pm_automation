from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import json
from .data_store import DataStore

class MCPMetadata(BaseModel):
    schema_version: str
    project_name: str
    last_updated: datetime

class QueryContext(BaseModel):
    relevant_timeframe: str
    focus_areas: List[str]
    access_level: str

class MCPContext:
    def __init__(self, project_name: str):
        self.metadata = MCPMetadata(
            schema_version="1.0",
            project_name=project_name,
            last_updated=datetime.now()
        )
        self.data_store = DataStore()
        self.context = {
            "profiles": {},
            "workstreams": {},
            "timesheet_summary": {},
            "relationships": {
                "profile_workstream": {},
                "workstream_dependencies": {}
            }
        }
        self.query_context = QueryContext(
            relevant_timeframe="current_month",
            focus_areas=[],
            access_level="project_manager"
        )

    def update_context(self, data_type: str, data: Dict[str, Any]) -> None:
        """Update a specific section of the context with new data."""
        if data_type == "profiles":
            for profile_id, profile_data in data.items():
                anonymized_id = self.data_store.store_profile(profile_data)
                self.context["profiles"][anonymized_id] = profile_data
        elif data_type == "workstreams":
            for workstream_id, workstream_data in data.items():
                anonymized_id = self.data_store.store_workstream(workstream_data)
                self.context["workstreams"][anonymized_id] = workstream_data
        elif data_type == "timesheet_entries":
            for entry_id, entry_data in data.items():
                anonymized_id = self.data_store.store_timesheet(entry_data)
                if "timesheet_entries" not in self.context:
                    self.context["timesheet_entries"] = {}
                self.context["timesheet_entries"][anonymized_id] = entry_data
        
        self.metadata.last_updated = datetime.now()

    def get_context(self, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Retrieve context data, optionally filtered by focus areas."""
        # Get anonymized data from the data store
        anonymized_data = self.data_store.get_anonymized_data()
        
        if not focus_areas:
            return {
                **self.context,
                "anonymized_data": anonymized_data
            }
        
        filtered_context = {k: v for k, v in self.context.items() if k in focus_areas}
        filtered_anonymized = {k: v for k, v in anonymized_data.items() if k in focus_areas}
        
        return {
            **filtered_context,
            "anonymized_data": filtered_anonymized
        }

    def set_query_context(self, 
                         timeframe: Optional[str] = None,
                         focus_areas: Optional[List[str]] = None,
                         access_level: Optional[str] = None) -> None:
        """Update the query context parameters."""
        if timeframe:
            self.query_context.relevant_timeframe = timeframe
        if focus_areas is not None:
            self.query_context.focus_areas = focus_areas
        if access_level:
            self.query_context.access_level = access_level

    def add_relationship(self, rel_type: str, source_id: str, target_id: str) -> None:
        """Add a relationship between entities (e.g., profile-workstream)."""
        if rel_type == "profile_workstream":
            if source_id not in self.context["relationships"]["profile_workstream"]:
                self.context["relationships"]["profile_workstream"][source_id] = []
            if target_id not in self.context["relationships"]["profile_workstream"][source_id]:
                self.context["relationships"]["profile_workstream"][source_id].append(target_id)
        elif rel_type == "workstream_dependencies":
            if source_id not in self.context["relationships"]["workstream_dependencies"]:
                self.context["relationships"]["workstream_dependencies"][source_id] = []
            if target_id not in self.context["relationships"]["workstream_dependencies"][source_id]:
                self.context["relationships"]["workstream_dependencies"][source_id].append(target_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire MCP context to a dictionary."""
        return {
            "metadata": self.metadata.dict(),
            "context": self.context,
            "query_context": self.query_context.dict(),
            "anonymized_data": self.data_store.get_anonymized_data()
        }

    def to_json(self) -> str:
        """Convert the entire MCP context to a JSON string."""
        return json.dumps(self.to_dict(), default=str)

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Load MCP context from a dictionary."""
        self.metadata = MCPMetadata(**data["metadata"])
        self.context = data["context"]
        self.query_context = QueryContext(**data["query_context"])
        
        # Load data into the data store if anonymized data is present
        if "anonymized_data" in data:
            for profile in data["anonymized_data"].get("profiles", []):
                self.data_store.store_profile(profile)
            for workstream in data["anonymized_data"].get("workstreams", []):
                self.data_store.store_workstream(workstream)
            for timesheet in data["anonymized_data"].get("timesheets", []):
                self.data_store.store_timesheet(timesheet)

    @classmethod
    def from_json(cls, json_str: str) -> 'MCPContext':
        """Create an MCP context instance from a JSON string."""
        data = json.loads(json_str)
        instance = cls(data["metadata"]["project_name"])
        instance.load_from_dict(data)
        return instance

def get_mcp() -> MCPContext:
    """Create and return an MCPContext instance."""
    return MCPContext(project_name="Project Management Dashboard") 
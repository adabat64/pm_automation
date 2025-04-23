from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class WorkstreamStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkstreamPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Workstream(BaseModel):
    id: str = Field(..., description="Unique identifier for the workstream")
    name: str = Field(..., description="Name of the workstream")
    description: str = Field(..., description="Description of the workstream")
    status: str = Field(..., description="Current status of the workstream")
    estimated_hours: float = Field(..., description="Estimated hours for the workstream")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the workstream")
    assigned_profiles: List[str] = Field(
        default_factory=list,
        description="List of profile IDs assigned to this workstream"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "WS001",
                "name": "Project Planning",
                "description": "Initial project planning and setup",
                "status": "active",
                "estimated_hours": 100,
                "tags": ["planning", "setup", "management"],
                "assigned_profiles": ["P001", "P002"]
            }
        } 
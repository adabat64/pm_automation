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
    description: str = Field(..., description="Detailed description of the workstream")
    status: WorkstreamStatus = Field(
        default=WorkstreamStatus.PLANNED,
        description="Current status of the workstream"
    )
    priority: WorkstreamPriority = Field(
        default=WorkstreamPriority.MEDIUM,
        description="Priority level of the workstream"
    )
    total_budget_hours: float = Field(..., description="Total budgeted hours for the workstream")
    start_date: datetime = Field(..., description="Start date of the workstream")
    end_date: datetime = Field(..., description="End date of the workstream")
    assigned_profiles: List[str] = Field(
        default_factory=list,
        description="List of profile IDs assigned to this workstream"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of workstream IDs that this workstream depends on"
    )
    completion_percentage: float = Field(
        default=0.0,
        description="Percentage of completion (0-100)"
    )
    actual_hours: float = Field(
        default=0.0,
        description="Actual hours spent on the workstream"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags/categories for the workstream"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "WS001",
                "name": "Backend Development",
                "description": "Implement core backend services and APIs",
                "status": "in_progress",
                "priority": "high",
                "total_budget_hours": 400.0,
                "start_date": "2024-01-15T00:00:00",
                "end_date": "2024-03-31T00:00:00",
                "assigned_profiles": ["P001", "P002"],
                "dependencies": ["WS003"],
                "completion_percentage": 35.0,
                "actual_hours": 150.5,
                "tags": ["backend", "api", "development"]
            }
        } 
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Profile(BaseModel):
    id: str = Field(..., description="Unique identifier for the profile")
    name: str = Field(..., description="Full name of the team member")
    role: str = Field(..., description="Role/position in the project")
    workstreams: List[str] = Field(default_factory=list, description="List of workstream IDs this profile is assigned to")
    hourly_rate: float = Field(..., description="Hourly rate for budget calculations")
    allocated_hours: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of workstream_id to allocated hours"
    )
    skills: List[str] = Field(default_factory=list, description="List of skills and competencies")
    start_date: Optional[datetime] = Field(None, description="Start date on the project")
    end_date: Optional[datetime] = Field(None, description="End date on the project")
    utilization_target: float = Field(
        default=1.0,
        description="Target utilization percentage (1.0 = 100%)"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "P001",
                "name": "User_1",
                "role": "Role_1",
                "workstreams": ["WS001", "WS002"],
                "hourly_rate": 150.0,
                "allocated_hours": {
                    "WS001": 80.0,
                    "WS002": 40.0
                },
                "skills": ["Skill_1", "Skill_2", "Skill_3"],
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T00:00:00",
                "utilization_target": 0.8
            }
        } 
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ApprovalStatus(str, Enum):
    OPEN = "open"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class TimesheetEntry(BaseModel):
    id: str = Field(..., description="Unique identifier for the timesheet entry")
    date: datetime = Field(..., description="Date of the time entry")
    user_id: str = Field(..., description="ID of the profile/user")
    workstream_id: str = Field(..., description="ID of the workstream")
    hours: float = Field(..., description="Hours logged")
    notes: str = Field(..., description="Description of work done")
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.OPEN,
        description="Current approval status"
    )
    submitted_at: Optional[datetime] = Field(None, description="When the entry was submitted")
    approved_at: Optional[datetime] = Field(None, description="When the entry was approved")
    approved_by: Optional[str] = Field(None, description="ID of the approver")

    class Config:
        schema_extra = {
            "example": {
                "id": "TS001",
                "date": "2024-01-15T00:00:00",
                "user_id": "P001",
                "workstream_id": "WS001",
                "hours": 8.0,
                "notes": "[REDACTED]",
                "approval_status": "approved",
                "submitted_at": "2024-01-15T17:00:00",
                "approved_at": "2024-01-16T09:00:00",
                "approved_by": "P002"
            }
        }

class TimesheetSummary(BaseModel):
    total_hours: float = Field(..., description="Total hours logged")
    approved_hours: float = Field(..., description="Total approved hours")
    pending_hours: float = Field(..., description="Hours pending approval")
    by_workstream: dict = Field(..., description="Hours broken down by workstream")
    by_user: dict = Field(..., description="Hours broken down by user")
    date_range: tuple = Field(..., description="Start and end dates of the summary")

    class Config:
        schema_extra = {
            "example": {
                "total_hours": 160.0,
                "approved_hours": 120.0,
                "pending_hours": 40.0,
                "by_workstream": {
                    "WS001": 80.0,
                    "WS002": 80.0
                },
                "by_user": {
                    "P001": 100.0,
                    "P002": 60.0
                },
                "date_range": ["2024-01-01T00:00:00", "2024-01-31T00:00:00"]
            }
        } 
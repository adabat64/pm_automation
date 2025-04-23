from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class BudgetType(str, Enum):
    LABOR = "labor"
    NON_LABOR = "non_labor"
    TOTAL = "total"

class BudgetPeriod(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class BudgetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class BudgetEntry(BaseModel):
    id: str
    workstream_id: str
    profile_id: Optional[str] = None
    budget_type: BudgetType
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    planned_hours: Optional[float] = None
    planned_amount: float
    actual_hours: Optional[float] = None
    actual_amount: Optional[float] = None
    status: BudgetStatus = BudgetStatus.DRAFT
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class BudgetForecast(BaseModel):
    id: str
    workstream_id: str
    profile_id: Optional[str] = None
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    forecast_hours: Optional[float] = None
    forecast_amount: float
    confidence_level: float = Field(ge=0.0, le=1.0)
    assumptions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class BudgetSummary(BaseModel):
    workstream_id: str
    total_budget: float
    total_actual: float
    total_forecast: float
    variance: float
    variance_percentage: float
    by_period: Dict[str, Dict[str, float]]
    by_profile: Dict[str, Dict[str, float]]
    by_type: Dict[BudgetType, Dict[str, float]] 
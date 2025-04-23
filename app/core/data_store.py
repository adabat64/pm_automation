from typing import Dict, List, Any
import sqlite3
import pandas as pd
from pathlib import Path
import hashlib
import json
from datetime import datetime

class DataStore:
    def __init__(self, db_path: str = "local_data.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database with necessary tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    role TEXT,
                    rate REAL,
                    anonymized_id TEXT UNIQUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workstreams (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    estimated_hours REAL,
                    anonymized_id TEXT UNIQUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS timesheets (
                    id TEXT PRIMARY KEY,
                    date TEXT,
                    user_id TEXT,
                    workstream_id TEXT,
                    hours REAL,
                    notes TEXT,
                    approval_status TEXT,
                    anonymized_id TEXT UNIQUE,
                    FOREIGN KEY (user_id) REFERENCES profiles (id),
                    FOREIGN KEY (workstream_id) REFERENCES workstreams (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id TEXT PRIMARY KEY,
                    workstream_id TEXT,
                    profile_id TEXT,
                    budget_type TEXT,
                    period TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    planned_hours REAL,
                    planned_amount REAL,
                    actual_hours REAL,
                    actual_amount REAL,
                    status TEXT,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    anonymized_id TEXT UNIQUE,
                    FOREIGN KEY (workstream_id) REFERENCES workstreams (id),
                    FOREIGN KEY (profile_id) REFERENCES profiles (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budget_forecasts (
                    id TEXT PRIMARY KEY,
                    workstream_id TEXT,
                    profile_id TEXT,
                    period TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    forecast_hours REAL,
                    forecast_amount REAL,
                    confidence_level REAL,
                    assumptions TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    anonymized_id TEXT UNIQUE,
                    FOREIGN KEY (workstream_id) REFERENCES workstreams (id),
                    FOREIGN KEY (profile_id) REFERENCES profiles (id)
                )
            """)
    
    def _anonymize_id(self, original_id: str, prefix: str = "") -> str:
        """Create a consistent anonymized ID for a given original ID."""
        salt = "your_salt_here"  # In production, use a secure salt
        return prefix + hashlib.sha256((original_id + salt).encode()).hexdigest()[:8]
    
    def store_profile(self, profile_data: Dict[str, Any]) -> str:
        """Store a profile with anonymized data."""
        anonymized_id = self._anonymize_id(profile_data["id"], "P")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO profiles 
                (id, name, role, rate, anonymized_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                profile_data["id"],
                profile_data["name"],
                profile_data["role"],
                profile_data["rate"],
                anonymized_id
            ))
        return anonymized_id
    
    def store_workstream(self, workstream_data: Dict[str, Any]) -> str:
        """Store a workstream with anonymized data."""
        anonymized_id = self._anonymize_id(workstream_data["id"], "W")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO workstreams 
                (id, name, description, estimated_hours, anonymized_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                workstream_data["id"],
                workstream_data["name"],
                workstream_data["description"],
                workstream_data["estimated_hours"],
                anonymized_id
            ))
        return anonymized_id
    
    def store_timesheet(self, timesheet_data: Dict[str, Any]) -> str:
        """Store a timesheet entry with anonymized data."""
        anonymized_id = self._anonymize_id(timesheet_data["id"], "T")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO timesheets 
                (id, date, user_id, workstream_id, hours, notes, approval_status, anonymized_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timesheet_data["id"],
                timesheet_data["date"],
                timesheet_data["user_id"],
                timesheet_data["workstream_id"],
                timesheet_data["hours"],
                timesheet_data["notes"],
                timesheet_data["approval_status"],
                anonymized_id
            ))
        return anonymized_id
    
    def store_budget(self, budget_data: Dict[str, Any]) -> str:
        """Store a budget entry with anonymized data."""
        anonymized_id = self._anonymize_id(budget_data["id"], "B")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO budgets 
                (id, workstream_id, profile_id, budget_type, period, start_date, end_date, 
                planned_hours, planned_amount, actual_hours, actual_amount, status, notes, 
                created_at, updated_at, anonymized_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                budget_data["id"],
                budget_data["workstream_id"],
                budget_data.get("profile_id"),
                budget_data["budget_type"],
                budget_data["period"],
                budget_data["start_date"],
                budget_data["end_date"],
                budget_data.get("planned_hours"),
                budget_data["planned_amount"],
                budget_data.get("actual_hours"),
                budget_data.get("actual_amount"),
                budget_data["status"],
                budget_data.get("notes"),
                budget_data["created_at"],
                budget_data["updated_at"],
                anonymized_id
            ))
        return anonymized_id
    
    def store_budget_forecast(self, forecast_data: Dict[str, Any]) -> str:
        """Store a budget forecast with anonymized data."""
        anonymized_id = self._anonymize_id(forecast_data["id"], "F")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO budget_forecasts 
                (id, workstream_id, profile_id, period, start_date, end_date, 
                forecast_hours, forecast_amount, confidence_level, assumptions, 
                created_at, updated_at, anonymized_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                forecast_data["id"],
                forecast_data["workstream_id"],
                forecast_data.get("profile_id"),
                forecast_data["period"],
                forecast_data["start_date"],
                forecast_data["end_date"],
                forecast_data.get("forecast_hours"),
                forecast_data["forecast_amount"],
                forecast_data["confidence_level"],
                json.dumps(forecast_data["assumptions"]),
                forecast_data["created_at"],
                forecast_data["updated_at"],
                anonymized_id
            ))
        return anonymized_id
    
    def import_timesheet_csv(self, csv_path: str) -> List[str]:
        """Import timesheet data from a CSV file."""
        df = pd.read_csv(csv_path)
        anonymized_ids = []
        
        for _, row in df.iterrows():
            timesheet_data = {
                "id": str(row["id"]) if "id" in row else str(datetime.now().timestamp()),
                "date": row["date"],
                "user_id": row["user"],
                "workstream_id": row["task"],
                "hours": float(row["time"]),
                "notes": row["notes"],
                "approval_status": row["approval_status"]
            }
            anonymized_id = self.store_timesheet(timesheet_data)
            anonymized_ids.append(anonymized_id)
        
        return anonymized_ids
    
    def get_anonymized_data(self) -> Dict[str, Any]:
        """Retrieve all data in anonymized form."""
        with sqlite3.connect(self.db_path) as conn:
            profiles = pd.read_sql("SELECT * FROM profiles", conn)
            workstreams = pd.read_sql("SELECT * FROM workstreams", conn)
            timesheets = pd.read_sql("SELECT * FROM timesheets", conn)
            budgets = pd.read_sql("SELECT * FROM budgets", conn)
            forecasts = pd.read_sql("SELECT * FROM budget_forecasts", conn)
        
        return {
            "profiles": profiles.to_dict(orient="records"),
            "workstreams": workstreams.to_dict(orient="records"),
            "timesheets": timesheets.to_dict(orient="records"),
            "budgets": budgets.to_dict(orient="records"),
            "forecasts": forecasts.to_dict(orient="records")
        }
    
    def get_original_data(self, anonymized_id: str) -> Dict[str, Any]:
        """Retrieve original data for a given anonymized ID."""
        with sqlite3.connect(self.db_path) as conn:
            # Check each table for the anonymized ID
            for table in ["profiles", "workstreams", "timesheets", "budgets", "budget_forecasts"]:
                result = conn.execute(f"""
                    SELECT * FROM {table} WHERE anonymized_id = ?
                """, (anonymized_id,)).fetchone()
                if result:
                    return dict(zip([col[0] for col in conn.description], result))
        return None
    
    def get_budget_summary(self, workstream_id: str) -> Dict[str, Any]:
        """Get a summary of budget data for a workstream."""
        with sqlite3.connect(self.db_path) as conn:
            # Get budget entries
            budgets = pd.read_sql("""
                SELECT * FROM budgets WHERE workstream_id = ?
            """, conn, params=(workstream_id,))
            
            # Get forecasts
            forecasts = pd.read_sql("""
                SELECT * FROM budget_forecasts WHERE workstream_id = ?
            """, conn, params=(workstream_id,))
            
            # Calculate totals
            total_budget = budgets["planned_amount"].sum()
            total_actual = budgets["actual_amount"].sum() if "actual_amount" in budgets else 0
            total_forecast = forecasts["forecast_amount"].sum() if not forecasts.empty else 0
            
            # Calculate variance
            variance = total_actual - total_budget
            variance_percentage = (variance / total_budget * 100) if total_budget > 0 else 0
            
            # Group by period
            by_period = {}
            for _, row in budgets.iterrows():
                period = row["period"]
                if period not in by_period:
                    by_period[period] = {"planned": 0, "actual": 0}
                by_period[period]["planned"] += row["planned_amount"]
                if row["actual_amount"]:
                    by_period[period]["actual"] += row["actual_amount"]
            
            # Group by profile
            by_profile = {}
            for _, row in budgets.iterrows():
                if row["profile_id"]:
                    profile_id = row["profile_id"]
                    if profile_id not in by_profile:
                        by_profile[profile_id] = {"planned": 0, "actual": 0}
                    by_profile[profile_id]["planned"] += row["planned_amount"]
                    if row["actual_amount"]:
                        by_profile[profile_id]["actual"] += row["actual_amount"]
            
            # Group by type
            by_type = {}
            for _, row in budgets.iterrows():
                budget_type = row["budget_type"]
                if budget_type not in by_type:
                    by_type[budget_type] = {"planned": 0, "actual": 0}
                by_type[budget_type]["planned"] += row["planned_amount"]
                if row["actual_amount"]:
                    by_type[budget_type]["actual"] += row["actual_amount"]
            
            return {
                "workstream_id": workstream_id,
                "total_budget": total_budget,
                "total_actual": total_actual,
                "total_forecast": total_forecast,
                "variance": variance,
                "variance_percentage": variance_percentage,
                "by_period": by_period,
                "by_profile": by_profile,
                "by_type": by_type
            } 
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from app.utils.data_privacy import DataPrivacyManager

class ProjectDataAnalyzer:
    """Analyzes project data and prepares it for LLM queries."""
    
    def __init__(self, data_dir: str = "real_data"):
        self.data_dir = Path(data_dir)
        self.privacy_manager = DataPrivacyManager()
        
        # Load data
        self.timesheets = self._load_json("timesheets.json") or []
        self.budgets = self._load_json("budget_relations.json") or {}
        self.summary = self._load_json("timesheet_summary.json") or {}
    
    def _load_json(self, filename: str) -> Optional[Dict]:
        """Load JSON file from data directory."""
        file_path = self.data_dir / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def get_project_overview(self) -> Dict[str, Any]:
        """Get a high-level overview of the project."""
        df = pd.DataFrame(self.timesheets)
        
        return {
            "total_hours": self.summary.get("total_hours", 0),
            "date_range": self.summary.get("date_range", {}),
            "workstreams": {
                ws: {
                    "hours": hours,
                    "budget": self.budgets.get(ws, {}).get("budget_hours", 0),
                    "remaining_hours": self.budgets.get(ws, {}).get("budget_hours", 0) - hours
                }
                for ws, hours in self.summary.get("hours_by_workstream", {}).items()
            },
            "approval_status": self.summary.get("hours_by_status", {}),
            "total_entries": len(self.timesheets)
        }
    
    def get_workstream_analysis(self, workstream: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed analysis of workstream(s)."""
        df = pd.DataFrame(self.timesheets)
        
        if workstream:
            # Filter for specific workstream
            df = df[df['workstream'] == workstream]
        
        analysis = {
            "total_hours": df['hours'].sum(),
            "average_hours_per_day": df.groupby('date')['hours'].sum().mean(),
            "hours_by_user": df.groupby('user')['hours'].sum().to_dict(),
            "hours_by_status": df.groupby('approval_status')['hours'].sum().to_dict(),
            "date_range": {
                "start": df['date'].min(),
                "end": df['date'].max()
            }
        }
        
        if workstream and workstream in self.budgets:
            budget = self.budgets[workstream]
            analysis["budget"] = {
                "total_budget_hours": budget["budget_hours"],
                "hours_spent": analysis["total_hours"],
                "hours_remaining": budget["budget_hours"] - analysis["total_hours"],
                "budget_spent": analysis["total_hours"] * budget["hourly_rate"],
                "budget_remaining": (budget["budget_hours"] - analysis["total_hours"]) * budget["hourly_rate"]
            }
        
        return analysis
    
    def get_user_analysis(self, user: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed analysis of user(s)."""
        df = pd.DataFrame(self.timesheets)
        
        if user:
            # Filter for specific user
            df = df[df['user'] == user]
        
        return {
            "total_hours": df['hours'].sum(),
            "hours_by_workstream": df.groupby('workstream')['hours'].sum().to_dict(),
            "hours_by_status": df.groupby('approval_status')['hours'].sum().to_dict(),
            "date_range": {
                "start": df['date'].min(),
                "end": df['date'].max()
            },
            "average_hours_per_day": df.groupby('date')['hours'].sum().mean()
        }
    
    def get_budget_analysis(self) -> Dict[str, Any]:
        """Get detailed budget analysis."""
        df = pd.DataFrame(self.timesheets)
        
        analysis = {}
        for workstream, budget in self.budgets.items():
            ws_data = df[df['workstream'] == workstream]
            hours_spent = ws_data['hours'].sum()
            
            analysis[workstream] = {
                "budget_hours": budget["budget_hours"],
                "hours_spent": hours_spent,
                "hours_remaining": budget["budget_hours"] - hours_spent,
                "budget_spent": hours_spent * budget["hourly_rate"],
                "budget_remaining": (budget["budget_hours"] - hours_spent) * budget["hourly_rate"],
                "completion_percentage": (hours_spent / budget["budget_hours"]) * 100 if budget["budget_hours"] > 0 else 0
            }
        
        return analysis
    
    def get_trend_analysis(self, metric: str = "hours", period: str = "daily") -> Dict[str, Any]:
        """Get trend analysis for a specific metric."""
        df = pd.DataFrame(self.timesheets)
        df['date'] = pd.to_datetime(df['date'])
        
        if period == "daily":
            grouped = df.groupby('date')[metric].sum()
        elif period == "weekly":
            grouped = df.groupby(df['date'].dt.isocalendar().week)[metric].sum()
        else:  # monthly
            grouped = df.groupby(df['date'].dt.to_period('M'))[metric].sum()
        
        # Convert timestamps to strings in the trend data
        trend_dict = {str(k): float(v) for k, v in grouped.to_dict().items()}
        
        return {
            "trend": trend_dict,
            "average": float(grouped.mean()),
            "total": float(grouped.sum()),
            "period": period
        }
    
    def prepare_llm_context(self) -> Dict[str, Any]:
        """Prepare comprehensive context for LLM queries."""
        return {
            "project_overview": self.get_project_overview(),
            "workstream_analysis": self.get_workstream_analysis(),
            "budget_analysis": self.get_budget_analysis(),
            "trend_analysis": {
                "daily": self.get_trend_analysis(period="daily"),
                "weekly": self.get_trend_analysis(period="weekly"),
                "monthly": self.get_trend_analysis(period="monthly")
            }
        }

def format_llm_prompt(query: str, context: Dict[str, Any]) -> str:
    """Format the context and query for the LLM."""
    return f"""Based on the following project data, please answer this question: {query}

Project Overview:
- Total Hours: {context['project_overview']['total_hours']:.2f}
- Date Range: {context['project_overview']['date_range']['start']} to {context['project_overview']['date_range']['end']}
- Total Entries: {context['project_overview']['total_entries']}

Workstream Summary:
{json.dumps(context['workstream_analysis'], indent=2)}

Budget Summary:
{json.dumps(context['budget_analysis'], indent=2)}

Trend Analysis:
{json.dumps(context['trend_analysis'], indent=2)}

Please provide a detailed answer based on this data."""

def analyze_project_data(query: str) -> str:
    """Analyze project data based on a natural language query."""
    analyzer = ProjectDataAnalyzer()
    context = analyzer.prepare_llm_context()
    prompt = format_llm_prompt(query, context)
    
    # Here you would send the prompt to your LLM
    # For now, we'll return the formatted prompt
    return prompt

if __name__ == "__main__":
    # Example usage
    query = "How many hours have been spent on each workstream and what's the budget status?"
    prompt = analyze_project_data(query)
    print(prompt) 